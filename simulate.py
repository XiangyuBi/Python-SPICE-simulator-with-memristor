from control import*
from parsing import*
from stamp import*

class Simulate(object):
    """docstring for Simulate"""
    def __init__(self, file_name):
        super(Simulate, self).__init__()
        # self.file_name = file_name
        self.message = '\nLoading design:   '
        self.message += file_name
        self.parse = Parsing(file_name)
        if not self.parse.line_type == 'end':
            self.message += '\nError: There is no \'end\' in the file!'
        else:
            self.simulating()

    def simulating(self):
        self.Set_Sim_Option()    #those options in control lines
        #stp = Stamp(self.parse.element_list)
        self.start_analysis()       #those analysis types in control lines
        #self.print_result()         #print/plot... in control lines

    def Set_Sim_Option(self):
        pass

    def start_analysis(self):
        for i in range(len(self.parse.control_list['analysis'])):
            simu = self.parse.control_list['analysis'][i]
            self.ana_res = simu.analyze(self.parse.element_list)  #[variety, vi_result, stp.dict_i, stp.dict_v]
            #self.print_result(ana_res)
        self.message += '\nSimulate successfully!'

    def print_result(self):
        for i in range(len(self.parse.control_list['output'])):
            opt = self.parse.control_list['output'][i]
            opt.show_result(self.ana_res)

# sim = Simulate('test2.sp')
# Stamp(sim.parse.element_list)
