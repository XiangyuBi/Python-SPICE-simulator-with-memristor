import re
from math import*

class Device(object):
    """docstring for Device"""
    def __init__(self, arg):
        super(Device, self).__init__()
        self.arg = arg
        self.get_para()

    def max_node(self):
        return max(self.n1, self.n2)

    def get_para(self):
        if len(self.arg)<4:
            print 'Creating class error: not given enough parameters.'
            return
        self.name = self.arg[0]
        self.n1 = eval(self.arg[1])
        self.n2 = eval(self.arg[2])
        self.para = self.arg[3:]

    #1k,1p,1u...if have unit...
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
        if re.match('^[0-9.]+$',char):
            return eval(char)
        else:
            unit = re.match('^[0-9.]+(meg|k|m|u|n|p|f)$', char)
            if unit:
                char = re.sub('(meg|k|m|u|n|p|f)$', units_list.get(unit.group(1)), char)
                return eval(char)
            else:
                print 'The value is wrong!!!'
                return 0


class Resistor(Device):
    """docstring for Resistor"""
    def __init__(self, arg):
        super(Resistor, self).__init__(arg)
        self.value = self.get_value(self.para[0])

class Capacitor(Device):
    """docstring for Capacitor"""
    def __init__(self, arg):
        super(Capacitor, self).__init__(arg)
        self.value = self.get_value(self.para[0])
        

    def BE_LTE(self, h, I_next, I_current):
        #be
        self.error = 1e-4
        return h*abs(I_next - I_current) > 2.*self.value*self.error

    def TR_LTE(self, h1, h2, I_after_next, I_next, I_current):
        self.error = 1e-8
        return abs(h1 / (12.*self.value*h2) * ( h1*(I_after_next - I_next) + h2*(I_current - I_next) ) ) > self.error

class Inductor(Device):
    """docstring for Inductor"""
    def __init__(self, arg):
        super(Inductor, self).__init__(arg)
        self.value = self.get_value(self.para[0])
        

    def BE_LTE(self, h, V_next, V_current):
        #be
        self.error = 1e-4
        return h*abs(V_next - V_current) > 2.*self.value*self.error

    def TR_LTE(self, h1, h2, V_after_next, V_next, V_current):
        self.error = 1e-8
        return abs(h1 / (12.*self.value*h2) * ( h1*(V_after_next - V_next) + h2*(V_current - V_next) ) ) > self.error






class Current_Source(Device):
    """docstring for Current_Source"""
    def __init__(self, arg):
        super(Current_Source, self).__init__(arg)
        #self.value = self.get_value(self.para[0])
        self.type = ''
        self.parse_para()
        self.run_t = 0
    def parse_para(self):
        if re.match('^sin', self.para[0]):
            self.type = 'sin'
            self.value = self.get_value(re.match('^sin\((.+)', self.para[0]).group(1))
            self.sin_A = self.get_value(self.para[1])
            self.sin_f = self.get_value(self.para[2][:-1])
        elif re.match('^pulse', self.para[0]):
            self.type = 'pulse'
            self.get_pulse_para(*self.para[1:])
        else:
            self.value = self.get_value(self.para[0])
            self.sin_A = 0
            self.sin_f = 0
    def get_pulse_para(self, v1, v2, td='0', tr='0', tf='0', pw=float('inf'), per=float('inf'), *other):
        self.value = self.get_value(v1)
        self.value2 = self.get_value(v2)
        self.td = self.get_value(td)
        self.tr = self.get_value(tr)
        self.tf = self.get_value(tf)
        if pw == float('inf'):
            self.pw = pw
        else:
            self.pw = self.get_value(pw)
        if per == float('inf'):
            self.per = per
        else:
            self.per = self.get_value(per)
    def value_var_t(self, h, runtime=0):
        self.run_t += h
        # self.value_t = self.calculate_vt(self.run_t) - self.calculate_vt(self.run_t-h)
        self.value_t = self.calculate_vt(runtime) - self.calculate_vt(runtime-h)
        #print self.value_t
        return self.value_t
    def calculate_vt(self, t):
        if self.type == 'sin':
            vt = self.sin_A*sin(2*pi*self.sin_f*t)

        elif self.type == 'pulse':
            if t <= self.td:
                vt = 0
            elif t <= (self.td + self.tr):
                vt = (t-self.td)/(self.tr)*(self.value2-self.value)
            else:
                vt = self.value2 - self.value
        else:
            vt = 0
        #print vt
        return vt

