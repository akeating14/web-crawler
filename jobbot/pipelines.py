# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from sqlalchemy.orm import sessionmaker
from models import (db_connect, create_generic_listings_table,
                    GenericListings)


class CompanyPipeline(object):

    def __init__(self):
        """
        Initializes database connection and sessionmaker.
        Creates generic_listings table.
        """
        engine = db_connect()
        create_generic_listings_table(engine)
        self.Session = sessionmaker(bind=engine)

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
