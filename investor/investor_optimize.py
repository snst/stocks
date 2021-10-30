from geneticalgorithm import geneticalgorithm as ga
import numpy as np
from investor import *

train_investor = None
variable_names = None

def train_func(params):
    global train_investor
    global variable_names
    for i, val in enumerate(params):
        var_name = variable_names[i]
        train_investor.settings.set_value(var_name, val)
    balance = train_investor.run()
    return -balance


class InvestorOptimizer():
    def __init__(self, df, settings):
        global train_investor
        global variable_names
        train_investor = Investor(df, settings)
        self.settings = settings
        variable_names_all = self.settings.get_variable_names()
        variable_names = []
        for name in variable_names_all:
            if settings.get_value(f'cb_{name}', False):
                variable_names.append(name)
        min_max_list = []
        for name in variable_names:
            min_max = self.settings.get_value(f'range_{name}', 0)
            min_max_list.append(min_max)

        self.varbound = np.array(min_max_list)
        self.dimensions = len(variable_names)

        self.algorithm_param = {'max_num_iteration': 10,
                           'population_size': 100,
                           'mutation_probability': 0.1,
                           'elit_ratio': 0.01,
                           'crossover_probability': 0.5,
                           'parents_portion': 0.3,
                           'crossover_type': 'uniform',
                           'max_iteration_without_improv': None}


    def run(self):
        global variable_names
        model = ga(function=train_func, dimension=self.dimensions, variable_type='real',
                   variable_boundaries=self.varbound, algorithm_parameters=self.algorithm_param)
        model.run()
        for i, val in enumerate(model.best_variable):
            var_name = variable_names[i]
            self.settings.set_value(var_name, val)
