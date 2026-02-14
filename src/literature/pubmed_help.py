import pandas as pd
from Bio import Entrez
import yaml
import os

def load_config_data(config_path):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    cities = config.get("cities", [])

    # Wydobycie aliasów miast
    city_aliases = config.get("city_aliases", {})
    expanded_cities = []

    for city in cities:
        if city in city_aliases:
            expanded_cities.extend(city_aliases[city])
        else:
            expanded_cities.append(city)

    return {
        'email': config['pubmed']['entrez_email'],
        'limit': config['pubmed']['retmax'],
        'queries': config['pubmed']['queries'],
        'cities': expanded_cities
    }




def download_pubmed_data(year, settings):
    Entrez.email = settings['email']
    all_papers = []

    # Iteracja po zapytaniach
    for query_text in settings['queries']:
        #cities_part = "(" + " OR ".join(settings['cities']) + ")"
        #linia u góry: wyszukiwanie miast w którychkolwiek polach artykułu
        #(artykuł wcale nie musi dotyczyć zanieczyszczeń w podanych miastach)
        cities_tagged = [f"{city}[TIAB]" for city in settings['cities']]
        cities_part = "(" + " OR ".join(cities_tagged) + ")"
        full_query = f"({query_text}) AND {cities_part} AND {year}[DP]"

        print(f"Pobieranie dla frazy: '{query_text}' w roku {year}...")

        # Połączenie z PubMed; uzyskanie numerów ID pasujących do zapytania
        handle = Entrez.esearch(db="pubmed", term=full_query, retmax=settings['limit'])
        search_results = Entrez.read(handle)
        handle.close()


        id_list = search_results['IdList']
        if not id_list:
            continue

        # Prośba o kompletne dane dla artykułów, które pasują do zapytania
        fetch_handle = Entrez.efetch(db="pubmed", id=",".join(id_list), retmode="xml")
        records = Entrez.read(fetch_handle)
        fetch_handle.close()

        # Iteracja po artykułach i wyciągnięcie informacji z interesujących nas pól
        for article in records['PubmedArticle']:
            try:
                citation = article['MedlineCitation']
                details = citation['Article']

                authors_list = details.get('AuthorList', [])
                names = []
                for auth in authors_list:
                    # PubMed przechowuje nazwisko w 'LastName' i inicjały w 'Initials'
                    if 'LastName' in auth and 'Initials' in auth:
                        names.append(f"{auth['LastName']} {auth['Initials']}")

                #Łączenie autorów przecinkiem, jeśli lista jest pusta: "Brak danych"
                authors_string = ", ".join(names) if names else "Brak danych"

                #dodanie do listy słownika z danymi (dla każdego artykułu osobny słownik)
                all_papers.append({
                    'PMID': str(citation['PMID']),
                    'Title': details.get('ArticleTitle', 'Brak tytułu'),
                    'Year': year,
                    'Journal': details['Journal'].get('Title', 'Nieznany'),
                    'Authors': authors_string,
                    'Query': query_text #ważne do statystyk, które zapytanie ile zwróciło
                })

            # Zabezpieczenie przed artykułami, w których brakuje pól; przejście dalej
            except Exception:
                continue
    return all_papers



def save_results_to_csv(data_list, year, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    # Zabezpieczenie przed brakiem danych dla wyszukiwań
    if not data_list:

        pd.DataFrame(columns=['PMID', 'Title', 'Year', 'Journal', 'Authors']).to_csv(
            os.path.join(output_dir, "pubmed_papers.csv"), index=False)

        pd.DataFrame([{'Year': year, 'Total_Papers': 0}]).to_csv(
            os.path.join(output_dir, "summary_by_year.csv"), index=False)

        pd.DataFrame(columns=['Journal', 'Count']).to_csv(
            os.path.join(output_dir, "top_journals.csv"), index=False)

        print(f"Brak wyników dla roku {year}. Zapisano puste pliki.")
        return

    # Stworzenie DateFrame i zapis do pliku
    df = pd.DataFrame(data_list).drop_duplicates(subset='PMID')

    #plik: główna lista publikacji
    df.to_csv(os.path.join(output_dir, "pubmed_papers.csv"), index=False)

    #plik: publikacje w danym roku
    summary_df = pd.DataFrame([{'Year': year, 'Total_Papers': len(df)}])
    summary_df.to_csv(os.path.join(output_dir, "summary_by_year.csv"), index=False)

    #plik: top 10 czasopism
    top_journals = df['Journal'].value_counts().head(10).reset_index()
    top_journals.columns = ['Journal', 'Count']
    top_journals.to_csv(os.path.join(output_dir, "top_journals.csv"), index=False)

    print(f"Sukces! Pliki dla roku {year} zapisane w: {output_dir}")






















