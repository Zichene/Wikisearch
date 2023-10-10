from os import system

from prune import *
from scraping import find_wiki_links, find_wiki_page

"""
Uses breadth-first search inside of depth first (faster results
if base and target are closely linked).
Added dynamic search of DB: this will make it so that sometimes will not return shortest path
if a path is found in DB from depth 1 or depth 2.
However, it is much faster to find any path.
"""


def find_path(base, target, database, dynamic):
    # check if the target is also a valid wikipedia page
    find_wiki_page(target)
    # check if path can be found in database
    # try to look in database first!
    ret = find_path_in_database(base, target, database)
    if ret is not None:
        return ret
    print("[Info]: Could not find path in database (depth=0).")
    ret = [base]
    # trivial edge case
    if page_equals(base, target):
        ret.append(target)
        return ret
    # convert target's spaces into underscores
    target = target.replace(" ", "_")
    base_links = store_wiki_links(base, database)  # all the links FROM the base page
    counter = 1
    # warning message
    if dynamic:
        print("[Warning]: Dynamic search may yield paths which are not shortest.")
    for base_link in base_links:
        if dynamic:
            # look for link between base_link and target in DB
            path = find_path_in_database(base_link, target, database)
            if path is not None:
                # remove possible duplicates from path (e.g. A -> B -> A -> D)
                ret = path_remove_duplicates(base, ret + path)
                return ret
        # depth 1
        if page_equals(base_link, target):
            ret.append(base_link)
            return ret
    print("[Info]: Could not find path in database (depth=1).")
    for base_link in base_links:
        # depth 2
        print_percentage(base_links, base_link, counter)
        counter += 1
        base_links_depth_2 = store_wiki_links(base_link, database)
        for base_link_depth_2 in base_links_depth_2:
            # look in DB
            if dynamic:
                path = find_path_in_database(base_link_depth_2, target, database)
                if path is not None:
                    ret = path_remove_duplicates(base, ret + path)
                    return ret
            if page_equals(base_link_depth_2, target):
                ret.append(base_link)
                ret.append(base_link_depth_2)
                system('cls')  # clear
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


"""
Prints out the percentage of the task remaining. Based on how many elements are left to process in n0 (the list of
links from the base).
"""


def print_percentage(n0, n0_cur, counter):
    system('cls')  # clear
    pct = round(counter / len(n0) * 100)
    print("[Info]: Searching ... " + n0_cur + " " + str(pct) + "% done.")


"""
Check if two page names are equal: cap insensitive and replace all underscores by spaces.
"""


def page_equals(n1, n2):
    return n1.replace("_", " ").lower() == n2.replace("_", " ").lower()


"""
Removes duplicates from path. For example: [A, B, A, D] -> [A, D].
Not most efficient code but paths are expected to be very short so doesnt matter.
"""


def path_remove_duplicates(start, path: list):
    # find the last index of "start" in path
    if start not in path:
        return None  # we have a problem in this case
    index = 0
    # find last index in list where we have duplicate of start
    for i in range(len(path)):
        if path[i] == start and i != 0:
            index = i
    ret = []
    for i in range(index, len(path)):
        ret.append(path[i])
    return ret

