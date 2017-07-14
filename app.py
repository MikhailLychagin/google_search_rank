from flask import Flask, render_template, request
from flask.views import MethodView
from check_rank import get_search_rank

flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return render_template("index.html")

@flask_app.route("/result", methods=["POST"])
def result():
    if request.form and request.form.get('search_query') and request.form.get('searched_url'):
        query = {'search_query': request.form['search_query'],
             'searched_url': request.form['searched_url']}
        rank = get_search_rank(**query)
        query.update({"rank": rank})
        return render_template("result.html", **query)

if __name__ == '__main__':
    flask_app.run()