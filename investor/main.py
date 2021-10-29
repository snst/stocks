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
matplotlib.use('Qt5Agg')


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super(MplCanvas, self).__init__(self.fig)


class MainWindow(QMainWindow):
    def add_widget_row(self, widgets):
        layout = QHBoxLayout()
        for w in widgets:
            layout.addWidget(w)
        self.layout_vl.addLayout(layout)

    def add_widget(self, widget):
        self.layout_vl.addWidget(widget)
        return widget

    def add_button(self, text, connect=None):
        widget = QPushButton(text)
        if connect:
            widget.clicked.connect(connect)
        self.layout_vl.addWidget(widget)
        return widget

    def add_edit(self, name, var):
        widget = create_edit(var)
        self.add_label_with_widget(name, widget)
        return widget

    def create_edit(self, var):
        widget = QLineEdit(self.settings.get_value(var, ''))
        widget.textChanged.connect(lambda x: self.settings.set_value(var, x))
        return widget

    def add_label_with_widget(self, label, widget):
        self.add_widget_row([QLabel(label), widget])

    def settings_spinbox_changed(self, var_name, value):
        self.settings.set_value(var_name, value)
        self.auto_update()

    def add_dspinbox(self, text, min=-10, max=10, step=0.1, var=None, default=0):
        widget = QDoubleSpinBox()
        widget.setRange(min, max)
        widget.setSingleStep(step)
        widget.setValue(self.settings.get_value(var, default))
        widget.valueChanged.connect(lambda x: self.settings_spinbox_changed(
            var, x),  type=Qt.QueuedConnection)
        self.add_label_with_widget(text, widget)
        return widget

    def add_list(self, items=None, selected=[], connect=None):
        widget = QListWidget()
        widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        if connect:
            widget.itemClicked.connect(lambda: connect(widget.selectedItems()))
        if items:
            for i, name in enumerate(items):
                item = QListWidgetItem(name)
                widget.insertItem(i, item)
                if name in selected:
                    item.setSelected(True)
        self.add_widget(widget)
        return widget

    def add_checkbox(self, name, var):
        widget = self.create_checkbox(name, var)
        self.add_widget(widget)
        return widget

    def create_checkbox(self, name, var):
        widget = QCheckBox(name)
        widget.setChecked(self.settings.get_value(var, False))
        widget.stateChanged.connect(
            lambda: self.settings.set_value(var, widget.isChecked()))
        return widget

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

    def auto_update(self):
        if self.settings.auto_update:
            self.simulate()

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

    def click_stocknames(self, val):
        self.settings.selected_stocks = val[0].text()
        self.auto_update()

    def click_columns1(self, val):
        self.settings.selected_col1 = []
        if len(val) > 0:
            for col in val:
                self.settings.selected_col1.append(col.text())
        self.auto_update()

    def click_columns2(self, val):
        self.settings.selected_col2 = []
        if len(val) > 0:
            for col in val:
                self.settings.selected_col2.append(col.text())
        self.auto_update()

    def info(self, text):
        self.qedit_info.setText(text)

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.settings = Settings()
        self.settings.load()
        self.stock = StockLoader()
        self.layout_vl = QVBoxLayout()
        self.layout_vr = QVBoxLayout()
        self.layout_h = QHBoxLayout()
        widget = QWidget()
        widget.setMaximumWidth(220)
        widget.setLayout(self.layout_vl)
        self.layout_h.addWidget(widget)
        self.layout_h.addLayout(self.layout_vr)

        self.add_list(ALL_STOCKNAMES, selected=self.settings.selected_stocks,
                      connect=self.click_stocknames)
        self.add_list(
            ALL_COLUMNS, selected=self.settings.selected_col1, connect=self.click_columns1)
        self.add_list(
            ALL_COLUMNS, selected=self.settings.selected_col2, connect=self.click_columns2)

        self.add_button("Simulate", connect=self.simulate)
        self.add_button("Optimize", connect=self.optimize)
        self.add_button("Save", connect=lambda: self.settings.save())
        self.add_dspinbox("buy threshold", var='var_buy_threshold',
                          min=-10.0, max=0.0, step=0.1)
        self.add_dspinbox(
            "sell threshold", var='var_sell_threshold', min=0.0, max=10.0, step=0.1)
        self.add_dspinbox("buy factor", var='var_buy_factor',
                          min=0.0, max=10.0, step=0.1)
        self.add_dspinbox("sell factor", var='var_sell_factor',
                          min=0.0, max=1.0, step=0.1)
        self.add_dspinbox("min reach", var='minimum_reach',
                          min=0.0, max=1.0, step=0.1)
        self.add_dspinbox("max reach", var='maximum_reach',
                          min=0.0, max=1.0, step=0.1)
        self.add_dspinbox("initial order", var='initial_order',
                          min=0.0, max=10000, step=50)
        self.add_dspinbox("min order", var='min_order',
                          min=10, max=1000000, step=10)
        self.add_dspinbox("max order", var='max_order',
                          min=100, max=1000000, step=100)
        self.add_dspinbox("max depot", var='max_depot',
                          min=100, max=1000000, step=100)
        self.add_dspinbox("order costs", var='order_costs',
                          min=0.0, max=50.0, step=1)
        self.add_dspinbox("tax", var='tax', min=0.0, max=50.0, step=1)
        self.add_widget_row([QLabel('range'), self.create_edit(var='start_date'), self.create_edit(var='end_date')])
        self.add_widget_row([self.create_checkbox(
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
        self.show()
        self.auto_update()


app = QApplication(sys.argv)
w = MainWindow()
app.exec_()