class Voltage_Source(Device):
    """docstring for Voltage_Source"""
    def __init__(self, arg):
        super(Voltage_Source, self).__init__(arg)
        self.type = ''
        self.parse_para()
        self.run_t = 0.
        
    def parse_para(self):
        if re.match('^sin', self.para[0]):
            self.type = 'sin'
            # print 'sin'
            self.value = self.get_value(re.match('^sin\((.+)', self.para[0]).group(1))
            self.sin_A = self.get_value(self.para[1])
            self.sin_f = self.get_value(self.para[2][:-1])
        elif re.match('^pulse', self.para[0]):
            self.type = 'pulse'
            self.get_pulse_para(*self.para[1:])
        else:
            self.value = self.get_value(self.para[0])
            self.sin_A = 0
            self.sin_f = 0
        try:
            if re.match('^ac$', self.para[1]):
                self.value_f = self.get_value(self.para[2])
            else:
                self.value_f = 0
        except:
            self.value_f = 0
    def get_pulse_para(self, v1, v2, td='0', tr='0', tf='0', pw=float('inf'), per=float('inf'), *other):
        self.value = self.get_value(v1)
        self.value2 = self.get_value(v2)
        self.td = self.get_value(td)
        self.tr = self.get_value(tr)
        self.tf = self.get_value(tf)
        if pw == float('inf'):
            self.pw = pw
        else:
            self.pw = self.get_value(pw)
        if per == float('inf'):
            self.per = per
        else:
            self.per = self.get_value(per)
    def value_var_t(self, h, runtime=0):
        if self.type == 'sin':
            self.run_t += h
            # self.value_t = self.sin_A*sin(2*pi*self.sin_f*self.run_t)
            self.value_t = self.sin_A*sin(2*pi*self.sin_f*runtime)
        elif self.type == 'pulse':
            self.run_t += h
            # if self.run_t <= self.td:
            #     self.value_t = 0
            # elif self.run_t <= (self.td + self.tr):
            #     self.value_t = (self.run_t-self.td)/(self.tr)*(self.value2-self.value)
            # else:
            #     self.value_t = self.value2 - self.value
            # print self.td + self.tr + self.per + self.tf
            # runtime -=h
            while runtime > self.td + self.per:
                runtime -= self.per
                
            if runtime <= self.td:
                self.value_t = 0
            elif runtime <= (self.td + self.tr):
                self.value_t = (runtime-self.td)/(self.tr)*(self.value2-self.value)
            elif runtime <= (self.td + self.tr + self.pw):
                # print 'p', runtime
                self.value_t = self.value2 - self.value
            elif runtime <= (self.td + self.tr + self.pw + self.tf):
                # print 'f', runtime
                self.value_t = self.value2 - (runtime - (self.td + self.tr + self.pw))*(self.value2 - self.value)/self.tf
            elif runtime <= (self.td + self.per):
                self.value_t = self.value
            else:
                self.value_t = self.value
                # self.value_t = self.value2 - self.value
        else:
            self.value_t = 0
        #print self.value_t
        return self.value_t

    def value_var_f(self, w, omega):
        self.value_f = omega/(omega**2 + (1j*w)**2)
        return self.value_f

class VCVS(Device):
    """docstring for VCVS"""
    def __init__(self, arg):
        super(VCVS, self).__init__(arg)
        self.parse_para()

    def parse_para(self):
        if len(self.para)<3:
            print 'Creating class error: not given enough parameters.'
            return
        self.n3 = eval(self.para[0])
        self.n4 = eval(self.para[1])
        self.value = self.get_value(self.para[2])

class CCCS(Device):
    """docstring for CCCS"""
    def __init__(self, arg):
        super(CCCS, self).__init__(arg)
        self.parse_para()

    def parse_para(self):
        if len(self.para)<2:
            print 'Creating class error: not given enough parameters.'
            return
        self.v_name = self.para[0]
        self.value = self.get_value(self.para[1])

