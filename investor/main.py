from investor_constants import *
from datetime import timedelta, datetime, date
from geneticalgorithm import geneticalgorithm as ga
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from settings import *
from stock_loader import *
from investor import *
import sys
import matplotlib
from investor_optimize import *
from ui_helper import *
matplotlib.use('Qt5Agg')


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super(MplCanvas, self).__init__(self.fig)


class MainWindow(QMainWindow, UIHelper):

    def plot_axix(self, df, ax, column):
        if column == D_SPREAD_BAR:
            ax.bar(df.index, df[D_SPREAD], bottom=df[D_LOW],
                   label=column, color=COLOR_MAP.get(column, None))
        elif column == D_BUY or column == D_SELL:
            ax.bar(df.index, df[column], color=COLOR_MAP.get(
                column, None), label=column)
        else:
            ax.plot(df.index, df[column], label=column,
                    color=COLOR_MAP.get(column, None))
#            ax.step(df.index, df[column], label=column, where='post', color=col.get(column, None))

    def plot(self, df, c1=[], c2=[], title=""):
        self.plot_widget.fig.clear()
        ax = self.plot_widget.fig.add_subplot(111)
        for column in c1:
            self.plot_axix(df, ax, column)
        ax = ax.twinx()
        for column in c2:
            self.plot_axix(df, ax, column)
        self.plot_widget.fig.legend()
        ax.grid()
        self.plot_widget.draw()

    def simulate(self):
        self.update_stock()
        self.investor = Investor(self.df, self.settings)
        self.investor.run()
        self.update_plot()
        i = self.investor
        self.info(f'netto: {i.netto_balance:.2f}, brutto: {i.brutto_balance:.2f}, tax won: {i.tax_won:.2f}, tax loss: {i.tax_loss:.2f}, tax: {i.tax:.2f}, invested: {i.sum_invested:.2f}, depot: {i.sum_depot:.2f}, cnt sell: {i.cnt_sell}, cnt buy: {i.cnt_buy}, trading cost: {i.trading_cost:.2f}')

    def optimize(self):
        opt = InvestorOptimizer(self.df, self.settings)
        opt.run()
        self.settings.update_ui()

    def auto_update(self):
        if self.settings.auto_update:
            self.simulate()

    def ui_changed(self, name, val):
        self.auto_update()

    def parse_date(self, val):
        if val == None or len(val) == 0:
            return datetime.now()
        else:
            return datetime.strptime(val, "%Y-%m-%d")

    def copy_df(self):
        self.df = self.df_.copy()

    def update_plot(self):
        self.plot(df=self.df, c1=self.settings.selected_col1,
                  c2=self.settings.selected_col2)

    def update_stock(self):
        start = None
        end = None
        period = None
        if self.settings.use_period:
            period = self.settings.period
        else:
            start = self.parse_date(self.settings.start_date)
            end = self.parse_date(self.settings.end_date)

        self.df_ = self.stock.load(
            names=self.settings.selected_stocks, start=start, end=end, period=period)
        self.stock.preprocess_hist(self.df_, self.settings)
        self.copy_df()

    def info(self, text):
        self.qedit_info.setText(text)

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.widget_dict = {}
        self.settings = Settings(self.set_widget_value)
        self.settings.load()
        self.stock = StockLoader()
        self.layout_vl = QVBoxLayout()
        self.set_add_layout(self.layout_vl)
        self.layout_vr = QVBoxLayout()
        self.layout_h = QHBoxLayout()
        widget = QWidget()
        widget.setMaximumWidth(220)
        widget.setLayout(self.layout_vl)
        self.layout_h.addWidget(widget)
        self.layout_h.addLayout(self.layout_vr)

        self.add_list(ALL_STOCKNAMES, 'selected_stocks',
                      selected=self.settings.selected_stocks)
        self.add_list(ALL_COLUMNS, 'selected_col1',
                      selected=self.settings.selected_col1)
        self.add_list(ALL_COLUMNS, 'selected_col2',
                      selected=self.settings.selected_col2)

        self.add_button("Simulate", connect=self.simulate)
        self.add_button("Optimize", connect=self.optimize)
        self.add_button("Save", connect=lambda: self.settings.save())
        self.add_spinbox("buy threshold", var='var_buy_threshold',
                         min=-10.0, max=0.0, step=0.1, checkbox=True)
        self.add_spinbox(
            "sell threshold", var='var_sell_threshold', min=0.0, max=10.0, step=0.1, checkbox=True)
        self.add_spinbox("buy factor", var='var_buy_factor',
                         min=0.0, max=self.settings.range_var_buy_factor[1], step=0.1, checkbox=True)
        self.add_spinbox("sell factor", var='var_sell_factor',
                         min=0.0, max=1.0, step=0.1, checkbox=True)
        self.add_spinbox("min reach", var='minimum_reach',
                         min=0.0, max=1.0, step=0.1)
        self.add_spinbox("max reach", var='maximum_reach',
                         min=0.0, max=1.0, step=0.1)
        self.add_spinbox("initial order", var='initial_order',
                         min=0.0, max=10000, step=50)
        self.add_spinbox("min order", var='min_order',
                         min=10, max=1000000, step=10)
        self.add_spinbox("max order", var='max_order',
                         min=100, max=1000000, step=100)
        self.add_spinbox("max depot", var='max_depot',
                         min=100, max=1000000, step=100)
        self.add_spinbox("order costs", var='order_costs',
                         min=0.0, max=50.0, step=1)
        self.add_spinbox("tax", var='tax', min=0.0, max=50.0, step=1)
        self.add_widget([QLabel('range'), self.create_edit(
            var='start_date'), self.create_edit(var='end_date')])
        self.add_widget([self.create_checkbox(
            "use period", var="use_period"), self.create_edit(var='period')])
        self.add_checkbox("auto update", var="auto_update")

        self.plot_widget = MplCanvas(self, width=10, height=8, dpi=100)
        toolbar = NavigationToolbar(self.plot_widget, self)
        self.layout_vr.addWidget(toolbar)
        self.layout_vr.addWidget(self.plot_widget)
        self.qedit_info = QLineEdit("")
        self.layout_vr.addWidget(self.qedit_info)

        widget = QWidget()
        widget.setLayout(self.layout_h)
        self.setCentralWidget(widget)
        self.settings.update_ui()
        self.show()
        #self.auto_update()
        self.register_ui_changed(self.settings.set_value)
        self.register_ui_changed(self.ui_changed)


app = QApplication(sys.argv)
w = MainWindow()
app.exec_()
