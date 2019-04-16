"""Using headless browser to scrape job openings from jobs.dou.ua"""
import datetime
import sys

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import ElementNotVisibleException, WebDriverException
from pandas import DataFrame


# TODO: consider adding DB support and turning this into telegram bot

def scrape_dou_vacancies(city, category):
    """
    Scrapes info about job openings, then writes that info into a csv file
    Requires two arguments: city and job category
    """
    csv_file_name = f'{city}_{category}_{datetime.date.today()}.csv'
    csv_columns = ['name', 'company', 'info', 'link']
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
        driver.get(f'{jobs_dou_url}?city={city}&category={category}')
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
        except WebDriverException:
            driver.quit()
            sys.exit('Webdriver bugged out, please run the script again')

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

    # saving vacancies info to csv file
    data = get_vacancy_info()
    data_frame = DataFrame(data, columns=csv_columns)
    try:
        data_frame.to_csv(csv_file_name)
    except IOError:
        print('I/O error')
    else:
        print(f'\n{csv_file_name} file was created')


scrape_dou_vacancies('Київ', 'QA')
