import yaml
import os

with open("config/task4.yaml", "r") as f:
    config = yaml.safe_load(f)

YEARS = config["years"]

rule all:
    input:
        expand("results/pm25/{year}/exceedance_days.csv", year=YEARS),
        expand("results/pm25/{year}/daily_means.csv", year=YEARS),
        expand("results/literature/{year}/pubmed_papers.csv", year=YEARS),
        expand("results/pm25/{year}/figures/top_exceedances.png", year=YEARS),
        expand("results/pm25/{year}/figures/monthly_heatmap.png",year=YEARS),
        "results/report_task4.md"

# Pobieranie surowych danych
rule download_pm25:
    output:
        "data/raw/pm25_{year}.pkl"
    shell:
        "python src/wczytywanie.py --year {wildcards.year} --output {output}"

# Czyszczenie danych
rule clean_pm25_year:
    input:
        raw = "data/raw/pm25_{year}.pkl",
        script = "src/czyszczenie_danych.py"
    output:
        cleaned = "data/processed/pm25_{year}_cleaned.pkl"
    shell:
        "python {input.script} "
        "--input {input.raw} "
        "--year {wildcards.year} "
        "--output {output.cleaned} "



# Analiza danych
rule analyze_pm25:
    input:
        data = "data/processed/pm25_{year}_cleaned.pkl",
        script = "src/obliczenia.py",
        config = "config/task4.yaml"
    output:
        exceedance = "results/pm25/{year}/exceedance_days.csv",
        daily = "results/pm25/{year}/daily_means.csv",
    params:
        cities = config.get("cities", [])

    run:
        cities_arg = " ".join(params.cities) if params.cities else ""
        shell(
            f"python {input.script} "
            f"--input {input.data} "
            f"--year {wildcards.year} "
            f"--output_dir results/pm25/{wildcards.year} "
            f"--cities {cities_arg}"
        )

# Wykresy
rule plot_pm25_yearly:
    input:
        ex_csv = "results/pm25/{year}/exceedance_days.csv",
        daily_csv = "results/pm25/{year}/daily_means.csv"
    output:
        plot_ex = "results/pm25/{year}/figures/top_exceedances.png",
        plot_daily = "results/pm25/{year}/figures/monthly_heatmap.png"
    shell:
        "python src/wykresy_rok.py "
        "--input_exc {input.ex_csv} "
        "--input_daily {input.daily_csv} "
        "--output_dir results/pm25/{wildcards.year} "
        "--year {wildcards.year}"


# Literatura PubMed
rule pubmed_year:
    input:
        script = "src/literature/pubmed_fetch.py",
    output:
        papers = "results/literature/{year}/pubmed_papers.csv",
        summary = "results/literature/{year}/summary_by_year.csv",
        journals = "results/literature/{year}/top_journals.csv",
    shell:
        "python {input.script} "
        "--year {wildcards.year} "
        "--config config/task4.yaml "
        "--output_dir results/literature/{wildcards.year}"


# Raport
rule report_task4:
    input:
        pm25 = expand("results/pm25/{year}/exceedance_days.csv", year=YEARS),
        lit = expand("results/literature/{year}/pubmed_papers.csv", year=YEARS)
    output:
        report = "results/report_task4.md"
    shell:
        "python src/generate_report.py --output {output.report}"
