# Pipeline Snakemake do analizy poziomu zanieczyszczeń (PM2.5) i przeglądu literatury PubMed

Projekt ma na celu wizualizację danych dotyczących poziomu zanieczyszczenia powietrza PM2.5 w wybranych polskich miastach oraz zestawienie tych wyników z trendami w literaturze naukowej z bazy PubMed, co pozwala na lepszą interpretację zmian poziomu zanieczyszczenia powietrza w czasie.

## Repozytorium zawiera:

#### Pipeline Snakemake:
 - Snakefile - główny plik definiujący cały workflow
 - config/task4.yaml - plik konfiguracyjny

#### Skrypty PubMed w folderze src/literature:
- pubmed_fetch.py - pobieranie metadanych o artykułach (tytuły, autorzy, czasopisma) przy użyciu Biopython
- pubmed_help.py - funkcje pomocnicze i parsowanie odpowiedzi z API Entrez

#### Skrypty PM2.5 w folderze src:
- wczytywanie.py - wczytywanie danych zanieczyszczeń ze strony GIOŚ
- czyszczenie_danych - przygotowuje dane do analizy i obliczeń
- obliczenia.py - wykonuje obliczenia (średnie dobowe w danych miejscowościach, dni z przekroczeniem normy w danych stacjach)
- wykresy_rok.py - generuje: 
  - wykres średnich miesięcznych stężeń PM2.5 w danych miejscowościach
  - wykres dni z przekroczeniem dobowej normy WHO stężenia PM2.5
- generate_report.py - generuje raport dla danych zanieczyszczeń PM2.5 oraz znalezionej literatury

W repozytorium znajduje się także folder tests, w którym znajdują się testy dla funkcji w innych skryptach.

### Dane wejściowe w folderze data/raw:
- pm25_{year}.pkl - surowe dane z GIOŚ

### Dane przetworzone w folderze data/processed:
- pm25_cleaned_{year}_.pkl

## Dane wyjśiowe:

### W folderze results/pm25/{year}:
- ranking_exceedances.png - wykres słupkowy prezentujący miejscowości o największej liczbie dni z przekroczeniem normy PM2.5
- monthly_heatmap.png - mapa ciepła obrazująca sezonowe zmiany stężeń pyłów w poszczególnych miesiącach
- exceedances_days.csv - dane statystyczne o liczbie naruszeń norm jakości powietrza dla każdej stacji
- daily_mean.csv - wyliczone średnie dobowe stężeń PM2.5 w danych miejscowościach

### W folderze results/literature/{year}
- pubmed_papers.csv - kompletna lista pobranych artykułów
- summary_by_year.csv - liczba artykułów opublikowana na dany temat w danym roku
- top_journals.csv - ranking czasopism naukowych, które najczęściej publikują prace na dany temat (wyszukiwania)

### W folderze results/
- report_task4.md - raport agregujący wyniki analizy danych GIOŚ oraz przeglądu literatury PubMed w spójną całość


### Incremental
Pipeline Snakemake został tak skonfigurowany, że nie wykonuje reguł dla lat, które już były policzone, jeśli ich wejścia (ani kod) się nie zmieniły.
Weryfikacja odbywa się przez wynik w terminalu: 
- przy dodawaniu nowych danych (np. kolejnego roku), w statystykach uruchomienia (Job stats) wyświetla wyłącznie te kroki, które są niezbędne do uzupełnienia brakujących wyników.
- w przypadku próby ponownego uruchomienia pipeline'u bez wprowadzania zmian w danych wejściowych lub kodzie, system informuje o pełnej aktualności wyników komunikatem "Nothing to be done".
## Instalacja

Sklonuj repozytorium

    git clone https://github.com/alipinska7/Projekt4_ZTP.git

Utwórz i aktywuj wirtualne środowisko

    python -m venv venv
    source ./venv/bin/activate

Zainstaluj potrzebne biblioteki

    pip install -r requirements.txt

## Konfiguracja

Przed uruchomieniem pipeline'u należy uzupełnić plik:
- config/task4.yaml

Należy podać m. in.:

- lata do analizy
- lista miast (niekoniecznie)
- parametry zapytań do PubMed


## Uruchomienie pipeline'u
### Dry-run (sprawdzenie workflow)
snakemake -n

### Pełne uruchomienie pipeline'u
snakemake --cores 1

## Źródła danych

Główny Inspektorat Ochrony Środowiska – powietrze.gios.gov.pl \
PubMed (NCBI) \
Autor: Anna Lipińska