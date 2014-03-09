import csv
import sys

import psycopg2


def load(tsv):
    with psycopg2.connect(database='buzzfeed') as db:
        with db.cursor() as cur:
            cur.execute('drop table lists;')
            cur.execute('create table lists (id serial primary key, n integer, url varchar, title varchar, views integer, facebook integer, twitter integer, email integer);')
            cur.execute('create index on lists (n, views desc);')

            for row in csv.DictReader(tsv, delimiter='\t'):
                # insert all columns into db:
                cur.execute('insert into lists ({}) values ({})'.format(','.join(row), ','.join('%({})s'.format(k) if v else 'null' for k, v in row.items())),
                            row)


if __name__ == '__main__':
    with open(sys.argv[1]) as tsv:
        load(tsv)
