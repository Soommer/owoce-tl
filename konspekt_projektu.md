# Klasyfikacja owoców na podstawie zdjęć
**Konspekt Projektu (v1.1)**

---

## 1. Temat projektu
Tematem projektu jest stworzenie aplikacji wykorzystującej metody uczenia maszynowego do rozpoznawania owoców na podstawie zdjęć. 

Projekt obejmie:
* Przygotowanie danych,
* Budowę i trenowanie modelu,
* Sprawdzenie jego skuteczności,
* Stworzenie prostego interfejsu graficznego do obsługi programu.

---

## 2. Cel projektu
Głównym celem jest stworzenie działającej aplikacji, która automatycznie klasyfikuje zdjęcia owoców do odpowiednich kategorii.

Model będzie trenowany na przygotowanym zbiorze zdjęć, a następnie sprawdzony na obrazach, których nie wykorzystywano podczas treningu. Aplikacja umożliwi wybranie zdjęcia z komputera i wyświetli przewidywaną klasę owocu oraz pewność, z jaką dany owoc należy do wybranej grupy.

---

## 3. Opis problemu
Rozpoznawanie owoców na zdjęciach jest przykładem zadania klasyfikacji obrazów. W tym przypadku wejściem modelu będzie obraz, a wynikiem jedna z dostępnych kategorii owoców.

Model powinien nauczyć się rozpoznawać cechy charakterystyczne dla poszczególnych klas, takie jak:
* Kolor,
* Kształt,
* Wzory widoczne na powierzchni owocu.

Nie będziemy ręcznie ustalać wszystkich tych cech — sieć neuronowa będzie uczyć się ich na podstawie przykładów dostarczonych podczas treningu. W projekcie zostanie wykorzystane **uczenie nadzorowane**, ponieważ zdjęcia treningowe są przypisane do określonych kategorii.

---

