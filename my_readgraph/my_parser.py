import pickle
from netlist import *
import re
from my_init import *

inductance_types = []

def read_netlist(filename):
    """解析SPICE网表文件,取子电路及其元件信息
    参数：
        filename: SPICE网表文件路径
    返回：
        subckts: 包含所有子电路信息的列表
    """
    subckts = []        # 存储所有子电路的列表
    subckt_flag = False  # 标记是否处于子电路定义块中
    potential = [[]]    # 存储电势分组信息，用于处理3阱工艺
    with open(filename, "r") as f:
        for line in f:
            potential_flag = False  # 标记当前行是否包含电势参数
            # 预处理行内容：移除括号和首尾空格
            line = re.sub(r"[\(\)]", "", line)
            line = line.strip()  # 去除空格
            
            if not line:  # 跳过空行
                continue
                
            tokens = line.split()
            if line.startswith("*"):  # 跳过注释行
                continue
                
            # 处理子电路定义开始
            elif line.startswith(".subckt") or line.startswith(".SUBCKT") or line.startswith(".topckt"):
                # class SpiceSubckt(object):
                #   def __init__(self):
                #       self.name = ""
                #       self.pins = []
                #       self.entries = []
                tmpckt = SpiceSubckt()
                tmpckt.name = tokens[1]    # 子电路名称
                tmpckt.pins = tokens[2:]   # 子电路引脚列表
                subckts.append(tmpckt)
                subckt_flag = True
                
            # 处理子电路定义结束    
            elif line.startswith(".ends") or line.startswith(".ENDS"):
                subckt_flag = False
                
            else:
                if subckt_flag:  # 处理子电路内部的元件定义
                    # class SpiceEntry(object):
                    #   def __init__(self):
                    #     self.name = ""
                    #     self.pins = []
                    #     self.cell = None
                    #     self.attributes = {}
                    entry = SpiceEntry()
                    entry.name = tokens[0]  # 元件实例名（如M1、R2等）
                    # 设置默认参数值
                    entry.attributes['w'] = '1.0e-6'   # 默认宽度
                    entry.attributes['l'] = '1.0e-6'   # 默认长度
                    entry.attributes['nf'] = '1'       # 默认finger数
                    
                    # 反向解析参数（从后往前找器件类型）
                    for i in range(len(tokens) - 1, 0, -1):
                        token = tokens[i]
                        if '=' in token:  # 处理参数赋值（如w=2u）
                            potential_flag = True
                            a_eq_b = token.split('=')
                            assert len(a_eq_b) == 2  # 确保参数格式正确
                            
                            # 处理宽度参数（w/wr/wt）
                            if a_eq_b[0] == 'w' or a_eq_b[0] == 'wr' or a_eq_b[0] == 'wt':
                                # 处理不同单位表示（w1 -> 1e-6，2u -> 2e-6，5n ->5e-9）
                                if a_eq_b[1][0] == 'w':
                                    entry.attributes['w'] = str((float(a_eq_b[1][1:]) + 1)) + 'e' + '-6'
                                elif a_eq_b[1][-1] == 'u':
                                    entry.attributes['w'] = a_eq_b[1][0:-1] + 'e-6'
                                elif a_eq_b[1][-1] == 'n':
                                    entry.attributes['w'] = a_eq_b[1][0:-1] + 'e-9'
                                else:
                                    entry.attributes['w'] = a_eq_b[1]
                                    
                            # 处理长度参数（l/lr/lt）逻辑同上
                            elif a_eq_b[0] == 'l' or a_eq_b[0] == 'lr' or a_eq_b[0] == 'lt':
                                if a_eq_b[1][0] == 'l':
                                    entry.attributes['l'] = str((float(a_eq_b[1][1:]) + 1)) + 'e' + '-6'
                                elif a_eq_b[1][-1] == 'u':
                                    entry.attributes['l'] = a_eq_b[1][0:-1] + 'e-6'
                                elif a_eq_b[1][-1] == 'n':
                                    entry.attributes['l'] = a_eq_b[1][0:-1] + 'e-9'
                                else:
                                    entry.attributes['l'] = a_eq_b[1]
                                    
                            # 处理finger数参数    
                            elif a_eq_b[0] == 'mf' or a_eq_b[0] == 'nf':
                                entry.attributes['nf'] = a_eq_b[1]
                                
                        else:  # 遇到非参数项时确定器件类型
                            entry.cell = tokens[i]  # 器件类型（nmos/pmos等）
                            temp_pin = tokens[1:i]  # 提取引脚信息
                            
                            # 处理3阱工艺的特殊情况（引脚数>4）
                            if len(temp_pin) > 4 and potential_flag:  
                                entry.pins = temp_pin[:4]  # 前4个为真实引脚
                                # 剩余引脚存入potential分组
                                index = next((i for i, sublist in enumerate(potential) if sublist == [temp_pin[4:]]), None)
                                if index is None:
                                    potential.append([temp_pin[4:]])
                                    entry.attributes['potential'] = len(potential) - 1
                                else:
                                    entry.attributes['potential'] = index
                            else:  # 普通情况直接存储引脚
                                entry.pins = tokens[1:i]
                                entry.attributes['potential'] = 0  # 默认分组
                            break  # 结束参数解析循环
                            
                    subckts[-1].entries.append(entry)  # 将元件添加到当前子电路
                else:
                    assert 0, "not in a subckt: %s" % line  # 异常：非子电路内容

                pass

    return subckts


