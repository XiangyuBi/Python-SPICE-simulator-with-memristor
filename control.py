import re
from stamp import*
import matplotlib.pyplot as plt
import numpy as np


class Control(object):
    """docstring for Control"""
    def __init__(self, arg):
        super(Control, self).__init__()
        self.arg = arg
        self.get_para()

    def get_para(self):
        self.name = self.arg[0]
        self.para = self.arg[1:]


class Options(Control):
    """docstring for Options"""
    def __init__(self, arg):
        super(Options, self).__init__(arg)
        self.parse_para(*self.para)

    def parse_para(self):
        self.method = 'be'
        self.LTE = 'on'


class Analysis(Control):
    """docstring for Analysis"""
    def __init__(self, arg):
        super(Analysis, self).__init__(arg)

    def get_value(self, char):
        units_list = {
            'meg': 'e6',
            'k': 'e3',
            'm': 'e-3',
            'u': 'e-6',
            'n': 'e-9',
            'p': 'e-12',
            'f': 'e-15',
        }
        if re.match('^[\d\.]+$',char):
            return eval(char)
        else:
            unit = re.match('^[\d\.]+(meg|k|m|u|n|p|f)$', char)
            if unit:
                char = re.sub('(meg|k|m|u|n|p|f)$', units_list.get(unit.group(1)), char)
                return eval(char)
            else:
                print 'The value is wrong!!!'
                return 0

class Output(Control):
    """docstring for Output"""
    def __init__(self, arg):
        super(Output, self).__init__(arg)


class DC(Analysis):
    """docstring for DC"""
    def __init__(self, arg):
        super(DC, self).__init__(arg)
        self.parse_para()

    def parse_para(self):
        self.src1 = self.para[0]
        self.start1 = self.get_value(self.para[1])
        self.stop1 = self.get_value(self.para[2])
        self.incr1 = self.get_value(self.para[3])

    def analyze(self, element_list):
        stp = Stamp(element_list)
        value = self.start1
        variety = [value]
        vi_result = np.zeros(stp.rows)
        while not value>self.stop1:
            if self.src1[0] == 'v':
                stp.stamp_elem(Voltage_Source([self.src1, '0', '0', '%f'%value]))
                if not stp.nonlinear():
                    vi_result = np.row_stack((vi_result, stp.solving_matrix_equation()))
                else:
                    vi_result = np.row_stack((vi_result, stp.VI))
                value += self.incr1
                variety += [value]
            else:
                stp.stamp_elem(Current_Source([self.src1, '0', '0', '%f'%value]))
                if not stp.nonlinear():
                    vi_result = np.row_stack((vi_result, stp.solving_matrix_equation()))
                else:
                    vi_result = np.row_stack((vi_result, stp.VI))
                value += self.incr1
                variety += [value]
        return [variety, vi_result, stp.dict_i, stp.dict_v]

class AC(Analysis):
    """docstring for AC"""
    def __init__(self, arg):
        super(AC, self).__init__(arg)
        self.parse_para()

    def parse_para(self):
        self.var_type = self.para[0]
        self.num_of_points = self.get_value(self.para[1])
        self.fstart = self.get_value(re.sub('hz$','',self.para[2]))
        self.fstop = self.get_value(re.sub('hz$','',self.para[3]))
    def analyze(self, element_list):
        stp = Stamp(element_list, self.fstart, 0)
        num = 0
        value = self.fstart * 10**(num/self.num_of_points)
        # print value
        # print self.fstart
        variety = [value]
        vi_result = np.zeros(stp.rows)
        list_of_f_device = stp.dict_f_device.items()
        while not value>self.fstop:
            
            for i in range(len(list_of_f_device)):
                stp.stamp_elem(list_of_f_device[i][1][1], 2*pi*value, 0)
            if not stp.nonlinear(2*pi*value): 
                vi_result = np.row_stack((vi_result,stp.solving_matrix_equation()))
            else:
                vi_result = np.row_stack((vi_result, stp.VI))
            # vi_result = np.row_stack((vi_result,stp.solving_matrix_equation()))
            stp.Add_Freq(value)
            value = self.fstart * 10**(1.*num/self.num_of_points)
            num += 1
            # print 1.*num/self.num_of_points
            variety += [value]
            # print value
        # print vi_result
        # print num
        # print variety
        return [variety, vi_result, stp.dict_i, stp.dict_v]

