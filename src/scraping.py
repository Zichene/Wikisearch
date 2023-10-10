import re

import requests
from bs4 import BeautifulSoup

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
Takes in an url for a wikipedia article, and returns the name of the article
"""


def url_to_name(url):
    return url[url.rfind('/') + 1: len(url)]


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