def read_symfile(filename):
    """解析对称性定义文件，提取子电路对称元件对
    参数：
        filename: 对称性定义文件路径(.txt格式)
    返回：
        symmetry_map: 字典结构，键为子电路名，值为对称元件对列表
    """
    subckt = ""  # 当前处理的子电路模块名
    symmetry_map = {}  # 存储对称关系：{子电路名: [[元件对1], [元件对2]]}

    with open(filename, "r") as f:
        for line in f:
            line = line.strip()  # 去除首尾空白
            if not line:  # 跳过空行
                continue
            tokens = line.split()
            if len(tokens) == 1 and not tokens[0].startswith("x"):
                # 子电路定义行（如CLK_COMP）
                subckt = tokens[0]  # 更新当前子电路名
                symmetry_map[subckt] = []  # 初始化对称关系列表
            else:
                # 对称元件对行（如["M1", "M2"]）
                symmetry_map[subckt].append(tokens)  # 添加对称元件对到当前子电路

    return symmetry_map


def read_symattr(subckts):
    """从子电路元件的'sg'属性中解析对称组信息
    参数：
        subckts: SpiceSubckt对象列表，包含所有子电路信息
    返回：
        symmetry_map: 字典结构，键为子电路名，值为对称元件对列表
    """
    symmetry_map = {}  # 存储对称关系 {子电路名: [[对称元件对1], [对称元件对2]]}

    for subckt in subckts:
        symmetry_map[subckt.name] = []  # 初始化当前子电路的对称关系存储
        # 遍历子电路中的所有元件
        for i in range(len(subckt.entries)):
            # 检查元件是否包含对称组标识符'sg'
            if "sg" in subckt.entries[i].attributes.keys():
                # 在当前元件之后的范围寻找相同sg值的对称元件
                for j in range(i + 1, len(subckt.entries)):
                    # 跳过没有sg属性的元件
                    if "sg" not in subckt.entries[j].attributes.keys():
                        continue
                    # 发现匹配的对称组
                    if subckt.entries[i].attributes["sg"] == subckt.entries[j].attributes["sg"]:
                        # 记录对称元件对（如[M1, M2]）
                        symmetry_map[subckt.name].append([subckt.entries[i].name, subckt.entries[j].name])

    return symmetry_map


def print_graph_subckt(subckt, graph):
    content = ".subckt " + subckt.name
    for pin in subckt.pins:
        content += " " + pin
    content += "\n"
    for tmpnode in graph.nodes:
        if tmpnode.attributes["cell"] != "IO":
            content += tmpnode.attributes["name"]
            for pin in tmpnode.pins:
                assert graph.pins[pin].node_id == tmpnode.id
                content += " " + graph.nets[graph.pins[pin].net_id].attributes["name"]
            content += " " + tmpnode.attributes["cell"]
            for key, value in tmpnode.attributes.items():
                if key not in ["name", "cell"]:
                    content += " %s=%s" % (key, value)
            content += "\n"
    content += ".ends " + subckt.name
    print(content)


