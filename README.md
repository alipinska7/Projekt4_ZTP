# Dokumentacja Projektu Projekt3_ZTP
Projekt dotyczy analizy danych zanieczyszczeń powietrza PM2.5 w Polsce. Projekt obejmuje 4 etapy:
1. Wczytywanie danych
2. Czyszczenie danych i przygotowanie do analizy
3. Przeprowadzenie odpowiednich obliczeń do późniejszych wizualizacji
4. Generowanie wykresów przedstawiających różne zależności

## Jak zainstalować i uruchomić projekt
1. Sklonuj repozytorium
```python

```
2. Utwórz wirtualne środowisko
```python
python -m venv venv
source ./venv/bin/activate
```
3. Zainstaluj potrzebne biblioteki
```python
pip install -r requirements.txt
```

## Moduł czyszczenie_danych
Służy do:
- oczyszczenia z nieprawidłowych danych (np. puste wiersze, nieprawidłowe daty)
- aktualizacji kodów nieaktualnych kodów stacji
- przygotowuje zbiorczy DateFrame z danymi ze wszystkich analizowanych lat
### Funkcja `add_place`
```python
add_place(df, meta)
```

        Dodaje kolumnę 'miejscowość' do DataFrame na podstawie metadanych stacji i ustala kolejność kolumn.

        Args:
            df (pd.DataFrame): DataFrame w formacie long z kolumnami 'czas', 'stacja', 'wartość'.
            meta (pd.DataFrame): DataFrame z metadanymi stacji zawierający kolumny:
                                'Kod stacji', 'Stary kod stacji (o ile inny od aktualnego)', 'Miejscowość'.
        Returns:
            pd.DataFrame: DataFrame z dodaną kolumną 'miejscowość' i ustaloną kolejnością kolumn:
                          ['czas', 'stacja', 'miejscowość', 'wartość'].
    

### Funkcja `clear_data`
```python
clear_data(df, year)
```
        Funkcja:
        1. Usuwa nieprawidłowe wiersze
        2. Konwertuje "czas" na datetime
        3. Przesuwa pomiary o północy na dzień poprzedni
        Args:
            df (pd.DataFrame*): DataFrame z surowymi danymi.
            year (int): Rok, dla którego dane są przetwarzane.
        Returns:
            pd.DataFrame: Dane w formacie long z kolumnami 'czas', 'stacja', 'wartość'.
    

### Funkcja `combine_years`
```python
combine_years(all_data)
```
        Łączy dane PM2.5 z wielu lat w jeden DataFrame w formacie long.

        Funkcja:
        1. Zachowuje kolumnę 'miejscowość' z oryginalnych DataFrame'ów.
        2. Tworzy pivot dla każdego roku, by filtrować tylko stacje obecne we wszystkich latach.
        3. Łączy dane w jeden DataFrame.
        4. Dodaje kolumnę 'miejscowość' i kolumnę 'rok'.
        5. Wykonuje sanity check – wypisuje liczbę unikalnych stacji i liczbę dni w każdym roku.

        Args:
            all_data (dict): Słownik DataFrame'ów (jeden DataFrame na każdy rok), w formacie long
                             z kolumnami 'czas', 'stacja', 'wartość', 'miejscowość'.
        Returns:
            pd.DataFrame: Połączone dane w formacie long z kolumnami:
                          'czas', 'stacja', 'wartość', 'miejscowość', 'rok'.
    

### Funkcja `prepare_to_analize`
```python
prepare_to_analize(all_data, meta)
```

        Przygotowuje i oczyszcza dane PM2.5 do analizy dla wielu lat.
        Funkcja:
        1. Oczyszcza dane za pomocą `clear_data`
        2. Aktualizuje stare kody stacji na nowe (`update_data`)
        3. Dodaje kolumnę 'miejscowość' (`add_place`)
        4. Porządkuje kolejność kolumn w DataFrame

        Args:
            all_data (dict): Słownik z kluczami będącymi latami (int), a wartościami DataFrame z danymi surowymi.
            meta (pd.DataFrame): DataFrame z metadanymi stacji zawierający kolumny:
                                'Kod stacji', 'Stary kod stacji (o ile inny od aktualnego)', 'Miejscowość'.
        Returns:
            dict: Słownik DataFrame'ów przygotowanych do analizy, jeden DataFrame na każdy rok.
    

