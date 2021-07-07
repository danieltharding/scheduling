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
        if name == "":
            return render_template("inde.html", success="Please enter a name into the box")
        return redirect('/tasks')
    return render_template("inde.html")


@app.route('/tasks', methods=['GET', "POST"], endpoint="tasks")
def tasks():
    if request.method == "POST":
        form = request.form
        re = graph_lib.add_vertex(form['task'])
        if re:
            string = form['task'] + " was added"
        else:
            if form['task'] == "":
                string = "Please enter something into the box"
            else:
                string = form['task'] + " already exists"
        return render_template("home.html", success=string)
    return render_template("home.html")


@app.route('/links', methods=['Get', 'POST'])
def link():
    global current
    if request.method == 'POST':
        if request.form.get('yes'):
            graph_lib.add_edge(current[0], current[1])
    next_available, first, second = graph_lib.next_pairs()
    if next_available:
        current = [first, second]
        return render_template("make_connections.html", first=first, second=second)
    else:
        return render_template('make_connections.html', first=None)


@app.route('/done')
def done():
    global name
    graph_lib.make_spreadsheet(name)
    return render_template("get_spreadsheet.html", link=url_for('static', filename="{}.xlsx".format(name)))


if __name__ == "__main__":
    app.run()