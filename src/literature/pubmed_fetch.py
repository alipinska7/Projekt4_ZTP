import argparse
import os
from pubmed_help import *

parser = argparse.ArgumentParser()
parser.add_argument("--year", required=True)
parser.add_argument("--config", required=True)
parser.add_argument("--output_dir", required=True)
args = parser.parse_args()

#Wczytywanie parametrów z configu
ustawienia = load_config_data(args.config)

#Pobranie danych (przekazujemy rok i wczytane ustawienia)
pobrane_artykuly = download_pubmed_data(args.year, ustawienia)

#Zapisanie wyników
save_results_to_csv(pobrane_artykuly, args.year, args.output_dir)

