import os
import sys
import datetime
import psycopg2
import urllib

from psycopg2._psycopg import DatabaseError
from psycopg2.extras import DictCursor


def db_connection(function):
    def wrapper(*args, **kwargs):
        _db_connection = None
        _cursor = None
        dev_env = os.environ.get('APP_ENV') == 'dev'
        if dev_env:
            connection_data = {
                'dbname': os.environ.get('MY_PSQL_DBNAME'),
                'user': os.environ.get('MY_PSQL_USER'),
                'host': os.environ.get('MY_PSQL_HOST'),
                'password': os.environ.get('MY_PSQL_PASSWORD')
            }
            connect_string = "dbname='{dbname}' user='{user}' host='{host}' password='{password}'"
            connect_string = connect_string.format(**connection_data)
        else:
            urllib.parse.uses_netloc.append('postgres')
            url = urllib.parse.urlparse(os.environ.get('DATABASE_URL'))
        try:
            if dev_env:
                _db_connection = psycopg2.connect(connect_string, cursor_factory=DictCursor)
            else:
                _db_connection = psycopg2.connect(
                    database=url.path[1:],
                    user=url.username,
                    password=url.password,
                    host=url.hostname,
                    port=url.port,
                    cursor_factory=DictCursor
                )
            _db_connection.autocommit = True
            _cursor = _db_connection.cursor()
            result = function(*args, **kwargs, cursor=_cursor)
        except psycopg2.DatabaseError as e:
            print('Database error occured:', file=sys.stderr)
            print(e, file=sys.stderr)
            raise DatabaseError()
        finally:
            if _cursor is not None:
                _cursor.close()
            if _db_connection is not None:
                _db_connection.close()
        return result
    return wrapper


@db_connection
def get_user(username, cursor=None):
    query = '''
            SELECT * FROM users
              WHERE username = %s;
            '''
    if cursor is None:
        print('No database cursor.', file=sys.stderr)
        raise psycopg2.DatabaseError()
    cursor.execute(query, [username])
    return cursor.fetchone()


@db_connection
def add_user(username, password, cursor=None):
    query = '''
            INSERT INTO users (username, password)
              VALUES (%s, %s);
            '''
    if cursor is None:
        print('No database cursor.', file=sys.stderr)
        raise psycopg2.DatabaseError()
    cursor.execute(query, [username, password])


@db_connection
def add_vote(user_id, planet_name, cursor=None):
    query = '''
            INSERT INTO votes (planet_name, user_id, submission_time)
              VALUES (%s, %s, %s);
            '''
    if cursor is None:
        print('No database cursor.', file=sys.stderr)
        raise psycopg2.DatabaseError()
    cursor.execute(query, [planet_name, user_id, datetime.datetime.now()])


@db_connection
def get_statistics(cursor=None):
    query = '''
            SELECT planet_name, COUNT(*) AS votes
              FROM votes
              GROUP BY planet_name
              ORDER BY planet_name;
            '''
    if cursor is None:
        print('No database cursor.', file=sys.stderr)
        raise psycopg2.DatabaseError()
    cursor.execute(query)
    return cursor.fetchall()