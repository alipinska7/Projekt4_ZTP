import pytest
import pandas as pd
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from literature.pubmed_help import load_config_data, download_pubmed_data, save_results_to_csv

from unittest.mock import patch, MagicMock

def test_load_config_data(tmp_path):
    config_yaml = tmp_path / "config.yaml"
    config_yaml.write_text("""
cities:
  - Warsaw
  - Katowice

city_aliases:
  Warsaw: ["Warsaw", "Warszawa"]
  Katowice: ["Katowice"]

pubmed:
  entrez_email: test@example.com
  queries:
    - '"PM2.5"[TIAB]'
    - '"fine particulate matter"[TIAB]'
  retmax: 50
""")
    result = load_config_data(str(config_yaml))

    assert result['cities'] == ["Warsaw", "Warszawa", "Katowice"]
    assert result['email'] == "test@example.com"
    assert result['queries'] == ['"PM2.5"[TIAB]', '"fine particulate matter"[TIAB]']
    assert result['limit'] == 50



#test download_pubmed_data
# Mockowanie zapytań do API PubMed, w celu przetestowania funkcji bez faktycznego pobierania danych
@patch("literature.pubmed_help.Entrez.esearch")
@patch("literature.pubmed_help.Entrez.efetch")
@patch("literature.pubmed_help.Entrez.read")
def test_download_pubmed_data(mock_read, mock_efetch, mock_esearch):
    # przygotowanie danych zwracanych przez Entrez.read

    mock_read.side_effect = [
        {'IdList': ['1', '2']},  # Wynik esearch
        {'PubmedArticle': [
            {'MedlineCitation': {'PMID': '1', 'Article': {
                'ArticleTitle': 'Title 1',
                'AuthorList': [{'LastName': 'Kowalski', 'Initials': 'J'}],  # Dodane dane autora
                'Journal': {'Title': 'Journal1'}}}},
            {'MedlineCitation': {'PMID': '2', 'Article': {
                'ArticleTitle': 'Title 2',
                'AuthorList': [{'LastName': 'Nowak', 'Initials': 'A'}],  # Dodane dane autora
                'Journal': {'Title': 'Journal2'}}}}
        ]}  # Wynik efetch
    ]
    settings = {
        'email': 'test@example.com',
        'limit': 10,
        'queries': ['PM2.5'],
        'cities': ['Warsaw']
    }
    papers = download_pubmed_data(2024, settings)
    assert len(papers) == 2
    assert papers[0]['Authors'] == "Kowalski J"

    # Sprawdzenie, czy wszystkie kolumny są obecne
    for paper in papers:
        assert 'PMID' in paper
        assert 'Title' in paper
        assert 'Year' in paper
        assert 'Journal' in paper
        assert 'Authors' in paper



def test_save_results_to_csv(tmp_path):
    data_list = [
        {'PMID': '1', 'Title': 'A', 'Year': 2024, 'Journal': 'J1', 'Authors': 'X'},
        {'PMID': '2', 'Title': 'B', 'Year': 2024, 'Journal': 'J2', 'Authors': 'Y'},
    ]
    out_dir = tmp_path / "results"
    save_results_to_csv(data_list, 2024, str(out_dir))

    # sprawdzenie, czy pliki istnieją
    assert (out_dir / "pubmed_papers.csv").exists()
    assert (out_dir / "summary_by_year.csv").exists()
    assert (out_dir / "top_journals.csv").exists()

    # sprawdzenie, czy w pliku jest odpowiednia ilość pozycji i czy zawiera on wszystkie kolumny
    df = pd.read_csv(out_dir / "pubmed_papers.csv")
    assert len(df) == 2
    assert set(df.columns) == {'PMID', 'Title', 'Year', 'Journal', 'Authors'}
