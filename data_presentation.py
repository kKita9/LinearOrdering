import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import math
import pandas as pd
import os

global PLOT_FOLDER_PATH


def prepare_folder_plots(proj_path):
    """
    Przygotowanie folderu do zapisania wykresow
    :param proj_path: sciezka do folderu z projektem
    :return:
    """
    global PLOT_FOLDER_PATH
    try:
        PLOT_FOLDER_PATH = os.path.join(proj_path, 'plots')
        os.mkdir(PLOT_FOLDER_PATH)
    except FileExistsError:
        # clear files in plot folders
        for file in os.listdir(PLOT_FOLDER_PATH):
            try:
                file_path = os.path.join(PLOT_FOLDER_PATH, file)
                os.remove(file_path)
            except Exception:
                continue


def pricing_comparison(data):
    """
    Zakresy cen telefonów i ich ilosc w rankingu
    :param data: zbior danych rankingu
    """
    bins = [0, 200, 400, 600, 800, 1000, 2000, 3000, 6000]
    labels = ['0-200', '201-400', '401-600', '601-800', '801-1000', '1001-2000', '2001-3000', '3001-6000']
    data['price_range'] = pd.cut(data['price'], bins=bins, labels=labels, include_lowest=True)
    plt.figure(figsize=(10, 6))
    sns.countplot(x='price_range', data=data, color='g')
    plt.title('Wielkości cen telefonów w przedziałach')
    plt.xlabel('Przedział cenowy telefonu')
    plt.ylabel('Liczba telefonów')
    plt.xticks(rotation=45)
    plot_name = os.path.join(PLOT_FOLDER_PATH, 'pricing_comparison.png')
    plt.savefig(plot_name)


def pricing_distribution(data):
    """
    Rozklad cen
    :param data:
    :return: zbior danych
    """
    plt.figure(figsize=(10, 6))
    sns.histplot(data['price'], kde=True, color='r')
    plt.title('Rozkład cen telefonów')
    plt.xlabel('Cena')
    plt.ylabel('Liczba telefonów')
    plot_name = os.path.join(PLOT_FOLDER_PATH, 'pricing_distribution.png')
    plt.savefig(plot_name)


def price_ram_memory(data):
    """
    wykres zaleznosci pomiedzy cena telefonu, pamiecia wawnetrzna i RAM
    :param data: zbior danych rankingu
    :return:
    """
    data['scaled_memory'] = data['memory'].apply(math.sqrt) * 10
    unique_memories = data['memory'].unique()
    colors = plt.cm.jet(np.linspace(0, 1, len(unique_memories)))
    memory_color_map = dict(zip(unique_memories, colors))
    data['color'] = data['memory'].map(memory_color_map)
    plt.figure(figsize=(14, 10))
    scatter = plt.scatter(data['ram'], data['price'], s=data['scaled_memory'], c=data['color'], alpha=0.5)
    legend_labels = [plt.Line2D([0], [0], marker='o', color='w', label=f'{mem} GB',
                                markerfacecolor=memory_color_map[mem], markersize=10, alpha=0.5)
                     for mem in unique_memories]
    plt.legend(handles=legend_labels, title='Pamięć wewnętrzna', scatterpoints=1, frameon=True, labelspacing=1,
               loc='upper left')

    plt.title('Porównanie ceny telefonów z pamięcią RAM')
    plt.xlabel('Pamięć RAM (GB)')
    plt.ylabel('Cena')
    plt.grid(True)
    plot_name = os.path.join(PLOT_FOLDER_PATH, 'price_ram_memory.png')
    plt.savefig(plot_name)


PLOTTING_FUNCTIONS = [pricing_comparison,  price_ram_memory, pricing_distribution]