class VCCS(Device):
    """docstring for VCCS"""
    def __init__(self, arg):
        super(VCCS, self).__init__(arg)
        self.parse_para()

    def parse_para(self):
        if len(self.para)<3:
            print 'Creating class error: not given enough parameters.'
            return
        self.n3 = eval(self.para[0])
        self.n4 = eval(self.para[1])
        self.value = self.get_value(self.para[2])

class CCVS(Device):
    """docstring for CCVS"""
    def __init__(self, arg):
        super(CCVS, self).__init__(arg)
        self.parse_para()

    def parse_para(self):
        if len(self.para)<2:
            print 'Creating class error: not given enough parameters.'
            return
        self.v_name = self.para[0]
        self.value = self.get_value(self.para[1])

class Diode(Device):
    """docstring for Diode"""
    def __init__(self, arg):
        super(Diode, self).__init__(arg)
        self.parse_para()

    def parse_para(self):
        self.alpha = 40
        self.Isat = 1#0e-15  
        #MODEL: Id = Isat*(exp(self.alpha*Vd)-1)
        pass

    def Gn(self, vd):
        #'gn', alpha*exp(alpha*vd)
        return self.Isat*self.alpha*exp(self.alpha*vd)

    def In(self, vd):
        #'in', -Isat*alpha*exp(alpha*vd)*vd+Isat*(exp(alpha*vd)-1)
        return -self.Isat*self.alpha*exp(self.alpha*vd)*vd+self.Isat*(exp(self.alpha*vd)-1)

    def convergence(self, VI, VI_last):
        c1 = 1e-6
        c2 = 1e-4
        if abs((VI[self.n1]-VI[self.n2])-(VI_last[self.n1]-VI_last[self.n2])) <= min(c1, c2*abs(VI_last[self.n1]-VI_last[self.n2])):
            return 1
        else:
            return 0




class MEMRISTOR(Device):
    def __init__(self,arg):
        super(MEMRISTOR,self).__init__(arg)
        self.parse_para()

    def parse_para(self):
        self.Ron = self.get_value(self.para[0])
        self.Roff = self.get_value(self.para[1])
        self.Rinit = self.get_value(self.para[2])
        self.D = 5*(10**(-8))#default
        self.ux = 1*(10**(-8)) #default
        self.a = (self.ux *self.Ron*(self.Roff-self.Ron))
        self.w_init = (self.Roff- self.Rinit)/(self.Roff- self.Ron) #default
        self.constan = self.ux*self.Ron/(self.D**2)
        self.E0 = 1*(10**(8)) #default
        self.p = 5 #default
        self.value = 0 #default
    def caculate_F(self,vt,w,h,type):
     #   print self.ux * self.E0 * h * (1. / self.D) , sinh(vt / (self.D * self.E0)) * self.F(w),self.F(w),'1'
        if type == 1:
             return self.ux*self.E0*h*(1./self.D)*sinh(vt/(self.D*self.E0))*self.F_1(w)
        elif type == 0:
             return  self.ux*self.E0*h*(1./self.D)*sinh(vt/(self.D*self.E0))*self.F_2(w)

    def F_1(self,w):

        return 1.-w**(2*self.p)

    def F_2(self,w):
        return 1. - (w-1) ** (2 * self.p)


    def memristance(self, w):
      #  print self.Ron * w + self.Roff * (1. - w), w
        return (self.Ron * w + self.Roff * (1. - w))


 #   def memristance(self, w):
        # print self.Ron*w + self.Roff*(1.-w)
 #        return self.Ron*w + self.Roff*(1.-w)
 #   def caculate_w_be(self, h, current):
 #        w_former = self.w
 #        w_current = (h * self.u * self.Ron * current) / self.D + w_former
 #        if w_current > 1.:
 #           return 1.
 #        elif -0.000000000001 <= w_current <= 1.:
 #           self.w = w_current
 #           return w_current
 #        elif w_current < -0.000000000001:
 #           w_current = 0.0
 #           return w_current


#    def caculate_w_tr(self, h, current):
#        return 0'''


