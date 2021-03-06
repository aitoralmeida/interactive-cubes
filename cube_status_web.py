# -*- coding: utf-8 -*-
"""
Created on Wed Oct 22 11:31:35 2014

@author: aitor
"""

''' 
CUBE IDS
 - Violet: 1
 - Yellow : 2
 - Blue: 3
 - Red: 4
 - Green: 5
 - Orange: 6
'''

from flask import Flask, render_template

import serial

import networkx as nx
from networkx.readwrite import json_graph
import json

app = Flask(__name__)

SERIAL_NUMBER = 11
EOL_CHAR = '\r'
CMD_GET_BATTERY = 'GET_BATTERY'
CMD_GET_GRAPH = 'GET_GRAPH'
RPL_BATTERY = 'BATTERY'
RPL_GRAPH = 'GRAPH'
SEP_CHAR = ','
SEP_CHAR2 = ';'
SEP_CHAR3 = '-'
SEP_CHAR4 = '.'
ERROR = 'error'


def read_eol(ser):
    command = ''
    while(True):
        c = ser.read()        
        if c == EOL_CHAR:
            break
        else:
            command += c
    return command
    
    
def get_battery_level(cube_id):
    ser = serial.Serial(SERIAL_NUMBER)
    reply = ERROR
    command = '%s %s%s' % (CMD_GET_BATTERY, cube_id, EOL_CHAR)
    #Reply: BATTERY 6,84
    print ' - Sending:', command
    try:        
        ser.write(command)
        reply = read_eol(ser) 
        print 'reply:', reply
        while not reply.startswith(RPL_BATTERY):
            reply = read_eol(ser)
            print 'reply:', reply
    except TypeError as e:
        print 'get_graph:', e
        print ' - command:', command
        reply = ERROR
    finally:        
        ser.close()
        
    return reply
    
def get_graph():
    ser = serial.Serial(SERIAL_NUMBER)
    command = CMD_GET_GRAPH + EOL_CHAR
    reply = ERROR
    try:        
        print ' - Sending:', command
        ser.write(command + EOL_CHAR)
        reply = read_eol(ser)
        print reply
        while not reply.startswith(RPL_GRAPH):
            reply = read_eol(ser)
            print reply
    except TypeError as e:
        print 'get_graph:', e
        print ' - command:', command
        reply = ERROR
    finally:        
        ser.close()
    return reply
    
def split_edges(seq):
    edges = []
    tokens = seq.split(SEP_CHAR2)
    i = 0
    a = ''
    b = ''
    for t in tokens:
        i += 1
        if i == 1:
            a = t
        elif i == 2:
            b = t
            edges.append([a,b])
        elif i == 4:
            i = 0     
    return edges   

    
def build_graph(graph_state):
    faces = graph_state.split(SEP_CHAR)[0].split(SEP_CHAR2)
    if SEP_CHAR in graph_state:
        edges = []
        for e in graph_state.split(SEP_CHAR)[1:]:
            edges.append([e.split(SEP_CHAR2)[0], e.split(SEP_CHAR2)[1]])
    else:
        edges = []

    G = nx.Graph()
    for f in faces:
        node = f.split(SEP_CHAR3)[0]
        face = f.split(SEP_CHAR3)[1]
        G.add_node(node, label='CUBE-%s' % (node), face=face)
        
    for edge in edges:
        a = edge[0]
        b = edge[1]
        G.add_edge(a, b)
        
    return G


@app.route("/graph/")
def show_graph():
    reply = get_graph()
    if reply != ERROR:
        G = build_graph(reply.split(' ')[1])
        data = json_graph.node_link_data(G)
        json_data = json.dumps(data)          
    else:
        json_data = None 
        

    #json_data = '{"directed": false, "graph": [], "nodes": [{"label": "CUBE-4", "id": "4", "face": "5"}, {"label": "CUBE-6", "id": "6", "face": "5"}], "links": [{"source": 0, "target": 1, "value" : 5}], "multigraph": false} '
    return render_template('graph.html', data = json_data)
        
    
@app.route("/battery_level/<int:cube_id>/")
def show_battery_level(cube_id):
    reply = get_battery_level(cube_id)
    if reply != ERROR:
        level = reply.split(SEP_CHAR)[1]
    else:
        level = None
    
    return render_template('battery.html', cube_id=cube_id, level=level)
    
@app.route("/battery_levels/")
def show_battery_levels():
    reply = get_graph()
    battery_levels = {}
    if reply != ERROR:
        graph_state = reply.split(' ')[1]
        faces = graph_state.split(SEP_CHAR)[0].split(SEP_CHAR2)
        for f in faces:
            node = f.split(SEP_CHAR3)[0]
            reply = get_battery_level(int(node))
            level = reply.split(SEP_CHAR)[1]
            battery_levels[node] = level                            
    else:
        battery_levels = None
        
    return render_template('battery_levels.html', battery_levels = battery_levels)

if __name__ == "__main__":
    app.debug = True
    app.run()