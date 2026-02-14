import pandas as pd
import os
import argparse
from datetime import datetime


def generate_report(output_path):
    report = [f"# Raport Analizy Jakości Powietrza i Literatury\n",
              f"Data powstania raportu: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"]

    # --- PM2.5 ---
    report.append("## 1. Podsumowanie PM2.5 - Przekroczenia normy dobowej stężenia)")
    pm25_files = []

    for root, dirs, files in os.walk("results/pm25"):
        if "exceedance_days.csv" in files:
            pm25_files.append(pd.read_csv(os.path.join(root, "exceedance_days.csv")))

    if pm25_files:
        df_pm25 = pd.concat(pm25_files) #złączenie lat w tabelę
        #sortowanie od najnowszych danych, alfabetycznie według miejscowości
        df_pm25 = df_pm25.sort_values(by=['rok', 'miejscowość'], ascending=[False, True])
        report.append(df_pm25.to_markdown(index=False) + "\n")
    else:
        report.append("*Brak danych o przekroczeniach PM2.5.*\n")

    # Sekcja literatury
    report.append("## 2. Literatura (PubMed)")
    lit_files = []
    for root, dirs, files in os.walk("results/literature"):
        if "pubmed_papers.csv" in files:
            lit_files.append(pd.read_csv(os.path.join(root, "pubmed_papers.csv")))

    if lit_files:
        # Usunięcie duplikatów: ten sam artykuł mógł wpaść pod różne zapytania
        df_lit = pd.concat(lit_files).drop_duplicates(subset=['PMID', 'Query'])

        # Obliczanie łącznej liczby unikalnych publikacji
        total_unique = df_lit['PMID'].nunique()
        report.append(f"**Łączna liczba znalezionych unikalnych publikacji:** {total_unique}\n")

        # Ilość publikacji przypadająca na zapytanie
        report.append("### 2.1 Rozkład publikacji według zapytań")
        query_stats = df_lit.groupby('Query').size().reset_index(name='Liczba publikacji')
        report.append(query_stats.to_markdown(index=False) + "\n")

        # Trend w czasie (unikalne PMID, żeby nie liczyć dwa razy tego samego artykułu)
        report.append("### 2.2 Trend liczby publikacji w czasie")
        trend = df_lit.drop_duplicates('PMID').groupby('Year').size().reset_index(name='Liczba publikacji')
        report.append(trend.to_markdown(index=False) + "\n")

        # Top Czasopisma
        report.append("### 2.3 Top 8 czasopism")
        top_j = df_lit.drop_duplicates('PMID')['Journal'].value_counts().head(8).reset_index()
        top_j.columns = ['Journal', 'Liczba']
        report.append(top_j.to_markdown(index=False) + "\n")

        # Przykładowe tytuły artykułów
        report.append("### 2.4 Przykładowe tytuły")
        examples = df_lit.drop_duplicates('PMID')['Title'].head(5)
        for i, title in enumerate(examples, 1):
            report.append(f"{i}. {title}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    generate_report(args.output)