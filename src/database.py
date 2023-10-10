import collections
import sqlite3

"""
This class represents a SQLite database where wikipedia pages are stored, each page is stored as
a SQLite table, whose rows represent a link to another wikipedia page.
"""


class PageDatabase:
    MAX_PAGES = 1000  # too much memory use, can be changed later
    """
    Constructor. Initiates a new SQLite database.
    @:arg name: Name of database. If database already exists then no new database will be created.
    """

    def __init__(self, name):
        self.name = name
        self.connection = sqlite3.connect(name)
        self.cursor = self.connection.cursor()
        self.connection.commit()
        self.connection.close()
        self.is_closed = True
        self.num_of_pages = 0
        self.query_all_pages()  # this will update the num_of_pages

    """
    Connects to the database and initiates the cursor object.
    """

    def connect(self):
        self.connection = sqlite3.connect(self.name)
        # make it so the output of cursor.fetchall() returns lists and not lists of tuples
        self.connection.row_factory = lambda cursor, row: row[0]
        self.cursor = self.connection.cursor()
        self.is_closed = False

    """
    Closes the connection to the database.
    """

    def close(self):
        self.connection.close()
        self.is_closed = True

    """
    Creates a new SQLite table with a given name. Represents a Wikipedia page along with rows acting as links to
    other pages.
    @:arg page_name (str): Name of the page
    """

    def create_page_table(self, page_name):
        if self.is_closed is True:
            self.connect()
        # check if too many pages are in the db
        if self.num_of_pages >= self.MAX_PAGES:
            # delete LAST table that has been entered
            last_page = self.query_all_pages()[self.num_of_pages - 1]
            self.remove_page_table(last_page)

        # create table for this one page
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS [{}] (
            id INTEGER PRIMARY KEY,
            link TEXT,
            UNIQUE(link)
        )
        """.format(page_name))
        self.connection.commit()
        self.num_of_pages += 1

    """
    Inserts a new row into a page table consisting of the name of a linked page.
    @:arg page_name (str): Name of the parent page  
    @:arg link_name (str): Name of the linked page
    """

    def insert_link(self, page_name, link_name):
        if self.is_closed is True:
            self.connect()
        self.cursor.execute("""
        INSERT OR IGNORE INTO [{}](link) VALUES 
        (?)
        """.format(page_name), [link_name])
        self.connection.commit()

    """
    Deletes a row in a page table corresponding to the name of a linked page.
    @:arg page_name (str): Name of the parent page  
    @:arg link_name (str): Name of the linked page
    """

    def delete_link(self, page_name, link_name):
        if self.is_closed is True:
            self.connect()
        self.cursor.execute("""
        DELETE FROM [{}]
        WHERE link = ?;
        """.format(page_name), [link_name])
        self.connection.commit()

    """
    Deletes all of the rows of a given page table.
    @:arg page_name (str): Name of parent page
    """

    def delete_page_links_all(self, page_name):
        if self.is_closed is True:
            self.connect()
        self.cursor.execute("""
        DELETE FROM [{}]
        """.format(page_name))
        self.connection.commit()

    """
    Deletes a page table
    @:arg page_name (str): Name of page
    """

    def remove_page_table(self, page_name):
        if self.is_closed is True:
            self.connect()
        # create table for this one page
        self.cursor.execute("""
        DROP TABLE IF EXISTS [{}];
        """.format(page_name))
        self.connection.commit()
        self.num_of_pages -= 1

    """
    Queries for a link name from a specific parent table.
    @:arg page_name (str): Name of parent page
    @:arg link_name (str): Name of linked page
    @:return: name of linked page, if found in the given table
    """

    def query_page_link(self, page_name, link_name):
        if self.is_closed is True:
            self.connect()
        # check if page_name is a valid table
        if not self.query_page_exists(page_name):
            return None
        self.cursor.execute("""
        SELECT link FROM [{}] 
        WHERE link = ?
        """.format(page_name), [link_name])
        return self.cursor.fetchone()

    """
    Queries for all of the links of a page.
    @:arg page_name (str): Name of the parent page
    @:return: an array containing all of the links associated with the parent page
    """

    def query_page_link_all(self, page_name):
        if self.is_closed is True:
            self.connect()
        # check if page_name is a valid table
        if not self.query_page_exists(page_name):
            return None
        self.cursor.execute("""
        SELECT link FROM [{}]
        """.format(page_name))
        return self.cursor.fetchall()

    """
    Queries for a specific page. Returns whether or not this page exists in the database.
    """

    def query_page_exists(self, page_name):
        if self.is_closed is True:
            self.connect()
        self.cursor.execute("""
        SELECT name from sqlite_master
        WHERE type='table' AND name = ?
        """, [page_name])
        return self.cursor.fetchone() is not None

    """
    Queries for all of the pages (tables) in the database. Returns an array with the names of all the
    found tables.
    """

    def query_all_pages(self):
        if self.is_closed is True:
            self.connect()
        self.cursor.execute("""
        SELECT name from sqlite_master
        WHERE type='table'
        """, )
        ret = self.cursor.fetchall()
        self.num_of_pages = len(ret) - 2  # sqlite_sequence and sqlite_master do not count!
        return ret


