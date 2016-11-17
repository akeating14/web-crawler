from sqlalchemy.orm import sessionmaker
from models import db_connect, create_all_tables


def create_db_conn():
    """
    This creates a database connection and then checks to see if
    all tables are created. If there are missing tables they are created
    and then a db session is returned.

    :return: sqlalchmey session
    """
    engine = db_connect()
    create_all_tables(engine)
    return sessionmaker(bind=engine)