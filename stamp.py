import numpy as np
from device import*
import matplotlib.pyplot as plt

class Stamp(object):
    """docstring for Stamp"""
    def __init__(self, element_list, s=0, h=0):
        super(Stamp, self).__init__()
        self.method = 'be'
        self.lte_on = 'on'
        self.MAX_ITERATIONS = 300
        self.element_list = element_list
        self.rows = 0
        self.omega = 0      #used for ac anylasis
        self.runtime = 0    #used for tran anylasis
        self.dict_i = {}    #record the row of the device which current is unknown in the maxtrix
        self.dict_v = {}    #record the value of the device to calculate current
        self.dict_t_device = {}    #record the row of t_device for tran analysis
        self.dict_f_device = {}
        self.dict_nl_device = {}    #dict of nonlin device
        # self.testtmp = []
        self.init_state = 0 #when init_state==1, initial is over
        self.initial_matrix(s, h)

        #self.solving_matrix_equation()

    #search in element_list to find vc (ccvs, cccs)
    def search_v(self, name):   
        for i in range(len(self.element_list)):
            if self.element_list[i].name == name:
                return self.element_list[i]

    #cheak if vc has been stamped (ccvs, cccs, voltage_source)
    def check_v(self, name):
        if self.dict_i.has_key(name):
            return self.dict_i[name]
        else:
            self.dict_i[name] = self.rows
            return 0

    def check_f_device(self, elem):
        if self.dict_f_device.has_key(elem.name):
            return self.dict_f_device[elem.name][0]
        else:
            self.dict_f_device[elem.name] = [self.rows, elem]
            return 0

    def check_t_device(self, elem):
        #dict_t_device={'name':[row, elem]}
        if self.dict_t_device.has_key(elem.name):
            return self.dict_t_device[elem.name][0]
        else:
            self.dict_t_device[elem.name] = [self.rows, elem]
            return 0

    def check_nonlin(self, elem):
        if self.dict_nl_device.has_key(elem.name):
            return 1
        else:
            self.dict_nl_device[elem.name] = elem
            return 0

    def add_to_dict_v(self, elem):
        if self.dict_v.has_key(elem.name):
            return 1
        else:
            self.dict_v[elem.name] = [elem.n1, elem.n2, elem.value]
            return 0
    #get the num of nodes
    def get_num_of_nodes(self):
        num_of_nodes = 0
        for i in range(len(self.element_list)):
            num_of_nodes = max(self.element_list[i].max_node(), num_of_nodes)
        return num_of_nodes

    #solve matrix equation: a*x=b --> x
    def solving_matrix_equation(self, mode=0):
        if not mode:
            # print self.MNA
            # print self.RHS
            # raw_input()
            try:
                self.VI = np.linalg.solve(self.MNA[1:,1:], self.RHS[1:])
            except:
                self.VI = np.linalg.lstsq(self.MNA[1:,1:], self.RHS[1:])[0]
            self.VI = np.append(np.zeros(1), self.VI)
        else:
            a = np.zeros((self.rows, self.rows), dtype = self.MNA_for_nl.dtype)
            b = np.zeros(self.rows, dtype = self.MNA_for_nl.dtype)
            a[:len(self.MNA_for_nl), :len(self.MNA_for_nl)] = self.MNA_for_nl + self.MNA[:len(self.MNA_for_nl), :len(self.MNA_for_nl)]
            b[:len(self.RHS_for_nl)] = self.RHS_for_nl + self.RHS[:len(self.RHS_for_nl)]
            a[len(self.MNA_for_nl):] = self.MNA[len(self.MNA_for_nl):]
            a[:,len(self.MNA_for_nl):] = self.MNA[:,len(self.MNA_for_nl):]
            b[len(self.RHS_for_nl):] = self.RHS[len(self.RHS_for_nl):]

            try:
                self.VI = np.linalg.solve(a[1:,1:], b[1:])
            except:
                self.VI = np.linalg.lstsq(a[1:,1:], b[1:])[0]
            self.VI = np.append(np.zeros(1), self.VI)   #voltage of node 0
        return self.VI

    def initial_matrix(self, s=0, h=0):
        self.rows = self.get_num_of_nodes() + 1
        if s==0:
            self.MNA = np.zeros((self.rows, self.rows))
            self.RHS = np.zeros(self.rows)
            self.MNA_for_nl = np.zeros((self.rows, self.rows))
            self.RHS_for_nl = np.zeros(self.rows)
        else:
            self.MNA = np.zeros((self.rows, self.rows), dtype=complex)
            self.RHS = np.zeros(self.rows, dtype=complex)
            self.MNA_for_nl = np.zeros((self.rows, self.rows), dtype=complex)
            self.RHS_for_nl = np.zeros(self.rows, dtype=complex)
        for i in range(len(self.element_list)):
            elem = self.element_list[i]
            self.stamp_elem(elem, s, h)

        if not self.nonlinear():
            self.solving_matrix_equation()

        self.init_state = 1
        print self.MNA,self.RHS
        return

    def Less_Than_LTE_BE(self, h, VI_next, VI_current):
        list_t_device = self.dict_t_device.items()
        for i in range(len(list_t_device)):
            if list_t_device[i][1][1].name[0]=='c':
                I_next = VI_next[list_t_device[i][1][0]]
                I_current = VI_current[list_t_device[i][1][0]]
                if list_t_device[i][1][1].BE_LTE(h, I_next, I_current):
                    return 0
            elif list_t_device[i][1][1].name[0]=='l':
                V_next = VI_next[list_t_device[i][1][1].n1] - VI_next[list_t_device[i][1][1].n2]
                V_current = VI_current[list_t_device[i][1][1].n1] - VI_current[list_t_device[i][1][1].n2]
                if list_t_device[i][1][1].BE_LTE(h, V_next, V_current):
                    return 0
        return 1

    def Less_Than_LTE_TR(self, h1, h2, VI_after_next, VI_next, VI_current):
        list_t_device = self.dict_t_device.items()
        for i in range(len(list_t_device)):
            if list_t_device[i][1][1].name[0] == 'c':
                I_after_next = VI_after_next[list_t_device[i][1][0]]
                I_next = VI_next[list_t_device[i][1][0]]
                I_current = VI_current[list_t_device[i][1][0]]
                if list_t_device[i][1][1].TR_LTE(h1, h2, I_after_next, I_next, I_current):
                    return 0
            elif list_t_device[i][1][1].name[0] == 'l':
                V_after_next = VI_after_next[list_t_device[i][1][0]]
                V_next = VI_next[list_t_device[i][1][0]]
                V_current = VI_current[list_t_device[i][1][0]]
                if list_t_device[i][1][1].TR_LTE(h1, h2, V_after_next, V_next, V_current):
                    return 0
        return 1


    def Add_Time(self, step):
        self.runtime += step
        return

    def Add_Freq(self, s):
        self.omega = s
        return

    def nonlinear(self, s=0):
        #list_nl_device = [[elem.name, elem],...,..]
        list_nl_device = self.dict_nl_device.items()
        if not list_nl_device:
            return 0

        self.solving_matrix_equation(1)
        self.MNA_for_nl = np.zeros((self.rows,self.rows), dtype = self.MNA_for_nl.dtype)
        self.RHS_for_nl = np.zeros(self.rows, dtype=self.MNA_for_nl.dtype)
        IerationTime = 0
        while 1:
            VI_last = self.VI
            flag = 1
            for i in range(len(list_nl_device)):
                self.stamp_elem(list_nl_device[i][1], s)
            self.solving_matrix_equation(1)
            for i in range(len(list_nl_device)):
                flag *= list_nl_device[i][1].convergence(self.VI, VI_last)
            if flag:
                IerationTime = 0
                break
            IerationTime+=1
            if IerationTime >= self.MAX_ITERATIONS:
                IerationTime = 0
                break
            self.MNA_for_nl = np.zeros((self.rows,self.rows), dtype=self.MNA_for_nl.dtype)
            self.RHS_for_nl = np.zeros(self.rows, dtype=self.MNA_for_nl.dtype)
        # plt.plot(self.testtmp, np.zeros(len(self.testtmp)),'o')
        # x = np.linspace(0, 0.11, 100)
        # #plt.plot(x,x)
        # plt.plot(x, 0.5*x-3./2+np.exp(40*x))

        # for i in range(len(self.testtmp)):
        #     plt.plot(x, (0.5+40*np.exp(40*self.testtmp[i]))*(x-self.testtmp[i])+0.5*self.testtmp[i]-3./2+np.exp(40*self.testtmp[i]),'--')
        # #plt.plot(x, 0.5+40*np.exp(40*x))
        # plt.ylim(0,90)
        # plt.show()
        return 1

        
    def stamp_elem(self, elem, s=0, h=0):
        if isinstance(elem, Resistor):
            self.add_to_dict_v(elem)
            self.MNA[elem.n1, elem.n1] += 1./elem.value
            self.MNA[elem.n1, elem.n2] -= 1./elem.value
            self.MNA[elem.n2, elem.n1] -= 1./elem.value
            self.MNA[elem.n2, elem.n2] += 1./elem.value




        elif isinstance(elem, Current_Source):
            if self.init_state == 0:
                self.check_t_device(elem)

                if not self.add_to_dict_v(elem):
                    self.RHS[elem.n1] -= elem.value
                    self.RHS[elem.n2] += elem.value
                # else:
                #     para = self.dict_v[elem.name]   #[n1,n2,value]
                #     self.RHS[para[0]] -= elem.value - para[2]    #dc value change
                #     self.RHS[para[1]] += elem.value - para[2]    #dc value change

            elif self.init_state == 1:
                if s!=0:
                    pass
                elif h!=0:
                    value_t = elem.value_var_t(h, self.runtime)
                    self.RHS[elem.n1] -= value_t    #tran: ac value change
                    self.RHS[elem.n2] += value_t    #tran: ac value change
                else:
                    para = self.dict_v[elem.name]   #[n1,n2,value]
                    self.RHS[para[0]] -= elem.value - para[2]    #dc value change
                    self.RHS[para[1]] += elem.value - para[2]    #dc value change
                    para[2] = elem.value

        elif isinstance(elem, Voltage_Source):
            if self.init_state == 0:
                if not self.check_v(elem.name):
                    self.check_f_device(elem)
                    self.check_t_device(elem)
                    self.MNA = np.column_stack((self.MNA, np.zeros(self.rows)))
                    self.rows += 1
                    self.MNA = np.row_stack((self.MNA, np.zeros(self.rows)))
                    self.RHS = np.append(self.RHS, np.zeros(1))
                    self.MNA[elem.n1, self.rows-1] = 1
                    self.MNA[elem.n2, self.rows-1] = -1
                    self.MNA[self.rows-1, elem.n1] = 1
                    self.MNA[self.rows-1, elem.n2] = -1
                    self.RHS[self.rows-1] = elem.value + elem.value_var_t(0)
                else:
                    vc_row = self.dict_i[elem.name]
                    self.dict_t_device[elem.name] = [vc_row, elem]
                    self.dict_f_device[elem.name] = [vc_row, elem]
                    self.RHS[vc_row] = elem.value + elem.value_var_t(0)

            elif self.init_state == 1:
                vc_row = self.dict_i[elem.name]

                if h!=0:
                    self.RHS[vc_row] = elem.value + elem.value_var_t(h, self.runtime)
                elif s!=0:
                    self.RHS[vc_row] = elem.value_f
                else:
                    self.RHS[vc_row] = elem.value

        elif isinstance(elem, VCVS):
            #br-VS: add row and column
            self.check_v(elem.name)

            self.MNA = np.column_stack((self.MNA, np.zeros(self.rows)))
            self.rows += 1
            self.MNA = np.row_stack((self.MNA, np.zeros(self.rows)))

            self.MNA[elem.n1, self.rows-1] += 1
            self.MNA[elem.n2, self.rows-1] -= 1
            self.MNA[self.rows-1, elem.n1] += 1
            self.MNA[self.rows-1, elem.n2] -= 1
            self.MNA[self.rows-1, elem.n3] -= elem.value
            self.MNA[self.rows-1, elem.n4] += elem.value
        elif isinstance(elem, CCCS):
            #br-VC: check if it has been stamped! if not, add row and column.
            if not self.check_v(elem.v_name):
                vc_row = self.dict_i[elem.name]
                self.MNA = np.column_stack((self.MNA, np.zeros(self.rows)))
                self.rows += 1
                self.MNA = np.row_stack((self.MNA, np.zeros(self.rows)))
                self.RHS = np.append((self.RHS, np.zeros(1)))

                elem_v = self.search_v(elem.v_name)
                self.MNA[elem.n1, self.rows-1] += elem.value
                self.MNA[elem.n2, self.rows-1] -= elem.value
                self.MNA[elem_v.n1, self.rows-1] += 1
                self.MNA[elem_v.n2, self.rows-1] -= 1
                self.MNA[self.rows-1, elem_v.n1] += 1
                self.MNA[self.rows-1, elem_v.n2] -= 1
                self.RHS[self.rows-1] = elem_v.value  
            else:
                self.MNA[elem.n1, vc_row] += elem.value
                self.MNA[elem.n2, vc_row] -= elem.value
        elif isinstance(elem, VCCS):
            self.add_to_dict_v(elem)
            self.MNA[elem.n1, elem.n3] += elem.value
            self.MNA[elem.n1, elem.n4] -= elem.value
            self.MNA[elem.n2, elem.n3] -= elem.value
            self.MNA[elem.n2, elem.n4] += elem.value
        elif isinstance(elem, CCVS):
            #br-vs: add row and column
            self.check_v(elem.name)
            self.MNA = np.column_stack((self.MNA, np.zeros(self.rows)))
            self.rows += 1
            self.MNA = np.row_stack((self.MNA, np.zeros(self.rows)))
            self.RHS = np.append(self.RHS, np.zeros(1))

            self.MNA[elem.n1, self.rows-1] = 1
            self.MNA[elem.n2, self.rows-1] = -1
            self.MNA[self.rows-1, elem.n1] = 1
            self.MNA[self.rows-1, elem.n2] = -1

            #br-VC: check if it has been stamped? if not, add row and column.
            

            if not self.check_v(elem.v_name):
                vc_row = self.dict_i[elem.name]
                self.MNA = np.column_stack((self.MNA, np.zeros(self.rows)))
                self.rows += 1
                self.MNA = np.row_stack((self.MNA, np.zeros(self.rows)))
                self.RHS = np.append(self.RHS, np.zeros(1))

                elem_v = self.search_v(elem.v_name)
                self.MNA[elem_v.n1, self.rows-1] = 1
                self.MNA[elem_v.n2, self.rows-1] = -1
                self.MNA[self.rows-1, elem_v.n1] = 1
                self.MNA[self.rows-1, elem_v.n2] = -1
                self.MNA[self.rows-2, self.rows-1] -= elem.value
                self.RHS[self.rows-1] = elem_v.value
            else:
                self.MNA[self.rows, vc_row] -= elem.value
        elif isinstance(elem, Capacitor):
            if self.init_state == 0:
                self.check_v(elem.name)
                self.check_f_device(elem)
                self.check_t_device(elem)

                if s==0:
                #to calculate current and voltage when t=0
                    self.MNA = np.column_stack((self.MNA, np.zeros(self.rows)))
                    self.rows += 1
                    self.MNA = np.row_stack((self.MNA, np.zeros(self.rows)))
                    self.RHS = np.append(self.RHS, np.zeros(1))

                    self.MNA[self.rows-1, self.rows-1] = 1
                else:
                    pass

            elif self.init_state == 1:
                if h!=0:
                    c_row = self.check_t_device(elem)
                    #using TR:trapezoidal rule
                    #2*C/h*V(t) - I(t) = 2*C/h*V(t-h) + I(t-h)
                    if self.method == 'tr':
                        self.MNA[elem.n1, c_row] = 1
                        self.MNA[elem.n2, c_row] = -1
                        self.MNA[c_row, elem.n1] = 2.*elem.value/h
                        self.MNA[c_row, elem.n2] = -2.*elem.value/h
                        self.MNA[c_row, c_row] = -1
                        self.RHS[c_row] = 2.*elem.value/h*(self.VI[elem.n1] - self.VI[elem.n2]) + self.VI[c_row]

                    #using be
                    elif self.method == 'be':
                        self.MNA[elem.n1, c_row] = 1
                        self.MNA[elem.n2, c_row] = -1
                        self.MNA[c_row, elem.n1] = 1.*elem.value/h
                        self.MNA[c_row, elem.n2] = -1.*elem.value/h
                        self.MNA[c_row, c_row] = -1
                        self.RHS[c_row] = 1.*elem.value/h*(self.VI[elem.n1] - self.VI[elem.n2])   
            
                if s!=0:
                    self.MNA = self.MNA.astype(complex)
                    self.MNA[elem.n1, elem.n1] += 1j*(s-self.omega)*elem.value
                    self.MNA[elem.n1, elem.n2] -= 1j*(s-self.omega)*elem.value
                    self.MNA[elem.n2, elem.n1] -= 1j*(s-self.omega)*elem.value
                    self.MNA[elem.n2, elem.n2] += 1j*(s-self.omega)*elem.value

