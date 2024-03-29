from typing import TYPE_CHECKING
import numpy as np
from copy import deepcopy
import yaml

from .classification_model import LabelClassificationModel
from .classification_view import LabelClassificationView
from .classification_controller import LabelClassificationController

from .demo import demo_data

import napari
from PyQt5.QtWidgets import QWidget

if TYPE_CHECKING:
    import napari

from PyQt5.QtWidgets import QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout


# Connect the keyboard input and double-click events to the controller
def setup_classification_callbacks(controller, view, config):
    # Set up key bindings based on the config
    class_names = []
    for group in config['classifications']:
        for classification in group['classes']:
            key = classification['key']
            name = classification['name']
            class_names.append(name)

            @view.viewer.bind_key(key)
            def key_binding(viewer, the_key=key):
                controller.on_keyboard_input(the_key)

            if 'subclasses' in classification:
                for subclass in classification['subclasses']:
                    key = subclass['key']
                    sub_name = subclass['name']
                    class_names.append(f'{name}:{sub_name}')

                    @view.viewer.bind_key(key)
                    def key_binding(viewer, the_key=key):
                        controller.on_keyboard_input(the_key)



    # Set up the mouse drag event
    layer_names = [layer.name for layer in view.viewer.layers]
    for layer_name in layer_names:
        if layer_name in class_names:
            @view.viewer.layers[layer_name].mouse_drag_callbacks.append
            def select_label(layer, event):
                coordinates = np.round(event.position).astype(int)
                controller.on_label_selection(tuple(coordinates))

    # Set up the list widget events
    view.label_list.table.cellDoubleClicked.connect(
        controller.on_double_click_label)

    view.label_list.save_button.clicked.connect(
        controller.on_save_button_click)


class LabelClassificationWidget(QWidget):
    def __init__(self, napari_viewer: 'napari.viewer.Viewer' = None):
        super().__init__()

        # Create the textbox and button for config file location
        self.config_textbox = QLineEdit()
        self.config_button = QPushButton("Load Config")
        self.config_button.clicked.connect(lambda: self.load_config(napari_viewer))

        # Create the layout for the textbox and button
        config_layout = QHBoxLayout()
        config_layout.addWidget(self.config_textbox)
        config_layout.addWidget(self.config_button)

        # Create the main layout for the widget
        main_layout = QVBoxLayout()
        main_layout.addLayout(config_layout)

        # Set the main layout for the widget
        self.setLayout(main_layout)

    def load_config(self, napari_viewer):
        config_path = self.config_textbox.text()
        self.model = LabelClassificationModel(napari_viewer.layers,
                                              config_path)
        self.view = LabelClassificationView(self.model, napari_viewer)
        self.controller = LabelClassificationController(self.model, self.view)

        # Set up the keyboard input and double-click events
        setup_classification_callbacks(self.controller, self.view,
                                       self.model.config)
