"""Scrapes coursehunters.net using requests-html library"""
import datetime
from urllib.parse import urljoin

from pandas import DataFrame, to_datetime
from requests_html import HTMLSession

every_article_on_the_site = []  # this variable will hold every article from every page
csv_file_name = f'data_{datetime.date.today()}.csv'
csv_columns = ['title', 'description', 'language', 'number of lessons', 'duration', 'date posted', 'link']


def scrape_coursehunters(start_url):
    session = HTMLSession()
    r = session.get(start_url)
    all_articles_on_page = []

    #  scraping info for every article on the page
    articles = r.html.find('article')
    for article in articles:
        article_title = article.find('h3[itemprop="headline"]', first=True).text
        article_description = article.find('div.standard-course-block__description', first=True).text
        article_lang = article.find('span.standard-course-block__course-lang', first=True).text
        article_lessons_number = article.find('span.standard-course-block__course-lessons', first=True).text
        article_duration = article.find('div.standard-course-block__duration', first=True).text.replace('Duration ', '')
        article_add_date = article.find('time.standard-course-block__add-date', first=True).text
        article_link = article.find('a.standard-course-block__russian', first=True).attrs['href']
        article_info = {'title': article_title, 'description': article_description, 'language': article_lang,
                        'number of lessons': article_lessons_number, 'duration': article_duration,
                        'date posted': article_add_date, 'link': article_link}
        all_articles_on_page.append(article_info)

    #  creating next page link and recursively calling same function to scrape next page
    try:
        next_page_elem = r.html.find('a[rel="next"]', first=True).attrs['href']
        next_page_link = urljoin(start_url, next_page_elem)  # creating absolute link for next page
    except AttributeError:
        pass  # no more pages left
    else:
        scrape_coursehunters(next_page_link)

    #  adding articles from single page to list of articles from previous pages
    for a in all_articles_on_page:
        every_article_on_the_site.append(a)


if __name__ == '__main__':
    scrape_coursehunters('https://coursehunters.net/backend/python?page=1')

    # sorting articles by year of publication
    every_article_on_the_site.sort(key=lambda article: to_datetime(article['date posted']))

    #  saving articles info to csv file
    data_frame = DataFrame(every_article_on_the_site, columns=csv_columns)
    try:
        data_frame.to_csv(csv_file_name)
    except IOError:
        print('I/O Error')
    else:
        print(f'{csv_file_name} file was created')
