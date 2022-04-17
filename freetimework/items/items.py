# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FreeTimeWorkItem(scrapy.Item):
    channel_id = scrapy.Field()
    channel_name = scrapy.Field()
    publisher = scrapy.Field()
    journal_id = scrapy.Field()
    journal_name = scrapy.Field()
    journal_url = scrapy.Field()
    article_id = scrapy.Field()
    article_title = scrapy.Field()
    article_url = scrapy.Field()
    article_pdf_url = scrapy.Field()
    article_abstract = scrapy.Field()
    author = scrapy.Field()
    email = scrapy.Field()
    company = scrapy.Field()
