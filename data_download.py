import pandas
from bs4 import BeautifulSoup
import math
import asyncio
import aiohttp
import pandas as pd
from ast import literal_eval
from main import USER_BRANDS

BASIC_URL = 'https://www.sferis.pl'
BASIC_BRAND_URL = f'https://www.sferis.pl/telefony-3910?s=BrandName&o=popularity'


def get_brands_to_download_from_user(available_brands: list):
    """
    Pobranie nazw marek od uzytkownika, ktore maja byc w rankingu
    :param available_brands: lista dostepnych marek, ktore moga byc zawarte w rankingu
    :return:
    """
    # zapytaj jakie marki user chce miec w rankingu
    user_choice = input('Jesli chcesz brac wszystkie dostepne marki do rankingu wpisz "YES", jesli chcesz wybrac marki '
                        'wpisz "NO": ')
    while user_choice.upper() not in ['YES', 'NO']:
        user_choice = input(f'Podales niepoprawna wartosc: {user_choice}, sprobuj jeszcze raz ["YES", "NO"]: ')

    # wszystkie dostepne modele
    if user_choice.upper() == 'YES':
        USER_BRANDS.extend(available_brands)
        return USER_BRANDS

    # wybrane modele
    print('Aby wybrac marki do rankingu, nalezy wpisac w konsoli liste z nazwami dostepnych marek '
          '(np.: ["Apple", "Samsung", "Motorola"])')
    end_user_choice = False
    while not end_user_choice:
        user_choice = input(f'Podaj swoj wybor: ')

        # przekonwertuj podana liste marek na zmienna
        try:
            user_choice = literal_eval(user_choice)
        except Exception:
            print('Cos poszlo nie tak, sprobuj ponownie. ')
            continue

        # przypadek, gdy uzytkownik nie poda zadnej marki
        if len(user_choice) == 0:
            print('Nie podales zadnego modelu!')
            continue

        # sprawdzanie poprawnosci wpisanych marek
        is_user_brands_correct = [user_c.lower() in available_brands for user_c in user_choice]
        if not all(is_user_brands_correct):
            print('Podales nie poprawna marke! Sprobuj ponownie!')
        else:
            end_user_choice = True

    user_choice = [choice.lower() for choice in user_choice]
    USER_BRANDS.extend(user_choice)
    return USER_BRANDS


async def prepare_sites_links_for_brand(session: aiohttp.ClientSession, brand_name:str, brand_link: str,
                                        models_on_page=30, max_number_phones=100) -> list:
    """
    Przygotowanie linkow do wszystkich podstron z telefonami dla danej marki
    :param session: sesja do wykonywania asynchronicznych zapytan HTTP
    :param brand_name: nazwa marki
    :param brand_link: link do strony z telefonami dla danej marki
    :param models_on_page: liczba telefonow dostepnych na jednej stronie
    :param max_number_phones: maksymalna liczba telefonow ktore chcemy pobrac
    :return: lista linkow z dostepnymi stronami telefonow dla danej marki
    """
    async with session.get(brand_link) as response:
        if response.status != 200:
            return []

        text = await response.text()
        soup = BeautifulSoup(text, 'html.parser')

        try:
            available_models = soup.find(id='jsProductListingCounter').text
        except AttributeError:
            return []

        try:
            available_models = int(available_models[1:-1])
            available_models = available_models if available_models < max_number_phones else max_number_phones
        except TypeError:
            available_models = 0

        available_pages = math.ceil(available_models / models_on_page)
        pages_links = [brand_link + f'&p={page + 1}' for page in range(available_pages)]

        return pages_links


async def get_phone_names_and_links_from_page(session: aiohttp.ClientSession, page_link: str) -> dict:
    """
    Pobieranie nazw telefonow i linku do kazdego z telefonu znajdujacego sie na stronie
    :param session sesja do wykonywania asynchronicznych zapytan HTTP
    :param page_link: link do strony, z ktorej beda pobierane telefony
    :return: slownik, w ktorym klucz to nazwa telefonu, a wartosc to link do telefonu
    """
    async with session.get(page_link) as response:
        if response.status != 200:
            print(f'Problem przy linku {page_link}')
            return {}

        text = await response.text()
        soup = BeautifulSoup(text, 'html.parser')

        phones_links = {phone_elem.p.text[1:-1]: phone_elem['href'] for phone_elem in
                        soup.find_all('a', class_='tcz')}

        return phones_links


