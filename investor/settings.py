import yaml
from investor_constants import *


class Settings():
    def __init__(self):
        self.var_minimum_reach = 1.0
        self.var_maximum_reach = 1.0
        self.var_max_depot = 10000.0
        self.var_min_order = 50.0
        self.var_max_order = 2000.0
        self.var_buy_threshold = -0.11
        self.var_sell_threshold = 4.06
        self.var_buy_factor = 3.00
        self.var_sell_factor = 1.0
        self.var_start_date = '2021-10-1'
        self.var_end_date = '2021-10-29'
        self.var_period = '1mo'
        self.var_selected_stocks = 'SIE.DE'
        self.var_selected_col1 = [D_CLOSE]
        self.var_selected_col2 = [D_CLOSE]
        self.var_order_price = 1.0
        self.var_tax = 25.0
        self.var_initial_order = 500.0
        self.var_auto_update = False
        self.var_use_period = True

    def get_variable_names(self):
        return [attr for attr in dir(self) if not callable(getattr(self, attr)) and attr.startswith("var_")]

    def set_value(self, name, val):
        setattr(self, name, val)

    def get_value(self, name, default):
        return getattr(self, name, default)

    def load(self):
        members = self.get_variable_names()
        try:
            with open(SETTINGS_FILENAME, 'r') as infile:
                data = yaml.load(infile, Loader=yaml.FullLoader)
                if data:
                    for key, value in data.items():
                        if key in members:
                            setattr(self, key, value)
        except Exception as e:
            print(str(e))

    def save(self):
        members = self.get_variable_names()
        data = {}
        for var in members:
            data[var] = getattr(self, var)
        with open(SETTINGS_FILENAME, 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False)