def subckts2graph(subckts, root_hint):  # subckts
    hierarchy_graph = nx.DiGraph()
    subckts_map = {}
    subckts2nodes_map = {}

    for subckt in subckts:
        subckts_map[subckt.name] = subckt  # subckt
        hierarchy_graph.add_node(subckt.name)
        subckts2nodes_map[subckt.name] = []

    for subckt in subckts:
        for entry in subckt.entries:
            if entry.cell in subckts_map:
                hierarchy_graph.add_edge(subckt.name, entry.cell)

    roots = []
    for n, d in hierarchy_graph.in_degree():  # d in
        if d == 0:
            roots.append(n)
    print("roots", roots)

    graph = SpiceGraph()

    def build_flat(subckt, context, context_nets):
        local_nets = {}
        for entry in subckt.entries:
            for pin in entry.pins:
                if pin not in subckt.pins:
                    # assert pin not in context_nets, "%s not in %s failed" % (pin, str(context_nets.keys()))
                    if pin not in local_nets:
                        tmpnet = SpiceNet()
                        tmpnet.id = len(graph.nets)
                        tmpnet.attributes["name"] = context + pin
                        graph.nets.append(tmpnet)
                        local_nets[pin] = tmpnet
        print("local nets", local_nets.keys())

        def entry_pins(entry, pin):
            if len(entry.pins) == 4 and (entry.cell in p_types or entry.cell in n_types):  # MOS
                if i == 0:
                    pin.attributes["type"] = "drain"
                elif i == 1:
                    pin.attributes["type"] = "gate"
                elif i == 2:
                    pin.attributes["type"] = "source"
                elif i == 3:
                    pin.attributes["type"] = "substrate"
                else:
                    assert 0, "unknown %d" % i
            elif entry.cell in res_types or entry.cell in cap_types:
                if i == 0:
                    pin.attributes["type"] = "passive"
                elif i == 1:
                    pin.attributes["type"] = "passive"
                elif i == 2:
                    pin.attributes["type"] = "substrate"
                else:
                    assert 0, "unknown %d" % i
            elif entry.cell in diode_types:
                if i == 0:
                    pin.attributes["type"] = "N+"
                elif i == 1:
                    pin.attributes["type"] = "N-"
                else:
                    assert 0, "unknown %d" % i
            # bipolar junction transistor
            elif entry.cell in npn_types or entry.cell in pnp_types:
                if i == 0:
                    pin.attributes["type"] = "c"
                elif i == 1:
                    pin.attributes["type"] = "b"
                elif i == 2:
                    pin.attributes["type"] = "e"
                elif i == 3:
                    pin.attributes["type"] = "hbeta"
                else:
                    assert 0, "unknown %d" % i
            else:
                # pdb.set_trace()
                assert 0, "unknown device: %s" % entry.cell

        for entry in subckt.entries:
            if entry.cell not in subckts_map:
                tmpnode = SpiceNode()
                tmpnode.id = len(graph.nodes)
                tmpnode.attributes["name"] = context + entry.name
                tmpnode.attributes["cell"] = entry.cell
                tmpnode.attributes.update(entry.attributes)
                graph.nodes.append(tmpnode)
                for i, pin in enumerate(entry.pins):
                    if pin in subckt.pins:
                        # assert pin in context_nets, "%s in %s failed" % (pin, str(context_nets.keys()))
                        tmppin = SpicePin()
                        tmppin.id = len(graph.pins)
                        tmppin.node_id = tmpnode.id
                        tmppin.net_id = context_nets[pin].id
                        entry_pins(entry, tmppin)
                        tmpnode.pins.append(tmppin.id)
                        context_nets[pin].pins.append(tmppin.id)
                        graph.pins.append(tmppin)
                    # local nets not power
                    else:
                        # assert pin not in context_nets, "%s not in %s failed" % (pin, str(context_nets.keys()))
                        tmppin = SpicePin()
                        tmppin.id = len(graph.pins)
                        tmppin.node_id = tmpnode.id
                        tmppin.net_id = local_nets[pin].id
                        entry_pins(entry, tmppin)
                        tmpnode.pins.append(tmppin.id)
                        local_nets[pin].pins.append(tmppin.id)
                        graph.pins.append(tmppin)
            else:
                subckt_sub = subckts_map[entry.cell]
                context_sub = context + entry.name + "/"
                context_nets_sub = {}
                for i in range(len(entry.pins)):
                    pin = entry.pins[i]
                    if pin in subckt.pins:
                        # assert pin in context_nets, "%s in %s failed" % (pin, str(context_nets.keys()))
                        context_nets_sub[subckt_sub.pins[i]] = context_nets[pin]
                    else:
                        # assert pin not in context_nets, "%s not in %s failed" % (pin, str(context_nets.keys()))
                        context_nets_sub[subckt_sub.pins[i]] = local_nets[pin]
                build_flat(subckt_sub, context_sub, context_nets_sub)

    if root_hint in roots:
        roots = [root_hint]
    assert len(roots) == 1
    for root in roots:
        subckt = subckts_map[root]
        context_nets = {}
        for pin in subckt.pins:
            tmpnode = SpiceNode()
            tmppin = SpicePin()
            tmpnet = SpiceNet()
            tmpnode.id = len(graph.nodes)
            tmpnet.id = len(graph.nets)
            tmppin.id = len(graph.pins)

            tmpnode.attributes["cell"] = "IO"
            tmpnode.attributes["name"] = pin
            tmpnode.pins.append(tmppin.id)

            tmpnet.attributes["name"] = pin
            tmpnet.pins.append(tmppin.id)

            tmppin.node_id = tmpnode.id
            tmppin.net_id = tmpnet.id
            tmppin.attributes["type"] = "IO"

            graph.nodes.append(tmpnode)
            graph.nets.append(tmpnet)
            graph.pins.append(tmppin)
            context_nets[pin] = tmpnet

        build_flat(subckt, subckt.name + "/", context_nets)
        print("recovered")
        # print_graph_subckt(subckt, graph)

    return graph, roots


