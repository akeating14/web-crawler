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

    def process_item(self, item, spider):
        """
        This method is called for every item pipeline component,
        and saves listings to a database.

        Is this try accept statement acceptable.
        It feels wrong.
        """

        session = self.Session()
        listing = GenericListings(**item)

        try:
            session.add(listing)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

        return item
