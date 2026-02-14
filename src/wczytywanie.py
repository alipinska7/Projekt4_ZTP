import pandas as pd
import requests
import zipfile
import io, os
import argparse

#słowniki
gios_archive_url = "https://powietrze.gios.gov.pl/pjp/archives/downloadFile/"
gios_ids = {
    2006: '227', 2007: '228', 2008: '229', 2009: '230', 2010: '231', 2011: '232',
    2012: '233', 2013: '234', 2014: '302', 2015: '236', 2016: '602', 2017: '262',
    2018: '603', 2019: '322', 2020: '424', 2021: '486', 2022: '524', 2023: '564', 2024: '582'
}
gios_pm25_file = {
    2006: '2006_PM2.5_1g.xlsx', 2007: '2007_PM2.5_1g.xlsx', 2008: '2008_PM2.5_1g.xlsx',
    2009: '2009_PM2.5_1g.xlsx', 2010: '2010_PM2.5_1g.xlsx', 2011: '2011_PM2.5_1g.xlsx',
    2012: '2012_PM2.5_1g.xlsx', 2013: '2013_PM2.5_1g.xlsx', 2014: '2014_PM2.5_1g.xlsx',
    2015: '2015_PM25_1g.xlsx', 2016: '2016_PM2.5_1g.xlsx', 2017: '2017_PM25_1g.xlsx',
    2018: '2018_PM25_1g.xlsx', 2019: '2019_PM25_1g.xlsx', 2020: '2020_PM25_1g.xlsx',
    2021: '2021_PM25_1g.xlsx', 2022: '2022_PM25_1g.xlsx', 2023: '2023_PM25_1g.xlsx', 2024: '2024_PM25_1g.xlsx'
}



# funkcja do ściągania podanego archiwum
def download_gios_archive(year, gios_id, filename):
    """
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
            requests.exceptions.HTTPError: gdy wystąpi błąd podczas pobierania pliku.
            zipfile.BadZipFile: gdy pobrany plik nie jest poprawnym archiwum ZIP.
        """
    # Pobranie archiwum ZIP do pamięci
    url = f"{gios_archive_url}{gios_id}"
    response = requests.get(url)
    response.raise_for_status()  # jeśli błąd HTTP, zatrzymaj

    # Otwórz zip w pamięci
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        # znajdź właściwy plik z PM2.5
        if not filename:
            print(f"Błąd: nie znaleziono {filename}.")
        else:
            # wczytaj plik do pandas
            with z.open(filename) as f:
                try:
                    df = pd.read_excel(f, header=None)
                except Exception as e:
                    print(f"Błąd przy wczytywaniu {year}: {e}")


    return df


def load_all_data(gios_url_ids, gios_pm25_file):
    """
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
    """

    all_years_data = {}

    #pętla po latach z słownika gios_url_ids
    for year in gios_url_ids.keys():
        print(f"Wczytywanie roku {year}...")

        #pobranie id i nazwy pliku
        current_id = gios_url_ids[year]
        current_file = gios_pm25_file[year]

        #wywołanie funkcji
        df = download_gios_archive(year, current_id, current_file)

        if df is not None:
            all_years_data[year] = df

    return all_years_data

# załadowywanie metadanych
def load_metadane():
    """
        Wczytuje metadane stacji pomiarowych PM2.5 z archiwum GIOŚ.
        Returns:
            pd.DataFrame: DataFrame zawierający metadane stacji, w tym kolumny:
                          'Kod stacji', 'Miejscowość', 'Stary kod stacji (o ile istnieje)'.
    """
    url = "https://powietrze.gios.gov.pl/pjp/archives/downloadFile/622"
    df = pd.read_excel(url, engine='openpyxl')
    print(df.head())
    return df

#awaryjne: na wypadek, gdyby nie działała strona
def load_metadane2():
    """
        Wczytuje metadane stacji PM2.5 z lokalnego pliku Excel.
        Funkcja awaryjna, gdy serwis GIOŚ jest niedostępny.
        Returns:
            pd.DataFrame: DataFrame zawierający metadane stacji.
    """
    return pd.read_excel("metadane.xlsx")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    # Sprawdzenie, czy istnieje ID dla podanego roku
    if args.year not in gios_ids:
        raise ValueError(f"Brak ID GIOŚ dla roku {args.year}!")

    gios_id = gios_ids[args.year]
    filename = gios_pm25_file[args.year]

    print(f"Pobieranie danych GIOŚ dla roku {args.year} (ID: {gios_id})...")

    # Pobieranie danych
    df = download_gios_archive(args.year, gios_id, filename)

    # Zapis surowych danych do pliku w formacie pickle
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    df.to_pickle(args.output)
    print(f"Zapisano surowe dane do: {args.output}")