import pytest
import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from czyszczenie_danych import clear_data, combine_years


def test_clear_data():
    df = pd.DataFrame({
        0: ["coś", "Kod stacji", "2023-01-01 00:00", "2023-01-01 01:00"],
        1: ["", "ST01", 10, 12],
        2: ["", "ST02", 20, 22],
    })

    result = clear_data(df, year=2023)

    # Sprawdzenie, czy wynik nie jest None (np. z powodu braku nazwy "Kod Stacji")
    assert result is not None

    # Sprawdzenie, czy powstały wszystkie potrzebne kolumny
    assert set(result.columns) == {"czas", "stacja", "wartość"}, "Nie powstały wszystkie potrzebne kolumny"

    # Sprawdzenie liczby wierszy
    assert len(result) == 4, "Niepoprawna liczba wierszy"

    # Sprawdzenie przesunięcia pomiarów o północy
    midnight_row = result[result["wartość"] == 10].iloc[0]
    assert midnight_row["czas"].hour == 23, "Niepoprawne przesunięcie pomiarów o północy (godzina)"
    assert midnight_row["czas"].minute == 59, "Niepoprawne przesunięcie pomiarów o północy (minuta)"


def test_clear_data_no_station_code():
    df = pd.DataFrame({
        0: ["2023-01-01"],
        1: [10],
    })

    result = clear_data(df, year=2023)

    # Sprawdzenie, czy wykryto brak "Kod Stacji", czy wyjątek został podniesiony i zwrócono None
    assert result is None, "Nie wykryto braku 'Kod Stacji' "


def test_clear_data_removing():
    df = pd.DataFrame({
        0: ["Kod stacji", "2023-01-01 01:00", "brak daty"],
        1: ["ST01", 10, 99],
    })

    result = clear_data(df, year=2023)

    # Sprawdzenie, czy usunięto nieprawidłowe daty
    assert len(result) == 1, "Nie usunięto nieprawidłowych dat"
    assert result.iloc[0]["wartość"] == 10, "Nie usunięto nieprawidłowych dat"

def test_combine_years():

    all_data = {
        2020: pd.DataFrame({
            'czas': pd.date_range('2020-01-01', periods=3),
            'stacja': ['A', 'B', 'C'],
            'wartość': [1, 2, 3],
            'miejscowość': ['X', 'Y', 'Z']
        }),
        2021: pd.DataFrame({
            'czas': pd.date_range('2021-01-01', periods=3),
            'stacja': ['A', 'B', 'C'],
            'wartość': [3, 4, 5],
            'miejscowość': ['X', 'Y', 'Z']
        }),
    }

    df_all = combine_years(all_data)

    # Sprawdzenie typu
    assert isinstance(df_all, pd.DataFrame), "Funkcja powinna zwracać DataFrame"

    # Sprawdzenie, czy w df są wszystkie wymagane kolumny
    for col in ['czas', 'stacja', 'wartość', 'miejscowość', 'rok']:
        assert col in df_all.columns, f"Brak kolumny {col}"

    # Sprawdzenie, czy rok się zgadza
    assert all(df_all['rok'] == df_all['czas'].dt.year), "Kolumna 'rok' nie odpowiada kolumnie 'czas'"


def test_combine_years_filter():

    all_data = {
        2020: pd.DataFrame({
            'czas': pd.date_range('2020-01-01', periods=2),
            'stacja': ['A', 'C'],
            'wartość': [1, 2],
            'miejscowość': ['X', 'Z']
        }),
        2021: pd.DataFrame({
            'czas': pd.date_range('2021-01-01', periods=2),
            'stacja': ['A', 'B'],
            'wartość': [3, 4],
            'miejscowość': ['X', 'Y']
        }),
    }

    df_all = combine_years(all_data)

    # Sprawdzenie, czy odfiltrowano stacje, które nie są obecne we wszystkich latach
    assert set(df_all['stacja'].unique()) == {'A'}, "Nie odfiltrowano odpowiednich stacji"

