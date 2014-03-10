from flask import Flask, render_template, url_for, Markup
app = Flask(__name__)

import psycopg2

from models import Item

@app.route('/')
def index():
    with psycopg2.connect(database='buzzfeed') as db:
        with db.cursor() as cur:
            cur.execute('select n from lists where views is not null group by n order by max(views) desc;')
            rows = cur.fetchall()

    title = "{} Lists Of Lists Of Stuff You Won't Believe!".format(len(rows))
    items = [Item("{} Lists of {} Things That Will Leave You Comatose!".format(r[0], r[0]),
                  url_for('list', n=r[0], slug='whatever'))
             for r in rows]
    return render_template('list.html', title=title, items=items)

@app.route('/<int:n>/<slug>')
def list(n, slug):
    with psycopg2.connect(database='buzzfeed') as db:
        with db.cursor() as cur:
            cur.execute('select title, url from lists where n=%(n)s order by views desc limit %(n)s',
                        dict(n=n))
            rows = cur.fetchall()

    items = [Item(Markup(r[0]), 'http://www.buzzfeed.com' + r[1]) for r in rows]
    return render_template('list.html', title=slug, items=items)

if __name__ == '__main__':
    app.run(debug=True)
