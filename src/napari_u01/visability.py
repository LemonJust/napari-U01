# Model
from collections import defaultdict
# View
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QLabel, QPushButton, QHBoxLayout, QLineEdit
# Controller
import napari
from PyQt5.QtWidgets import QWidget, QVBoxLayout


# Model _________________________________________________________________
class LayerVisibilityModel:
    def __init__(self):
        self.key_to_layer_map = defaultdict(list)
        self.solo_layers = None
        self.visible_layers = []

    def set_mapping(self, key, layer_name):
        self.key_to_layer_map[key].append(layer_name)

    def remove_mapping(self, key):
        del self.key_to_layer_map[key]


# View _________________________________________________________________
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

        self._layout = QVBoxLayout()
        add_button = QPushButton("Add")
        self._layout.addWidget(add_button)
        self.setLayout(self._layout)
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
        self._layout.addLayout(h_layout)

    def on_assign_clicked(self, row):
        key = self.rows[row]['key'].text()
        layer_name = self.rows[row]['layer'].currentText()
        self.assign_clicked.emit(row, key, layer_name)

    def populate_combo_box(self, row):
        # populate combo box with layers that do not have bindings
        self.rows[row]['layer'].clear()
        self.rows[row]['layer'].addItems(
            [layer.name for layer in self.viewer.layers])

    def show_only_layers(self, layers):
        for layer in self.viewer.layers:
            if layer.name in layers:
                layer.visible = True
            else:
                layer.visible = False

    def restore_all_layers_visibility(self):
        for layer in self.model.visible_layers:
            self.viewer.layers[layer].visible = True


# Controller _________________________________________________________________
class LayerVisibilityController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def on_assign_clicked(self, row, key, layer_name):

        # if mapping existis,
        # remove it from the other use and unbind
        if key in self.model.key_to_layer_map:
            self.view.viewer.bind_key(key, None)

        # in case we removed it from itself
        self.model.set_mapping(key, layer_name)
        self.view.viewer.bind_key(key, lambda x: self.on_keyboard_input(key))

        # hide assign button
        self.view.rows[row]['assign'].hide()

        # update bindings
        self.update_bindings()

    def update_bindings(self):
        # ist of all keys in the widget
        view_keys = [
            self.view.rows[row]['key'].text() for row in self.view.rows]
        model_keys = list(self.model.key_to_layer_map.keys())

        # remove unused keys from model and viewer
        for key in model_keys:
            if key not in view_keys:
                self.model.remove_mapping(key)
                self.view.viewer.bind_key(key, None)

    def on_keyboard_input(self, key):
        layers = self.model.key_to_layer_map.get(key)
        # if not in the solo mode, remember the current state of the layers
        # and switch to the solo mode
        if self.model.solo_layers is None:
            self.model.visible_layers = [
                layer.name for layer in self.view.viewer.layers
                if layer.visible]

            if layers is not None and len(layers) > 0:
                self.model.solo_layers = layers
                self.view.show_only_layers(layers)
        # if in the solo mode, restore the previous state of the layers
        # or switch to another solo layer
        else:
            if layers == self.model.solo_layers:
                self.model.solo_layers = None
                self.view.restore_all_layers_visibility()
            else:
                self.model.solo_layers = layers
                self.view.show_only_layers(layers)


# Widget _________________________________________________________________
def setup_visability_callbacks(controller, view):
    # Will bind key when assigned clicked
    view.assign_clicked.connect(controller.on_assign_clicked)


class LayerVisabilityWidget(QWidget):
    def __init__(self, napari_viewer: 'napari.viewer.Viewer' = None):
        super().__init__()
        self.model = LayerVisibilityModel()
        self.view = LayerVisibilityView(self.model, napari_viewer)
        self.controller = LayerVisibilityController(self.model, self.view)

        # create layout
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)

        # Setup the keyboard input and double-click events
        setup_visability_callbacks(self.controller, self.view)
