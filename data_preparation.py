import pandas
import pandas as pd
import numpy as np
import time
import math
import main

COLUMNS_NAMES = ['price', 'screen_size', 'ram', 'memory', 'rear_camera', 'front_camera', 'weight']

# slownik zawierajacy definicje  typow zmiennych, ktore maja znaczenie podczas tworzenia rankingu
# mozliwosc zmiany typow zmiennych wedlug wlasnego uznania
# nalezy uwazac na pisownie zmiennych oraz zachowanie poprawnej struktury
# nalezy pamietac aby kazda zmienna byla przypisana tylko do jednego typu
# stimulants - typ zmiennej dla ktorej wartosci maja byc jak najwieksze, np. chcemy aby RAM telefonu byl jak najwiekszy
# destimulants - typ zmiennej dla ktorej wartosci maja byc jak najmniejsze, np. chcemy aby cena telefonu byla jak najmniejsza
# niminals - typ zmiennej dla ktorej ma byc pewna ustalona wartosc,np. chcemy aby telefon mial wielkosc ekranu rowna 6.1
VARIABLES_TYPES = {
    # zmienne dla ktorych chcemy aby ich wartosci byly jak najwieksze
    'stimulants': ['memory', 'rear_camera', 'front_camera', 'ram'],

    # zmienne dla ktorych chcemy aby ich wartosci byly jak najmniejsze
    'destimulants': ['weight', 'price'],

    # porzadane wartosci (np.: wielkosc ekranu rowna 6.1 cala), nalezy uwazac na typ oraz zakres definiowanych wartosci
    'nominals': {
        'screen_size': 6.5
    }
}


def data_cleaning(data, column_name):
    """
    czyszczenie i zamiana typu danych
    :param data: zbior danych
    :param column_name: reprezentujaca parametr modelu telefonu
    """
    column_index = data.columns.get_loc(column_name)
    for i, value in enumerate(data[column_name]):
        if not pd.isna(value):
            if column_name == 'price':
                value_cleaned = value.replace('zł','').replace(',', '.')
            elif column_name == 'screen_size':
                value_cleaned = value.replace('"', '').replace(',', '.')
            elif column_name == 'ram' or column_name == 'memory' :
                value_cleaned = value.replace('GB', '').replace(',', '.')
            elif column_name == 'rear_camera':
                value_cleaned = value.replace('MP', '').replace('Mpix', '').replace(',', '.')
            elif column_name == 'front_camera':
                value_cleaned = value.replace('MP', '').replace('Mpix', '').replace(',', '.')
            elif column_name == 'weight':
                value_cleaned = value.replace('g', '').replace(',', '.')
            try:
                data.iloc[i, column_index] = float(value_cleaned)
            except Exception:
                data.iloc[i, column_index] = np.nan


def clean_all(data):
    """
    czyszcznie i zamiana typu danych dla parametrow modelu
    :param data:zbior danych
    """
    print('Rozpoczynanie obrobki danych...' , end='')
    time.sleep(2)
    print(' dane są przygotowywane do dalszego przetwarzana..')
    for column in COLUMNS_NAMES:
        # data[column] = data_cleaning(data, column)
        data_cleaning(data, column)
    time.sleep(2)


def removal_missing_values(data):
    """
    usuwanie wartosci brakujacych
    :param data: zbior danych
    """
    print('Rozpoczecie usuwania danych brakujacych... \n')
    data.dropna(inplace=True)
    time.sleep(2)
    print('Dane zostaly przygotowane pomyślnie.')


def fill_ram_in_apple(data):
    """
    wypelnianie RAMu dla modeli telefonow Apple
    :param data:
    :return:
    """
    apple_data = data[data['name'].str.contains('Apple', na=False)]
    apple_data = apple_data.fillna(6)
    data[data['name'].str.contains('Apple', na=False)] = apple_data


# PORZADKOWANIE LINIOWE
def convert_data_to_linear_ordering(data: pandas.DataFrame) -> pandas.DataFrame:
    """
    Funkcja przygotowujaca dane do porzadkowania liniowego
    :param data: dane, ktore zostana przeksztalcone
    :return: przeksztalcone dane
    """
    data = data.copy()

    # nominanty -> stymulanty
    for col_name, desired_value in VARIABLES_TYPES['nominals'].items():
        data[col_name] = data[col_name].apply(lambda x: convert_nominals_to_stimulants(x, desired_value))

    # destymulanty -> stymulanty
    for col_name in VARIABLES_TYPES['destimulants']:
        data[col_name] = -1 * data[col_name]

    return data


def convert_nominals_to_stimulants(value, desired_value) -> float:
    """
    Zamiana nominant na stymulanty
    :param value: wartosc, ktora zostanie zamieniona
    :param desired_value: porzadana wartosc
    :return: nowa wartosc
    """
    if value == desired_value:
        value = 1
    elif value < desired_value:
        value = -1 / (value - desired_value - 1)
    else:
        value = 1 / (value - desired_value + 1)

    return value


def column_standarization(column):
    """
    Standaryzacja zmiennych
    :param column: kolumna DataFrame'u
    :return: zestandaryzowana kolumna
    """
    mean = column.mean()
    std = column.std()
    try:
        standarized_column = (column - mean) / std
    except ZeroDivisionError:
        standarized_column = (column - mean) / 1

    return standarized_column


def count_distance_from_pattern(data: pandas.DataFrame, pattern: list):
    """
    Liczenie odleglosci od wzorca
    :param data: dane
    :param pattern: wzorzec danych
    :return: dane telefonow z dodatkowa kolumna zawierajaca dystans od wzorca
    """
    data = data.copy()

    data[COLUMNS_NAMES] = (data[COLUMNS_NAMES] - pattern) ** 2
    data['distance'] = data[COLUMNS_NAMES].sum(axis=1)
    data['distance'] = data['distance'].apply(math.sqrt)
    return data


def calculate_distance_as_far_as_posibble_from_pattern(data: pd.DataFrame):
    """
    Obliczanie najwiekszej mozliwej odleglosci od wzorca
    :param data: dane
    :return: najwieksza odleglosc od wzorca
    """
    return data['distance'].mean() + 2 * data['distance'].std()


def determination_of_hellwigs_measure(data: pandas.DataFrame, far_distance: float):
    """
    Oblicznie miary hellwiga, ktora posluzy do wyznaczenia kolejnosci w rankingu
    :param data: dane
    :param far_distance: najwieksza odleglosc od wzorca
    :return: nowa kolumna z miarami hellwiga
    """
    return 1 - data['distance'] / far_distance


def contains_model(phone_name, ):
    """
    Wybranie modeli zdefiniowanych przez uzytkownika do ramki danych
    :param phone_name: nazwa telefonu z DataFrame'u
    :return: True jesli dany telefon ma byc brany do ramki danych, False jesli nie
    """
    return any(model in phone_name.lower() for model in main.USER_BRANDS)

