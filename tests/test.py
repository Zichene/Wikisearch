import time

from src.database import PageDatabase
from src.find_path import find_path_in_database_bfs

db = PageDatabase("page_data.db")

def test_length_1():
    db.create_page_table("A")
    db.create_page_table("B")
    db.create_page_table("C")
    db.create_page_table("D")
    db.insert_link("A", "B")
    db.insert_link("B", "C")
    db.insert_link("C", "D")
    assert find_path_in_database_bfs("A", "D", db) == ['A', 'B', 'C', 'D']
    print("test_length_1: Passed")


def test_length_2():
    db.create_page_table("E")
    db.create_page_table("F")
    db.insert_link("D", "E")
    db.insert_link("E", "F")
    assert find_path_in_database_bfs("A", "F", db) == ['A', 'B', 'C', 'D', 'E', 'F']
    print("test_length_2: Passed")


def test_no_path_1():
    db.create_page_table("Empty")
    db.create_page_table("Null")
    assert find_path_in_database_bfs("Empty", "Null", db) is None
    print("test_no_path_1: Passed")


def test_path_to_itself_1():
    db.create_page_table("Test")
    db.insert_link("Test", "Test")
    assert find_path_in_database_bfs("Test", "Test", db) == ['Test', 'Test']
    print("test_path_to_itself_1: Passed")


def test_circular_loop():
    db.create_page_table("C1")
    db.create_page_table("C2")
    db.create_page_table("C3")
    db.insert_link("C1", "C2")
    db.insert_link("C2", "C3")
    db.insert_link("C3", "C1")
    assert find_path_in_database_bfs("C1", "C3", db) == ['C1', 'C2', 'C3']
    print("test_circular_loop: Passed")

if __name__ == "__main__":
    test_length_1()
    test_length_2()
    test_no_path_1()
    test_path_to_itself_1()
    test_circular_loop()
    db.close()
