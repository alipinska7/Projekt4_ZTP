import matplotlib.pyplot as plt
import seaborn as sns

#ZADANIE 2
def city_trends_plot(df, cities, years):
    """
        Funkcja rysuje wykres liniowy trendów średnich miesięcznych wartości PM2.5
        dla wybranych miast i lat (po uśrednieniu wyników ze wszystkich stacji pomiarowych w danym mieście).
        Oś X przedstawia miesiące (1–12), natomiast oś Y średnie wartości PM2.5.
        Wykres umożliwia porównanie zmian poziomu zanieczyszczenia powietrza w danych miastach dla określonych lat.

        Args:
        df (pd.DataFrame): DataFrame zawierający uśrednione dane miesięczne PM2.5 dla miast, z kolumnami:
            'miejscowość', 'rok', 'miesiąc', 'średnie_PM25'.
        cities (list[str]): Lista miast do uwzględnienia w analizie
        years (list[int]): Lista lat do porównania

    Zwraca:
        None
        Funkcja wyświetla wykres, nie zwraca wartości.
    """
    for city in cities:
        for year in years:
            df_plot = df[(df['miejscowość'] == city) & (df['rok'] == year)]
            plt.plot(df_plot['miesiąc'], df_plot['średnie_PM25'],
                     marker='o', label=f"{city} {year}")

    plt.xlabel('Miesiące', fontsize=12)
    plt.ylabel('Średnia wartość PM2.5', fontsize=12)
    plt.title("Trend średnich miesięcznych wartości PM2.5")
    plt.grid()
    plt.legend()
    plt.show()


#ZADANIE 3
def heatmap_plot(df_mean_month):
    """
        Funkcja tworzy heatmapy średnich miesięcznych stężeń PM2.5 dla wybranych lat i miejscowości.

        Funkcja generuje wykresy typu heatmap, w których:
        - oś X przedstawia miesiące (1–12),
        - oś Y przedstawia lata
        - kolor reprezentuje średnie stężenie PM2.5 w danym miesiącu i roku,
          uśrednione po wszystkich stacjach w danej miejscowości.

        Każdy panel odpowiada jednej miejscowości, co pozwala
        porównać zmiany poziomu zanieczyszczeń w czasie
        pomiędzy różnymi miastami.

        Args:
            df_mean_month (pd.DataFrame):
                DataFrame zawierający uśrednione miesięczne dane PM2.5 dla miast, z kolumnami:
                'miejscowość', 'rok', 'miesiąc', 'średnie_PM25'.
        Returns:
            None
                Funkcja wyświetla heatmapy, nie zwraca wartości.

        Uwaga: Kolor heatmapy jest skalowany od 0 do 70 µg/m³.
        """
    # Lista badanych miast
    cities = df_mean_month['miejscowość'].unique()

    # Tworzenie siatki (5 wierszy x 4 kolumny)
    fig, axes = plt.subplots(nrows=5, ncols=4, figsize=(30, 25))
    axes = axes.flatten()  # spłaszczenie do listy

    for ax, city in zip(axes, cities):
        m_avg = df_mean_month[df_mean_month['miejscowość'] == city]
        h_data = (m_avg.pivot_table(values='średnie_PM25', index='rok', columns='miesiąc').astype(float))

        sns.heatmap(h_data, cmap='rocket_r', vmin=0.0, vmax=70.0, cbar=False, ax=ax)
        ax.set_title(city)
        ax.set_xlabel('Miesiąc')
        ax.set_ylabel('Rok')

    # Dodanie odpowiedniej skali kolorów
    cbar = fig.colorbar(axes[0].collections[0], ax=axes, orientation='vertical')
    cbar.set_label('Średnie PM2.5')

    plt.show()


#ZADANIE 4
def barplot(df_exc):
    """
        Funkcja tworzy grupowy wykres słupkowy liczby dni z przekroczeniem dobowej normy PM2.5.

        Funkcja wizualizuje liczbę dni, w których stężenie PM2.5 przekroczyło
        dobową normę dla wybranych stacji i lat.

        Na wykresie:
        - oś X przedstawia stacje, oś Y – liczbę dni z przekroczeniem,
        - kolor słupków reprezentuje rok.

        Args:
            df_exc (pd.DataFrame):
                DataFrame zawierający przekształcone dane o liczbie dni
                z przekroczeniem PM2.5 dla poszczególnych stacji i lat,
                z kolumnami:
                - 'miejscowość' (nazwa stacji),
                - 'rok',
                - 'ilość przekroczeń'.
        Returns:
            None
            Funkcja wyświetla wykres słupkowy, nie zwraca wartości.
    """
    plt.figure(figsize=(12, 9))
    sns.barplot(data=df_exc, x='miejscowość', y='ilość przekroczeń', hue='rok', width=0.8)
    plt.title("Wykres przekroczeń dobowej normy zanieczyszczeń PM2.5 dla wybranych stacji", size=20)
    plt.ylabel("Ilość wykroczeń ponad dobową normę dla danego roku", size=13)
    plt.xlabel("Stacje", size=13)
    plt.grid()
    plt.show()

def plot_voivodeship_comparison(df_voivodeship):

    df_long = df_voivodeship.reset_index().melt(
        id_vars='Województwo',
        var_name='rok',
        value_name='liczba_dni'
    )

    # Ustawienie stylu i rozmiaru wykresu
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(15, 8))

    # Rysowanie wykresu słupkowego
    # x: Województwo, y: liczba dni
    ax = sns.barplot(
        data=df_long,
        x='Województwo',
        y='liczba_dni',
        hue='rok',
        palette='Pastel2'
    )

    # 4. Dodanie legendy i opisów
    plt.title('Liczba dni z przekroczeniem normy PM2.5 w województwach', fontsize=16)
    plt.xlabel('Województwo', fontsize=12)
    plt.ylabel('Suma dni z przekroczeniem', fontsize=12)
    plt.xticks(rotation=45, ha='right')

    # Dostosowanie legendy, aby nie zasłaniała danych
    plt.legend(title='Rok pomiaru', bbox_to_anchor=(1.02, 1), loc='upper left')

    # Opcjonalne: Dodanie wartości nad słupkami dla precyzji
    for container in ax.containers:
        ax.bar_label(container, padding=3, fontsize=8, rotation=90)

    plt.tight_layout()
    plt.show()