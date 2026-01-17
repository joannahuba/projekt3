# Analiza stężeń PM2.5 w Polsce na podstawie danych GIOŚ

Projekt służy do pobierania, czyszczenia, przekształcania i analizowania danych dotyczących stężeń pyłu PM2.5 z Głównego Inspektoratu Ochrony Środowiska (GIOŚ) dla wybranych lat: 2015, 2018, 2021, 2024.

Celem projektu jest:

* przygotowanie spójnego zbioru danych z różnych lat,
* ujednolicenie kodów stacji,
* analiza średnich miesięcznych stężeń PM2.5,
* identyfikacja liczby dni z przekroczeniem norm.

---

## Struktura projektu

```
.
├── data
│   ├── raw
│   └── processed
├── src
│   ├── 01_download.py
│   ├── 02_data_cleanining.py
│   ├── utils.py
│   └── tests.py
├── tests
│   └── tests.py
├── README.md
├── pyproject.toml
└── main.py
```

---

## Wymagania

* Python ≥ 3.10
* Biblioteki:

  * pandas
  * requests
  * pytest
  * openpyxl
  * logging

Instalacja zależności:

```bash
pip install pandas requests pytest openpyxl
```

---

## Pobieranie danych

Skrypt `01_download.py`:

* pobiera archiwa ZIP z serwisu GIOŚ,
* wyciąga pliki Excel,
* zapisuje je jako pliki CSV w katalogu `data/raw`.

Obsługiwane lata:

* 2015
* 2018
* 2021
* 2024

Uruchomienie:

```bash
uv run src/01_download.py
```

Efekt:

```
data/raw/raw2015.csv
data/raw/raw2018.csv
data/raw/raw2021.csv
data/raw/raw2024.csv
```

---

## Czyszczenie i przetwarzanie danych

Skrypt `02_data_cleanining.py` wykonuje następujące kroki:

1. Wczytanie danych surowych i metadanych.
2. Usunięcie wierszy nagłówkowych i metadanych.
3. Standaryzacja nazw kolumn (kolumna czasu jako `Datetime`).
4. Normalizacja kodów stacji.
5. Konwersja danych do formatu długiego (`Datetime`, `station`, `PM2.5`).
6. Konwersja wartości PM2.5 do typu numerycznego.
7. Mapowanie stacji na miasta.
8. Połączenie danych z różnych lat (tylko wspólne stacje).
9. Usunięcie rekordów z brakującą datą lub PM2.5.
10. Agregacja miesięczna i dzienna.

Uruchomienie:

```bash
uv run src/02_data_cleanining.py
```

---

## Pliki wynikowe

Po uruchomieniu skryptu w katalogu `data/processed` powstaną:

| Plik                     | Opis                                            |
| ------------------------ | ----------------------------------------------- |
| cleaned_and_combined.csv | Połączone i wyczyszczone dane godzinowe         |
| monthly_PM25.csv         | Średnie miesięczne stężenia PM2.5               |
| df_ex2.csv               | Średnie miesięczne PM2.5 dla Warszawy i Katowic |
| df_ex4.csv               | Liczba dni z przekroczeniem normy PM2.5         |

---

## Testy

Projekt zawiera testy jednostkowe i integracyjne dla funkcji pomocniczych.

Uruchomienie testów:

```bash
pytest tests/*
```

Testy obejmują:

* poprawność czyszczenia danych dla różnych lat,
* poprawność mapowania stacji na miasta,
* poprawność konwersji wartości PM2.5 do typu numerycznego,
* poprawność całego przepływu danych.

---

## Zakres analiz

W projekcie analizowane są:

* średnie miesięczne stężenia PM2.5,
* zmiany jakości powietrza w czasie,
* liczba dni z przekroczeniem norm PM2.5,
* porównanie wybranych miast (np. Warszawa, Katowice).

---
