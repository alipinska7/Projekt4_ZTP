import pandas as pd
from wczytywanie import load_metadane
import argparse
import os

def clear_data(df, year):
    """
        Funkcja:
        1. Usuwa nieprawidłowe wiersze
        2. Konwertuje "czas" na datetime
        3. Przesuwa pomiary o północy na dzień poprzedni
        Args:
            df (pd.DataFrame): DataFrame z surowymi danymi.
            year (int): Rok, dla którego dane są przetwarzane.
        Returns:
            pd.DataFrame: Dane w formacie long z kolumnami 'czas', 'stacja', 'wartość'.
    """

    # Znalezienie wiersza z kodami stacji
    try:
        idx_kod = df.index[df.eq("Kod stacji").any(axis=1)][0]
    except IndexError:
        print(f"Nie znaleziono wiersza 'Kod stacji' w roku {year}")
        return None

    # Ustawienie nagłówków kolumn
    df.columns = df.iloc[idx_kod] #przypisanie tego wiersza jako kolumny
    df = df.iloc[idx_kod + 1:].reset_index(drop=True)

    # Usuwanie wierszy, które nie zawierają daty w pierwszej kolumnie
    df = df[pd.to_datetime(df[df.columns[0]], format='mixed', errors='coerce').notna()].reset_index(drop=True)

    # Ujednolicenie nazwy kolumny czasu
    df = df.rename(columns={df.columns[0]: "czas"})

    # Konwersja na datetime
    df['czas'] = pd.to_datetime(df['czas'], format='mixed', errors='coerce')
    df = df.dropna(subset=['czas']).reset_index(drop=True)

    # Przesunięcie pomiarów o północy na dzień poprzedni;
    mask_midnight = df['czas'].dt.hour == 0
    df.loc[mask_midnight, 'czas'] = df.loc[mask_midnight, 'czas'] - pd.Timedelta(seconds=1)

    # Sortowanie
    df = df.sort_values('czas').reset_index(drop=True)

    # Przygotowanie df do analizy danych
    df = df.melt(id_vars='czas', var_name='stacja', value_name='wartość')

    # Sanity Check
    if 'stacja' in df.columns:
        stations = df['stacja'].nunique()
        print(f"Liczba stacji: {stations}")
    if 'czas' in df.columns:
        df_year = df[df['czas'].dt.year == year]
        days = df_year['czas'].dt.date.nunique()
        print(f"Liczba dni w roku {year}, w których wykonywano pomiary: {days}")

    return df


def update_data(df, meta):
    """
        Aktualizuje kody stacji w DataFrame na podstawie danych metadanych.

        Funkcja tworzy mapowanie pomiędzy starymi kodami stacji a ich
        aktualnymi odpowiednikami na podstawie DataFrame `meta`, a następnie
        zastępuje stare kody w kolumnie `stacja` w DataFrame `df`.

        W kolumnie 'Stary Kod stacji \n(o ile inny od aktualnego)'
        może wystąpić wiele kodów oddzielonych przecinkami.

        Args:
            df (pd.DataFrame): DataFrame zawierający dane, w którym kolumna 'stacja' ma zostać zaktualizowana.
            meta (pd.DataFrame): DataFrame z metadanymi stacji, zawierający kolumny:
                - 'Kod stacji'
                - 'Stary Kod stacji \n(o ile inny od aktualnego)'
        Returns:
            pd.DataFrame: DataFrame `df` z uaktualnionymi kodami stacji.
    """
    # słownik klucz: stary kod, wartość: nowy kod
    code_map = {old_code.strip(): row['Kod stacji'] for _, row in meta.iterrows()
                for old_code in str(row['Stary Kod stacji \n(o ile inny od aktualnego)'] or '').split(',')
                if old_code.strip()}  # gwarancja braku pustych kluczy w słowniku

    # uaktualnienie nazw stacji w df
    df['stacja'] = df['stacja'].replace(code_map)

    return df


