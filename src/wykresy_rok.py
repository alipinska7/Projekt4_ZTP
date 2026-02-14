import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import os


def generate_yearly_plots(input_csv, output_dir, year):
    # Utworzenie folderu na wykresy (jeśli nie istnieje)
    figures_dir = os.path.join(output_dir, "figures")
    os.makedirs(figures_dir, exist_ok=True)

    # Wczytanie danych o przekroczeniach
    df = pd.read_csv(input_csv)

    # Sortowanie od miejscowości z najczęściej przekroczoną normą w danym roku
    df_max = df.groupby('miejscowość', as_index=False)['ilość przekroczeń'].max()
    df_sorted = df_max.sort_values('ilość przekroczeń', ascending=False).head(15)

    # Przygotowanie wykresu
    plt.figure(figsize=(10, 8))
    sns.barplot(
        data=df_sorted,
        x='ilość przekroczeń',
        y='miejscowość',
        palette='OrRd_r'
    )

    plt.title(f"Miejscowości z największą liczbą przekroczeń w {year} roku", fontsize=14)
    plt.xlabel("Liczba dni powyżej normy (15 µg/m³)")
    plt.ylabel("Miejscowość")
    plt.grid(axis='x', linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(figures_dir, "top_exceedances.png"))
    plt.close()

    print(f"Wygenerowano wykresy dla roku {year} w folderze {figures_dir}")


def plot_monthly_heatmap(csv_path, output_path, year):
    df = pd.read_csv(csv_path)

    # Przygotowanie danych
    df['data'] = pd.to_datetime(df['data'])
    df['miesiąc'] = df['data'].dt.month

    # Średnia miesięczna dla każdego miasta
    monthly_avg = df.groupby(['miejscowość', 'miesiąc'])['pm25_dobowe'].mean().unstack()

    # Zapewnienie wszystkich 12 miesięcy na osi X
    monthly_avg = monthly_avg.reindex(columns=range(1, 13))

    # Wybór miast (obsługa przypadku gdy jest ich mniej niż 20)
    n_cities = min(20, len(df['miejscowość'].unique()))
    top_cities = df.groupby('miejscowość')['pm25_dobowe'].mean().nlargest(n_cities).index
    monthly_avg = monthly_avg.loc[top_cities]

    # Rysowanie wykresu
    plt.figure(figsize=(12, max(4, len(top_cities) * 0.5)))

    sns.heatmap(
        monthly_avg,
        cmap='YlOrRd',
        annot=True,  # Wyświetla liczby w kwadracikach
        fmt=".1f",  # Formatowanie liczb do 1 miejsca po przecinku
        cbar_kws={'label': 'Średnie stężenie PM2.5 [µg/m³]'}
    )

    plt.title(f"Miesięczne stężenia PM2.5 w {year} roku (Top 20 miejscowości)", fontsize=15)
    plt.xlabel("Miesiąc")
    plt.ylabel("Miejscowość")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()




if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--input_exc", required=True, help="Ścieżka do exceedance_days.csv")
    parser.add_argument("--input_daily", required=True, help="Ścieżka do daily_means.csv")
    parser.add_argument("--output_dir", required=True, help="Folder roku")
    parser.add_argument("--year", required=True)
    args = parser.parse_args()

    generate_yearly_plots(args.input_exc, args.output_dir, args.year)
    path_heatmap = os.path.join(args.output_dir, "figures", "monthly_heatmap.png")
    plot_monthly_heatmap(args.input_daily, path_heatmap, args.year)