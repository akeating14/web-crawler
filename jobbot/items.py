# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import scrapy


class ListingItem(scrapy.Item):
    # define the fields for your item here like
    company_name = scrapy.Field()
    position_title = scrapy.Field()
    description = scrapy.Field()
    qualifications = scrapy.Field()
    location = scrapy.Field()
    listing_link = scrapy.Field()
    position_page = scrapy.Field()
