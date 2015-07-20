import sys
import MySQLdb as mdb
from collections import defaultdict
import smtplib
from email.mime.text import MIMEText
import json
import os.path

__author__ = 'jloosli'

COMMASPACE = ', '


class DB:
    connections = defaultdict(list)

    def __init__(self, config):
        self.config = config

    def __del__(self):
        for db in self.connections:
            con = self.connections[db]['con']
            if con:
                con.close()

    def setup_connection(self, database):
        try:
            con = mdb.connect(self.config['host'], self.config['user'], self.config['password'], database)
            cur = con.cursor()
            self.connections[database] = {'con': con, 'cur': cur}
        except mdb.Error as e:
            print("Error {}: {}".format(e.args[0], e.args[1]))
            sys.exit(1)

    def get_cursor(self, database):
        if database not in self.connections:
            self.setup_connection(database)
        return self.connections[database]['cur']

    def query(self, database, query, params=None):
        return self.get_cursor(database).execute(query, params)


def check_databases(conn, databases):
    results = defaultdict(list)
    for database in databases:
        print("Checking database {}".format(database))
        try:
            conn.get_cursor(database).execute("""SELECT casings.barcode
        FROM `co_items`
        LEFT JOIN casings on casings.id = co_items.casing_id
        LEFT JOIN `finished_goods` fg on fg.casing_id = casings.id
        WHERE fg.id is null and casings.casing_status_id = 9""")
            rows = conn.get_cursor(database).fetchall()
            print("Found {} bad barcodes".format(conn.get_cursor(database).rowcount))
            for row in rows:
                print(row)
                results[database].append(row[0])
        except mdb.Error as e:
            print("Error {}: {}".format(e.args[0], e.args[1]))
            sys.exit(1)

    return results


def fix_finished_good(database, barcodes, notifications=[]):
    body = "Database '{}' was missing the finished goods for the following barcodes:\n{}\n\n".format(database, barcodes)
    print(body)
    msg = MIMEText(body)
    msg['Subject'] = 'Finished goods issues on {}'.format(database)
    msg['From'] = 'donotreply@donotreply.com'
    msg['To'] = COMMASPACE.join(notifications)
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()


def main():
    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), 'config.json')), 'r') as f:
        config = json.load(f)
    conn = DB(config)
    databases_to_check = config['databases']
    issues = check_databases(conn, databases_to_check)
    for db, barcodes in issues.items():
        print(db)
        fix_finished_good(db, barcodes, notifications=config['notifications'])


if __name__ == '__main__':
    main()