class TRAN(Analysis):
    """docstring for TRAN"""
    def __init__(self, arg):
        super(TRAN, self).__init__(arg)
        self.parse_para()

    def parse_para(self):
        self.tstep = self.get_value(re.sub('s$','',self.para[0]))
        self.tstop = self.get_value(re.sub('s$','',self.para[1]))
        if len(self.para)<3:
            self.tstart = 0
            self.tmax = min(self.tstep, (self.tstop-self.tstart)/50.0)
        else:
            self.tstart = self.get_value(re.sub('s$','', self.para[2]))
            if len(self.para)>3:
                self.tmax = min(self.tstep, self.get_value(re.sub('s$', '', self.para[3])))
            else:
                self.tmax = min(self.tstep, (self.tstop-self.tstart)/50.0)
    def analyze(self, element_list):
        stp = Stamp(element_list, 0, self.tmax)
        time = self.tstart
        variety = [time]
        #vi_result = np.zeros(stp.rows-1)
        #vi_result = np.row_stack((vi_result, stp.VI))
        vi_result = np.row_stack((stp.VI, stp.VI))
        list_of_t_device = stp.dict_t_device.items()
        step = self.tmax

        #LTE-TR
        if stp.method == 'tr' and stp.lte_on == 'on':
            while not time>self.tstop:
                stp.Add_Time(step)
                for i in range(len(list_of_t_device)):
                    stp.stamp_elem(list_of_t_device[i][1][1], 0, step)
                if not stp.nonlinear():
                    #no nonlinear device
                    stp.solving_matrix_equation()
                VI_tmp = stp.VI

                stp.Add_Time(step)
                for i in range(len(list_of_t_device)):
                    stp.stamp_elem(list_of_t_device[i][1][1], 0, step)
                if not stp.nonlinear():
                    #no nonlinear device
                    stp.solving_matrix_equation()

                if not stp.Less_Than_LTE_TR(step, step, stp.VI, VI_tmp, vi_result[-1]):
                    # change step and restart
                    stp.Add_Time(-2*step)
                    step = step/2.
                    stp.VI = vi_result[-1]
                else:
                    stp.Add_Time(-step)
                    vi_result = np.row_stack((vi_result, VI_tmp))
                    stp.VI = VI_tmp
                    time += step
                    variety += [time]
                    step = min(self.tmax, 2.*step)

        #LTE-BE
        else:
            while not time>self.tstop:
                stp.Add_Time(step)
                for i in range(len(list_of_t_device)):
                    stp.stamp_elem(list_of_t_device[i][1][1], 0, step)
                if not stp.nonlinear():
                    #no nonlinear device
                    stp.solving_matrix_equation()

                if stp.method == 'tr':
                    flag = 1
                elif stp.method == 'be' and stp.lte_on == 'off':
                    flag = 1
                elif stp.method == 'be' and stp.lte_on == 'on':
                    flag = stp.Less_Than_LTE_BE(step, stp.VI, vi_result[-1])


                if not flag:
                    # change step and restart
                    stp.Add_Time(-step)
                    step = step/2.
                    stp.VI = vi_result[-1]
                else:
                    vi_result = np.row_stack((vi_result, stp.VI))
                    time += step
                    variety += [time]
                    step = min(self.tmax, 2.*step)
        # tmp += [variety, vi_result[1:], stp.dict_i, stp.dict_v]
        # return tmp
        return [variety, vi_result[1:], stp.dict_i, stp.dict_v]

class OP(Analysis):
    """docstring for OP"""
    def __init__(self, arg):
        super(OP, self).__init__(arg)

class IC(Analysis):
    """docstring for IC"""
    def __init__(self, arg):
        super(IC, self).__init__(arg)


