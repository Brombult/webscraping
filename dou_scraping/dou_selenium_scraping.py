"""Using headless browser to scrape job openings from jobs.dou.ua"""
import datetime
import argparse
import sys

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import ElementNotVisibleException, WebDriverException
from pandas import DataFrame

JOBS_DOU_URL = 'https://jobs.dou.ua/vacancies/'
BEGINNERS_CATEGORY_LIST = ['начинающим', 'початківцям', 'for beginners']
RELOCATION_CATEGORY_LIST = ['за рубежом', 'за кордоном', 'relocation']
CSV_COLUMNS_NAME = ['name', 'company', 'info', 'link']


def init_headless_driver():
    """
    Initiating and configuring headless browser
    Returns webdriver instance
    """
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    print('Headless browser is initiated')

    return driver


def open_dou_vacancies(driver, category, city):
    """
    Handles user input and opens jobs.dou
    :param driver: webdriver instance
    :param category: job category (e.g. 'QA' or 'Python')
    :param city: city to search vacancies in
    :return: webdriver instance and csv file name, constructed with category and city names
    """
    csv_file_name = f'{city}_{category}_{datetime.date.today()}.csv'

    if category.lower() in BEGINNERS_CATEGORY_LIST:
        driver.get(f'{JOBS_DOU_URL}?city={city}&beginners')
    elif category.lower() in RELOCATION_CATEGORY_LIST:
        driver.get(f'{JOBS_DOU_URL}?relocation')
    else:
        driver.get(f'{JOBS_DOU_URL}?city={city}&category={category}')
    print('Jobs.dou is open')

    return driver, csv_file_name


def click_on_more_jobs_button(driver):
    """
    Since there's no pagination on jobs.dou this function clicks through all "more jobs" buttons
    so every job opening is present on the page and can be scraped.
    Returns webdriver instance
    """
    try:
        more_vacancies_button = driver.find_element_by_css_selector('.more-btn > a')
        while more_vacancies_button:
            more_vacancies_button.click()
    except (ElementNotVisibleException, WebDriverException):
        print("Scraping has started\n")

    return driver


def get_vacancies_info(driver):
    """
    Gets every job openings on the page.
    Returns list of dictionaries with collected info those job openings
    """
    click_on_more_jobs_button(driver)
    all_vacancies = []
    vacancies_counter = 0

    soup = BeautifulSoup(driver.page_source, 'lxml')

    try:
        vacancies = soup.find_all(name='li', class_='l-vacancy')
        for vacancy in vacancies:
            title = vacancy.find(name='div', class_='title')
            name = title.find(name='a', class_='vt')
            company = title.find(name='a', class_='company')
            info = vacancy.find(name='div', class_='sh-info')
            link = name.attrs['href']

            vacancy_details_dict = {
                'name': name.text, 'company': company.text, 'info': info.text.strip(), 'link': link}
            all_vacancies.append(vacancy_details_dict)
            vacancies_counter += 1
            print(f'Vacancies scraped: {vacancies_counter}')

    except Exception as exc:
        print(exc)
    finally:
        driver.quit()

    if vacancies_counter == 0:
        sys.exit('No vacancies were scraped, please check your category/city input')

    return all_vacancies


def save_data_to_csv(data, csv_file_name, csv_columns):
    """
    Saves data to csv file
    :param data: data to save
    :param csv_file_name: csv file name
    :param csv_columns: csv columns
    """
    data_frame = DataFrame(data, columns=csv_columns)
    try:
        data_frame.to_csv(csv_file_name)
    except IOError:
        print('I/O error')
    else:
        print(f'\n{csv_file_name} file was created')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--category', help="job category to search vacancies for (e.g. 'QA' or 'Python')", default='QA')
    parser.add_argument('--city', help="city to search vacancies in", default='Kiev')
    args = parser.parse_args()

    driver, file_name = open_dou_vacancies(driver=init_headless_driver(), category=args.category, city=args.city)
    vacancies = get_vacancies_info(driver)
    save_data_to_csv(data=vacancies, csv_file_name=file_name, csv_columns=CSV_COLUMNS_NAME)