### Funkcja `update_data`
```python
update_data(df, meta)
```
        Aktualizuje kody stacji w DataFrame na podstawie danych metadanych.

        Funkcja tworzy mapowanie pomiędzy starymi kodami stacji a ich aktualnymi odpowiednikami 
        na podstawie DataFrame `meta`, a następnie zastępuje stare kody w kolumnie `stacja` w DataFrame `df`.

        W kolumnie 'Stary Kod stacji (o ile inny od aktualnego)' może wystąpić wiele kodów oddzielonych przecinkami.

        Args:
            df (pd.DataFrame): DataFrame zawierający dane, w którym kolumna 'stacja' ma zostać zaktualizowana.
            meta (pd.DataFrame): DataFrame z metadanymi stacji, zawierający kolumny:
                - 'Kod stacji'
                - 'Stary Kod stacji (o ile inny od aktualnego)'
        Returns:
            pd.DataFrame: DataFrame `df` z uaktualnionymi kodami stacji.
    

---
## Moduł obliczenia
Służy do obliczeń takicj jak:
- średnie dobowe stężenie PM2.5 i wykrycia przekroczenia ich norm
- średnie miesięczne stężenie PM2.5 dla wybranych miast i lat
- średnie miesięczne stężenie dla każdej stacji w danym roku

### Funkcja `add_month_column`
```python
add_month_column(df)
```
        Dodaje kolumnę 'miesiąc' do DataFrame i zmienia kolejność kolumn na bardziej czytelną.
        Funkcja dodatkowo:
        - konwertuje kolumnę 'wartość' na typ numeryczny (zastępując przecinki kropkami)
        - ustawia kolumny w kolejności: ['czas', 'stacja', 'miejscowość', 'rok', 'miesiąc', 'wartość']
        Args:
            df (pd.DataFrame): DataFrame z kolumnami 'czas', 'stacja', 'miejscowość', 'rok', 'wartość'.
        Returns:
            pd.DataFrame: DataFrame z dodaną kolumną 'miesiąc' i uporządkowanymi kolumnami.
    

### Funkcja `count_daily_avg`
```python
count_daily_avg(df)
```
        Oblicza średnie dobowe stężenia PM2.5, wykrywa przekroczenia normy i wybiera stacje z najwyższymi oraz najniższymi wykroczeniami.
        Funkcja:
        1. Filtruje dane, aby pozostawić tylko lata z co najmniej 10 miesiącami danych (`filter_data`).
        2. Wylicza średnie dobowe stężenia PM2.5 dla każdej stacji i roku.
        3. Tworzy kolumnę binarną `przekroczenie`, wskazującą, czy dobowa średnia przekroczyła normę 15 µg/m³.
        4. Sumuje liczbę przekroczeń dla każdej stacji w danych latach
        5. Dla roku 2024 wybiera 3 stacje z największą i 3 z najmniejszą liczbą przekroczeń.
        6. Zwraca tabelę przekroczeń dla wybranych stacji dla danych lat.

        Args:
            df (pd.DataFrame): DataFrame z kolumnami 'stacja', 'miejscowość', 'rok', 'czas', 'wartość'.
        Returns:
            pd.DataFrame: DataFrame z liczbą przekroczeń dobowej normy PM2.5 dla wybranych stacji
                          (kolumny: 'stacja', 'rok', 'miejscowość', 'ilość przekroczeń').
        

