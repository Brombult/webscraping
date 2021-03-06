# -*- coding: utf-8 -*-
"""
Spider that scrapes Dou Calendar events
Can be run with "scrapy crawl events -o events.csv" command in terminal
"""
import scrapy

from dou_calendar.items import DouCalendarItem, CalendarItemLoader


class EventsSpider(scrapy.Spider):
    name = 'events'
    allowed_domains = ['dou.ua']
    start_urls = [f'https://dou.ua/calendar/page-{num}/' for num in range(1, 17)]

    def parse(self, response):
        l = CalendarItemLoader(item=DouCalendarItem(), response=response)
        events = response.css('article')
        for event in events:
            title = event.css('h2.title > a::text').extract_first()
            desc = event.css('p.b-typo::text').extract_first()
            date = event.css('div.when-and-where > .date::text').extract_first()
            try:
                price = event.css('div.when-and-where > .date + span::text').extract_first()
            except AttributeError:
                price = 'None'
            where = event.xpath('//div[@class="when-and-where"]').extract_first().split()[5]
            link = event.xpath('.//h2[@class="title"]/a/@href').extract_first()

            l.add_value('Title', title)
            l.add_value("Description", desc)
            l.add_value('Date', date)
            l.add_value("Price", price)
            l.add_value('Where', where)
            l.add_value('Link', link)

            return l.load_item()
