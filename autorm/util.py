# autorm.util.py


from threading import local as threading_local

# AutORM ORM
from autorm.model import Model
from autorm.db.relations import ForeignKey, OneToMany
from autorm.db.query import Query
from autorm.db.connection import Database


"""
Convenience functions for the AutORM ORM.
"""

def table_exists(db, table_name):
    """
    Given an AutORM model, check to see if its table exists.
    """
    try:
        s_sql = "SELECT * FROM %s LIMIT 1;" % table_name
        Query.raw_sql(s_sql, db=db)
    except Exception:
        return False

    # if no exception, the table exists and we are done
    return True


def create_table(db, s_create_sql):
    """
    Create a table for an AutORM class.
    """
    Query.begin(db=db)
    Query.raw_sqlscript(s_create_sql, db=db)
    Query.commit(db=db)


def create_table_if_needed(db, table_name, s_create_sql):
    """
    Check to see if an AutORM class has its table created; create if needed.
    """
    if not table_exists(db, table_name):
        create_table(db, s_create_sql)


class AutoConn(object):
    """
    A container that will automatically create a database connection object
    for each thread that accesses it.  Useful with SQLite, because the Python
    modules for SQLite require a different connection object for each thread.
    """
    def __init__(self, db_name, container=None):
        self.b_debug = False
        self.b_commit = True
        self.db_name = db_name
        self.container = threading_local()
    def __getattr__(self, name):
        try:
            if "conn" == name:
                return self.container.conn
        except BaseException:
            self.container.conn = Database()
            self.container.conn.connect('sqlite3', self.db_name)
            return self.container.conn
        raise AttributeError


# examples of usage:
#
# class FooClass(object):
#     db = autorm.util.AutoConn("foo.db")
#
# _create_sql = "_create_sql = """\
# DROP TABLE IF EXISTS bar;
# CREATE TABLE bar (
#     id INTEGER PRIMARY KEY,
#     value VARCHAR(128) NOT NULL,
#     UNIQUE (value));
# CREATE INDEX idx_bar0 ON bar (value);"""
#
# autorm.util.create_table_if_needed(FooClass.db, "bar", _create_sql)
#
# class Bar(FooClass, Model):
#    ...standard AutORM class stuff goes here...