async def prepare_links_to_phones(user_brands_url: dict):
    """
    Przygotowanie adresów url dla każdego z telefonow
    :param user_brands_url: marki telefonow ktore uzytkownik chce miec w rankingu
    :return: slownik z adresami url do telefonow ktore beda brane pod uwage w rankingu
    """
    async with aiohttp.ClientSession() as session:
        print(f'Pobieranie adresów url do podstron dla marek: {list(user_brands_url.keys())} ...', end=' ')
        brands_pages_tasks = [
            prepare_sites_links_for_brand(session, brand_name, brand_link) for brand_name, brand_link
            in user_brands_url.items()
        ]
        brands_pages = await asyncio.gather(*brands_pages_tasks)
        print('zakonczono pobieranie.')

        print('Pobieranie nazw oraz adresow url do specyfikacji kazdego z telefonow ...', end=' ')

        phones_links = {}
        for brand_pages, brand_name in zip(brands_pages, user_brands_url):
            for page_url in brand_pages:
                phone_links = await get_phone_names_and_links_from_page(session, page_url)
                if phone_links:
                    phones_links.update(phone_links)

        print(f'pobieranie zakończone, udało się pobrać {len(phones_links)} adresów url.')
        return phones_links


async def get_phone_details(session: aiohttp.ClientSession, phone_name: str, phone_link: str) -> dict:
    """
    Pobieranie specyfikacji danego telefonu
    :param session: sesja do wykonywania asynchronicznych zapytan HTTP
    :param phone_name: nazwa telefonu
    :param phone_link: link do specyfikacji telefomu
    :return: slownik zawierajacy specyfikacje telefonu
    """
    p_details = {'name': phone_name}

    phone_link = BASIC_URL + phone_link

    async with session.get(phone_link) as response:
        if response.status != 200:
            return p_details

        details_text = await response.text()

        soup_details = BeautifulSoup(details_text, 'html.parser')

        price = soup_details.select_one('div.taq')
        if price is not None:
            p_details['price'] = price.text.replace(' ', '')

        spec_section = soup_details.find(id='section-spec')
        table_rows = spec_section.find_all('td')

        for idx_row in range(0, len(table_rows), 2):
            if table_rows[idx_row].text == 'Przekątna ekranu':
                p_details['screen_size'] = table_rows[idx_row + 1].text.replace(' ', '')
            elif table_rows[idx_row].text == 'Pamięć RAM':
                p_details['ram'] = table_rows[idx_row + 1].text.replace(' ', '')
            elif table_rows[idx_row].text == 'Pamięć wbudowana':
                p_details['memory'] = table_rows[idx_row + 1].text.replace(' ', '')
            elif table_rows[idx_row].text == 'Rozdzielczość tylnej kamery':
                p_details['rear_camera'] = table_rows[idx_row + 1].text.replace(' ', '')
            elif table_rows[idx_row].text == 'Rozdzielczość przedniej kamery':
                p_details['front_camera'] = table_rows[idx_row + 1].text.replace(' ', '')
            elif table_rows[idx_row].text == 'Waga produktu':
                p_details['weight'] = table_rows[idx_row + 1].text.replace(' ', '')

    return p_details


async def create_phones_details_df(p_links: dict) -> pandas.DataFrame:
    """
    Asynchorniczne pobieranie danych telefonów i tworzenie DataFrame'u
    :param p_links: slownik z nazwami i adresami url telefonow
    :return: DataFrame z informacjami o telefonach
    """
    print('Pobieranie szczegolowych informacji telefonow... To moze chwile potrwac...', end='')
    async with aiohttp.ClientSession() as session:
        tasks = []
        for phone_name, phone_links in p_links.items():
            task = asyncio.create_task(get_phone_details(session, phone_name, phone_links))
            tasks.append(task)

        phones = await asyncio.gather(*tasks)

        print('pobieranie zakonczone.')

        return pd.DataFrame(phones)
