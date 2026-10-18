# Klasyfikacja owoców na podstawie zdjęć

---

## 1. Temat projektu
Tematem projektu jest stworzenie aplikacji wykorzystującej metody uczenia maszynowego do rozpoznawania owoców na podstawie zdjęć. 

Projekt obejmie:
* Przygotowanie i analizę danych
* Budowę i trenowanie modelu uczenia maszynowego
* Weryfikację skuteczności modelu
* Stworzenie prostego interfejsu graficznego (GUI) do obsługi programu

---

## 2. Cel projektu
Głównym celem jest stworzenie działającej aplikacji, która automatycznie klasyfikuje zdjęcia owoców do odpowiednich kategorii.

Model będzie trenowany na przygotowanym zbiorze zdjęć, a następnie sprawdzony na obrazach, których nie wykorzystywano podczas treningu. Aplikacja umożliwi wybranie zdjęcia z komputera i wyświetli przewidywaną klasę owocu oraz pewność, z jaką dany owoc należy do wybranej grupy.

---

## 3. Opis problemu
Rozpoznawanie owoców na zdjęciach jest przykładem zadania klasyfikacji obrazów. W tym przypadku:
* **Wejście modelu:** Obraz (zdjęcie owocu)
* **Wyjście modelu:** Jedna z dostępnych kategorii owoców

Model powinien nauczyć się rozpoznawać cechy charakterystyczne dla poszczególnych klas, takie jak kolor, kształt i wzory widoczne na powierzchni owocu. Nie będziemy jednak ręcznie ustalać wszystkich tych cech — sieć neuronowa będzie uczyć się ich na podstawie przykładów dostarczonych podczas treningu.

> **Typ uczenia:** W projekcie zostanie wykorzystane **uczenie nadzorowane** (*supervised learning*), ponieważ zdjęcia treningowe są przypisane do określonych kategorii.

---

