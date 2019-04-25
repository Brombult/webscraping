# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader


def strip_value_processor(self, values):
    """This processor removes spaces and newlines from the beginning and the end of the string"""
    for value in values:
        yield value.strip()


class DouCalendarItem(scrapy.Item):
    Title = scrapy.Field()
    Description = scrapy.Field()
    Date = scrapy.Field()
    Price = scrapy.Field()
    Where = scrapy.Field()
    Link = scrapy.Field()


class CalendarItemLoader(ItemLoader):
    """Custom ItemLoader for cleaning up the data"""
    Title_in = strip_value_processor  # "_in" stands for "input"
    Description_in = strip_value_processor
    Date_in = strip_value_processor
    Price_in = strip_value_processor
    Where_in = strip_value_processor
    Link_in = strip_value_processor
