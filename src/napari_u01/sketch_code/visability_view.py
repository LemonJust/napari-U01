from PyQt5 import QtWidgets
import numpy as np
import csv

from PyQt5.QtWidgets import QWidget, \
    QVBoxLayout, QListWidget, QLabel, QFileDialog
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QComboBox, QLabel, \
    QPushButton, QHBoxLayout, QLineEdit


class ComboBox(QtWidgets.QComboBox):
    popupAboutToBeShown = QtCore.pyqtSignal()

    def showPopup(self):
        self.popupAboutToBeShown.emit()
        super(ComboBox, self).showPopup()


class Signal:
    def __init__(self):
        self._subscribers = []

    def connect(self, callback):
        self._subscribers.append(callback)

    def emit(self, *args, **kwargs):
        for subscriber in self._subscribers:
            subscriber(*args, **kwargs)


class LayerVisibilityView(QWidget):
    def __init__(self, model, viewer):
        super().__init__()

        self.model = model
        self.viewer = viewer
        self.rows = {}

        self.layout = QVBoxLayout()
        add_button = QPushButton("Add")
        self.layout.addWidget(add_button)
        self.setLayout(self.layout)
        self.add_row()

        add_button.clicked.connect(self.add_row)

        # Signals
        self.assign_clicked = Signal()

    def add_row(self):
        row = len(self.rows)

        layer_combo_box = ComboBox()
        layer_combo_box.popupAboutToBeShown.connect(
            lambda: self.populate_combo_box(row))

        number_label = QLabel("Key:")
        number_box = QLineEdit()

        assign_button = QPushButton("Assign")
        assign_button.clicked.connect(
            lambda: self.on_assign_clicked(row))

        # hide assign button by default
        assign_button.hide()
        # show assign button only if layer is selected or text changed
        layer_combo_box.currentTextChanged.connect(assign_button.show)
        number_box.textChanged.connect(assign_button.show)

        h_layout = QHBoxLayout()
        h_layout.addWidget(layer_combo_box)
        h_layout.addWidget(number_label)
        h_layout.addWidget(number_box)
        h_layout.addWidget(assign_button)

        self.rows[row] = {'layer': layer_combo_box,
                          'key': number_box,
                          'assign': assign_button}

        # add layer combo box
        self.layout.addLayout(h_layout)

    def on_assign_clicked(self, row):
        key = self.rows[row]['key'].text()
        layer_name = self.rows[row]['layer'].currentText()
        self.assign_clicked.emit(row, key, layer_name)

    def populate_combo_box(self, row):
        # populate combo box with layers that do not have bindings
        self.rows[row]['layer'].clear()
        self.rows[row]['layer'].addItems(
            [layer.name for layer in self.viewer.layers])

    def show_only_layer(self, layer_name):
        for layer in self.viewer.layers:
            if layer.name == layer_name:
                layer.visible = True
            else:
                layer.visible = False

    def restore_all_layers_visibility(self):
        for layer in self.model.visible_layers:
            self.viewer.layers[layer].visible = True
