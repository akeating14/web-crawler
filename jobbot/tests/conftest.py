import pytest
import jobbot.settings as settings
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


@pytest.fixture(scope="module")
def create_session():
    """
    This function creates a database and monkeypatches the existing
    database variable to point to that database. Once the tests are finished
    it destroys the database unless the user ran the database with the keepdb
    flag.
    :return:

    TODO: 1. Create a keepdb tag
          2. This is possibly super inefficient because it creates a db
             and drops a db every time it is used.
          3. database does not copy existing data it just creates an empty db
    """
    engine = create_engine(settings.LISTINGS_DATABASE)
    db_name = engine.url.database
    test_db_name = 'test_{name}'.format(name=db_name)

    conn = engine.connect()
    conn.execute("commit")  # closes transaction block
    conn.execute('CREATE DATABASE {name}'.format(name=test_db_name))
    conn.close()

    engine.url.database = test_db_name
    yield sessionmaker(bind=engine)

    if not False:
        conn  = engine.connect()
        conn.execute("commit")  # closes transaction block
        conn.execute('DROP DATABASE {name}'.format(name=test_db_name))
        conn.close()