import sys
import os
# init spcicefile
path_read_SPICE = "/home/zhangxiang/work/Analog_Symmetry/example"
# specify netlist save path
path_save_netlist = "/home/zhangxiang/work/Analog_Symmetry/saves"

read_file = "/home/zhangxiang/work/Analog_Symmetry/saves/dataXY_file.txt"
save_file = "/home/zhangxiang/work/Analog_Symmetry/saves"

file_path = "/home/zhangxiang/work/Analog_Symmetry/saves"  # saved file dir from readgraph

p_types = ['pfet', 'pfet_lvt', 'pmos', 'pmos2v_mac', 'pmos50_ckt', 'pch_5_mac', 'pch_5', 'pch_mac', 'hvtpfet',
           'lvtpfet','pch_lvt','pch']
n_types = ['nfet', 'nfet_lvt', 'nmos', 'nmos2v_mac', 'nmos50_ckt', 'nch_5_mac', 'nch_5', 'nch_mac', 'hvtnfet',
           'lvtnfet','nch_lvt','nch']
npn_types = ['npnhbeta1a36_mis_ckt']  # npn
pnp_types = ['pnp2_rpo_mis']  # pnp
res_types = ['rpposab', 'resnwsti_pure5v', 'rppolyhri3d3k', 'rppolyhri1k_dis', 'rnpo1rpo_dis', 'res','rppolywo','rppolywo_m']  # res
cap_types = ['mimcap_2p0_sin', 'cap','cfmom']  # cap
diode_types = ['diode']  # diode

passive_types = res_types + cap_types
mosfet_types = p_types + n_types
power_types = ['gnd', 'GND', 'vss', 'VSS', 'vdd', 'VDD', 'vcc', 'VCC']
vdd_types = ['vdd', 'VDD', 'vcc', 'VCC']
gnd_types = ['gnd', 'GND', 'vss', 'VSS']
inductance_types = []

# 在现有路径变量后添加日志路径
path_save_logs = "/home/zhangxiang/work/Analog_Symmetry/logs"
para_log_path = os.path.join(path_save_logs, "parser.log")  # para日志文件路径


# 添加日志类（保持原有变量不变）
# 添加控制变量（在日志路径下方添加）
log_to_terminal = False  # 是否在终端显示日志
log_to_file = True      # 是否写入日志文件

class TeeLogger:
    """双路日志记录器，可控制输出目标"""
    def __init__(self, filename, mode='w'):
        self.terminal = sys.stdout
        self.logfile = open(filename, mode) if log_to_file else None
        
    def write(self, message):
        if log_to_terminal:
            self.terminal.write(message)
        if log_to_file and self.logfile:
            self.logfile.write(message)
            
    def flush(self):
        if log_to_terminal:
            self.terminal.flush()
        if log_to_file and self.logfile:
            self.logfile.flush()