def parse_all(filedir, save_dir):
    sys.stdout = TeeLogger(para_log_path)
    try:
        dataX = []
        dataY = []

        netlists = glob.glob(os.path.join(filedir, "*.sp"))
        netlists = sorted(netlists)
        symfiles = glob.glob(os.path.join(filedir, "*.txt"))

        for netlist in netlists:
            print("read netlist file: %s" % netlist)
            root_hint = netlist.split('/')[-1].split('.')[0]
            subckts = read_netlist(netlist)

            # parse symfile
            # 生成对应的对称文件路径
            txt_file = netlist.replace(".sp", ".txt")
            symfile = txt_file if txt_file in symfiles else None  # 检查是否存在对应txt文件

            if symfile:
                print("read symmetry file: %s" % symfile)
                symmetry_map = read_symfile(symfile)
            else:
                print("parse symmetry info from attributes")
                symmetry_map = read_symattr(subckts)
                pass

            # spice graph
            graph, roots = subckts2graph(subckts, root_hint)

            symmetry_id_array = []

            def add_symmetry_pairs(subckt_inst, pairs):
                for pair in pairs:
                    skip_flag = False
                    if len(pair) == 1:
                        for subckt in subckts:
                            for entry in subckt.entries:
                                if entry.name == pair[0] and entry.cell in symmetry_map:
                                    skip_flag = True
                                    break
                            if skip_flag:
                                break
                    if skip_flag:
                        continue

                    names = pair  # (M1,M2)...
                    node_id_pair = []
                    groups = {}
                    for name in names:
                        groups[name] = []
                    for tmpnode in graph.nodes:
                        for name in names:  # M1 M2...
                            if subckt_inst in roots:
                                if root_hint + "/" + name == tmpnode.attributes["name"]:
                                    groups[name].append(tmpnode.id)  # group[M1]:1 group[M2]:2
                            elif subckt_inst not in roots:
                                if root_hint + "/" + subckt_inst + "/" + name == tmpnode.attributes["name"]:
                                    groups[name].append(tmpnode.id)  # group[M1]:1 group[M2]:2
                    for key, value in groups.items():
                        assert len(value) == 1
                        node_id_pair.append(value[0])
                    symmetry_id_array.append(node_id_pair)  # M1,M2) to [1,2]

            for subckt_sym, pairs in symmetry_map.items():
                if subckt_sym in roots:  # roots is the topckt
                    add_symmetry_pairs(subckt_sym, pairs)
                else:
                    for subckt in subckts:
                        for entry in subckt.entries:
                            if entry.cell == subckt_sym:
                                add_symmetry_pairs(entry.name, pairs)

            print("symmetry_map")
            print(symmetry_map)
            print("symmetry_id_array")
            print(symmetry_id_array)

            content = ""
            for pair in symmetry_id_array:
                content += "("
                for node_id in pair:
                    if isinstance(node_id, tuple):
                        content += " { "
                        for nid in node_id:
                            content += " " + graph.nodes[nid].attributes["name"]
                        content += " } "
                    else:
                        content += " " + graph.nodes[node_id].attributes["name"]
                content += " ) "
            print(content)
            print("----------------------------------------------------------------------------------")

            dataX.append({"subckts": subckts, "graph": graph})
            dataY.append(symmetry_id_array)
        with open(save_dir + "/" + "dataXY_file.txt", 'wb') as f:
            pickle.dump((dataX, dataY), f)
        # return dataX, dataY
        # dataX:[{'subckts':subgraph1,'graph':graph1},{'subckts':subgraph2,'graph':graph2},.....]
        # dataY:[[labels1],[labels2],.....]
    finally:
        sys.stdout.logfile.close()
        sys.stdout = sys.stdout.terminal


if __name__ == '__main__':
    parse_all(path_read_SPICE,
              path_save_netlist)
    print("parse_all done")
