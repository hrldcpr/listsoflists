from flask import Flask, render_template, url_for
app = Flask(__name__)

from models import Item

@app.route('/')
def index():
    title = "54 Lists Of Lists Of Stuff You Won't Believe!"
    items = [Item("17 Lists of 17 Things That Will Leave You Comatose!",
                  url_for('list', n=17, slug='whatever'))]
    return render_template('list.html', title=title, items=items)

@app.route('/<int:n>/<slug>')
def list(n, slug):
    return render_template('list.html', title=slug, items=[])

if __name__ == '__main__':
    app.run(debug=True)