## 4. Źródło i przygotowanie danych
Do projektu zostanie wykorzystany zbiór danych dostępny na platformie Kaggle:
* **Zbiór danych:** [Fruit Classification 10-Class (Kaggle)](https://www.kaggle.com/datasets/karimabdulnabi/fruit-classification10-class)

Zbiór dotyczy klasyfikacji **10 kategorii owoców**. Przed rozpoczęciem treningu sprawdzimy jego dokładną strukturę, liczbę zdjęć w poszczególnych klasach oraz format plików.

### Podział zbioru danych:
| Folder | Przeznaczenie |
| :--- | :--- |
| `train` | Zdjęcia wykorzystywane do uczenia modelu |
| `test` | Zdjęcia przeznaczone do końcowej oceny skuteczności modelu |
| `predict` | Zdjęcia, na których program będzie wykonywał przewidywania |

---

## 5. Plan realizacji
Projekt zostanie zrealizowany w następujących etapach:

1. Pobranie i analiza zbioru zdjęć z platformy Kaggle.
2. Przygotowanie danych do trenowania i testowania modelu.
3. Opracowanie architektury/dostosowanie sieci neuronowej do klasyfikacji obrazów.
4. Wytrenowanie modelu z wykorzystaniem biblioteki **PyTorch**.
5. Stworzenie interfejsu graficznego umożliwiającego wybór zdjęcia i wyświetlenie wyniku rozpoznawania.
6. Integracja interfejsu z wytrenowanym modelem.
7. Przetestowanie modelu na zdjęciach testowych i ocena jego skuteczności.
8. Analiza błędów klasyfikacji.
9. Przeprowadzenie końcowych testów aplikacji i przygotowanie dokumentacji projektu.

---

## 6. Metoda uczenia maszynowego
Zamiast uczyć sieć od zera, projekt wykorzysta sieć **EfficientNet-B0** wytrenowaną wcześniej na 1,28 mln zdjęć z bazy ImageNet. Sieć zostanie douczona (*fine-tuning*) na danych z platformy Kaggle.

### Uczenie Transferowe (*Transfer Learning*)
Transfer learning polega na tym, że model wytrenowany na jednym, zwykle dużym zadaniu wykorzystujemy jako punkt startowy do innego, pokrewnego zadania. Nie uczymy sieci od zera — przejmujemy jej wiedzę (wagi) i tylko dopasowujemy ją do nowych danych.

> Z uwagi na dość małą liczbę danych w każdej klasie, powyższe podejście wydaje się najbardziej optymalne w celu uzyskania najlepszego modelu.

---

## 7. Technologie i narzędzia

* **Python** – główny język programowania.
* **PyTorch** – budowa, trening i wykorzystanie sieci neuronowej.
* **Pillow (PIL)** – otwieranie i wstępne przetwarzanie zdjęć.
* **NumPy** – operacje na macierzach i danych liczbowych.
* **scikit-learn** – obliczanie wybranych miar oceny klasyfikacji (np. raportu klasyfikacji).
* **Tkinter** – stworzenie interfejsu graficznego aplikacji.
* **Matplotlib** – tworzenie wykresów, wizualizacja procesu szkolenia modelu.

*Uwaga: Dokładny zestaw bibliotek może zostać nieznacznie zmieniony w trakcie realizacji, jeśli okaże się to potrzebne.*

---

## 8. Plan treningu i oceny modelu
Po przygotowaniu danych model zostanie wytrenowany na zbiorze treningowym.

1. **Monitorowanie przebiegu:** W trakcie uczenia zapisywana będzie wartość funkcji straty (*loss*) oraz skuteczność klasyfikacji na zbiorze treningowym i walidacyjnym. Pozwoli to ocenić, czy model rzeczywiście się uczy i czy nie następuje zjawisko przeuczenia (*overfitting*).
2. **Ewaluacja końcowa:** Po zakończeniu prac nad modelem przeprowadzimy końcową ocenę na zbiorze testowym.
3. **Metryki oceny:**
   * **Accuracy:** odsetek poprawnie sklasyfikowanych zdjęć.
   * **Precision:** informacja o tym, jak często przewidywanie danej klasy było poprawne.
   * **Recall:** informacja o tym, jaką część przykładów danej klasy model poprawnie rozpoznał.
   * **Macierz pomyłek (*Confusion Matrix*):** zestawienie prawidłowych klas z klasami przewidzianymi przez model.

> Model zostanie zapisany po treningu do pliku, a aplikacja będzie go wczytywać podczas uruchamiania. Dzięki temu nie będzie konieczne ponowne trenowanie sieci przy każdym uruchomieniu programu.

---

## 9. Interfejs graficzny aplikacji
Ostatnim etapem będzie przygotowanie prostej aplikacji desktopowej przy użyciu biblioteki **Tkinter**.

### Funkcjonalności interfejsu:
* Uruchomienie programu.
* Wybranie zdjęcia z dysku za pomocą okna dialogowego.
* Wyświetlenie wybranego obrazu w oknie aplikacji.
* Uruchomienie klasyfikacji przez wczytany model.
* Wyświetlenie przewidywanej kategorii owocu.
* Przedstawienie wyników dla poszczególnych klas (np. w postaci wartości procentowych).

*Uwaga: Wyniki procentowe będą prezentowane jako wyjście modelu dla poszczególnych klas, a nie jako gwarancja prawdopodobieństwa poprawnej odpowiedzi.*

---

## 10. Podział obowiązków w zespole

Projekt zostanie podzielony pomiędzy cztery osoby:

| Rola / Obszar | Zakres obowiązków |
| :--- | :--- |
| **Przygotowanie danych** | Pobranie i analiza struktury zbioru, sprawdzenie liczby klas i zdjęć, przygotowanie danych do treningu i walidacji. |
| **Budowa i trening modelu** | Opracowanie architektury sieci neuronowej w PyTorch, przygotowanie procesu uczenia, dobór hiperparametrów, trenowanie oraz zapis najlepszej wersji. |
| **Testowanie i analiza wyników** | Przygotowanie procesu oceny modelu, obliczenie wybranych miar skuteczności, generowanie wykresów i macierzy pomyłek. |
| **Interfejs graficzny** | Przygotowanie okna aplikacji w Tkinter, dodanie wyboru i wyświetlania zdjęć, połączenie interfejsu z modelem, prezentacja wyników. |

---

## 11. Wstępna hipoteza
Zakładamy, że sieć neuronowa wykorzystująca transfer learning będzie w stanie rozpoznawać owoce na zdjęciach z dokładnością wyższą niż przypadkowe przypisywanie klas.

Oczekujemy również, że jakość wyników będzie zależała od liczby i różnorodności zdjęć treningowych oraz podobieństwa wizualnego poszczególnych kategorii.

*Hipoteza zostanie zweryfikowana na podstawie wyników uzyskanych na zbiorze testowym.*

---

## 12. Oczekiwany rezultat
Rezultatem projektu będzie działająca aplikacja komputerowa, która pozwoli użytkownikowi wczytać zdjęcie owocu i uzyskać wynik klasyfikacji.

Projekt pozwoli przećwiczyć pełny proces tworzenia rozwiązania z zakresu uczenia maszynowego:
$$\text{Dane} \longrightarrow \text{Model i Trening} \longrightarrow \text{Ewaluacja} \longrightarrow \text{Aplikacja z GUI}$$

---

## Artykuły naukowe

### Artykuł 1
* **Tytuł:** *A Transfer Learning Evaluation of Deep Neural Networks for Image Classification*
* **Tłumaczenie:** Ocena uczenia transferowego w głębokich sieciach neuronowych do klasyfikacji obrazów
* **Rok publikacji:** 2022
* **Link:** [MDPI Article](https://www.mdpi.com/2504-4990/4/1/2) | **DOI:** [10.3390/make4010002](https://doi.org/10.3390/make4010002)

#### Streszczenie
Artykuł poświęcony jest ocenie wykorzystania transfer learningu w zadaniach klasyfikacji obrazów z użyciem głębokich sieci neuronowych. Autorzy koncentrują się na problemie wyboru odpowiedniego modelu wstępnie wytrenowanego oraz jego dostosowania do nowego zbioru danych.

Istotnym z punktu widzenia autorów jest fakt, że współczesne głębokie sieci neuronowe wymagają dużej ilości danych do skutecznego uczenia. Zebranie i ręczne oznaczenie odpowiednio dużego zbioru obrazów może być czasochłone i kosztowne. Jednocześnie istnieją modele wytrenowane na rozbudowanych zbiorach danych (ImageNet), które nauczyły się rozpoznawać różnorodne cechy wizualne obrazów. Transfer learning pozwala wykorzystać zdobyte wcześniej informacje do nowego zadania klasyfikacyjnego.

Autorzy przedstawiają transfer learning jako metodę polegającą na przeniesieniu wiedzy z zadania źródłowego do zadania docelowego. W praktyce często wykorzystuje się wcześniej wytrenowaną sieć jako ekstraktor cech lub przeprowadza się tzw. *fine-tuning* (dalsze douczanie sieci). 

Skuteczność zależy między innymi od charakterystyki zbioru docelowego, podobieństwa między danymi wykorzystanymi do wstępnego treningu i nowymi obrazami oraz sposobu dostosowania parametrów sieci. Publikacja jest przydatna jako podstawa do opisania metodologii uczenia modelu oraz uzasadnienia wykorzystania wcześniej wytrenowanej sieci zamiast rozpoczynania treningu od losowych wag.

---

### Artykuł 2
* **Tytuł:** *Fruit Image Classification Model Based on MobileNetV2 with Deep Transfer Learning Technique*
* **Tłumaczenie:** Model klasyfikacji obrazów owoców oparty na MobileNetV2 z wykorzystaniem głębokiego uczenia transferowego
* **Rok publikacji:** 2023
* **Link:** [MDPI Article](https://www.mdpi.com/2071-1050/15/3/1906) | **DOI:** [10.3390/su15031906](https://doi.org/10.3390/su15031906)

#### Streszczenie
Artykuł dotyczy automatycznej klasyfikacji owoców na podstawie zdjęć z wykorzystaniem głębokiego uczenia oraz transfer learningu. Autor przedstawia problem rozpoznawania owoców jako zadanie klasyfikacji obrazów, w którym model powinien automatycznie przyporządkować zdjęcie do właściwej kategorii (zastosowanie w rolnictwie, handlu i sortowaniu).

W badaniu wykorzystano architekturę **MobileNetV2**, zaprojektowaną z myślą o efektywnym przetwarzaniu obrazów przy ograniczonych wymaganiach obliczeniowych. Zastosowano transfer learning, a zmodyfikowany model nazwano **TL-MobileNetV2**.

#### Szczegóły eksperymentu i wyniki:
* **Zbiór danych:** 26 149 zdjęć przedstawiających 40 rodzajów owoców (podział train/test w proporcji $3:1$).
* **Porównywane modele:** AlexNet, VGG16, InceptionV3, ResNet, MobileNetV2.
* **Wyniki TL-MobileNetV2:**
  * Dokładność (*Accuracy*): **99%** (o 3 punkty procentowe więcej niż podstawowy MobileNetV2)
  * Precision, Recall, F1-score: po **99%**
* **Inne techniki:** Zastosowano odrzucanie neuronów (*dropout*), aby ograniczyć nadmierne dopasowanie (*overfitting*).

Wyniki wskazują, że połączenie wcześniej wytrenowanej sieci z odpowiednio dostosowaną częścią klasyfikacyjną może być wysoce skuteczne w rozpoznawaniu wielu kategorii owoców.