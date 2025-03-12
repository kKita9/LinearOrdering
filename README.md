# Linear Ordering - Mobile Phone Ranking Project

## Project Description
The **LinearOrdering** project is an application that generates a ranking of mobile phones based on data collected from the "sferis.pl" website. The process consists of three main stages: web scraping, data processing, and linear ordering using Hellwig's method.

The primary goal was to develop a program that provides a clear and structured output in the console, showcasing the ranking of mobile phones based on the selected brands and criteria.

## Linear Ordering with Hellwig's Method
Hellwig's method is a statistical technique used for multi-criteria analysis, allowing the determination of a synthetic development measure. In our case, this method enables the evaluation and ranking of mobile phones based on selected features such as price, battery capacity, camera resolution, and RAM amount.

## Technologies and Libraries Used
The project is written in Python and utilizes the following libraries:
- **aiohttp** – asynchronous data retrieval from the "sferis.pl" website.
- **BeautifulSoup** – parsing HTML code.
- **pandas** – data processing and analysis.
- **numpy** – numerical operations and statistical calculations.
- **matplotlib** and **seaborn** – data visualization.

## Project Structure
- `main.py` – the main script that runs the application.
- `data_download.py` – module responsible for web scraping.
- `data_preparation.py` – data cleaning and processing, implementation of Hellwig's method and ranking generation.
- `data_presentation.py` – results visualization.
- `data/` – directory containing saved input data.
- `plots/` – directory containing result charts.

## Installation and Usage
1. Clone the repository:
   ```bash
   git clone https://github.com/Karina11006/LinearOrdering.git
   cd LinearOrdering
   ```
2. Install required libraries:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the main script:
   ```bash
   python main.py
   ```
### Fallback Data Handling

If the website structure changes and scraping fails due to modifications in CSS selectors, the program automatically loads data from a backup CSV file located in the data/ directory. This ensures that the ranking process can still function even when real-time data retrieval is unavailable.


## Console Output Example:

![obraz](https://github.com/user-attachments/assets/3e7086ed-41ac-439b-9a46-7153d039bbf9)

![obraz](https://github.com/user-attachments/assets/df829bed-7048-47e2-a888-5eae8ea02fb4)

![obraz](https://github.com/user-attachments/assets/4eb665f7-d86c-4ed3-82f6-2ad6183d1628)

![obraz](https://github.com/user-attachments/assets/25026d82-da4b-4856-857b-6c1fd59d133f)

![obraz](https://github.com/user-attachments/assets/7548b707-6a5a-44c2-8dfe-859725896e7e)

![obraz](https://github.com/user-attachments/assets/4bd9745b-0818-4295-a0f8-9c805f52e3bc)


### 👩🏻‍💻 Project authors:
* Karina Krotkiewicz - karina.krotkiewicz@gmail.com
* Karol Kita - kkita970@gmail.com
