"""Using headless browser to scrape vacancies from jobs.dou.ua"""
import csv
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import ElementNotVisibleException


def scrape_dou_vacancies(city, category):
    """
    Scrapes info about job openings, then creates csv and writes that info into the file
    Requires two arguments: city and job category
    """
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    driver.get(f'https://jobs.dou.ua/vacancies/?city={quote(city)}&category={category}')

    def click_on_more_jobs_button():
        """
        Since there's no pagination on jobs.dou:
        this function clicks through all "more jobs" buttons on the page so every job opening is present
        and can be scraped
        """
        try:
            more_vacancies_button = driver.find_element_by_css_selector('.more-btn > a')
            while more_vacancies_button:
                more_vacancies_button.click()
        except ElementNotVisibleException:
            pass

    def get_vacancy_info():
        """
        Gets every job openings on the page, returns list of dictionaries with collected info about job openings
        """
        click_on_more_jobs_button()
        all_vacancies = []
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
            return all_vacancies
        finally:
            driver.quit()

    def write_to_csv(vacancies_list, file_name):
        """
        Writes vacancy details to csv file
        """
        csv_columns = ['name', 'company', 'info', 'link']
        try:
            with open(file_name, 'w') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
                writer.writeheader()
                for vacancy in vacancies_list:
                    writer.writerow(vacancy)
        except IOError:
            print('I/O Error')

    data = get_vacancy_info()
    write_to_csv(data, 'Vacancies_QA_Kyiv.csv')


scrape_dou_vacancies('Київ', 'QA')
