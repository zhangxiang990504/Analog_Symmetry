
import os
import sys
import glob

import numpy as np
import networkx as nx


class SpiceEntry(object):
    def __init__(self):
        self.name = ""        # 元件实例名称（如M1、R2等）
        self.pins = []        # 引脚连接列表（存储节点名称或网络名）
        self.cell = None      # 元件类型（如nmos/pmos/电阻等基础器件）
        self.attributes = {}  # 元件参数字典（包含w/l/nf等工艺参数）

    def __str__(self):
        content = "name: " + self.name
        content += "; pins: " + " ".join(self.pins)
        content += "; cell: " + self.cell
        content += "; attr: " + str(self.attributes)
        return content

    def __repr__(self):
        return self.__str__()


class SpiceSubckt(object):
    def __init__(self):
        self.name = ""        # 子电路名称（如CLK_COMP）
        self.pins = []        # 子电路引脚列表（如["vdd", "gnd"]）
        self.entries = []     # 子电路包含的元件实例列表（SpiceEntry对象集合）

    def __str__(self):
        content = "subckt: " + self.name + "\n"
        content += "pins: " + " ".join(self.pins) + "\n"
        content += "entries: \n"
        for entry in self.entries:
            content += str(entry) + "\n"
        return content

    def __repr__(self):
        return self.__str__()


class SpiceNode(object):
    def __init__(self):
        self.id = None
        self.attributes = {}
        self.pins = []

    def __str__(self):
        content = "Node: " + str(self.id) + ", " + str(self.attributes) + ", " + str(self.pins)
        return content

    def __repr__(self):
        return self.__str__()


class SpiceNet(object):
    def __init__(self):
        self.id = None
        self.attributes = {}
        self.pins = []

    def __str__(self):
        content = "Net: " + str(self.id) + ", " + str(self.attributes) + ", " + str(self.pins)
        return content

    def __repr__(self):
        return self.__str__()


class SpicePin(object):
    def __init__(self):
        self.id = None
        self.node_id = None
        self.net_id = None
        self.attributes = {}

    def __str__(self):
        content = "SpicePin( " + str(self.id) + ", node: " + str(self.node_id) + ", net: " + str(
            self.net_id) + " attributes: " + str(self.attributes) + " )"
        return content

    def __repr__(self):
        return self.__str__()


class SpiceGraph(object):
    def __init__(self):
        self.nodes = []
        self.pins = []
        self.nets = []

    def __str__(self):
        content = "Graph\n"
        for node in self.nodes:
            content += str(node) + "\n"
        for pin in self.pins:
            content += str(pin) + "\n"
        for net in self.nets:
            content += str(net) + "\n"
        return content

    def __repr__(self):
        return self.__str__()