class MOSFET(Device):
    """docstring for MOSFET"""
    def __init__(self, arg):
        super(MOSFET, self).__init__(arg)
        #n1,n2,n3,n4 = d, g, s, b
        self.parse_para()
        
    def parse_para(self):
        self.n3 = self.get_value(self.para[0])
        self.n4 = self.get_value(self.para[1])
        self.MODEL = self.para[2]
        if self.MODEL == 'nmos':
            self.VT = 0.7
            self.LAMBDA = 0.1
            self.K = 1.3429e-6
            self.W_plus_L = 20.
        elif self.MODEL == 'pmos':
            self.VT = -0.8
            self.LAMBDA = -0.2
            self.K = -3.8367e-7 
            self.W_plus_L = 100.
        
    def Gm(self, vgs, vds):
        if (vgs>self.VT and self.MODEL=='nmos') or (vgs<self.VT and self.MODEL=='pmos'):
            if (vds>=vgs - self.VT and self.MODEL=='nmos') or (vds<=vgs-self.VT and self.MODEL=='pmos'):
                return self.K*self.W_plus_L*(vgs-self.VT)*(1+self.LAMBDA*vds)
            elif (vds<vgs-self.VT and vds>0 and self.MODEL=='nmos') or (vds>vgs-self.VT and vds<0 and self.MODEL=='pmos'):
                return self.K*self.W_plus_L*vds*(1+self.LAMBDA*vds)
            elif (vds<=0 and self.MODEL=='nmos') or (vds>=0 and self.MODEL=='pmos'):
                return self.K*self.W_plus_L*vds
        else:
            return 0
    def Gds(self, vgs, vds):
        if (vgs> self.VT and self.MODEL=='nmos') or (vgs<self.VT and self.MODEL=='pmos'):
            if (vds>=vgs - self.VT and self.MODEL=='nmos') or (vds<=vgs-self.VT and self.MODEL=='pmos'):
                return 1./2.*self.K*self.W_plus_L*(vgs-self.VT)**2*self.LAMBDA
            elif (vds<vgs-self.VT and vds>0 and self.MODEL=='nmos') or (vds>vgs-self.VT and vds<0 and self.MODEL=='pmos'):
                return self.K*self.W_plus_L*(vgs-self.VT+2*self.LAMBDA*(vgs-self.VT)*vds-vds-3./2.*self.LAMBDA*vds*vds)
            elif (vds<=0 and self.MODEL=='nmos') or (vds>=0 and self.MODEL=='pmos'):
                return self.K*self.W_plus_L*(vgs-self.VT-vds)
        else:
            return 0
    def Ids(self, vgs, vds):
        #Ids(vgs, vds) - gm*vgs - gds*vds
        if (vgs>self.VT and self.MODEL=='nmos') or (vgs<self.VT and self.MODEL=='pmos'):
            if (vds>=vgs - self.VT and self.MODEL=='nmos') or (vds<=vgs-self.VT and self.MODEL=='pmos'):
                return 1./2.*self.K*self.W_plus_L*(vgs-self.VT)**2*(1+self.LAMBDA*vds)-self.Gm(vgs, vds)*vgs-self.Gds(vgs, vds)*vds
            elif (vds<vgs-self.VT and vds>0 and self.MODEL=='nmos') or (vds>vgs-self.VT and vds<0 and self.MODEL=='pmos'):
                return self.K*self.W_plus_L*((vgs-self.VT)*vds-1./2.*vds**2)*(1+self.LAMBDA*vds)-self.Gm(vgs, vds)*vgs-self.Gds(vgs, vds)*vds
            elif (vds<=0 and self.MODEL=='nmos') or (vds>=0 and self.MODEL=='pmos'):
                return self.K*self.W_plus_L*((vgs-self.VT)*vds-1./2.*vds**2)-self.Gm(vgs, vds)*vgs-self.Gds(vgs, vds)*vds
        else:
            return 0
 
    def convergence(self, VI, VI_last):
        c1 = 1e-6
        c2 = 1e-4
        if abs((VI[self.n1]-VI[self.n3])-(VI_last[self.n1]-VI_last[self.n3])) <= min(c1, c2*abs(VI_last[self.n1]-VI_last[self.n3])):
            if abs((VI[self.n2]-VI[self.n3])-(VI_last[self.n2]-VI_last[self.n3])) <= min(c1, c2*abs(VI_last[self.n2]-VI_last[self.n3])):
                return 1
            else:
                return 0
        else:
            return 0
