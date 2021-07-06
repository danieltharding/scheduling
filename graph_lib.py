import igraph
import pandas as pd
from math import inf

g = igraph.Graph(directed=True)
dic = {}
li = []
index = 0
first = 0
second = 0
sw = True


def new_graph():
    global li, dic, index, first, second, sw
    g.delete_vertices(igraph.VertexSeq(g))
    li = []
    dic = {}
    index = 0
    first = 0
    second = 0
    sw = True


def add_vertex(name):
    global index
    if name in li or name == "":
        return False
    dic[name] = index
    g.add_vertex(index)
    index += 1
    li.append(name)
    return True


def add_edge(vert_from, vert_to):
    if (vert_from, vert_to) in g.get_edgelist():
        return
    g.add_edges([(dic[vert_from], dic[vert_to])])


def next_pairs():
    global first, second, sw
    if second + 1 == len(li):
        if first + 1 == len(li):
            return False, "", ""
        else:
            first += 1
            second = first + 1
            if second == len(li):
                return False, "", ""
    else:
        second += 1
    while causes_cycle(first, second):
        if not causes_cycle(second, first):
            sw = False
            return True, li[second], li[first]
        if second + 1 == len(li):
            if first + 1 == len(li):
                return False, "", ""
            else:
                first += 1
                second = first + 1
                if second == len(li):
                    return False, "", ""
        else:
            second += 1
    sw = True
    return True, li[first], li[second]


def swap():
    global first, second, sw
    if sw and not causes_cycle(second, first):
        sw = False
        return True, li[second], li[first]
    else:
        return False, "", ""


def causes_cycle(i, j):
    g.add_edges([(i, j)])
    re = g.is_dag()
    g.delete_edges([(i, j)])
    return not re


def fill(list_to_fill):
    global li
    re = []
    for element in list_to_fill:
        re.append(li[element])
    return re


def get_data_frame(dic):
    re = {}
    i = 0
    for key in dic.keys():
        re[key] = fill(dic[key])
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
    topo = topological()
    frame = get_data_frame(topo)
    writer = pd.ExcelWriter('./static/{}.xlsx'.format(name), engine='xlsxwriter')
    df = pd.DataFrame(frame)
    df.to_excel(writer, sheet_name="Sheet 1", index=False)
    formulae(writer, topo)
    writer.close()


def formulae(writer, sorted):
    worksheet = writer.sheets['Sheet 1']
    started = {}
    finished = {}
    for key in sorted.keys():
        for i in range(len(sorted[key])):
            started[sorted[key][i]] = chr(ord('A') + 3 * int(key) + 1) + str(i + 2)
            finished[sorted[key][i]] = chr(ord('A') + 3 * int(key) + 2) + str(int(i) + 2)
    for key in sorted.keys():
        for i in range(len(sorted[key])):
            if_statement = '=IF({0},"Yes", "")'.format(ands(sorted[key][i], finished))
            worksheet.write(started[sorted[key][i]], if_statement)


def ands(element, finished):
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


def topological():
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


if __name__ == "__main__":
    add_vertex("hello")
    add_vertex("there")
    add_edge("hello", "there")
    make_spreadsheet()
