# DataLoaderModel
import os
import yaml
import napari
import numpy as np
import tifffile as tif
from napari.layers import Image, Labels
from qtpy.QtWidgets import QFileDialog
from qtpy.QtWidgets import QWidget, QVBoxLayout, QPushButton, \
    QLabel, QLineEdit, QHBoxLayout


class DataLoaderModel:
    def __init__(self, config_path):
        self.config = self.load_config(config_path)
        self.images = {}
        self.labels = {}

    @staticmethod
    def load_config(config_path):
        with open(config_path, 'r') as config_file:
            config = yaml.unsafe_load(config_file)
        return config

    def load_images(self):
        for img_info in self.config['data']['images']:
            image_data = tif.imread(img_info['path'])
            image = Image(image_data, name=img_info['name'])
            self.images[img_info['name']] = image

    def load_labels(self):
        for lbl_info in self.config['data']['labels']:
            label_data = tif.imread(lbl_info['path'])
            label = Labels(label_data, name=lbl_info['name'], properties={})
            if lbl_info['color'] is not None:
                label.color = self.create_colormap(lbl_info['color'],
                                                   label.data)
            self.labels[lbl_info['name']] = label

    @staticmethod
    def create_colormap(color, data):
        unique_labels = np.unique(data)
        colormap_dict = {label: color for label in unique_labels}
        colormap_dict[0] = 'transparent'
        return colormap_dict

    def process_classifications(self):
        # process each classification group
        for group_dict in self.config['classifications']:
            group = group_dict['classes']
            for class_info in group:
                self.process_class(class_info)

    def _create_labels_layer(self, layer_name, data):
        layer = Labels(data, name=layer_name)
        self.labels[layer_name] = layer
        return layer

    def _assign_labels_layer(self, new_layer_name, layer_to_assign):

        old_layer_name = layer_to_assign.name
        layer_to_assign.name = new_layer_name
        self.labels[new_layer_name] = layer_to_assign
        # remove duplicate layer if it exists
        if old_layer_name != new_layer_name:
            self.labels.pop(old_layer_name)
        return layer_to_assign

    def process_class(self, class_info, parent_class_info=None):
        class_name = class_info['name']
        print(f"Processing {class_name}")
        if parent_class_info is not None:
            parent_class_name = parent_class_info['name']
            layer_name = f"{parent_class_name}:{class_name}"
        else:
            layer_name = f"{class_name}"

        # create label layer if it doesn't exist in loaded labels
        if class_info['labels'] is None:
            label_layer = self._create_labels_layer(
                layer_name,
                np.zeros_like(next(iter(self.labels.values())).data))
        else:
            label_layer = self._assign_labels_layer(
                layer_name,
                self.labels[class_info['labels']])

        # set label layer color or overwrite existing color
        color = class_info['color']
        if color is not None:
            label_layer.color = self.create_colormap(color, label_layer.data)

        if parent_class_info is not None:
            parent_color = parent_class_info['color']
            if parent_color is not None:
                label_layer.color = self.create_colormap(parent_color,
                                                         label_layer.data)

        if 'subclasses' in class_info:
            print(f"Processing subclasses of {class_name}...")
            self.process_subclasses(class_info, class_info['subclasses'])

    def process_subclasses(self, class_info, subclasses_info):
        for subclass_info in subclasses_info:
            self.process_class(subclass_info, class_info)


class DataLoaderView(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        layout = QVBoxLayout()
        self.load_button = QPushButton("Load Images and Labels")
        layout.addWidget(self.load_button)
        self.setLayout(layout)

        self.viewer = napari_viewer


class DataLoaderController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.view.load_button.clicked.connect(self.load_data)

    def load_data(self):
        self.model.load_images()
        self.model.load_labels()
        self.model.process_classifications()

        for image in self.model.images.values():
            self.view.viewer.add_layer(image)

        for label in self.model.labels.values():
            self.view.viewer.add_layer(label)


# _________________________________________________________________
class DataLoaderWidget(QWidget):
    def __init__(self, napari_viewer: 'napari.viewer.Viewer' = None):
        super().__init__()
        config_path = 'D:/Code/repos/napari-U01/data/demo3/' \
                      'classification_config_cell_type_demo.yaml'
        self.model = DataLoaderModel(config_path)
        self.view = DataLoaderView(napari_viewer)
        self.controller = DataLoaderController(self.model, self.view)

        self.setLayout(self.view.layout())
