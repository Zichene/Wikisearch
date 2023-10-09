import re
import os
import sys
import time
from bs4 import BeautifulSoup
import requests

import prune
from database import PageDatabase
from prune import *

"""
Tries to finds a path between two wikipedia articles consisting of redirects, depth = 2.
@:returns: a list representing the path
"""

"TODO: Optimize this algorithm, more pruning? keep track of page names that have already been visited in a hashmap?"

"""
def find_path(base, target):
    # global set keeping track of ALL names that have been visited for that particular search
    nset = set()
    # check if the target is also a valid wikipedia page
    find_wiki_page(target)
    ret = [base]
    # trivial edge case
    if base == target:
        ret.append(target)
        return ret
    # convert target's spaces into underscores
    target = target.replace(" ", "_")
    n0 = find_wiki_links(base, False, nset)
    counter = 0
    for n0_cur in n0:
        # print percentage to user
        print_percentage(n0, n0_cur, counter)
        counter += 1
        # depth 1
        if n0_cur == target:
            ret.append(n0_cur)
            os.system('cls')  # clear console text
            return ret
        # depth 2
        n1 = find_wiki_links(n0_cur, False, nset)
        for n1_cur in n1:
            if n1_cur == target:
                ret.append(n0_cur)
                ret.append(n1_cur)
                os.system('cls')  # clear console text
                return ret
    return None
"""

"""
Different implementation of find_path but uses breadth-first search inside of depth first (faster results
if base and target are closely linked).
Added dynamic search of DB: this will make it so that sometimes will not return shortest path
if a path is found in DB from depth 1 or depth 2.
However, it is much faster to find any path.
"""


def find_path_v2(base, target, database, dynamic):
    # check if the target is also a valid wikipedia page
    find_wiki_page(target)
    # check if path can be found in database
    # try to look in database first!
    ret = find_path_in_database(base, target, database)
    if ret is not None:
        return ret
    print("Could not find path in database (depth=0).")
    ret = [base]
    # trivial edge case
    if page_equals(base, target):
        ret.append(target)
        return ret
    # convert target's spaces into underscores
    target = target.replace(" ", "_")
    base_links = store_wiki_links(base, database)  # all the links FROM the base page
    counter = 1
    for base_link in base_links:
        if dynamic:
            # look for link between base_link and target in DB
            path = find_path_in_database(base_link, target, database)
            if path is not None:
                return ret + path
        # depth 1
        if page_equals(base_link, target):
            ret.append(base_link)
            return ret
    print("Could not find path in database (depth=1).")
    for base_link in base_links:
        # depth 2
        print_percentage(base_links, base_link, counter)
        counter += 1
        base_links_depth_2 = store_wiki_links(base_link, database)
        for base_link_depth_2 in base_links_depth_2:
            # look in DB
            if dynamic:
                path = find_path_in_database(base_link, target, database)
                if path is not None:
                    return ret + path
            if page_equals(base_link_depth_2, target):
                ret.append(base_link)
                ret.append(base_link_depth_2)
                os.system('cls')  # clear
                return ret
    return None


"""
Stores all of the pages as well as the children of the page into the database.
"""


def store_wiki_links_deep(page_name, database):
    n0 = store_wiki_links(page_name, database)
    counter = 1
    for n0_cur in n0:
        # depth 2
        print_percentage(n0, n0_cur, counter)
        counter += 1
        store_wiki_links(n0_cur, database)
    return None


"""
Prints out the path (which is just a list) to show user
"""


def print_path(path):
    if path is None:
        print("Path not found.")
        return
    print("Length of shortest path found: " + str(len(path) - 1))
    for i in range(len(path)):
        # last element does not print out arrow
        if i == len(path) - 1:
            print(path[i] + " (" + "https://en.wikipedia.org/wiki/" + path[i] + ")")
        else:
            print(path[i] + " (" + "https://en.wikipedia.org/wiki/" + path[i] + ")" + " -> ", end="")


"""
Finds the relevant wikipedia redirects from a starting page
@:return: the set of strings corresponding to all the page redirects
"""


