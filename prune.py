"""
Pruning in database to remove unnecessary entries/tables.
"""
from database import PageDatabase


# removes the pages which have different links but are the exact same
def remove_same_pages(database: PageDatabase):
    pages = database.query_all_pages()
    for page in pages:
        if "#" in page:  # assume that this page is a copy
            database.remove_page_table(page)
