# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from models import GenericListings
from database import create_db_conn


class CompanyPipeline(object):

    def __init__(self):
        """
        Initializes database connection and sessionmaker.
        Creates generic_listings table.
        """
        self.Session = create_db_conn()
        self.session = self.Session()

    def close_spider(self, spider):
        self.session.close()


    def process_item(self, item, spider):
        """
        This method is called for every item pipeline component,
        and saves listings to a database.
        """

        listing = GenericListings(**item)

        self.session.add(listing)

        try:
            self.session.commit()
        except:
            self.session.rollback()
            raise


        return item
