from typing import TYPE_CHECKING
import numpy as np

from .classification_model import LabelClassificationModel
from .classification_view import LabelClassificationView
from .classification_controller import LabelClassificationController

from .demo import demo_data

import napari
from PyQt5.QtWidgets import QWidget

if TYPE_CHECKING:
    import napari


# Connect the keyboard input and double-click events to the controller
def setup_classification_callbacks(controller, view):
    # connect all the keyboard inputs to the controller
    # https://forum.image.sc/t/napari-keypressevent/63658
    # for key in ['g', 'n', 'e', 'i', 'b', 'Escape']:
    #     view.viewer.bind_key(key, controller.on_keyboard_input(key))
    # for some reason the method above doesn't work
    # ...so I'm using the method below instead ... even though it's uglier
    # TODO : figure out why the method above doesn't work
    @view.viewer.bind_key('Escape')
    def key_escape(viewer):
        controller.on_keyboard_input('Escape')

    @view.viewer.bind_key('n')
    def key_n(viewer):
        controller.on_keyboard_input('n')

    @view.viewer.bind_key('g')
    def key_g(viewer):
        controller.on_keyboard_input('g')

    @view.viewer.bind_key('e')
    def key_e(viewer):
        controller.on_keyboard_input('e')

    @view.viewer.bind_key('i')
    def key_i(viewer):
        controller.on_keyboard_input('i')

    @view.viewer.bind_key('Delete')
    def key_b(viewer):
        controller.on_keyboard_input('Delete')

    @view.viewer.bind_key('s')
    def key_s(viewer):
        controller.on_keyboard_input('s')

    # view.label_list.itemDoubleClicked.connect(
    #     controller.on_double_click_label)
    view.label_list.table.cellDoubleClicked.connect(
        controller.on_double_click_label)
    view.label_list.save_button.clicked.connect(
        controller.on_save_button_click)

    @view.viewer.layers['unclassified'].mouse_drag_callbacks.append
    def select_label(layer, event):
        coordinates = np.round(event.position).astype(int)
        # label value at the current coordinates
        label = layer.data[tuple(coordinates)]
        controller.on_label_selection(label)

    @view.viewer.layers['neuron'].mouse_drag_callbacks.append
    def select_label(layer, event):
        coordinates = np.round(event.position).astype(int)
        # label value at the current coordinates
        label = layer.data[tuple(coordinates)]
        controller.on_label_selection(label)

    @view.viewer.layers['glia'].mouse_drag_callbacks.append
    def select_label(layer, event):
        coordinates = np.round(event.position).astype(int)
        # label value at the current coordinates
        label = layer.data[tuple(coordinates)]
        controller.on_label_selection(label)

    @view.viewer.layers['background'].mouse_drag_callbacks.append
    def select_label(layer, event):
        coordinates = np.round(event.position).astype(int)
        # label value at the current coordinates
        label = layer.data[tuple(coordinates)]
        controller.on_label_selection(label)


class LabelClassificationWidget(QWidget):
    def __init__(self, napari_viewer: 'napari.viewer.Viewer' = None):
        super().__init__()
        self.model = LabelClassificationModel()
        self.view = LabelClassificationView(self.model, napari_viewer)
        self.controller = LabelClassificationController(self.model, self.view)

        # Load the 3D images (three-channel image and segmentation) into the
        img, label, neuron = demo_data()
        self.model.image_data = img  # load_image_data()
        self.model.segmentation_data = label  # load_segmentation_data()
        n_unique_labels = len(np.unique(self.model.segmentation_data))

        # Add the images to the napari viewer
        self.view.viewer.add_image(self.model.image_data,
                                   name='nuclei data')
        self.view.viewer.add_image(neuron,
                                   name='neuron data')
        self.view.viewer.add_labels(self.model.segmentation_data,
                                    name='unclassified')
        # create zero layers for the classified labels
        self.view.viewer.add_labels(
            np.zeros_like(self.model.segmentation_data), name='neuron')
        self.view.viewer.add_labels(
            np.zeros_like(self.model.segmentation_data), name='glia')
        self.view.viewer.add_labels(
            np.zeros_like(self.model.segmentation_data), name='background',
            visible=False)

        # select the unclassified layer
        self.view.viewer.layers.selection.active = self.view.viewer.layers[
            'unclassified']

        # Setup the keyboard input and double-click events
        setup_classification_callbacks(self.controller, self.view)

