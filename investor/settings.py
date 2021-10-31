import yaml
from investor_constants import *

VAR_PREFIX = 'var_'


class Settings():
    def __init__(self, set_func):
        self.set_func = set_func
        self.low_spread_percent = 1.0
        self.high_spread_percent = 1.0
        self.max_depot = 10000.0
        self.min_order = 50.0
        self.max_order = 2000.0
        self.start_date = '2021-10-1'
        self.end_date = '2021-10-29'
        self.period = '1mo'
        self.selected_stocks = 'SIE.DE'
        self.selected_col1 = [D_CLOSE]
        self.selected_col2 = [D_BALANCE_NETTO]
        self.order_costs = 1.0
        self.tax = 25.0
        self.initial_order = 500.0
        self.auto_update = False
        self.use_period = True
        self.var_buy_threshold = -0.11
        self.range_var_buy_threshold = [-5.0, 0.0]
        self.cb_var_buy_threshold = False
        self.var_sell_threshold = 4.06
        self.range_var_sell_threshold = [0.0, 5]
        self.cb_var_sell_threshold = False
        self.var_buy_factor = 3.00
        self.range_var_buy_factor = [0.0, 500.0]
        self.cb_var_buy_factor = False
        self.var_sell_factor = 1.0
        self.range_var_sell_factor = [0.0, 1.0]
        self.cb_var_sell_factor = False

    def get_variable_names(self):
        return [attr for attr in dir(self) if not callable(getattr(self, attr)) and attr.startswith(VAR_PREFIX)]

    def get_setting_names(self):
        return [attr for attr in dir(self) if not callable(getattr(self, attr)) and not attr.startswith('__')]

    def set_value(self, name, val):
        setattr(self, name, val)

    def get_value(self, name, default):
        val = getattr(self, name, default)
        return val

    def update_ui(self):
        names = self.get_setting_names()
        for name in names:
            self.set_func(name, self.get_value(name, 0))

    def load(self):
        members = self.get_setting_names()
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
        members = self.get_setting_names()
        data = {}
        for var in members:
            data[var] = getattr(self, var)
        with open(SETTINGS_FILENAME, 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False)