# add w as a new variable, the 'check_v' function needs to be taken into consideration
        elif isinstance(elem, MEMRISTOR):
            if self.init_state == 0:
                if s == 0:
                  self.add_to_dict_v(elem)
                  self.check_v(elem.name)
                  self.check_f_device(elem)
                  self.check_t_device(elem)
                  self.MNA = np.column_stack((self.MNA, np.zeros(self.rows)))
                  self.RHS = np.append(self.RHS, np.zeros(1))
                  self.rows += 1
                  self.MNA = np.row_stack((self.MNA, np.zeros(self.rows)))

                  self.MNA = np.column_stack((self.MNA, np.zeros(self.rows)))
                  self.RHS = np.append(self.RHS, np.zeros(1))
                  self.rows += 1
                  self.MNA = np.row_stack((self.MNA, np.zeros(self.rows)))
                #  print 1
                else :
                    pass

                self.MNA[elem.n1, self.rows-2] = 1
                self.MNA[elem.n2, self.rows-2] = -1
                self.MNA[self.rows-2, elem.n1] = 1./elem.Rinit
                self.MNA[self.rows-2, elem.n2] = -1./elem.Rinit
                self.MNA[self.rows-2, self.rows-2] = -1.
                self.MNA[self.rows-1, self.rows-1] = 1.
                self.RHS[self.rows-1] = elem.w_init
            elif self.init_state == 1:
                if h != 0:
                    x_row = self.check_t_device(elem)
                    if self.method == 'be':
                        print self.VI[x_row+1]
                        if self.VI[x_row] >= 0.:
                         #  print self.VI[x_row],self.VI[x_row+1]
                           if 0.<=self.VI[x_row+1]<=1.:
                              self.MNA[x_row,elem.n1] = 1./elem.memristance(self.VI[x_row+1])
                              self.MNA[x_row,elem.n2] = -1./elem.memristance(self.VI[x_row+1])
                              self.MNA[x_row+1,x_row+1] = 1
                              self.RHS[x_row+1] = self.VI[x_row+1] + elem.caculate_F(self.VI[elem.n1]-self.VI[elem.n2], self.VI[x_row+1],h,1)
                           #   print self.VI[x_row],self.VI[x_row+1]
                           elif self.VI[x_row+1] < 0.:
                              self.VI[x_row+1] = 0.
                              self.MNA[x_row,elem.n1] = 1./elem.memristance(0.)
                              self.MNA[x_row,elem.n2] = -1./elem.memristance(0.)
                              self.MNA[x_row+1,x_row+1] = 1
                              self.RHS[x_row+1] = elem.caculate_F(self.VI[elem.n1]-self.VI[elem.n2], self.VI[x_row+1],h,1)
                           elif self.VI[x_row+1] > 1.:
                              self.VI[x_row+1] = 1.
                              self.MNA[x_row, elem.n1] = 1. / elem.memristance(1.)
                              self.MNA[x_row, elem.n2] = -1. / elem.memristance(1.)
                              self.MNA[x_row + 1, x_row + 1] = 1
                              self.RHS[x_row + 1] = 1. + elem.caculate_F(self.VI[elem.n1]-self.VI[elem.n2], self.VI[x_row+1], h,1)
                              #print self.VI[x_row], self.VI[x_row + 1], self.VI[elem.n1] - self.VI[elem.n2], elem.memristance(self.VI[x_row + 1])
                              # print elem.constan, elem.ux, elem.D, elem.Ron
                        elif self.VI[x_row] < 0:
                           if 0.<=self.VI[x_row+1]<=1.:
                              self.MNA[x_row,elem.n1] = 1./elem.memristance(self.VI[x_row+1])
                              self.MNA[x_row,elem.n2] = -1./elem.memristance(self.VI[x_row+1])
                              self.MNA[x_row+1,x_row+1] = 1
                              self.RHS[x_row+1] = self.VI[x_row+1] + elem.caculate_F(self.VI[elem.n1]-self.VI[elem.n2], self.VI[x_row+1],h,0)
                           #   print self.VI[x_row],self.VI[x_row+1]
                           elif self.VI[x_row+1] < 0.:
                              self.VI[x_row+1] = 0.
                              self.MNA[x_row,elem.n1] = 1./elem.memristance(0.)
                              self.MNA[x_row,elem.n2] = -1./elem.memristance(0.)
                              self.MNA[x_row+1,x_row+1] = 1
                              self.RHS[x_row+1] = elem.caculate_F(self.VI[elem.n1]-self.VI[elem.n2], self.VI[x_row+1],h,0)
                           elif self.VI[x_row+1] > 1.:
                              self.VI[x_row+1] = 1.
                              self.MNA[x_row, elem.n1] = 1. / elem.memristance(1.)
                              self.MNA[x_row, elem.n2] = -1. / elem.memristance(1.)
                              self.MNA[x_row + 1, x_row + 1] = 1
                              self.RHS[x_row + 1] = 1. + elem.caculate_F(self.VI[elem.n1]-self.VI[elem.n2], self.VI[x_row+1], h,0)




                    elif self.method == 'tr':
                        if 0.<=self.VI[x_row+1]<=1.:
                            self.MNA[x_row,elem.n1] = 1./elem.memristance(self.VI[x_row+1])
                            self.MNA[x_row,elem.n2] = -1./elem.memristance(self.VI[x_row+1])
                            self.MNA[x_row+1,x_row+1] = 1.
                            self.MNA[x_row+1,x_row] = -0.5*elem.constan*h
                            self.RHS[x_row+1] = self.VI[x_row+1] + elem.constan*h*self.VI[x_row]*0.5
                            print self.VI[x_row], self.VI[x_row + 1],self.VI[elem.n1]-self.VI[elem.n2], elem.memristance(self.VI[x_row+1])
                        elif self.VI[x_row+1] >1.:
                            self.MNA[x_row, elem.n1] = 1. / elem.memristance(1.)
                            self.MNA[x_row, elem.n2] = -1. / elem.memristance(1.)
                            self.MNA[x_row + 1, x_row + 1] = 1.
                            self.MNA[x_row + 1, x_row] = -0.5 * elem.constan * h
                            self.RHS[x_row + 1] = 1. + elem.constan * h * self.VI[x_row] * 0.5
                        elif self.VI[x_row+1] < 0.:
                            self.MNA[x_row, elem.n1] = 1. / elem.memristance(0.)
                            self.MNA[x_row, elem.n2] = -1. / elem.memristance(0.)
                            self.MNA[x_row + 1, x_row + 1] = 1.
                            self.MNA[x_row + 1, x_row] = -0.5 * elem.constan * h
                            self.RHS[x_row + 1] = elem.constan * h * self.VI[x_row] * 0.5



        elif isinstance(elem, Inductor):
            #add row and column
            if self.init_state == 0:
                self.check_v(elem.name)
                self.check_f_device(elem)
                self.check_t_device(elem)
                self.MNA = np.column_stack((self.MNA, np.zeros(self.rows)))
                self.rows += 1
                self.MNA = np.row_stack((self.MNA, np.zeros(self.rows)))
                self.RHS = np.append(self.RHS, np.zeros(1))

                self.MNA[elem.n1, self.rows-1] = 1
                self.MNA[elem.n2, self.rows-1] = -1
                self.MNA[self.rows-1, elem.n1] = 1
                self.MNA[self.rows-1, elem.n2] = -1


            elif self.init_state == 1:
                if h!=0:
                    l_row = self.check_t_device(elem)
                    #using TR:trapezoidal rule
                    #V(t)-2L/h*I(t) = -2L/h*I(t-h) - V(t-h)
                    if self.method == 'tr':
                        self.MNA[l_row, l_row] = -2.*elem.value/h
                        self.RHS[l_row] = -2.*elem.value/h*self.VI[l_row] - (self.VI[elem.n1] - self.VI[elem.n2])

                    #using be
                    elif self.method == 'be':
                        self.MNA[l_row, l_row] = -1.*elem.value/h
                        self.RHS[l_row] = -1.*elem.value/h*self.VI[l_row]

                if s!=0:
                    l_row = self.check_f_device(elem)
                        # print s
                    self.MNA[l_row, l_row] = -1j*s*elem.value


        elif isinstance(elem, Diode):
            #nonlinear
            if self.check_nonlin(elem):
                self.MNA_for_nl[elem.n1, elem.n1] += elem.Gn(self.VI[elem.n1] - self.VI[elem.n2])
                self.MNA_for_nl[elem.n1, elem.n2] -= elem.Gn(self.VI[elem.n1] - self.VI[elem.n2])
                self.MNA_for_nl[elem.n2, elem.n1] -= elem.Gn(self.VI[elem.n1] - self.VI[elem.n2])
                self.MNA_for_nl[elem.n2, elem.n2] += elem.Gn(self.VI[elem.n1] - self.VI[elem.n2])
                self.RHS_for_nl[elem.n1] -= elem.In(self.VI[elem.n1] - self.VI[elem.n2])
                self.RHS_for_nl[elem.n2] += elem.In(self.VI[elem.n1] - self.VI[elem.n2])
                #self.testtmp += [self.VI[elem.n1]]
            else:
                #choosing a value for the first time
                #assume vd0 = 0.1
                self.MNA_for_nl[elem.n1, elem.n1] += elem.Gn(0.1)
                self.MNA_for_nl[elem.n1, elem.n2] -= elem.Gn(0.1)
                self.MNA_for_nl[elem.n2, elem.n1] -= elem.Gn(0.1)
                self.MNA_for_nl[elem.n2, elem.n2] += elem.Gn(0.1)
                self.RHS_for_nl[elem.n1] -= elem.In(0.1)
                self.RHS_for_nl[elem.n2] += elem.In(0.1)
                #self.testtmp +=[0.1]

        elif isinstance(elem, MOSFET):
            if self.init_state == 0:
                self.check_f_device(elem)
                if self.check_nonlin(elem):
                    #n1, n2, n3, n4 = d, g, s, b
                    vgs = self.VI[elem.n2] - self.VI[elem.n3]
                    vds = self.VI[elem.n1] - self.VI[elem.n3]
                else:
                    if elem.MODEL == 'nmos':
                        vgs = 1
                        vds = 1
                    else:
                        vgs = -1
                        vds = -1
                self.MNA_for_nl[elem.n1, elem.n1] += elem.Gds(vgs, vds)
                self.MNA_for_nl[elem.n1, elem.n3] -= elem.Gds(vgs, vds) + elem.Gm(vgs, vds)
                self.MNA_for_nl[elem.n1, elem.n2] += elem.Gm(vgs, vds)
                self.MNA_for_nl[elem.n3, elem.n1] -= elem.Gds(vgs, vds)
                self.MNA_for_nl[elem.n3, elem.n3] += elem.Gds(vgs, vds) + elem.Gm(vgs, vds)
                self.MNA_for_nl[elem.n3, elem.n2] -= elem.Gm(vgs, vds)
                self.RHS_for_nl[elem.n1] -= elem.Ids(vgs, vds)
                self.RHS_for_nl[elem.n3] += elem.Ids(vgs, vds)
                elem.gm = elem.Gm(vgs, vds)
                elem.id = elem.Ids(vgs, vds) + elem.Gm(vgs, vds)*vgs + elem.Gds(vgs, vds)*vds
                if elem.id!=0:
                    elem.ro = 1/elem.id/elem.LAMBDA
                else:
                    elem.ro = float('inf')

            elif self.init_state == 1:
                if s!=0:
                    self.MNA[elem.n1, elem.n1] += 1./elem.ro
                    self.MNA[elem.n1, elem.n3] -= 1./elem.ro
                    self.MNA[elem.n3, elem.n1] -= 1./elem.ro
                    self.MNA[elem.n3, elem.n3] += 1./elem.ro
                    self.MNA[elem.n1, elem.n2] += elem.gm
                    self.MNA[elem.n1, elem.n3] -= elem.gm
                    self.MNA[elem.n2, elem.n2] -= elem.gm
                    self.MNA[elem.n2, elem.n3] += elem.gm
                    elem.ro = float('inf')
                    elem.gm = 0
                else:
                    vgs = self.VI[elem.n2] - self.VI[elem.n3]
                    vds = self.VI[elem.n1] - self.VI[elem.n3]
                    self.MNA_for_nl[elem.n1, elem.n1] += elem.Gds(vgs, vds)
                    self.MNA_for_nl[elem.n1, elem.n3] -= elem.Gds(vgs, vds) + elem.Gm(vgs, vds)
                    self.MNA_for_nl[elem.n1, elem.n2] += elem.Gm(vgs, vds)
                    self.MNA_for_nl[elem.n3, elem.n1] -= elem.Gds(vgs, vds)
                    self.MNA_for_nl[elem.n3, elem.n3] += elem.Gds(vgs, vds) + elem.Gm(vgs, vds)
                    self.MNA_for_nl[elem.n3, elem.n2] -= elem.Gm(vgs, vds)
                    self.RHS_for_nl[elem.n1] -= elem.Ids(vgs, vds)
                    self.RHS_for_nl[elem.n3] += elem.Ids(vgs, vds)
        return 1
