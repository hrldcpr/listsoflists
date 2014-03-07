import csv
import sys

import psycopg2


def load(tsv):
    with psycopg2.connect(database='buzzfeed') as db:
        with db.cursor() as cur:
            cur.execute('create table lists (id serial primary key, n integer, url varchar);')

            for row in csv.DictReader(tsv, delimiter='\t'):
                cur.execute('insert into lists (n, url) values (%(n)s, %(url)s);',
                            row)


if __name__ == '__main__':
    with open(sys.argv[1]) as tsv:
        load(tsv)
