from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)
current = []
name = ""
base_url = "http://localhost:5000/"


@app.route('/', methods=['GET', 'POST'], endpoint="home")
def home():
    global name
    url = base_url
    if request.method == "POST":
        name = request.form['name']
        if name == "":
            return render_template("inde.html", success="Please enter a name into the box")
        requests.post(url, json={"name": name, "new": True})
        return redirect('/tasks')
    return render_template("inde.html")


@app.route('/tasks', methods=['GET', "POST"], endpoint="tasks")
def tasks():
    url = base_url + "add_vertex"
    if request.method == "POST":
        form = request.form
        payload = {"name": name, "vertex_name": form['task']}
        r = requests.post(url, json=payload)
        re = r.json()['success']
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
    url = base_url + "add_edge"
    url_available = base_url + "next_pairs"
    try:
        if request.method == 'POST':
            if request.form.get('yes'):
                payload = {'name': name, 'vert_from': current[0], 'vert_to': current[1]}
                r = requests.post(url, json=payload)
        payload = {'name': name}
        r = requests.post(url_available, json=payload)
        next_available = r.json().get("success")
        first = r.json().get("key_1")
        second = r.json().get("key_2")
        if next_available:
            current = [first, second]
            return render_template("make_connections.html", first=first, second=second)
        else:
            return render_template('make_connections.html', first=None)
    except Exception as e:
        return render_template("Error.html", error=e)


@app.route('/done')
def done():
    url = base_url + "get_spreadsheet"
    payload = {"name": name}
    r = requests.get(url, json=payload)
    open("static/{}.xlsx".format(name), "wb").write(r.content)
    return render_template("get_spreadsheet.html", link=url_for('static', filename="{}.xlsx".format(name)))


if __name__ == "__main__":
    app.run(port=8000)
