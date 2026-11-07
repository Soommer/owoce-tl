"""Klasyfikator owoców — prosta aplikacja desktopowa (Tkinter + PyTorch)."""

import argparse
import csv
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import numpy as np
from PIL import Image, ImageOps, ImageTk

MODEL_PATH = Path(__file__).with_name("fruit_effnet.pt")
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".gif", ".tif", ".tiff"}
PREVIEW_BG = "#e0e0e0"
PREVIEW_MAX = 1600  # zdjęcie trzymane w pamięci jest zmniejszane do tego rozmiaru, żeby skalowanie było szybkie
PREVIEW_MARGIN = 8
BAR_WIDTH = 200

START_TITLE = "Wybierz zdjęcie owocu"
START_INFO = "Kliknij przycisk „Wybierz zdjęcie” u dołu okna.\nProgram pokaże nazwę owocu i pewność."
START_STATUS = "Gotowe"

PL_NAMES = {
    "apple": "jabłko",
    "avocado": "awokado",
    "banana": "banan",
    "cherry": "wiśnia",
    "kiwi": "kiwi",
    "mango": "mango",
    "orange": "pomarańcza",
    "pineapple": "ananas",
    "strawberries": "truskawki",
    "watermelon": "arbuz",
}

# foldery w zbiorze z Kaggle mają literówki
FOLDER_NAMES = {"pinenapple": "pineapple", "stawberries": "strawberries"}


def wczytaj_obraz(sciezka):
    """Wczytuje zdjęcie jako RGB, obrócone zgodnie z EXIF, i od razu zamyka plik."""
    with Image.open(sciezka) as obraz:
        return ImageOps.exif_transpose(obraz).convert("RGB")


def kolor(pewnosc):
    if pewnosc >= 0.6:
        return "#2e7d32"
    if pewnosc >= 0.2:
        return "#e08b00"
    return "#9e9e9e"


class Klasyfikator:
    def __init__(self, plik=MODEL_PATH):
        import torch
        from torchvision.models import efficientnet_b0

        self.torch = torch
        dane = torch.load(plik, map_location="cpu", weights_only=True)

        self.klasy = dane["classes"]
        self.img_size = dane["img_size"]
        self.mean = torch.tensor(dane["mean"]).view(1, 3, 1, 1)
        self.std = torch.tensor(dane["std"]).view(1, 3, 1, 1)

        self.model = efficientnet_b0()
        self.model.classifier[1] = torch.nn.Linear(self.model.classifier[1].in_features, len(self.klasy))
        self.model.load_state_dict(dane["state_dict"])
        self.model.eval()

        # torch.cuda.is_available() może zwrócić True, a kernele i tak nie działają
        # (np. RTX 50xx na buildzie torcha bez sm_120) — dlatego GPU jest sprawdzane
        # próbnym przebiegiem, a w razie błędu używany jest CPU.
        self.device = torch.device("cpu")
        if torch.cuda.is_available():
            try:
                self._ustaw_urzadzenie(torch.device("cuda"))
                self._rozgrzej()
            except Exception as blad:
                print(f"GPU nie działa, używam CPU: {str(blad).splitlines()[0]}")
                self._ustaw_urzadzenie(torch.device("cpu"))
        if self.device.type == "cpu":
            self._rozgrzej()

    def _ustaw_urzadzenie(self, device):
        self.device = device
        self.model.to(device)
        self.mean = self.mean.to(device)
        self.std = self.std.to(device)

    def _rozgrzej(self):
        """Próbny przebieg: sprawdza urządzenie i usuwa jednorazowy koszt pierwszej predykcji."""
        x = self.torch.zeros(1, 3, self.img_size, self.img_size, device=self.device)
        with self.torch.no_grad():
            self.model((x - self.mean) / self.std).sum().item()

    def przewidz(self, sciezka):
        start = time.perf_counter()

        obraz = wczytaj_obraz(sciezka)
        obraz = obraz.resize((self.img_size, self.img_size), Image.BILINEAR)
        x = self.torch.from_numpy(np.array(obraz)).permute(2, 0, 1).unsqueeze(0)
        x = (x.to(self.device).float() / 255 - self.mean) / self.std

        with self.torch.no_grad():
            prawdopodobienstwa = self.torch.softmax(self.model(x), 1)[0].tolist()

        czas = (time.perf_counter() - start) * 1000
        wynik = sorted(zip(self.klasy, prawdopodobienstwa), key=lambda para: -para[1])
        return wynik, czas