def add_place(df, meta):
    """
        Dodaje kolumnę 'miejscowość' do DataFrame na podstawie metadanych stacji i ustala kolejność kolumn.

        Args:
            df (pd.DataFrame): DataFrame w formacie long z kolumnami 'czas', 'stacja', 'wartość'.
            meta (pd.DataFrame): DataFrame z metadanymi stacji zawierający kolumny:
                                'Kod stacji', 'Stary kod stacji (o ile inny od aktualnego)', 'Miejscowość'.
        Returns:
            pd.DataFrame: DataFrame z dodaną kolumną 'miejscowość' i ustaloną kolejnością kolumn:
                          ['czas', 'stacja', 'miejscowość', 'wartość'].
    """

    # słownik klucz: kod stacji, wartość: miejscowość stacji;
    place_map = dict(zip(meta['Kod stacji'], meta['Miejscowość']))

    # utworzenie kolumny 'miejscowość' i przypisanie każdej stacji w df odpowiedniej miejscowości
    df['miejscowość'] = df['stacja'].map(place_map)

    df = df[['czas', 'stacja', 'miejscowość', 'wartość']]  # ustalenie kolejności kolumn

    return df

# Funkcja przygotowująca DateFrame do  analizy (czyszczenie danych, aktualizacja kodów stacji, dodanie miejscowości)
def prepare_to_analize(all_data, meta):
    """
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
    """
    processed_data = {}

    # Czyszczenie i niezbędne modyfikacje
    for year, df in all_data.items():
        df_cleaned = clear_data(df, year)
        if df_cleaned is None:
            return None

        # Aktualizacja starych kodów na nowe
        df_updated = update_data(df_cleaned, meta)

        # Dodanie miejscowości i ustalenie kolejności kolumn
        df_final = add_place(df_updated, meta)

        # Dodanie DF do słownika
        processed_data[year] = df_final

    return processed_data



def combine_years(all_data):
    """
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
    """
    # Zachowanie miejscowości z dfów, w postaci słownika
    full_df = pd.concat(all_data.values())
    place_map = full_df.drop_duplicates('stacja').set_index('stacja')['miejscowość']

    dfs = []
    for year, df in all_data.items():
        # Zmiana na format szeroki (żeby join ='inner' działało)
        pivoted = df.pivot(index='czas', columns='stacja', values='wartość')
        dfs.append(pivoted)

    # Filtrowanie stacji: wszystkie te, które występują we wszystkich analizowanych latach
    combined_wide = pd.concat(dfs, axis=0, join='inner')

    # Powrót do odpowiedniego formatu do analizy danych
    df_all = combined_wide.reset_index().melt(
        id_vars='czas',
        var_name='stacja',
        value_name='wartość'
    )

    # Dodanie kolumny miejscowość
    df_all['miejscowość'] = df_all['stacja'].map(place_map)

    # Dodanie kolumny rok
    df_all['rok'] = df_all['czas'].dt.year

    # Sanity Check
    if 'stacja' in df_all.columns:
        stations = df_all['stacja'].nunique()
        print(f"Liczba unikalnych kodów stacji: {stations}")
    if 'czas' in df_all.columns:
        years = df_all['rok'].unique()
        for year in years:
            days = df_all[df_all['rok'] == year]['czas'].dt.date.nunique()
            print(f"Liczba dni w roku {year}: {days}")

    return df_all



if __name__ == "__main__":
    import argparse
    import os
    import pandas as pd

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    # Wczytanie danych
    print(f"Wczytywanie danych z: {args.input}")
    df_raw = pd.read_pickle(args.input)
    meta = load_metadane()

    # Przygotowanie danych do analizy
    df_cleaned = clear_data(df_raw, args.year)
    df_updated = update_data(df_cleaned, meta)
    df_final = add_place(df_updated, meta)

    # Dodanie kolumny rok
    df_final['rok'] = args.year

    # Zapis plików
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    df_final.to_pickle(args.output)
    print(f"Zapisano: {args.output}")
