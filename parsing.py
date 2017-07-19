from device import*
from control import*

class Parsing(object):
    """docstring for Parsing"""
    def __init__(self, file_name):
        super(Parsing, self).__init__()
        self.file_name = file_name
        self.line_num = 0
        self.line_type = ''
        self.element_list = []
        self.control_list = {'options':[], 'output':[], 'analysis': []}
        self.handle_file(self.file_name)

    def handle_file(self, file_name):
        file_handle = open(file_name, 'r')
        while 1:
            line = file_handle.readline()
            if not line: break
            if self.parsing_line(line): 
                break
        file_handle.close()

    def parsing_line(self, line):
        self.line_num += 1
        if (self.line_num==1): return 0
        line = line.strip().lower()
        line_elem = line.split()
        if not line_elem: return 0

        #element line
        if line_elem[0][0] >= 'a' and line_elem[0][0] <= 'z':
            self.line_type = 'element'
            device_type = self.type_of_elem(line_elem[0][0])
            self.element_list += [device_type(line_elem)]

        #control line
        elif line_elem[0][0] == '.':
            line_elem[0] = line_elem[0][1:]
            if line_elem[0] == 'end': 
                self.line_type = 'end'
                return 1

            self.line_type = 'control'
            ctrl_type = self.type_of_ctrl(line_elem[0])
            if line_elem[0] == 'options':
                self.control_list['options'] += [ctrl_type(line_elem)]
            elif line_elem[0] in {'print','plot','probe'}:
                self.control_list['output'] += [ctrl_type(line_elem)]
            else:
                self.control_list['analysis'] += [ctrl_type(line_elem)]

        #comment line
        elif line_elem[0][0] == '*':
            self.line_type = 'comment'

        #continuing line
        elif line_elem[0][0] == '+':
            line_elem[0] = line_elem[0][1:]
            if self.line_type == 'element':
                tmp = self.element_list[len(self.element_list)-1]
                line_elem = tmp.arg + line_elem
                self.element_list[len(self.element_list)-1] = type(tmp)(line_elem)
            elif self.line_type == 'control':
                tmp = self.control_list[len(self.control_list)-1]
                line_elem = tmp.arg + line_elem
                self.control_list[len(self.control_list)-1] = type(tmp)(line_elem)
            elif self.line_type == 'comment':
                pass

        else:
            pass

        return 0

    def type_of_elem(self, elem_name):
        DEVICE_DICT = {
            'r': Resistor,
            'c': Capacitor,
            'l': Inductor,
            'v': Voltage_Source,
            'i': Current_Source,
            'e': VCVS,
            'f': CCCS,
            'g': VCCS,
            'h': CCVS,
            'd': Diode,
            'm': MOSFET,
            'x': MEMRISTOR,
        }

        return DEVICE_DICT.get(elem_name, Device)

    def type_of_ctrl(self, ctrl_name):
        CTRL_DICT = {
            'options': Options,
            'dc': DC,
            'ac': AC,
            'tran': TRAN,
            'op': OP,
            'ic': IC,
            'print': PRINT,
            'plot': PLOT,
            'probe': PROBE,
        }

        return CTRL_DICT.get(ctrl_name, Control)
