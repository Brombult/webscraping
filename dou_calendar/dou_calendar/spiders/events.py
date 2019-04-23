# -*- coding: utf-8 -*-
import scrapy


class EventsSpider(scrapy.Spider):
    name = 'events'
    allowed_domains = ['dou.ua']
    start_urls = [f'https://dou.ua/calendar/page-{num}/' for num in range(1, 17)]

    def parse(self, response):
        events = response.css('article')
        for event in events:
            title = event.css('h2.title > a::text').extract_first().strip()
            desc = event.css('p.b-typo::text').extract_first().strip()
            date = event.css('div.when-and-where > .date::text').extract_first().strip()
            try:
                price = event.css('div.when-and-where > .date + span::text').extract_first().strip()
            except AttributeError:
                price = 'None'
            where = event.xpath('//div[@class="when-and-where"]').extract_first().split()[5].strip()
            link = event.xpath('.//h2[@class="title"]/a/@href').extract_first()

            yield {'Title': title,
                   "Description": desc,
                   'Date': date,
                   "Price": price,
                   'Where': where,
                   'Link': link, }
