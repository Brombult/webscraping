"""Utilities for DOU scraping"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import ElementNotVisibleException, WebDriverException
from pandas import DataFrame


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
