"""Using headless browser to scrape job openings from jobs.dou.ua"""
import csv
import datetime
from urllib.parse import quote

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import ElementNotVisibleException


# TODO: consider adding DB support and turning this into telegram bot

def scrape_dou_vacancies(city, category):
    """
    Scrapes info about job openings, then writes that info into a csv file
    Requires two arguments: city and job category
    """
    csv_file_name = f'{city}_{category}_{datetime.date.today()}.csv'
    jobs_dou_url = 'https://jobs.dou.ua/vacancies/'
    beginners_category_list = ['Начинающим', 'Початківцям', 'For beginners']
    relocation_category_list = ['За рубежом', 'За кордоном', 'Relocation']

    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    print('Headless browser is initiated')

    if category in beginners_category_list:
        driver.get(f'{jobs_dou_url}?city={city}&beginners')
    elif category in relocation_category_list:
        driver.get(f'{jobs_dou_url}?relocation')
    else:
        driver.get(f'{jobs_dou_url}?city={quote(city)}&category={quote(category)}')
    print('Jobs.dou is open')

    def click_on_more_jobs_button():
        """
        Since there's no pagination on jobs.dou this function clicks through all "more jobs" buttons
        so every job opening is present on the page and can be scraped
        """
        try:
            more_vacancies_button = driver.find_element_by_css_selector('.more-btn > a')
            while more_vacancies_button:
                more_vacancies_button.click()
        except ElementNotVisibleException:
            print("Scraping has started\n")

    def get_vacancy_info():
        """
        Gets every job openings on the page, returns list of dictionaries with collected info about those job openings
        """
        click_on_more_jobs_button()
        all_vacancies = []
        vacancies_counter = 0

        try:
            vacancies = driver.find_elements_by_css_selector('#vacancyListId li')
            for vacancy in vacancies:
                title = vacancy.find_element_by_css_selector('div.title')
                name = title.find_element_by_css_selector('a.vt')
                company = title.find_element_by_css_selector('.company')
                info = vacancy.find_element_by_class_name('sh-info')
                link = name.get_attribute('href')

                vacancy_details_dict = {'name': name.text, 'company': company.text, 'info': info.text, 'link': link}
                all_vacancies.append(vacancy_details_dict)
                vacancies_counter += 1
                print(f'Vacancies scraped: {vacancies_counter}')

            return all_vacancies
        except Exception as exc:
            print(exc)
        finally:
            driver.quit()

    def write_to_csv(vacancies_list, file_name):
        """
        Creates csv file with details about job openings
        Requires two arguments: list of dictionaries with scraped data and csv file name
        """
        csv_columns = ['name', 'company', 'info', 'link']
        try:
            with open(file_name, 'w') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
                writer.writeheader()
                for vacancy in vacancies_list:
                    writer.writerow(vacancy)
            print(f'\n{csv_file_name} file has been created')
        except IOError:
            print('I/O Error')

    data = get_vacancy_info()
    write_to_csv(data, csv_file_name)


scrape_dou_vacancies('Київ', 'QA')
