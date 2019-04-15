"""Scrapes coursehunters.net using requests-html library"""
import datetime
from urllib.parse import urljoin

from pandas import DataFrame, to_datetime
from requests_html import HTMLSession

every_article = []
csv_file_name = f'data_{datetime.date.today()}.csv'
csv_columns = ['title', 'description', 'language', 'number of lessons', 'duration', 'added', 'link']


def scrape_coursehunters(start_url):
    session = HTMLSession()
    r = session.get(start_url)
    all_articles_on_page = []

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
                        'added': article_add_date, 'link': article_link}
        all_articles_on_page.append(article_info)

    try:
        next_page_elem = r.html.find('a[rel="next"]', first=True).attrs['href']
        next_page_link = urljoin(start_url, next_page_elem)  # creating absolute link to next page
    except AttributeError:
        pass  # no more pages left
    else:
        scrape_coursehunters(next_page_link)

    for a in all_articles_on_page:
        every_article.append(a)


scrape_coursehunters('https://coursehunters.net/backend/python?page=1')

every_article.sort(key=lambda date: to_datetime(date['added']))  # sorting articles by year of publication

#  saving articles to csv file
data_frame = DataFrame(every_article, columns=csv_columns)
try:
    data_frame.to_csv(csv_file_name)
except IOError:
    print('I/O Error')
else:
    print(f'{csv_file_name} file was created')
