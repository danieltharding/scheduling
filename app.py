from flask import Flask, render_template, request, redirect, url_for
import graph_lib

app = Flask(__name__)
current = []
name = ""


@app.route('/', methods=['GET', 'POST'], endpoint="home")
def home():
    global name
    if request.method == "POST":
        graph_lib.new_graph()
        name = request.form['name']
        return redirect('/tasks')
    return render_template("inde.html")


@app.route('/tasks', methods=['GET', "POST"], endpoint="tasks")
def tasks():
    if request.method == "POST":
        form = request.form
        graph_lib.add_vertex(form['task'])
        return render_template("home.html")
    return render_template("home.html")


@app.route('/links', methods=['Get', 'POST'])
def link():
    global current
    if request.method == 'POST':
        form = request.form
        if form.get('yes'):
            graph_lib.add_edge(current[0], current[1])
        else:
            available, first, second = graph_lib.swap()
            if available:
                current = [first, second]
                return render_template("make_connections.html", first=first, second=second)
    next_available, first, second = graph_lib.next_pairs()
    if next_available:
        current = [first, second]
        return render_template("make_connections.html", first=first, second=second)
    else:
        return redirect('/done')


@app.route('/done')
def done():
    global name
    graph_lib.make_spreadsheet(name)
    return render_template("get_spreadsheet.html", link=url_for('static', filename="{}.xlsx".format(name)))


if __name__ == "__main__":
    app.run()
from flask import Flask, render_template, request, redirect, url_for
import graph_lib

app = Flask(__name__)
current = []
name = ""


@app.route('/', methods=['GET', 'POST'], endpoint="home")
def home():
    global name
    if request.method == "POST":
        graph_lib.new_graph()
        name = request.form['name']
        return redirect('/tasks')
    return render_template("inde.html")


@app.route('/tasks', methods=['GET', "POST"], endpoint="tasks")
def tasks():
    if request.method == "POST":
        form = request.form
        re = graph_lib.add_vertex(form['task'])
        if re:
            string = form["task"] + " added"
        else:
            string = form['task'] + " not added"
        return render_template("home.html", success=string)
    return render_template("home.html")


@app.route('/links', methods=['Get', 'POST'])
def link():
    global current
    if request.method == 'POST':
        form = request.form
        if form.get('yes'):
            graph_lib.add_edge(current[0], current[1])
        else:
            available, first, second = graph_lib.swap()
            if available:
                current = [first, second]
                return render_template("make_connections.html", first=first, second=second)
    next_available, first, second = graph_lib.next_pairs()
    if next_available:
        current = [first, second]
        return render_template("make_connections.html", first=first, second=second)
    else:
        return redirect('/done')


@app.route('/done')
def done():
    global name
    graph_lib.make_spreadsheet(name)
    return render_template("get_spreadsheet.html", link=url_for('static', filename="{}.xlsx".format(name)))


if __name__ == "__main__":
    app.run()