def find_wiki_links(name, prnt):
    ret = []
    page = find_wiki_page(name)
    soup = BeautifulSoup(page.text, "html.parser")
    links = soup.find_all('a', href=True, title=True)
    # get all links
    for link in links:
        text = link.attrs['href']
        if text.startswith('/wiki'):
            if prnt:
                print("https://en.wikipedia.org/" + text)
            pname = url_to_name(text)  # find the potential name of the article
            if valid_name(pname, name):  # check if name is "valid" according to validation criteria defined (see
                # valid_name function)
                ret.append(pname)
    if prnt:
        print("Number of links to other Wikipedia articles: " + str(len(ret)))
    return ret


"""
Stores all the links for a particular page in a SQL table, in a database object.
"""


def store_wiki_links(page_name, database: PageDatabase):
    # check if page_name is already a table in the database
    if database.query_page_exists(page_name):
        # directly return the links from db
        return database.query_page_link_all(page_name)

    database.create_page_table(page_name)
    link_names = find_wiki_links(page_name, False)
    for link_name in link_names:
        database.insert_link(page_name, link_name)
    return link_names


"""
Tries to find a connection between two pages in a PageDatabase. Returns a path array if found, otherwise
return a None object.
"""


def find_path_in_database(base_page_name, target_page_name, database: PageDatabase):
    res = database.query_page_link_deep(base_page_name, target_page_name, 1)
    if res is None:
        return None
    return res


"""Determines if a name is to be filtered out. Filtering criteria: if it contains a ':' character, if it is the 
Main_Page, if it has only two characters (assume its a languages thing), if it has the same name as the page it comes from
@:returns: True if the name is valid, False otherwise"""


def valid_name(link_name, page_name):
    if ':' in link_name:
        return False
    if "Main_Page" == link_name:
        return False
    if len(link_name) <= 2:
        return False
    if not re.search('[a-zA-Z]', link_name):
        return False
    if link_name == page_name:
        return False

    return True


"""
Copied from stackoverflow: https://stackoverflow.com/questions/19596750/is-there-a-way-to-clear-your-printed-text-in-python
"""


def delete_last_line():
    "Use this function to delete the last line in the STDOUT"

    # cursor up one line
    sys.stdout.write('\x1b[1A')

    # delete last line
    sys.stdout.write('\x1b[2K')


"""
Takes in an url for a wikipedia article, and returns the name of the article
"""


def url_to_name(url):
    return url[url.rfind('/') + 1: len(url)]


"""
Prints out the percentage of the task remaining. Based on how many elements are left to process in n0 (the list of
links from the base).
"""


def print_percentage(n0, n0_cur, counter):
    os.system('cls')  # clear
    pct = round(counter / len(n0) * 100)
    print("Searching ... " + n0_cur + " " + str(pct) + "% done.")


"""
Returns the page (request object) of the wikipedia page with name "name". If it doesnt exist, end program and display
error message.
"""


def find_wiki_page(name):
    url = "https://en.wikipedia.org/wiki/" + name
    page = requests.get(url)
    if page.status_code == 404:
        print("Error: Wikipedia page " + name + " does not exist.")
        exit(0)  # exit program
    return page


"""
Check if two page names are equal: cap insensitive and replace all underscores by spaces.
"""


def page_equals(n1, n2):
    return n1.replace("_", " ").lower() == n2.replace("_", " ").lower()


if __name__ == "__main__":
    db = PageDatabase('page_data.db')
    print("Current number of pages in database (max=" + str(db.MAX_PAGES) + "):" + str(db.num_of_pages))
    #print_path(find_path_v2("Egypt", "Savanna", db))

    if len(sys.argv) != 3:
        print("Incorrect usage: py wikisearch.py <base> <destination>")
        exit(0)

    t1 = time.time()
    print_path(find_path_v2(sys.argv[1], sys.argv[2], db, True))
    print("Time taken: " + str(time.time() - t1) + " s.")
    db.close()