### Funkcja `count_monthly_avg_city`
```python
count_monthly_avg_city(df, cities=None, years=None)
```
    Wylicza średnie miesięczne stężenie PM2.5 dla wybranych miast i lat.
    Jeśli cities lub years nie są podane, funkcja liczy dla wszystkich dostępnych.

    Args:
        df (pd.DataFrame): DataFrame z kolumnami 'miejscowość', 'rok', 'miesiąc', 'wartość'.
        cities (list, optional): Lista miast. Domyślnie None (wszystkie miasta).
        years (list, optional): Lista lat. Domyślnie None (wszystkie lata).

    Returns:
        pd.DataFrame: DataFrame z kolumnami:
                      'miejscowość', 'rok', 'miesiąc', 'średnie_PM25'.
    

### Funkcja `count_monthly_avg_station`
```python
count_monthly_avg_station(df)
```
    Wylicza średnie miesięczne stężenie PM2.5 dla każdej stacji i każdego roku.
    Args:
        df (pd.DataFrame): DataFrame z kolumnami 'rok', 'stacja', 'miesiąc', 'wartość', 'miejscowość', 'czas'.
    Returns:
        pd.DataFrame: DataFrame z kolumnami:
            'rok', 'stacja', 'miesiąc', 'średnie_PM25' zawierający średnie miesięczne wartości PM2.5.
    

### Funkcja `filter_data`
```python
filter_data(df)
```
        Filtruje dane, aby zachować tylko lata, dla których mamy dane dla co najmniej 10 miesięcy.
        Funkcja jest przydatna do analizy, aby uniknąć używania lat z brakującymi danymi.
        Args:
            df (pd.DataFrame): DataFrame z kolumnami 'rok' i 'miesiąc'.
        Returns:
            pd.DataFrame: Przefiltrowany DataFrame zawierający tylko lata z co najmniej 10 miesiącami danych.

---
## Moduł wczytywanie
Służy do wczytania wszystkich potrzebnych danych i metadanych GIOŚ. 

### Funkcja `download_gios_archive`
```python
download_gios_archive(year, gios_id, filename)
```
        Funkcja:
        1. Pobiera archiwum ZIP z bazy GIOŚ
        2. Wypakowuje wskazany plik
        3. Wczytuje ten plik do DataFrame.
        Args:
            year (int): Rok, którego dotyczą dane (używany głównie w obsłudze błędów).
            gios_id (str): Identyfikator zasobu w URL archiwum GIOŚ.
            filename (str): Dokładna nazwa pliku Excel wewnątrz archiwum ZIP do wczytania.

        Returns:
            pd.DataFrame: Dane wczytane z pliku Excel
        Raises:
            requests.exceptions.HTTPError: gdys wystąpi błąd podczas pobierania pliku.
            zipfile.BadZipFile: gdy pobrany plik nie jest poprawnym archiwum ZIP.

### Funkcja `load_all_data`
```python
load_all_data(gios_url_ids, gios_pm25_file)
```
    Pobiera dane PM2.5 dla wszystkich lat zdefiniowanych w słownikach `gios_url_ids` i `gios_pm25_file`.
    Funkcja:
    - Iteruje po wszystkich latach w słowniku `gios_url_ids`.
    - Pobiera dane dla każdego roku za pomocą funkcji `download_gios_archive`.
    - Zbiera wszystkie DataFrame'y do słownika: {rok: DataFrame}.
    - Wypisuje informację o wczytywaniu roku.
    Args:
        gios_url_ids (dict): Słownik {rok: ID archiwum GIOŚ}.
        gios_pm25_file (dict): Słownik {rok: nazwa pliku PM2.5}.
    Returns:
        - dict: Słownik DataFrame'ów, gdzie klucz to rok, a wartość to DataFrame z danymi PM2.5.
    

