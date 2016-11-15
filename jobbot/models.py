from sqlalchemy import create_engine, Column, Text, String, Integer
from sqlalchemy.ext.declarative import declarative_base

import settings


DeclarativeBase = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(settings.LISTINGS_DATABASE)


def create_all_tables(engine):
    """"""
    DeclarativeBase.metadata.create_all(engine)


class GenericListings(DeclarativeBase):
    """
    Sqlalchemy generic_listings model. This holds all listings
    scraped from generic company websites
    """
    __tablename__ = "generic_listings"

    listing_id = Column(Integer, primary_key=True)
    company_name = Column('company_name', String(length=300, convert_unicode=True),
                          nullable=True)
    position_title = Column('title', String(length=300, convert_unicode=True),
                            nullable=True)
    qualifications = Column('qualifications', Text, nullable=True)
    description = Column('description', Text, nullable=True)
    location = Column('location', String(length=300, convert_unicode=True),
                      nullable=True)
    listing_link = Column('link', String(length=300), nullable=True)
    position_page = Column('position_page', Text, nullable=True)
