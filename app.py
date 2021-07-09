from flask import Flask, render_template, request, redirect, url_for, make_response
import api

app = Flask(__name__)
# current = []


@app.route('/', methods=['GET', 'POST'], endpoint="home")
def home():
    if request.method == "POST":
        name = request.form['name']
        if name == "":
            return render_template("inde.html", success="Please enter a name into the box")
        api.get_graph(name)
        re = make_response(redirect('/tasks'))
        re.set_cookie("name", name)
        return re
    return render_template("inde.html")


@app.route('/tasks', methods=['GET', "POST"], endpoint="tasks")
def tasks():
    name = request.cookies.get("name")
    if request.method == "POST":
        form = request.form
        r = api.add_vertex(name, form['task'])
        re = r.json['success']
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
    name = request.cookies.get("name")
    if request.method == "GET":
        api.create_pot_edges(name)
    # try:
    if request.method == 'POST':
        print(request.cookies.get("key_1"))
        current = [request.cookies.get("key_1"), request.cookies.get("key_2")]
        if request.form.get('yes'):
            api.add_edge(current[0], current[1], name)
    r = api.next_pairs(name)
    next_available = r.json.get("success")
    first = r.json.get("key_1")
    second = r.json.get("key_2")
    if next_available:
        current = [first, second]
        re = make_response(render_template("make_connections.html", first=first, second=second))
        re.set_cookie("key_1", current[0])
        re.set_cookie("key_2", current[1])
        return re
    else:
        return render_template('make_connections.html', first=None)
    # except Exception as e:
    #     print("HERE")
    #     print(e)
    #     return render_template("Error.html", error=e)


@app.route('/done')
def done():
    name = request.cookies.get("name")
    api.get_spreadsheet(name)
    return render_template("get_spreadsheet.html", link=url_for('static', filename="{}.xlsx".format(name)))


if __name__ == "__main__":
    app.run(port=8000)