### Funkcja `load_metadane`
```python
load_metadane()
```
        Wczytuje metadane stacji pomiarowych PM2.5 z archiwum GIOŚ.
        Returns:
            pd.DataFrame: DataFrame zawierający metadane stacji, w tym kolumny:
                          'Kod stacji', 'Miejscowość', 'Stary kod stacji (o ile istnieje)'.
    

### Funkcja `load_metadane2`
```python
load_metadane2()
```
        Wczytuje metadane stacji PM2.5 z lokalnego pliku Excel.
        Funkcja awaryjna, gdy serwis GIOŚ jest niedostępny.
        Returns:
            pd.DataFrame: DataFrame zawierający metadane stacji.
---
## Moduł wykresy
Generuje:
1. wykres słupkowy liczby dni z przekroczeniem dobowej normy PM2.5
2. wykres liniowy trendów średnich miesięcznych wartości PM2.5 dla wybranych miast i lat
3. heatmapy średnich miesięcznych stężeń PM2.5 dla wybranych lat i miejscowości

### Funkcja `barplot`
```python
barplot(df_exc)
```
        Funkcja tworzy grupowy wykres słupkowy liczby dni z przekroczeniem dobowej normy PM2.5.

        Funkcja wizualizuje liczbę dni, w których stężenie PM2.5 przekroczyło
        dobową normę dla wybranych stacji i lat.

        Na wykresie:
        - oś X przedstawia stacje, oś Y – liczbę dni z przekroczeniem,
        - kolor słupków reprezentuje rok.

        Args:
            df_exc (pd.DataFrame):
                DataFrame zawierający przekształcone dane o liczbie dni
                z przekroczeniem PM2.5 dla poszczególnych stacji i lat,
                z kolumnami:
                - 'miejscowość' (nazwa stacji),
                - 'rok',
                - 'ilość przekroczeń'.
        Returns:
            None
            Funkcja wyświetla wykres słupkowy, nie zwraca wartości.
    

### Funkcja `city_trends_plot`
```python
city_trends_plot(df, cities, years)
```

        Funkcja rysuje wykres liniowy trendów średnich miesięcznych wartości PM2.5
        dla wybranych miast i lat (po uśrednieniu wyników ze wszystkich stacji pomiarowych w danym mieście).
        Oś X przedstawia miesiące (1–12), oś Y - średnie wartości PM2.5.
        Wykres umożliwia porównanie zmian poziomu zanieczyszczenia powietrza w danych miastach dla określonych lat.

        Args:
        df (pd.DataFrame): DataFrame zawierający uśrednione dane miesięczne PM2.5 dla miast, z kolumnami:
            'miejscowość', 'rok', 'miesiąc', 'średnie_PM25'.
        cities (list[str]): Lista miast do uwzględnienia w analizie
        years (list[int]): Lista lat do porównania

    Zwraca:
        None
        Funkcja wyświetla wykres, nie zwraca wartości.
    

### Funkcja `heatmap_plot`
```python
heatmap_plot(df_mean_month)
```

        Funkcja tworzy heatmapy średnich miesięcznych stężeń PM2.5 dla wybranych lat i miejscowości.

        Funkcja generuje wykresy typu heatmap, w których:
        - oś X przedstawia miesiące (1–12),
        - oś Y przedstawia lata
        - kolor reprezentuje średnie stężenie PM2.5 w danym miesiącu i roku,
          uśrednione po wszystkich stacjach w danej miejscowości.

        Każdy panel odpowiada jednej miejscowości, co pozwala porównać zmiany poziomu zanieczyszczeń w czasie
        pomiędzy różnymi miastami.

        Args:
            df_mean_month (pd.DataFrame):
                DataFrame zawierający uśrednione miesięczne dane PM2.5 dla miast, z kolumnami:
                'miejscowość', 'rok', 'miesiąc', 'średnie_PM25'.
        Returns:
            None
                Funkcja wyświetla heatmapy, nie zwraca wartości.

        Uwaga: Kolor heatmapy jest skalowany od 0 do 70 µg/m³.
        

---
