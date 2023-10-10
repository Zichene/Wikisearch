import sys
import time

from database import PageDatabase
from find_path import print_path, find_path, find_path_in_database_bfs

if __name__ == "__main__":
    db = PageDatabase('page_data.db')
    print("[Info]: Current number of pages in database (max=" + str(db.MAX_PAGES) + "):" + str(db.num_of_pages))

    if len(sys.argv) != 4 and len(sys.argv) != 3:
        print("[Warning]: Incorrect usage: py ws.py <base> <destination> [extra_cmd]")
        exit(0)
    dyn, db_only = False, False
    if len(sys.argv) == 4:
        match sys.argv[3]:
            case "-d":
                dyn = True
            case "-db":
                db_only = True
            case _:
                print("[Warning]: Unrecognized extra command: " + sys.argv[3])

    if not db_only:
        t1 = time.time()
        print_path(find_path(sys.argv[1], sys.argv[2], db, dyn))
    else:
        print("[Info]: Searching only in database.")
        t1 = time.time()
        print_path(find_path_in_database_bfs(sys.argv[1], sys.argv[2], db))

    print("[Info]: Time taken: " + str(time.time() - t1) + " s.")
    db.close()
