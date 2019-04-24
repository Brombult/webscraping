# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DouCalendarItem(scrapy.Item):
    Title = scrapy.Field()
    Description = scrapy.Field()
    Date = scrapy.Field()
    Price = scrapy.Field()
    Where = scrapy.Field()
    Link = scrapy.Field()
