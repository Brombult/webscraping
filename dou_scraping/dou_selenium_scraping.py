"""Using headless browser to scrape job openings from jobs.dou.ua"""
import datetime
import argparse
import sys

from bs4 import BeautifulSoup

from utils import init_headless_driver, click_on_more_jobs_button, save_data_to_csv

JOBS_DOU_URL = 'https://jobs.dou.ua/vacancies/'
BEGINNERS_CATEGORY_LIST = ['начинающим', 'початківцям', 'for beginners']
RELOCATION_CATEGORY_LIST = ['за рубежом', 'за кордоном', 'relocation']
CSV_COLUMNS_NAME = ['name', 'company', 'info', 'link']


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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--category', help="job category to search vacancies for (e.g. 'QA' or 'Python')", default='QA')
    parser.add_argument('--city', help="city to search vacancies in", default='Kiev')
    args = parser.parse_args()

    driver, file_name = open_dou_vacancies(driver=init_headless_driver(), category=args.category, city=args.city)
    vacancies = get_vacancies_info(driver)
    save_data_to_csv(data=vacancies, csv_file_name=file_name, csv_columns=CSV_COLUMNS_NAME)
