# -*- coding: utf-8 -*-
"""
Created on Wed Oct 22 11:31:35 2014

@author: aitor
"""

from flask import Flask
import serial
import time
import networkx as nx

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

ser = serial.Serial(SERIAL_NUMBER)


def read_eol():
    command = ''
    while(True):
        c = ser.read()        
        if c == EOL_CHAR:
            break
        else:
            command += c
    return command
    
def send_command(command):
    ser.write(command + EOL_CHAR)
    
def get_battery_level(cube_id):
    command = '%s %s%s' % (CMD_GET_BATTERY, cube_id, EOL_CHAR)
    #Reply: BATTERY 6,84
    print ' - Sending:', command
    reply = read_eol()    
    return reply
    
def get_graph():
    command = CMD_GET_GRAPH + EOL_CHAR
    print ' - Sending:', command
    ser.write(command + EOL_CHAR)
    reply = read_eol()
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
        G.add_node(node, face=face)
        
    for edge in edges:
        a = edge[0]
        b = edge[1]
        G.add_edge(a, b)
        
    return G


@app.route("/graph/")
def hello():
    command = get_graph()
    print command
    while not command.startswith(RPL_GRAPH):
        command = read_eol()
        
    G = build_graph(command.split(' ')[1])
    return str(G.edges())

if __name__ == "__main__":
    app.run()