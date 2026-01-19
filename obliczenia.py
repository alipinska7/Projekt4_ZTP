import pandas as pd

#dodanie kolumny z miesiącem i zmienienie kolejności kolumn na bardziej czytelną
def add_month_column(df):
    """
        Dodaje kolumnę 'miesiąc' do DataFrame i zmienia kolejność kolumn na bardziej czytelną.
        Funkcja dodatkowo:
        - konwertuje kolumnę 'wartość' na typ numeryczny (zastępując przecinki kropkami)
        - ustawia kolumny w kolejności: ['czas', 'stacja', 'miejscowość', 'rok', 'miesiąc', 'wartość']
        Args:
            df (pd.DataFrame): DataFrame z kolumnami 'czas', 'stacja', 'miejscowość', 'rok', 'wartość'.
        Returns:
            pd.DataFrame: DataFrame z dodaną kolumną 'miesiąc' i uporządkowanymi kolumnami.
    """

    df = df.copy()
    df['wartość'] = pd.to_numeric(df['wartość'].astype(str).str.replace(',', '.'), errors='coerce')
    df['miesiąc'] = df['czas'].dt.month
    df = df[['czas', 'stacja', 'miejscowość', 'rok', 'miesiąc', 'wartość']]

    return df

def count_monthly_avg_station(df):
    """
        Wylicza średnie miesięczne stężenie PM2.5 dla każdej stacji i każdego roku.
        Args:
            df (pd.DataFrame): DataFrame z kolumnami 'rok', 'stacja', 'miesiąc', 'wartość', 'miejscowość', 'czas'.
        Returns:
            pd.DataFrame: DataFrame z kolumnami:
                          'rok', 'stacja', 'miesiąc', 'średnie_PM25' zawierający średnie miesięczne wartości PM2.5.
    """

    monthly_avg = (df.groupby(['rok', 'stacja', 'miesiąc'])['wartość'].mean().reset_index()
    .rename(columns={'wartość': 'średnie_PM25'}))

    return monthly_avg


def count_monthly_avg_city(df, cities=None, years=None):
    """
    Wylicza średnie miesięczne stężenie PM2.5 dla wybranych miast i lat.
    Jeśli cities lub years nie są podane, funkcja liczy dla wszystkich dostępnych.

    Args:
        df (pd.DataFrame): DataFrame z kolumnami 'miejscowość', 'rok', 'miesiąc', 'wartość'.
        cities (list, optional): Lista miast. Domyślnie None (wszystkie miasta).
        years (list, optional): Lista lat. Domyślnie None (wszystkie lata).

    Returns:
        pd.DataFrame: DataFrame z kolumnami:
                      'miejscowość', 'rok', 'miesiąc', 'średnie_PM25'.
    """
    df = filter_data(df)
    df_filtered = df.copy()

    if cities is not None:
        df_filtered = df_filtered[df_filtered['miejscowość'].isin(cities)]
    if years is not None:
        df_filtered = df_filtered[df_filtered['rok'].isin(years)]

    monthly_avg = (df_filtered.groupby(['miejscowość', 'rok', 'miesiąc'])['wartość'].mean().reset_index()
                   .rename(columns={'wartość': 'średnie_PM25'}))

    return monthly_avg




def filter_data(df):
    """
        Filtruje dane, aby zachować tylko lata, dla których mamy dane dla co najmniej 10 miesięcy.
        Funkcja jest przydatna do analizy, aby uniknąć używania lat z brakującymi danymi.
        Args:
            df (pd.DataFrame): DataFrame z kolumnami 'rok' i 'miesiąc'.
        Returns:
            pd.DataFrame: Przefiltrowany DataFrame zawierający tylko lata z co najmniej 10 miesiącami danych.
    """
    # Sprawdzenie, czy mamy dane dla konkretnych miesięcy w danym roku
    # Potrzebne do tego, by w wykresach nie pojawiły nam się pojedyncze dane z innych lat, których nie analizujemy
    months_per_year = (df.groupby('rok')['miesiąc'].nunique())
    valid_years = months_per_year[months_per_year >= 10].index  # gdy mamy dane dla więcej niż 10 miesięcy to ich używamy
    df = df[df['rok'].isin(valid_years)]

    return df