class PRINT(Output):
    """docstring for PRINT"""
    def __init__(self, arg):
        super(PRINT, self).__init__(arg)
        self.index = []
        self.d_name = []
        self.parse_para()
        self.type_ac = {
            'r': np.real,
            'i': np.imag,
            'm': np.abs,
            'p': np.angle,
            'db': np.abs,
        }

    def parse_para(self):
        self.analysis_type = self.para[0]
        if self.analysis_type == 'dc' or self.analysis_type == 'tran':
            for i in range(len(self.para[1:])):
                i += 1
                if re.match('^v\(\d+\)$', self.para[i]):
                    self.index += [[eval(re.match('^v\((\d+)\)$', self.para[i]).group(1)), self.para[i]]]
                elif re.match('^v\(\d+[,]\d+\)$', self.para[i]):
                    index_1 = eval(re.match('^v\((\d+),(\d+)\)$', self.para[i]).group(1))
                    index_2 = eval(re.match('^v\((\d+),(\d+)\)$', self.para[i]).group(2))
                    self.index += [[(index_1, index_2), self.para[i]]]
                elif re.match('^i\((\w+)\)$', self.para[i]):
                    self.d_name += [re.match('^i\((\w+)\)$', self.para[i]).group(1)]
        elif self.analysis_type == 'ac':
            for i in range(len(self.para[1:])):
                i += 1
                if re.match('^v(r|i|m|p|db)\(\d+\)$', self.para[i]):
                    tmp = re.match('^v(r|i|m|p|db)\((\d+)\)$', self.para[i])
                    self.index += [[eval(tmp.group(2)), self.para[i], tmp.group(1)]]
                elif re.match('^v(r|i|m|p|db)\(\d+[,]\d+\)$', self.para[i]):
                    tmp = re.match('^v(r|i|m|p|db)\((\d+),(\d+)\)$', self.para[i])
                    index_1 = eval(tmp.group(2))
                    index_2 = eval(tmp.group(3))
                    self.index += [[(index_1, index_2), self.para[i], tmp.group(1)]]
                elif re.match('^v\(\d+\)$', self.para[i]):
                    self.index += [[eval(re.match('^v\((\d+)\)$', self.para[i]).group(1)), self.para[i], 'm']]
                elif re.match('^v\(\d+[,]\d+\)$', self.para[i]):
                    index_1 = eval(re.match('^v\((\d+),(\d+)\)$', self.para[i]).group(1))
                    index_2 = eval(re.match('^v\((\d+),(\d+)\)$', self.para[i]).group(2))
                    self.index += [[(index_1, index_2), self.para[i], 'm']]
                elif re.match('^i\((\w+)\)$', self.para[i]):
                    self.d_name += [[re.match('^i\((\w+)\)$', self.para[i]).group(1), 'm']]
                elif re.match('^i(r|i|m|p|db)\((\w+)\)$', self.para[i]):
                    tmp = re.match('^i\((\w+)\)$', self.para[i])
                    self.d_name += [[tmp.group(2), tmp.group(1)]]

    def show_result(self, result):
        print self.d_name, 'd_name',result
        plt.figure(1)
    #result = [variety, vi_result, stp.dict_i, stp.dict_v]
        plt.figure(1)
        plt.plot()
        left = plt.subplot()
        if self.analysis_type == 'dc':
            left.set_title('DC Transfer Analysis')
            plt.xlabel('V(V)')
        elif self.analysis_type == 'tran':
            left.set_title('Transient Analysis')
            plt.xlabel('T(s)')
        elif self.analysis_type == 'ac':
            left.set_title('AC Transfer Analysis')
            plt.xlabel('f(Hz)')
        if not self.index:
            right = left
        else:
            #plot in left axies
            if self.analysis_type == 'dc' or self.analysis_type == 'tran':
                for i in range(len(self.index)):
                    if type(self.index[i][0]) == int:
                        left.plot(result[0][:-1], result[1][1:, self.index[i][0]], '-', label = self.index[i][1])
                        # left.plot(result[0][:-1], result[1][1:, self.index[i][0]].imag, '-', label = self.index[i][1])
                        # left.plot(result[4][:-1], result[5][1:, self.index[i][0]], '-r', label = self.index[i][1]+' withoutLTE')
                    elif type(self.index[i][0]) == tuple:
                        left.plot(result[0][:-1], result[1][1:, self.index[i][0][0]]-result[1][1:, self.index[i][0][1]], '-', label = self.index[i][1])
                plt.ylabel('V(V)')
                # plt.ylim(0,3.1)
                if not self.d_name:
                    left.legend(loc=1)
                else:
                    left.legend(loc=2)
                    right = left.twinx()
            elif self.analysis_type == 'ac':
                for i in range(len(self.index)):
                    func = self.type_ac.get(self.index[i][-1])
                    if type(self.index[i][0]) == int:
                        if self.index[i][-1]=='p':
                            y_value = func(result[1][1:, self.index[i][0]], deg=True)
                        else:
                            y_value = func(result[1][1:, self.index[i][0]])
                        if self.index[i][-1]=='db':
                            y_value = 20*np.log10(y_value)
                        
                        # print y_value

                        left.semilogx(result[0][:-1], y_value, '-', label = self.index[i][1])
                        # left.plot(result[0][:-1], result[1][1:, self.index[i][0]].imag, '-', label = self.index[i][1])
                        # left.plot(result[4][:-1], result[5][1:, self.index[i][0]], '-r', label = self.index[i][1]+' withoutLTE')
                    elif type(self.index[i][0]) == tuple:
                        y_value = func(result[1][1:, self.index[i][0][0]]-result[1][1:, self.index[i][0][1]])
                        if self.index[-1]=='db':
                            y_value = 20*np.log10(y_value)
                        left.semilogx(result[0][:-1], y_value, '-', label = self.index[i][1])
                plt.ylabel('V(V)')
                if not self.d_name:
                    left.legend(loc=1)
                else:
                    left.legend(loc=2)
                    right = left.twinx()

        if self.d_name:
            if self.analysis_type == 'dc' or self.analysis_type == 'tran':
                for i in range(len(self.d_name)):
                   # print self.d_name,result
                    if result[2].has_key(self.d_name[i]):
                       # print self.d_name[i]
                        right.plot(result[0][:-1], result[1][1:, result[2][self.d_name[i]]], '-',color='red',label =('i(%s)'%self.d_name[i]))
                    elif result[3].has_key(self.d_name[i]):
                        right.plot(result[0][:-1], (result[1][1:, result[3][self.d_name[i]][0]]-result[1][1:, result[3][self.d_name[i]][1]])/result[3][self.d_name[i]][2], '-', label = ('i(%s)'%self.d_name[i]))
                right.legend(loc=1)
                plt.ylabel('I(A)')
            if self.analysis_type == 'ac':
                for i in range(len(self.d_name)):
                    func = self.type_ac.get(self.d_name[i][-1])
                    if result[2].has_key(self.d_name[i][0]):
                        if self.index[i][-1]=='p':
                            y_value = func(result[1][1:, result[2][self.d_name[i][0]]], deg=True)
                        else:
                            y_value = func(result[1][1:, result[2][self.d_name[i][0]]])
                        if self.d_name[i][-1] == 'db':
                            y_value = 20*np.log10(y_value)
                        right.semilogx(result[0][:-1], y_value, '-',label =('i(%s)'%self.d_name[i][0]))    
                    elif result[3].has_key(self.d_name[i][0]):
                        y_value = func((result[1][1:, result[3][self.d_name[i][0]][0]]-result[1][1:, result[3][self.d_name[i][0]][1]])/result[3][self.d_name[i][0]][2])
                        if self.d_name[i][-1] == 'db':
                            y_value = 20*np.log10(y_value)
                        right.semilogx(result[0][:-1], y_value, '-', label = ('i(%s)'%self.d_name[i]))
                right.legend(loc=1)
                plt.ylabel('I(A)')
        plt.show()

        for i in range(len(self.d_name)):
           # print self.d_name
            if self.d_name[i][0]== 'x':
               # print 'plot'
                #fig2 = plt.figure(2)
             #   print result[3]
                mem = plt.subplot()
                mem.plot((result[1][1:, result[3][self.d_name[i]][0]]-result[1][1:, result[3][self.d_name[i]][1]]),result[1][1:, result[2][self.d_name[i]]],)
                plt.xlabel('V(V)')
                plt.ylabel('I(A)')
                mem.set_title('memristor')
                plt.show()


class PLOT(Output):
    """docstring for PLOT"""
    def __init__(self, arg):
        super(PLOT, self).__init__(arg)

class PROBE(Output):
    """docstring for PROBE"""
    def __init__(self, arg):
        super(PROBE, self).__init__(arg)
        self.parse_para()

    def parse_para(self):
        pass
