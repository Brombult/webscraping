"""
Spider that scrapes book and video info from scanlibs.com
Can be run by "scrapy runspider scanlibs_standalone_spider.py -o items.csv" command in terminal
"""
from scrapy import Spider, Request
from w3lib.html import replace_escape_chars, remove_tags, replace_tags


class ScanlibsSpider(Spider):
    name = 'scanlibs'
    allowed_domains = ['scanlibs.com']
    start_urls = ['https://scanlibs.com/']
    download_delay = 0.5

    def parse(self, response):
        articles = response.css('article')

        for article in articles:
            title = article.css('.entry-title > a::text').extract_first()
            date_published = article.css('.entry-date.published::text').extract_first()
            link = article.xpath('.//*[@class="more-link"]/@href').extract_first()

            if 'category-video' in article.attrib['class']:
                content_dirty = article.css('.entry-content p').extract_first()
                content = remove_tags(content_dirty).replace('|', ' | ').replace('\n', ' ')
            else:
                content_dirty = article.xpath('.//*[@class="entry-content"]').extract_first()
                content = replace_tags(replace_escape_chars(content_dirty), '  '
                                       ).replace('(more…)', '').replace('Read More', '').strip()

            yield {
                'Title': title,
                'Published On': date_published,
                'Content': content,
                'Link': link,
            }

        next_page = response.xpath('.//a[contains(@class, "next")]/@href').extract_first()
        yield Request(next_page, callback=self.parse)
