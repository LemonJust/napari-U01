# model
import pandas as pd
from numpy.random import uniform
from napari.layers import Points

# view
from PyQt5.QtWidgets import (QWidget,
                             QVBoxLayout,
                             QLabel,
                             QPushButton,
                             QFileDialog,
                             QSlider,
                             QColorDialog)

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

# widget
from PyQt5.QtWidgets import QWidget


class SynapseModel:
    def __init__(self):
        self.point_layers = {}
        self.is_paired = {}

    def add_points_layer(self, layer_name, point_layer, is_paired=False):
        self.point_layers[layer_name] = point_layer
        self.is_paired[layer_name] = is_paired

    @staticmethod
    def get_points(file_path: str):
        data = pd.read_csv(file_path)
        if data is None:
            return None

        # if the csv file has the columns z, y, x
        if set(data.columns) >= {'z', 'y', 'x'}:
            print("one point cloud")
            return data[['z', 'y', 'x']].values
        
        # if the csv file has the columns z1, y1, x1, z2, y2, x2
        elif set(data.columns) >= {'z1', 'y1', 'x1', 'z2', 'y2', 'x2'}:
            print("two point clouds")
            # create a list of random colors the length of the number of points
            colors = [[uniform(), uniform(), uniform()] for _ in range(len(data))]
            return data[['z1', 'y1', 'x1']].values, data[['z2', 'y2', 'x2']].values, colors
        else:
            print("invalid csv file")
            return None


class SynapseView(QWidget):
    def __init__(self, viewer):
        super().__init__()
        self.viewer = viewer

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.load_csv_button = QPushButton("Load CSV")
        self.layout.addWidget(self.load_csv_button)

        self.refresh_button = QPushButton("Refresh points")
        self.layout.addWidget(self.refresh_button)

    def get_csv_path(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load CSV", "", "CSV Files (*.csv);;All Files (*)",
            options=options)
        return file_path


class SynapseController:
    def __init__(self, model, view):

        self.view = view
        self.model = model

        self.view.load_csv_button.clicked.connect(self.load_csv_and_display_points)
        self.view.refresh_button.clicked.connect(self.update_points_properties)

    def load_csv_and_display_points(self):
        # TODO : create FixedPointsLayer class and use it here instead of Points layer class
        file_path = self.view.get_csv_path()
        if file_path:
            points = self.model.get_points(file_path)

            if points is not None:
                # if it is one point cloud
                print(type(points))
                # if there are two point clouds (paired synapses)
                if isinstance(points, tuple):
                    zyx1, zyx2, colors = points
                    idx = len(self.model.point_layers)
                    # actually add the points to the viewer
                    layer_name = f"synapses_paired_{idx}_tp1"
                    point_layer = self.view.viewer.add_points(zyx1, name=layer_name, size=3, face_color=colors)
                    self.model.add_points_layer(layer_name, point_layer, is_paired=True)

                    # actually add the points to the viewer
                    layer_name = f"synapses_paired_{idx}_tp2"
                    point_layer = self.view.viewer.add_points(zyx2, name=layer_name, size=3, face_color=colors)
                    self.model.add_points_layer(layer_name, point_layer, is_paired=True)
                else:
                    # actually add the points to the viewer
                    layer_name = f"synapses_{len(self.model.point_layers)}"
                    point_layer = self.view.viewer.add_points(points, name=layer_name, size=3)
                    self.model.add_points_layer(layer_name, point_layer)

    def update_points_properties(self):
        for layer_name, point_layer in self.model.point_layers.items():
            # Update the point layer's properties
            point_layer.size = point_layer.current_size
            point_layer.edge_color = point_layer.current_edge_color
            point_layer.edge_width = point_layer.current_edge_width
            # do not update face color if it is a paired synapse layer
            # because the face color is the same for each pair of paired points
            if not self.model.is_paired[layer_name]:
                point_layer.face_color = point_layer.current_face_color

# TODO : turn into a reader https://napari.org/stable/plugins/guides.html
class SynapseWidget(QWidget):
    def __init__(self, napari_viewer: 'napari.viewer.Viewer' = None):
        super().__init__()

        self.model = SynapseModel()
        self.view = SynapseView(napari_viewer)
        self.controller = SynapseController(self.model, self.view)

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)
