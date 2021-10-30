from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

class UIHelper():
    def __init__(self):
        self.widget_dict = {}
        self.ui_layout = None
        self.ui_changed_callbacks = []
    
    def set_add_layout(self, layout):
        self.ui_layout = layout

    def register_widget(self, widget, var_name):
        self.widget_dict[var_name] = widget
        if isinstance(widget, QLineEdit):
            widget.textChanged.connect(lambda x: self.widget_changed(var_name))
        elif isinstance(widget, QCheckBox):
            widget.stateChanged.connect(lambda x: self.widget_changed(var_name))
        elif isinstance(widget, QDoubleSpinBox):
            widget.valueChanged.connect(lambda x: self.widget_changed(var_name), type=Qt.QueuedConnection)
        elif isinstance(widget, QListWidget):
            widget.itemClicked.connect(lambda: self.widget_changed(var_name))
        return widget

    def get_widget_value(self, var_name, default=None):
        ret = default
        widget = self.widget_dict.get(var_name, None)
        if widget:
            if isinstance(widget, QLineEdit):
                ret = widget.text()
            elif isinstance(widget, QCheckBox):
                ret = widget.isChecked()
            elif isinstance(widget, QDoubleSpinBox):
                ret = widget.value()
            elif isinstance(widget, QListWidget):
                items = widget.selectedItems()
                ret = [x.text() for x in items]
        return ret

    def set_widget_value(self, var_name, val):
        widget = self.widget_dict.get(var_name, None)
        if widget:
            if isinstance(widget, QLineEdit):
                widget.setText(val)
            elif isinstance(widget, QCheckBox):
                widget.setChecked(val)
            elif isinstance(widget, QDoubleSpinBox):
                widget.setValue(val)

    def widget_changed(self, var_name):
        val = self.get_widget_value(var_name)
        print(f'{var_name}: {val}')
        for func in self.ui_changed_callbacks:
            func(var_name, val)
        pass

    def create_edit(self, var):
        widget = self.register_widget(QLineEdit(), var)
        return widget

    def create_spinbox(self, text, var, min=-10, max=10, step=0.1, default=0, checkbox=False):
        spinbox = self.register_widget(QDoubleSpinBox(), var)
        spinbox.setRange(min, max)
        spinbox.setSingleStep(step)
        if checkbox:
            first = self.create_checkbox(text, f'cb_{var}')
        else:
            first = QLabel(text)
        return [first, spinbox]

    def create_checkbox(self, name, var):
        widget = self.register_widget(QCheckBox(name), var)
        return widget

    def create_list(self, items, var, selected=[]):
        widget = self.register_widget(QListWidget(), var)
        widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        if items:
            for i, name in enumerate(items):
                item = QListWidgetItem(name)
                widget.insertItem(i, item)
                if name in selected:
                    item.setSelected(True)
        return widget

    def add_widget(self, widget):
        if isinstance(widget, list):
            layout = QHBoxLayout()
            for w in widget:
                layout.addWidget(w)
            self.ui_layout.addLayout(layout)
        else:
            self.ui_layout.addWidget(widget)
        return widget

    def add_edit(self, name, var):
        return self.add_widget([QLabel(name), create_edit(var)])

    def add_spinbox(self, text, var, min=-10, max=10, step=0.1, default=0, checkbox=False):
        return self.add_widget(self.create_spinbox(text=text, var=var, min=min, max=max, step=step, default=default, checkbox=checkbox))

    def add_list(self, items, var, selected=[]):
        return self.add_widget(self.create_list(items, var, selected))

    def add_checkbox(self, name, var):
        return self.add_widget(self.create_checkbox(name, var))

    def add_button(self, text, connect=None):
        widget = QPushButton(text)
        widget.clicked.connect(connect)
        return self.add_widget(widget)

    def register_ui_changed(self, func):
        self.ui_changed_callbacks.append(func)