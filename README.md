# Linear Ordering - Mobile Phone Ranking Project

This project focuses on web scraping and linear ordering to generate a ranking of mobile phones based on user-selected criteria. Using Python, it scrapes data from the "sferis.pl" website, processes it, and creates a console-based output ranking. The project employs a variety of Python libraries for asynchronous web scraping, data processing, and visualization.

The primary goal was to develop a program that provides a clear and structured output in the console, showcasing the ranking of mobile phones based on the selected brands and criteria.
## Project Structure:
```
LinearOrdering/
│
├── data/
│   ├── data_download.py          # Script for downloading mobile phone data
│   ├── data_preparation.py       # Script for cleaning and preparing the data for ranking
│   ├── data_presentation.py      # Script for visualizing the results (charts)
│
├── main.py                       # Main script to run the ranking process
```

## Key Steps:
1. **Data Download**:  
   The data is fetched from the website using asynchronous HTTP requests. The user selects which mobile phone brands to include in the ranking.
   
2. **Data Preparation**:  
   The dataset is cleaned, and variables are transformed for the ranking process, which includes linear ordering of phones based on stimulants, destimulants, and nominals.

3. **Data Presentation**:  
   Visualizations are generated, showing various analyses like pricing comparisons, RAM-to-price relationships, and more.

## Console Output Example:

