"""Klasyfikator owoców — prosta aplikacja desktopowa (Tkinter + PyTorch)."""

import argparse
import csv
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

import numpy as np
from PIL import Image, ImageOps, ImageTk

MODEL_PATH = Path(__file__).with_name("fruit_effnet.pt")
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".gif", ".tif", ".tiff"}
PREVIEW_SIZE = 500
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

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.mean = self.mean.to(self.device)
        self.std = self.std.to(self.device)

    def przewidz(self, sciezka):
        start = time.perf_counter()

        obraz = ImageOps.exif_transpose(Image.open(sciezka)).convert("RGB")
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

        root.title("Klasyfikator owoców")
        root.geometry("1100x720")
        root.minsize(1000, 680)

        gora = tk.Frame(root)
        gora.pack(fill="both", expand=True, padx=16, pady=16)

        rzad = tk.Frame(gora)
        rzad.pack(expand=True)

        lewa = tk.Frame(rzad)
        lewa.pack(side="left", fill="both", expand=True)
        self.podglad = tk.Label(lewa, width=PREVIEW_SIZE, height=PREVIEW_SIZE, bg="#e0e0e0", bd=1, relief="solid")
        self.podglad.pack(anchor="n")
        self.pusty = ImageTk.PhotoImage(Image.new("RGB", (PREVIEW_SIZE, PREVIEW_SIZE), "#e0e0e0"))
        self.podglad.configure(image=self.pusty)

        prawa = tk.Frame(rzad)
        prawa.pack(side="left", fill="both", expand=True, padx=(20, 0))
        srodek = tk.Frame(prawa)
        srodek.pack()
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

        root.after(100, self.wczytaj_model)

    def wczytaj_model(self):
        self.status.configure(text="Wczytywanie modelu...")
        self.root.update_idletasks()
        try:
            self.model = Klasyfikator()
        except Exception as blad:
            messagebox.showerror("Błąd", f"Nie udało się wczytać modelu:\n{blad}")
            self.status.configure(text="Model nie jest wczytany")
            return
        self.status.configure(text="Model gotowy")
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
            obraz = ImageOps.exif_transpose(Image.open(sciezka)).convert("RGB")
            obraz = ImageOps.pad(obraz, (PREVIEW_SIZE, PREVIEW_SIZE), color="#e0e0e0", method=Image.LANCZOS)
            self.obrazek = ImageTk.PhotoImage(obraz)
        except Exception as blad:
            messagebox.showerror("Błąd", f"Nie można otworzyć zdjęcia:\n{blad}")
            return
        self.sciezka = sciezka
        self.podglad.configure(image=self.obrazek)
        self.klasyfikuj()

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
        self.podglad.configure(image=self.pusty)
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

    poprawne = 0
    start = time.perf_counter()
    with open(plik_csv, "w", encoding="utf-8-sig", newline="") as plik:
        zapis = csv.writer(plik)
        zapis.writerow(["plik", "prawdziwa", "przewidziana", "pewnosc", "poprawnie", "czas_ms"])
        for i, (sciezka, prawdziwa) in enumerate(zdjecia, 1):
            wynik, czas = model.przewidz(sciezka)
            klasa, pewnosc = wynik[0]
            trafione = klasa == prawdziwa
            poprawne += trafione
            zapis.writerow([
                sciezka.relative_to(katalog), prawdziwa, klasa,
                f"{pewnosc:.3f}", "tak" if trafione else "nie", f"{czas:.0f}",
            ])
            if i % 100 == 0:
                print(f"{i}/{len(zdjecia)}", end="\r", flush=True)

    print(f"\nzdjęć: {len(zdjecia)}")
    print(f"accuracy: {poprawne / len(zdjecia):.3f} ({poprawne}/{len(zdjecia)})")
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