## 4. Źródło i przygotowanie danych
Do projektu zostanie wykorzystany zbiór danych dostępny na platformie Kaggle:
> 🔗 [Fruit Classification (10 Class) – Kaggle](https://www.kaggle.com/datasets/karimabdulnabi/fruit-classification10-class)

Zbiór dotyczy klasyfikacji dziesięciu kategorii owoców. Przed rozpoczęciem treningu sprawdzimy jego dokładną strukturę, liczbę zdjęć w poszczególnych klasach oraz format plików.

Dane są zorganizowane w folderach:
* `train` – zdjęcia wykorzystywane do uczenia modelu.
* `test` – zdjęcia przeznaczone do końcowej oceny skuteczności modelu, o ile zawierają prawidłowe etykiety klas.
* `predict` – zdjęcia, na których program będzie wykonywał przewidywania.

---

## 5. Plan realizacji
Projekt zostanie zrealizowany w kilku etapach:

1. Pobranie i analiza zbioru zdjęć z platformy Kaggle.
2. Przygotowanie danych do trenowania i testowania modelu.
3. Opracowanie własnej sieci neuronowej do klasyfikacji obrazów.
4. Wytrenowanie modelu z wykorzystaniem biblioteki PyTorch.
5. Stworzenie interfejsu graficznego umożliwiającego wybór zdjęcia i wyświetlenie wyniku rozpoznawania.
6. Integracja interfejsu z wytrenowanym modelem.
7. Przetestowanie modelu na zdjęciach testowych i ocena jego skuteczności.
8. Analiza błędów klasyfikacji.
9. Przeprowadzenie końcowych testów aplikacji i przygotowanie dokumentacji projektu.

---

## 6. Metoda uczenia maszynowego
Zamiast uczyć sieć od zera, projekt wykorzysta sieć **EfficientNet-B0** wytrenowaną wcześniej na 1,28 mln zdjęć z ImageNetu. Sieć zostanie douczona na danych z platformy Kaggle.

> **Transfer Learning (uczenie transferowe)** polega na tym, że model wytrenowany na jednym, zwykle dużym zadaniu wykorzystujemy jako punkt startowy do innego, pokrewnego zadania. Nie uczymy sieci od zera — przejmujemy jej wiedzę (wagi) i dopasowujemy ją do nowych danych.

Z uwagi na dość małą liczbę danych w każdej klasie, powyższe podejście wydaje się najbardziej optymalne w celu uzyskania najlepszego modelu.

---

## 7. Technologie i narzędzia
W projekcie planujemy wykorzystać:

| Narzędzie / Biblioteka | Zastosowanie |
| :--- | :--- |
| **Python** | Główny język programowania |
| **PyTorch** | Budowa, trening i wykorzystanie sieci neuronowej |
| **Pillow (PIL)** | Otwieranie i wstępne przetwarzanie zdjęć |
| **NumPy** | Operacje na danych liczbowych |
| **scikit-learn** | Obliczanie wybranych miar oceny klasyfikacji (np. raportu klasyfikacji) |
| **Tkinter** | Stworzenie interfejsu graficznego aplikacji |
| **Matplotlib** | Tworzenie wykresów, wizualizacja etapu szkolenia modelu |

*Dokładny zestaw bibliotek może zostać nieznacznie zmieniony w trakcie realizacji, jeśli okaże się to potrzebne.*

---

## 8. Plan treningu i oceny modelu
Po przygotowaniu danych model zostanie wytrenowany na zbiorze treningowym. W trakcie uczenia będziemy zapisywać wartość funkcji straty oraz skuteczność klasyfikacji na zbiorze treningowym i walidacyjnym. Pozwoli to ocenić, czy model rzeczywiście się uczy i czy nie zaczyna nadmiernie dopasowywać do danych treningowych (overfitting).

Po zakończeniu prac nad modelem przeprowadzimy końcową ocenę na zbiorze testowym, który nie będzie wykorzystywany do dobierania parametrów.

### Metryki oceny:
* **Accuracy** – odsetek poprawnie sklasyfikowanych zdjęć.
* **Precision** – informacja o tym, jak często przewidywanie danej klasy było poprawne.
* **Recall** – informacja o tym, jaką część przykładów danej klasy model poprawnie rozpoznał.
* **Macierz pomyłek (Confusion Matrix)** – zestawienie prawidłowych klas z klasami przewidzianymi przez model.

Model zostanie zapisany po treningu do pliku, a aplikacja będzie go wczytywać podczas uruchamiania. Dzięki temu nie będzie konieczne trenowanie sieci za każdym razem, gdy użytkownik wybierze nowe zdjęcie.

---

## 9. Interfejs graficzny aplikacji
Ostatnim etapem będzie przygotowanie prostej aplikacji desktopowej w bibliotece **Tkinter**.

### Interfejs będzie umożliwiał:
* Uruchomienie programu.
* Wybranie zdjęcia z dysku za pomocą okna dialogowego.
* Wyświetlenie wybranego obrazu w oknie aplikacji.
* Uruchomienie klasyfikacji przez wczytany model.
* Wyświetlenie przewidywanej kategorii owocu.
* Przedstawienie wyników dla poszczególnych klas (np. w postaci procentów).

*Wyniki procentowe będą prezentowane jako wyniki modelu dla poszczególnych klas, a nie jako gwarancja prawdopodobieństwa poprawnej odpowiedzi.*

---

## 10. Podział obowiązków w zespole
Projekt zostanie podzielony pomiędzy cztery osoby, z których każda będzie odpowiedzialna za określony etap realizacji:

1. **Przygotowanie danych:**
   * Pobranie i analiza struktury zbioru,
   * Sprawdzenie liczby klas i zdjęć w poszczególnych klasach,
   * Przygotowanie danych do treningu i walidacji.

2. **Budowa i trening modelu:**
   * Opracowanie architektury sieci neuronowej w PyTorch,
   * Przygotowanie procesu uczenia,
   * Dobór parametrów,
   * Trenowanie modelu oraz zapisanie jego najlepszej wersji.

3. **Testowanie i analiza wyników:**
   * Przygotowanie procesu oceny modelu,
   * Obliczenie wybranych miar skuteczności.

4. **Interfejs graficzny:**
   * Przygotowanie okna aplikacji w Tkinter,
   * Dodanie wyboru i wyświetlania zdjęć,
   * Połączenie interfejsu z wytrenowanym modelem,
   * Prezentacja wyników klasyfikacji.

---

## 11. Wstępna hipoteza
Zakładamy, że wytrenowana sieć będzie w stanie rozpoznawać owoce na zdjęciach z dokładnością wyższą niż przypadkowe przypisywanie klas.

Oczekujemy również, że jakość wyników będzie zależała od liczby i różnorodności zdjęć treningowych oraz podobieństwa wizualnego poszczególnych kategorii.

*Hipoteza zostanie zweryfikowana na podstawie wyników uzyskanych na zbiorze testowym. Ostateczna skuteczność modelu nie jest z góry zakładana i zostanie określona dopiero po przeprowadzeniu eksperymentów.*

---

## 12. Oczekiwany rezultat
Rezultatem projektu będzie działająca aplikacja komputerowa, która pozwoli użytkownikowi wczytać zdjęcie owocu i uzyskać wynik klasyfikacji.

Projekt pozwoli przećwiczyć cały podstawowy proces tworzenia rozwiązania z zakresu uczenia maszynowego: od przygotowania danych, przez implementację i trening modelu, aż po jego ocenę i wykorzystanie w aplikacji z interfejsem graficznym.