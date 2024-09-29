import data_download as download
import data_preparation as preparation
import data_presentation as presentation
import asyncio
from tabulate import tabulate
import pandas as pd
import time
import os
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
RED = '\033[31m'
GREEN = '\033[32m\033[1m'
YELLOW = '\033[33m'
PURPLE = '\033[35m'
RESET = '\033[0m'
BASIC_BRANDS = ['samsung', 'apple', 'motorola', 'xiaomi', 'huawei', 'realme']
USER_BRANDS = []


def print_header(text: str, h_width=150, h_color='\033[0m'):
    global RESET
    header = text.center(h_width, '-')
    print(f'{h_color}{header.upper()}{RESET}')


def main():
    global USER_BRANDS

    print()
    print_header('System tworzenia rankigu telefonow', h_color=GREEN)
    print()
    print('Witaj w systemie tworzenia rankigu telefonow dostepnych na stronie "sferis.pl".')
    basic_models = ', '.join(list(map(lambda b: b.capitalize(), BASIC_BRANDS)))
    print(f'Aktualnie dostepne marki brane do rankingu to: {basic_models}.')

    USER_BRANDS = download.get_brands_to_download_from_user(BASIC_BRANDS)

    start_time = time.time()
    # przygotowania do pobierania danych
    user_brands_url = {brand: download.BASIC_BRAND_URL.replace('BrandName', brand) for brand in USER_BRANDS}

    # pobieranie adresow url
    print()
    print_header('POBIERANIE DANYCH', h_color=PURPLE)

    phones_links = asyncio.run(download.prepare_links_to_phones(user_brands_url))

    # sprawdzenie czy pobieranie adresów poszlo pomyslnie
    do_continue_download = False if len(phones_links) == 0 else True

    # przygotowanie ramki danych
    phones_df = []

    # pobieranie danych ze strony
    if do_continue_download:
        print('Wczytuje dane ze strony!')
        phones_df = asyncio.run(download.create_phones_details_df(phones_links))

    # awaryjne wczytanie danych, na wypadek problemow z pobieraniem danych ze strony
    if len(phones_df) == 0 or not do_continue_download:
        print('Wczytuje dane z pliku .csv!')
        phones_df = pd.read_csv('data/phones_details.csv')
        phones_df = phones_df[phones_df['name'].apply(preparation.contains_model)]

    download_time = time.time() - start_time

    # przerwij program na wypadek gdyby nie udalo sie zaladowac zadnych danych ani ze strony ani z pliku csv
    if len(phones_df) == 0:
        print()
        print_header('Nie ma zadnych danych. Cos poszlo nie tak. Sprobuj ponownie!', h_color=RED)
        return

    print()
    print(f'Czas pobierania danych: {download_time:.2f}s')
    print()

    print()
    print_header('PRZETWARZANIE DANYCH', h_color=PURPLE)
    start_time = time.time()

    # obróbka danych
    preparation.clean_all(phones_df)

    # wypełnianie ramu dla Apple
    if 'apple' in USER_BRANDS:
        preparation.fill_ram_in_apple(phones_df)

    # usuwanie wartości brakujących
    preparation.removal_missing_values(phones_df)

    # ustawienie kolumny 'name' jako indeks
    phones_df.set_index('name', inplace=True)

    # przygotowanie danych do porzadkowania liniowego
    linear_ordering_data = preparation.convert_data_to_linear_ordering(phones_df)

    # standaryzacja danych
    for column in preparation.COLUMNS_NAMES:
        column_to_standarize = linear_ordering_data[column]
        linear_ordering_data[column] = preparation.column_standarization(column_to_standarize)

    # wyznaczenie wzorca
    pattern = [max(linear_ordering_data[column]) for column in preparation.COLUMNS_NAMES]

    # obliczenie odleglosci od wzorca
    linear_ordering_data = preparation.count_distance_from_pattern(linear_ordering_data, pattern)

    # mozliwie daleka odleglosc od wzorca
    far_distance = preparation.calculate_distance_as_far_as_posibble_from_pattern(linear_ordering_data)

    # wyznaczenie miary Hellwiga
    phones_df['h_measure'] = preparation.determination_of_hellwigs_measure(linear_ordering_data, far_distance)

    preparation_time = time.time() - start_time

    print()
    print(f'Czas przetwarzania danych: {preparation_time:.2f}s')
    print()

    # stworzenie rankingu
    phones_ranking = phones_df.sort_values(by='h_measure', ascending=False)
    phones_ranking['ranking'] = range(1, len(phones_ranking)+1)
    top_10_phones = phones_ranking.head(10).reset_index()

    print()
    print_header('TOP 10 TELEFONÓW', h_color=RED)
    print(tabulate(top_10_phones[['ranking', 'name', 'price']], headers='keys', tablefmt='grid', showindex=False))
    print()

    print(f'Ranking zostal zapisany do pliku: ranking.csv')
    ranking_columns = ['ranking', 'name', 'price', 'screen_size', 'ram', 'memory', 'rear_camera', 'front_camera', 'weight']
    phones_ranking = phones_ranking.reset_index()
    phones_ranking[ranking_columns].to_csv('ranking.csv', index=False)

    start_time = time.time()
    print()
    print_header('PREZENTACJA DANYCH', h_color=PURPLE)
    presentation.prepare_folder_plots(PROJECT_PATH)
    print('Wykresy zostaly zapisane do folderu: "plots/"')
    presentation.prepare_folder_plots(PROJECT_PATH)
    for plot_fun in presentation.PLOTTING_FUNCTIONS:
        plot_fun(phones_ranking)
    print()

    presentation_time = time.time() - start_time

    print()
    print(f'Czas tworzenia prezentacji danych: {presentation_time:.2f}s')
    print()

    print_header('ZYCZYMY UDANYCH ZAKUPOW !!!', h_color=YELLOW)


if __name__ == '__main__':
    main()