class Okno:
    def __init__(self, root):
        self.root = root
        self.model = None
        self.sciezka = None
        self.oryginal = None  # zdjęcie (RGB) do podglądu, skalowane przy każdej zmianie rozmiaru
        self.obrazek = None   # referencja do PhotoImage, inaczej Tkinter go zgubi
        self._podglad_po = None

        root.title("Klasyfikator owoców")
        root.geometry("1100x720")
        root.minsize(840, 560)

        # kolumna 0 (podgląd) zabiera całe wolne miejsce, kolumna 1 (wyniki) ma stałą szerokość
        gora = tk.Frame(root)
        gora.pack(fill="both", expand=True, padx=16, pady=16)
        gora.columnconfigure(0, weight=1)
        gora.rowconfigure(0, weight=1)

        # Canvas nie zmienia swojego rozmiaru od zawartości, więc nie ma pętli
        # „większe zdjęcie → większy widżet → jeszcze większe zdjęcie”
        self.podglad = tk.Canvas(gora, bg=PREVIEW_BG, highlightthickness=1, highlightbackground="#bdbdbd")
        self.podglad.grid(row=0, column=0, sticky="nsew")
        self.podglad.bind("<Configure>", self._zaplanuj_podglad)

        prawa = tk.Frame(gora)
        prawa.grid(row=0, column=1, sticky="ns", padx=(20, 0))
        srodek = tk.Frame(prawa)
        srodek.pack(anchor="nw")
        self.wynik = tk.Label(srodek, text=START_TITLE, font=("Segoe UI", 18, "bold"))
        self.wynik.pack(anchor="w")
        self.info = tk.Label(srodek, text=START_INFO, fg="#555555", justify="left", wraplength=400)
        self.info.pack(anchor="w", pady=(0, 10))
        self.paski = tk.Frame(srodek)
        self.paski.pack(fill="x", anchor="w")
        tk.Frame(srodek, width=440, height=1).pack()  # stała szerokość, żeby paski nie przesuwały układu

        przyciski = tk.Frame(root)
        przyciski.pack(fill="x", padx=10, pady=(0, 10))
        ttk.Button(przyciski, text="Wybierz zdjęcie", command=self.wybierz).pack(side="left")
        ttk.Button(przyciski, text="Ponów", command=self.klasyfikuj).pack(side="left", padx=6)
        ttk.Button(przyciski, text="Wyczyść", command=self.wyczysc).pack(side="left")

        self.status = tk.Label(root, text=START_STATUS, anchor="w", fg="#555555")
        self.status.pack(fill="x", padx=10, pady=(0, 8))

        self.wczytaj_model()

    def wczytaj_model(self):
        """Wczytuje model w osobnym wątku, żeby okno nie zamarzało."""
        self.status.configure(text="Wczytywanie modelu...")
        self._ladowanie = None
        threading.Thread(target=self._laduj_w_tle, daemon=True).start()
        self.root.after(100, self._sprawdz_ladowanie)

    def _laduj_w_tle(self):
        # tu nie wolno dotykać widżetów Tkintera — wynik odbiera _sprawdz_ladowanie
        try:
            self._ladowanie = (Klasyfikator(), None)
        except Exception as blad:
            self._ladowanie = (None, blad)

    def _sprawdz_ladowanie(self):
        if self._ladowanie is None:
            self.root.after(100, self._sprawdz_ladowanie)
            return
        model, blad = self._ladowanie
        if blad is not None:
            messagebox.showerror("Błąd", f"Nie udało się wczytać modelu:\n{blad}")
            self.status.configure(text="Model nie jest wczytany")
            return
        self.model = model
        self.status.configure(text=f"Model gotowy ({model.device.type.upper()})")
        if self.sciezka:
            self.klasyfikuj()

    def wybierz(self):
        plik = filedialog.askopenfilename(
            title="Wybierz zdjęcie owocu",
            filetypes=[("Obrazy", "*.jpg *.jpeg *.png *.bmp *.webp *.gif *.tif *.tiff")],
        )
        if plik:
            self.otworz(Path(plik))

    def otworz(self, sciezka):
        try:
            obraz = wczytaj_obraz(sciezka)
            obraz.thumbnail((PREVIEW_MAX, PREVIEW_MAX), Image.LANCZOS)
        except Exception as blad:
            messagebox.showerror("Błąd", f"Nie można otworzyć zdjęcia:\n{blad}")
            return
        self.sciezka = sciezka
        self.oryginal = obraz
        self._rysuj_podglad()
        self.klasyfikuj()

    def _zaplanuj_podglad(self, _event=None):
        # przy przeciąganiu krawędzi okna <Configure> przychodzi wiele razy —
        # przerysowanie odkładamy, aż rozmiar przestanie się zmieniać
        if self._podglad_po is not None:
            self.root.after_cancel(self._podglad_po)
        self._podglad_po = self.root.after(40, self._rysuj_podglad)

    def _rysuj_podglad(self):
        self._podglad_po = None
        plotno = self.podglad
        szer, wys = plotno.winfo_width(), plotno.winfo_height()
        plotno.delete("all")
        if szer <= 2 * PREVIEW_MARGIN or wys <= 2 * PREVIEW_MARGIN:
            return
        if self.oryginal is None:
            plotno.create_text(szer // 2, wys // 2, text="Brak zdjęcia", fill="#9e9e9e", font=("Segoe UI", 14))
            return
        rozmiar = (szer - 2 * PREVIEW_MARGIN, wys - 2 * PREVIEW_MARGIN)
        obraz = ImageOps.contain(self.oryginal, rozmiar, method=Image.LANCZOS)
        self.obrazek = ImageTk.PhotoImage(obraz)
        plotno.create_image(szer // 2, wys // 2, image=self.obrazek)

    def klasyfikuj(self):
        if self.sciezka is None:
            return
        if self.model is None:
            self.status.configure(text="Model jeszcze się wczytuje...")
            return
        try:
            wynik, czas = self.model.przewidz(self.sciezka)
        except Exception as blad:
            messagebox.showerror("Błąd", f"Nie udało się rozpoznać zdjęcia:\n{blad}")
            return

        klasa, pewnosc = wynik[0]
        self.wynik.configure(text=f"{klasa} ({PL_NAMES.get(klasa, klasa)})", fg=kolor(pewnosc))
        self.info.configure(text=f"pewność: {pewnosc * 100:.1f}%   czas: {czas:.0f} ms")
        self.rysuj_paski(wynik)
        self.status.configure(text=self.sciezka.name)

    def rysuj_paski(self, wynik):
        for widget in self.paski.winfo_children():
            widget.destroy()
        for klasa, pewnosc in wynik:
            wiersz = tk.Frame(self.paski)
            wiersz.pack(fill="x", pady=1)
            tk.Label(wiersz, text=f"{klasa} ({PL_NAMES.get(klasa, klasa)})", width=24, anchor="w").pack(side="left")
            pasek = tk.Canvas(wiersz, width=BAR_WIDTH, height=14, bg="#dddddd", highlightthickness=0)
            pasek.pack(side="left")
            pasek.create_rectangle(0, 0, int(BAR_WIDTH * pewnosc), 14, fill=kolor(pewnosc), width=0)
            tk.Label(wiersz, text=f"{pewnosc * 100:4.1f}%", width=7, anchor="e").pack(side="left")

    def wyczysc(self):
        self.sciezka = None
        self.oryginal = None
        self._rysuj_podglad()
        self.wynik.configure(text=START_TITLE, fg="black")
        self.info.configure(text=START_INFO)
        for widget in self.paski.winfo_children():
            widget.destroy()
        self.status.configure(text=START_STATUS)


def raport(katalog, plik_csv):
    katalog = Path(katalog)
    if not katalog.is_dir():
        print(f"Nie ma takiego katalogu: {katalog}")
        return

    print("Wczytywanie modelu...")
    model = Klasyfikator()

    zdjecia = []
    for folder in sorted(katalog.iterdir()):
        if not folder.is_dir():
            continue
        klasa = FOLDER_NAMES.get(folder.name.lower(), folder.name.lower())
        if klasa not in model.klasy:
            print(f"Pomijam folder: {folder.name}")
            continue
        for plik in sorted(folder.iterdir()):
            if plik.suffix.lower() in IMAGE_EXT:
                zdjecia.append((plik, klasa))

    if not zdjecia:
        print("Brak zdjęć w podkatalogach klas.")
        return

    print(f"urządzenie: {model.device.type}")
    poprawne = 0
    bledy = []
    start = time.perf_counter()
    with open(plik_csv, "w", encoding="utf-8-sig", newline="") as plik:
        zapis = csv.writer(plik)
        zapis.writerow(["plik", "prawdziwa", "przewidziana", "pewnosc", "poprawnie", "czas_ms"])
        for i, (sciezka, prawdziwa) in enumerate(zdjecia, 1):
            nazwa = sciezka.relative_to(katalog)
            try:
                wynik, czas = model.przewidz(sciezka)
            except Exception as blad:
                # uszkodzony plik nie przerywa raportu — trafia do CSV jako "błąd"
                bledy.append((nazwa, blad))
                zapis.writerow([nazwa, prawdziwa, "", "", "błąd", ""])
                continue
            klasa, pewnosc = wynik[0]
            trafione = klasa == prawdziwa
            poprawne += trafione
            zapis.writerow([
                nazwa, prawdziwa, klasa,
                f"{pewnosc:.3f}", "tak" if trafione else "nie", f"{czas:.0f}",
            ])
            if i % 100 == 0:
                print(f"{i}/{len(zdjecia)}", end="\r", flush=True)

    ocenione = len(zdjecia) - len(bledy)
    print(f"\nzdjęć: {len(zdjecia)}")
    if bledy:
        print(f"nie udało się odczytać: {len(bledy)}")
        for nazwa, blad in bledy[:10]:
            print(f"  {nazwa}: {blad}")
        if len(bledy) > 10:
            print(f"  ... i {len(bledy) - 10} więcej (szczegóły w CSV)")
    if ocenione:
        print(f"accuracy: {poprawne / ocenione:.3f} ({poprawne}/{ocenione})")
    else:
        print("accuracy: brak (żadne zdjęcie nie zostało odczytane)")
    print(f"czas: {time.perf_counter() - start:.1f} s")
    print(f"zapisano: {plik_csv}")


def main():
    parser = argparse.ArgumentParser(description="Klasyfikator owoców")
    parser.add_argument("--raport", metavar="KATALOG", help="katalog z podkatalogami klas do policzenia accuracy")
    parser.add_argument("--out", default="raport.csv", help="plik CSV z wynikami (domyślnie raport.csv)")
    args = parser.parse_args()

    if args.raport:
        raport(args.raport, args.out)
        return

    root = tk.Tk()
    Okno(root)
    try:
        root.state("zoomed")
    except tk.TclError:
        root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")
    root.mainloop()


if __name__ == "__main__":
    main()
