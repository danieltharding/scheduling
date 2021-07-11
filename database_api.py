from sqlalchemy import create_engine
import database
from dotenv import load_dotenv
import os

load_dotenv()
database_url = os.getenv("DB_CONN")
engine = create_engine(database_url, echo=False)


def add_new_graph(name, replace_if_exists=False):
    result = graph_exists(name)
    if result.rowcount == 1:
        if replace_if_exists:
            engine.execute("DELETE FROM Graphs WHERE `name` = '" + name + "';")
        else:
            return
    engine.execute("INSERT INTO Graphs (name) VALUES ('" + name + "');")


def graph_exists(name):
    result = engine.execute("SELECT current_index FROM Graphs WHERE name = '" + name + "';")
    return result


def graph_is_indatabase(name):
    result = graph_exists(name)
    return result.rowcount > 0


def vertex_exists(name, vertex_name):
    result = engine.execute(
        "SELECT * FROM Vertices WHERE name = '" + name + "' and vertex_name = '" + vertex_name + "';")
    if result.rowcount == 0:
        return False, {}
    else:
        dic = {}
        for row in result:
            for key, value in row._mapping.items():
                dic[key] = value
        return True, dic


def add_new_vertex(name, vertex_name):
    result = graph_exists(name)
    if result.rowcount == 0:
        print("Graph does not exist")
        return False
    current_index = 0
    for row in result:
        for key, value in row._mapping.items():
            if key == "current_index":
                current_index = value
                break
    result = engine.execute(
        "SELECT * FROM Vertices WHERE name = '" + name + "' and vertex_name = '" + vertex_name + "';")
    if result.rowcount != 0:
        print("vertex exists")
        return False
    engine.execute(
        "INSERT INTO Vertices (name, `index`, vertex_name) VALUE ('" + name + "', " + str(
            current_index) + ", '" + vertex_name + "');"
    )
    # current_index += 1
    # engine.execute(
    #     "UPDATE Graphs SET Graphs.current_index = " + str(current_index) + " WHERE Graphs.name = '" + name + "';")
    return True


def add_new_edge(name, vertex_from, vertex_to):
    result = graph_exists(name)
    if result.rowcount == 0:
        print("Graph doesn't exist")
        return False

    dic_from = vertex_exists(name, vertex_from)
    dic_to = vertex_exists(name, vertex_to)

    if not dic_from[0] or not dic_to[0]:
        print("One of those don't exist")
        return False
    if edge_in_graph(name, dic_from[1]['index'], dic_to[1]['index']):
        return False
    values = "'{0}', {1}, {2}".format(name, dic_from[1]['index'], dic_to[1]['index'])
    engine.execute("INSERT INTO Edges (name, index_from, index_to) VALUE (" + values + ");")
    return True


def edge_exists(name, vert_from, vert_to):
    result = graph_exists(name)
    if result.rowcount == 0:
        return True
    vert_from_info = vertex_exists(name, vert_from)
    vert_to_info = vertex_exists(name, vert_to)
    if not vert_to_info[0] or not vert_from_info[0]:
        return True
    return edge_in_graph(name, vert_from_info[1]['index'], vert_to_info[1]['index'])


def edge_in_graph(name, index_from, index_to):
    where_clause = "`name` = '{0}' and index_from = {1} and index_to = {2}".format(name, index_from, index_to)
    result = engine.execute("SELECT * FROM Edges WHERE {};".format(where_clause))
    if result.rowcount > 0:
        return True
    return False


def vertex_info(name):
    result = graph_exists(name)
    if result.rowcount == 0:
        return {'set': [], 'dic': {}, 'exist': False}
    exist = True
    dic = {}
    result = engine.execute("SELECT `vertex_name`, `index` FROM Vertices WHERE name = '" + name + "'ORDER BY `index`;")
    for row in result:
        index = 0
        v_name = ""
        for key, value in row._mapping.items():
            if key == "index":
                index = value
            elif key == "vertex_name":
                v_name = value
        dic[index] = v_name
    re = {'set': list(dic.keys()), 'dic': dic, 'exist': exist}
    return re


def get_graph_edges(name):
    result = graph_exists(name)
    if result.rowcount == 0:
        return {'exist': False, 'edge_list': []}
    li = []
    result = engine.execute("SELECT index_from, index_to FROM Edges WHERE name = '" + name + "';")
    for row in result:
        index_from = 0
        index_to = 0
        for key, value in row._mapping.items():
            if key == "index_from":
                index_from = value
            elif key == "index_to":
                index_to = value
        li.append((index_from, index_to))
    return {'exist': True, 'edge_list': li}


def get_all_info(name):
    result = graph_exists(name)
    if result.rowcount == 0:
        return {'exist': False, 'edge_list': [], 'set': [], "dic": {}}
    edge_stuff = get_graph_edges(name)
    vertex_stuff = vertex_info(name)
    if result.rowcount == 0:
        return False
    current_index = 0
    for row in result:
        for key, value in row._mapping.items():
            if key == "current_index":
                current_index = value
                break
    return {'exist': True, 'current_index': current_index, 'edge_list': edge_stuff['edge_list'],
            'set': vertex_stuff['set'], 'dic': vertex_stuff['dic']}


def database_setup():
    database.create_database(engine)


if __name__ == "__main__":
    # database.populate_database("root", "sjc93545")
    add_new_graph("one")
    add_new_graph("one")
    add_new_vertex("one", "One")
    add_new_vertex("one", "Two")
    # add_new_vertex("one", "Three")
    # add_new_vertex("two", "One")
    # add_new_graph("two")
    # add_new_vertex("two", "One")
    # add_new_edge("one", "One", "Two")
    # add_new_edge("one", "Two", "Three")
    # print(add_new_edge("one", "One", "Two"))
    # print(vertex_info("one"))
    # print(get_graph_edges("one"))
    # print(get_all_info("one"))
    # print(vertex_exists("one", "One"))
    # print(edge_exists("one", "One", "Five"))
