import sys
import time

from database import PageDatabase
from find_path import print_path, find_path

if __name__ == "__main__":
    db = PageDatabase('page_data.db')
    print("[Info]: Current number of pages in database (max=" + str(db.MAX_PAGES) + "):" + str(db.num_of_pages))

    if len(sys.argv) != 4 and len(sys.argv) != 3:
        print("[Warning]: Incorrect usage: py ws.py <base> <destination> [-d]")
        exit(0)

    dyn = True if (len(sys.argv) == 4 and sys.argv[3] == "-d") else False

    t1 = time.time()
    print_path(find_path(sys.argv[1], sys.argv[2], db, dyn))  # -d command means dynamic
    print("[Info]: Time taken: " + str(time.time() - t1) + " s.")
    db.close()