#ZADANIE 4
def count_daily_avg(df):
    """
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
        """
    # Filtrowanie danych
    df = filter_data(df)

    # Tabela dobowych stężeń dla wszystkich stacji wynikająca z jednostkowych pomiarów.
    daily_avg = (df.groupby(['stacja', 'rok', 'miejscowość', df['czas']
        .dt.date])['wartość'].mean().reset_index() .rename(columns={'czas': 'data', 'wartość': 'pm25_dobowe'}) )

    # Tablica binarna stwierdzająca, czy zmierzone stężenia PM2.5 przekraczały dobową normę
    daily_avg['przekroczenie'] = ((daily_avg['pm25_dobowe'] > 15).astype(int))

    # Tabela sumująca ilość wykroczeń dla każdej stacji względem lat danych lat
    exceedances = (daily_avg.groupby(['stacja', 'rok', 'miejscowość'])['przekroczenie'].sum()
                   .reset_index().rename(columns={'przekroczenie': 'ilość przekroczeń'}))

    # Tabela dla roku 2024
    transgressions_2024 = exceedances[exceedances['rok'] == 2024]

    # Wyznaczenie 3 stacji o największej liczbie wykroczeń w roku 2024 i 3 o najmniejszej
    max_3 = transgressions_2024.nlargest(3, 'ilość przekroczeń')
    min_3 = transgressions_2024.nsmallest(3, 'ilość przekroczeń')

    chosen_stations = pd.concat([max_3, min_3])['stacja'].tolist()

    # Tabela wykroczeń dla wybranych stacji dla danych lat
    data_exceedances = exceedances[exceedances['stacja'].isin(chosen_stations)].copy()

    return data_exceedances



#zadanie 5
def voivodeship_above_norm_sum(df_meta, final_df):
    # tablica z województwami i kodami stacji
    voivodeship = df_meta[["Kod stacji", "Województwo"]]
    voivodeship = voivodeship.dropna()
    voivodeship.drop_duplicates(inplace=True)
# kod zaporzyczony z funkcji obliczenia.count_daily_avg()
    # Filtrowanie danych
    df= filter_data(final_df)
    final_df['czas'] = pd.to_datetime(final_df['czas'])

    # Tabela dobowych stężeń dla wszystkich stacji wynikająca z jednostkowych pomiarów.
    daily_avg = (df.groupby(['stacja', 'rok', 'miejscowość',df['czas'].dt.date])['wartość'].mean().reset_index() .rename(columns={'czas': 'data', 'wartość': 'pm25_dobowe'}) )

    #połaczenie df z pomiarami z nazwami województw
    df_with_voivodeship = daily_avg.merge(voivodeship, left_on='stacja', right_on='Kod stacji', how='left')
    # usunięcie niepotrzebnych kolumn
    df_with_voivodeship.drop(columns=['Kod stacji'], inplace=True)

    # Tablica binarna stwierdzająca, czy zmierzone stężenia PM2.5 przekraczały dobową normę
    df_with_voivodeship['przekroczenie'] = ((df_with_voivodeship['pm25_dobowe'] > 15).astype(int))

    # Tabela sumująca ilość wykroczeń dla każdej stacji względem lat danych lat
    exceedances = (df_with_voivodeship.groupby(['stacja', 'rok', 'miejscowość','Województwo'])['przekroczenie'].sum().reset_index().rename(columns={'przekroczenie': 'ilość przekroczeń'}))

    # Sumowanie przekroczeń dla województw i lat
    voivodeship_summary = exceedances.groupby(['Województwo', 'rok'])['ilość przekroczeń'].sum().reset_index()

    # Sortowanie dla lepszej czytelności
    voivodeship_summary = voivodeship_summary.sort_values(by=['Województwo', 'rok'])

    # Przekształcenie tabeli: Województwa w wierszach, lata w kolumnach
    voivodeship_summary = voivodeship_summary.pivot_table(
    index='Województwo',
    columns='rok',
    values='ilość przekroczeń',
    aggfunc='sum')

    return voivodeship_summary

if __name__ == "__main__":
    pass
