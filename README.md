# Klasyfikator owoców

Prosta aplikacja okienkowa (Tkinter) rozpoznająca 10 rodzajów owoców na zdjęciach.
Model: EfficientNet-B0 douczony na zbiorze z Kaggle (trening w `owoce_effnet.ipynb`),
wagi zapisane w `fruit_effnet.pt`.

## Uruchomienie

```
pip install -r requirements.txt
python app.py
```

Przy pierwszym uruchomieniu wczytanie modelu zajmuje kilka sekund.

## Obsługa

Okno otwiera się zmaksymalizowane. Na starcie w prawej części jest krótka
podpowiedź, co zrobić.

- **Wybierz zdjęcie** – wybór pliku z dysku, od razu pokazuje wynik.
- **Ponów** – liczy jeszcze raz to samo zdjęcie.
- **Wyczyść** – usuwa zdjęcie i wynik.

Wynik to nazwa klasy z polskim tłumaczeniem w nawiasie, np. `apple (jabłko)`,
oraz pewność i czas obliczeń. Pod spodem jest 10 pasków z prawdopodobieństwami
klas, od największego do najmniejszego. Kolor paska oznacza pewność:

- zielony – od 60%,
- pomarańczowy – 20–60%,
- szary – poniżej 20%.

## Raport z testu

Osobny tryb (bez okna) liczy accuracy na katalogu zdjęć, w którym podkatalogi
to nazwy klas:

```
python app.py --raport ..\archive\MY_data\test
python app.py --raport ..\archive\MY_data\test --out wyniki.csv
```

Wynik zapisuje się do CSV (kolumny: `plik`, `prawdziwa`, `przewidziana`,
`pewnosc`, `poprawnie`, `czas_ms`), a w konsoli pojawia się accuracy.

Na 1025 zdjęciach testowych: **0,938 (961/1025)**, około 46 ms na zdjęcie (CPU).

## Jak działa rozpoznawanie

1. Zdjęcie jest obracane zgodnie z EXIF, zamieniane na RGB i skalowane do 224×224.
2. Wartości pikseli dzielone przez 255 i normalizowane średnią/odchyleniem z treningu.
3. Sieć zwraca prawdopodobieństwa 10 klas (softmax); wybierana jest największa.

Lista klas, rozmiar wejścia i parametry normalizacji są zapisane w `fruit_effnet.pt`,
więc kod nie musi ich powtarzać.

## Pliki

```
app.py                aplikacja (GUI + raport)
fruit_effnet.pt       wagi modelu
owoce_effnet.ipynb    trening i analiza wyników
predykcje.csv         wynik dla 48 zdjęć bez etykiet (z notebooka)
konspekt_projektu.md  konspekt projektu
requirements.txt      biblioteki
LICENSE               licencja projektu (Apache 2.0)
```

Model korzysta z architektury EfficientNet-B0 z biblioteki torchvision
(licencja BSD-3-Clause).
