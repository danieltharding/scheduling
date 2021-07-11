import igraph
import pandas as pd
from flask import jsonify
from math import inf
import database_api as api



def get_graph(name, make_new=True):
    if name == "":
        return jsonify({"success": False})
    api.add_new_graph(name, replace_if_exists=make_new)
    return jsonify({'success': True})


def new_graph(name):
    r = api.get_all_info(name)
    if r['exist']:
        graph = igraph.Graph(n=r['current_index'], directed=True)
        graph.add_edges(r['edge_list'])
        return graph
    return None


def add_vertex(name, new_vertex):
    return jsonify({'success': api.add_new_vertex(name, new_vertex)})


def create_pot_edges(name):
    g = new_graph(name)
    hold = {}
    vertex_set = igraph.VertexSeq(g)
    for i in range(len(vertex_set)):
        for j in range(i + 1, len(vertex_set)):
            hold[(i, j)] = False
            hold[(j, i)] = False
    pot_edges = api.get_potential_edges(name)
    for key in pot_edges.keys():
        hold[key] = pot_edges[key]
    return hold


def add_edge(vert_from, vert_to, name):
    vert_to_info = api.vertex_exists(name, vert_to)
    vert_from_info = api.vertex_exists(name, vert_from)
    if not vert_to_info[0] or not vert_from_info[0]:
        return jsonify({'success': False})
    if causes_cycle(name, vert_from_info[1]['index'], vert_to_info[1]['index']):
        return jsonify({'success': False})
    return jsonify({'success': api.add_new_edge(name, vert_from, vert_to)})


def next_pairs(name):
    g = new_graph(name)
    if g is None:
        return jsonify({"success": False, "reason": "graph doesn't exist"})
    pot_edges = create_pot_edges(name)
    if len(pot_edges.keys()) == 0 or len(pot_edges.keys()) == 1:
        return jsonify({"success": False, "key_1": "", "key_2": ""})
    r = api.get_all_info(name)
    success = False
    key_1 = ""
    key_2 = ""
    for key in pot_edges.keys():
        if not pot_edges[key]:
            if not causes_cycle(name, key[0], key[1]):
                pot_edges[key] = True
                success = True
                key_1 = r['dic'][key[0]]
                key_2 = r['dic'][key[1]]
                break
            else:
                pot_edges[key] = True
    api.add_potential_edges(name, pot_edges)
    return jsonify({"success": success, "key_1": key_1, "key_2": key_2})


def causes_cycle(name, i, j):
    g = new_graph(name)
    g.add_edges([(i, j)])
    re = g.is_dag()
    g.delete_edges([(i, j)])
    return not re


def fill(list_to_fill, name):
    vertex = api.vertex_info(name)
    lists = vertex['dic']
    re = []
    for element in list_to_fill:
        re.append(lists[element])
    return re


def get_data_frame(dic, name):
    re = {}
    i = 0
    for key in dic.keys():
        re[key] = fill(dic[key], name)
        re["Can Start {}?".format(i)] = []
        if i == 0:
            for j in range(len(dic[key])):
                re["Can Start {}?".format(i)].append("Yes")
        re["Finished {}".format(i)] = []
        i += 1
    return correct_length(re)


def correct_length(dic):
    longest = 0
    for key in dic.keys():
        if len(dic[key]) > longest:
            longest = len(dic[key])
    for key in dic.keys():
        while len(dic[key]) < longest:
            dic[key].append("")
    return dic


def make_spreadsheet(name):
    topo = topological(name)
    frame = get_data_frame(topo, name)
    writer = make_file(name)
    df = pd.DataFrame(frame)
    df.to_excel(writer, sheet_name="Sheet 1", index=False)
    formulae(writer, topo, name)
    writer.close()


def make_file(name):
    return pd.ExcelWriter("static/{}.xlsx".format(name), engine='xlsxwriter')


def formulae(writer, sorted, name):
    worksheet = writer.sheets['Sheet 1']
    started = {}
    finished = {}
    for key in sorted.keys():
        for i in range(len(sorted[key])):
            started[sorted[key][i]] = chr(ord('A') + 3 * int(key) + 1) + str(i + 2)
            finished[sorted[key][i]] = chr(ord('A') + 3 * int(key) + 2) + str(int(i) + 2)
    for key in sorted.keys():
        for i in range(len(sorted[key])):
            if_statement = '=IF({0},"Yes", "")'.format(ands(sorted[key][i], finished, name))
            worksheet.write(started[sorted[key][i]], if_statement)


def ands(element, finished, name):
    g = new_graph(name)
    li = g.predecessors(element)
    string = ""
    for i in range(len(li)):
        if i != 0:
            string += ","
        hold = finished[li[i]] + '<>""'
        string += hold
    if len(li) == 0:
        string = "True"
    elif len(li) > 1:
        string = "And(" + string + ")"
    return string


def topological(name):
    g = new_graph(name)
    search = g.topological_sorting()
    shortest_paths = g.shortest_paths()
    order = 0
    re = {}
    li = [search[0]]
    for current in range(1, len(search)):
        same_level = True
        for element in li:
            if same_level and shortest_paths[element][search[current]] != inf:
                same_level = False
        if same_level:
            li.append(search[current])
        else:
            re[order] = li
            li = [search[current]]
            order += 1
    re[order] = li
    return re


def get_spreadsheet(name):
    if not api.graph_is_indatabase(name):
        return jsonify({"success": False, "reason": "graph doesn't exist"})
    # if name not in graphs.keys():
    #     return jsonify({"success": False, "reason": "graph doesn't exist"})
    make_spreadsheet(name)
    return jsonify({'success': True})


def db_setup():
    api.database_setup()

if __name__ == "__main__":
    g = igraph.Graph.Full(3, directed=True)
    print(igraph.VertexSeq(g))
    for i in igraph.VertexSeq(g):
        print(i)
