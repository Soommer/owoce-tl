# Klasyfikator owoców

Prosta aplikacja okienkowa (Tkinter) rozpoznająca 10 rodzajów owoców na zdjęciach.
Model: EfficientNet-B0 douczony na zbiorze
[Fruit Classification 10-Class (Kaggle)](https://www.kaggle.com/datasets/karimabdulnabi/fruit-classification10-class)
(trening w `owoce_effnet.ipynb`), wagi zapisane w `fruit_effnet.pt`.

## Wyniki

| zbiór | zdjęć | accuracy |
| :--- | ---: | ---: |
| walidacja (15% `train`, wybór najlepszej epoki) | 346 | 0,974 |
| test, bez TTA (tak liczy aplikacja) | 1025 | **0,938** (961/1025) |
| test, z TTA (średnia z oryginału i odbicia, tylko notebook) | 1025 | 0,936 |

Główny wynik projektu to **0,938 na zbiorze testowym**. Test nie był używany ani do
treningu, ani do wyboru epoki. TTA nie poprawia wyniku, więc aplikacja go nie stosuje.

## Uruchomienie

```
pip install -r requirements.txt
python app.py
```

Model wczytuje się w tle przez kilka sekund. W tym czasie okno działa, a pasek stanu
pokazuje „Wczytywanie modelu...”. Po wczytaniu pojawia się „Model gotowy (CPU)”
albo „Model gotowy (CUDA)”.

### GPU

Aplikacja używa karty NVIDIA, jeśli jest dostępna. Na starcie robi próbny przebieg
sieci. Jeśli GPU nie działa (np. karta RTX 50xx z wersją torcha bez obsługi tej
architektury), aplikacja wypisuje ostrzeżenie w konsoli i liczy na CPU. Do RTX 50xx
potrzebny jest torch ≥ 2.7 w wersji z CUDA 12.8 lub nowszej. Na CPU aplikacja działa
w pełni, jedno zdjęcie trwa kilkadziesiąt ms.

## Obsługa

Okno otwiera się zmaksymalizowane. Na starcie w prawej części jest krótka
podpowiedź, co zrobić.

- **Wybierz zdjęcie** – wybór pliku z dysku, od razu pokazuje wynik. Jeśli model
  jeszcze się wczytuje, wynik pojawi się zaraz po wczytaniu.
- **Ponów** – liczy jeszcze raz to samo zdjęcie.
- **Wyczyść** – usuwa zdjęcie i wynik.

Wynik to nazwa klasy z polskim tłumaczeniem w nawiasie, np. `apple (jabłko)`,
oraz pewność i czas obliczeń. Pod spodem jest 10 pasków z prawdopodobieństwami
klas, od największego do najmniejszego. Kolor paska oznacza pewność:

- zielony – od 60%,
- pomarańczowy – 20–60%,
- szary – poniżej 20%.

Pewność to wyjście softmax modelu, a nie gwarancja poprawnej odpowiedzi.

## Raport z testu

Osobny tryb (bez okna) liczy accuracy na katalogu zdjęć, w którym podkatalogi
to nazwy klas (literówki z Kaggle `pinenapple` i `stawberries` są rozpoznawane):

```
python app.py --raport ../archive/MY_data/test
python app.py --raport ../archive/MY_data/test --out wyniki.csv
```

Ukośniki `/` działają zarówno w Linuksie, jak i w Windowsie.

Wynik zapisuje się do CSV (kolumny: `plik`, `prawdziwa`, `przewidziana`,
`pewnosc`, `poprawnie`, `czas_ms`), a w konsoli pojawia się accuracy.
Pliku, którego nie da się odczytać, raport nie przerywa. Taki plik trafia do CSV
z `poprawnie = błąd`, jest wypisany w konsoli i nie wlicza się do accuracy.

Plik `wyniki.csv` w repozytorium to taki raport dla 1025 zdjęć testowych:
**0,938 (961/1025)**, około 46 ms na zdjęcie na CPU (wczytanie pliku, skalowanie
i sieć).

## Jak działa rozpoznawanie

1. Zdjęcie jest obracane zgodnie z EXIF, zamieniane na RGB i skalowane do 224×224
   (tak samo w treningu i w aplikacji).
2. Wartości pikseli dzielone przez 255 i normalizowane średnią/odchyleniem ImageNet
   (zapisanymi w checkpoincie).
3. Sieć zwraca prawdopodobieństwa 10 klas (softmax); wybierana jest największa.

Lista klas, rozmiar wejścia i parametry normalizacji są zapisane w `fruit_effnet.pt`,
więc kod nie musi ich powtarzać.

## Trening (notebook)

```
pip install -r requirements-notebook.txt
```

Notebook oczekuje katalogu z podkatalogami `train/`, `test/` i `predict/`.
Domyślna ścieżka to `/workspace/data/owoce`, a zmienia się ją zmienną środowiskową
`OWOCE_DATA`, np. `OWOCE_DATA=../archive/MY_data jupyter notebook`. Komórki
`!ls` i `!nvidia-smi` są tylko informacyjne i można je pominąć. Notebook zapisuje
`fruit_effnet.pt` oraz `predykcje.csv` (predykcje dla 48 zdjęć z `predict/`).

## Pliki

```
app.py                     aplikacja (GUI + raport)
fruit_effnet.pt            wagi modelu
owoce_effnet.ipynb         trening i analiza wyników
wyniki.csv                 raport app.py dla zbioru testowego (1025 zdjęć)
konspekt_projektu.md       konspekt projektu
requirements.txt           biblioteki aplikacji
requirements-notebook.txt  dodatkowe biblioteki do notebooka
LICENSE                    licencja projektu (Apache 2.0)
```

`predykcje.csv` nie jest w repozytorium. Powstaje po uruchomieniu notebooka.

Model korzysta z architektury EfficientNet-B0 z biblioteki torchvision
(licencja BSD-3-Clause).
