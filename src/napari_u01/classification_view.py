import numpy as np
import csv

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

# name of the highlight layer
HL_NAME = '_hightlight'


class TableView(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.table = QtWidgets.QTableWidget()
        self.table.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectRows)
        self.table.setSelectionMode(
            QtWidgets.QAbstractItemView.SingleSelection)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['ID', 'Class', 'Subclass'])
        self.table.setSortingEnabled(True)
        self.table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

        # Set the size policy for the table
        policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                       QtWidgets.QSizePolicy.Expanding)
        self.table.setSizePolicy(policy)

        # Set the layout for the widget
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.table)

        # Add a button to save the table data to a CSV file
        self.save_button = QtWidgets.QPushButton('Save to CSV')
        layout.addWidget(self.save_button)

        # Connect the double-click event to the on_double_click method
        # self.table.cellDoubleClicked.connect(self.on_double_click)

    def populate(self, data_dict):
        self.table.setRowCount(len(data_dict))
        for row, (id_, classification) in enumerate(data_dict.items()):
            class_name = classification['class']
            subclass_name = ''
            if ":" in class_name:
                class_name, subclass_name = class_name.split(":")
                # print(f"subclass found: {subclass_name}")

            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(str(id_)))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(class_name))
            self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(subclass_name))
            for col in range(self.table.columnCount()):
                self.table.item(row, col).setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

    def clear(self):
        self.table.setRowCount(0)

    def get_selected_id(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            return None
        return int(self.table.item(selected_row, 0).text())

    def select_label(self, label):
        for row in range(self.table.rowCount()):
            if int(self.table.item(row, 0).text()) == label:
                self.table.selectRow(row)
                break

    # not used at the moment, using model.save_classified_labels instead
    # but might be useful in the future to save with the
    # exact order of the labels in the table being displayed
    def save_to_csv(self, filename):
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['ID', 'Class', 'Subclass'])
            for row in range(self.table.rowCount()):
                id_ = self.table.item(row, 0).text()
                class_ = self.table.item(row, 1).text()
                subclass = self.table.item(row, 2).text()
                writer.writerow([id_, class_, subclass])


# View
class LabelClassificationView:
    def __init__(self, model, napari_viewer):
        self.model = model
        self.viewer = napari_viewer

        # Create a separate window for the list of classified labels
        self.label_list_window = QWidget()
        self.label_list_window.setWindowTitle('Classified Labels')
        layout = QVBoxLayout()

        self.label_list_label = QLabel('Classified Labels:')
        self.label_list = TableView()

        layout.addWidget(self.label_list_label)
        layout.addWidget(self.label_list)
        self.label_list_window.setLayout(layout)
        self.label_list_window.show()

        # keep track of the layers that are visible
        # when changing visibility from code
        self.segmentation_hidden = False
        self.visible_layers = None
        self.update_visible_layers()

    def update_label_layers(self, label, old_class_name=None):
        """
        Update the label layers when a label is classified or reclassified to
        a different class.
        """
        # Remove the label from old class layer
        segmentation_layer = self.viewer.layers[old_class_name]
        mask = segmentation_layer.data == label
        segmentation_layer.data[mask] = 0
        segmentation_layer.refresh()

        # Add the label to the new class layer
        label_class = self.model.class_per_label[label]['class']
        segmentation_layer = self.viewer.layers[label_class]
        segmentation_layer.data[mask] = label

        # update colormap of the new class layer
        self.model.update_class_colormap(label_class, label)
        segmentation_layer.color = self.model.class_colormaps[label_class]

        # refresh the layer to update the display
        segmentation_layer.refresh()

    def update_classified_labels_list(self):
        # Update the list of classified labels in the separate window
        self.label_list.clear()
        self.label_list.populate(self.model.class_per_label)

    def move_viewer_to_label(self, label):
        # Move the viewer to the center of the given label and zoom to the
        # specified box size
        label_class = self.model.class_per_label[label]['class']
        segmentation_layer = self.viewer.layers[label_class]
        mask = segmentation_layer.data == label
        z, y, x = np.where(mask)

        if z.size > 0 and y.size > 0 and x.size > 0:
            center_z, center_y, center_x = np.mean(z), np.mean(y), np.mean(x)
            # camera.center: In 2D viewing only the last two values are used,
            # so setting the x and y
            self.viewer.camera.center = (center_z, center_y, center_x)
            # setting z
            self.viewer.dims.set_point(0, center_z)
        else:
            print(f"Label {label} not found in {label_class} data.")

    def highlight_label(self, label):
        # looks like partseg highlights labels by adding a new layer too!
        # https://github.com/napari/napari/issues/3727

        label_class = self.model.class_per_label[label]['class']
        segmentation_layer = self.viewer.layers[label_class]
        mask = segmentation_layer.data == label

        segmentation_layer.selected_label = label

        highlighted_labels = np.zeros_like(segmentation_layer.data)
        highlighted_labels[mask] = 1  # label

        # create a highlight layer if it doesn't exist yet
        if HL_NAME not in self.viewer.layers:
            self.viewer.add_labels(highlighted_labels,
                                   name=HL_NAME,
                                   blending='additive',
                                   color={0: 'transparent', 1: 'white'})
        else:
            self.viewer.layers[HL_NAME].data = highlighted_labels
        self.viewer.layers[HL_NAME].refresh()

        # select segmentation_layer layer to be active instead of highlight
        self.viewer.layers.selection.active = segmentation_layer

    def unhighlight_label(self):
        # remove label from _highlight layer if it exists
        if HL_NAME in self.viewer.layers:
            segmentation_layer = self.viewer.layers[HL_NAME]
            segmentation_layer.data[segmentation_layer.data == 1] = 0
            segmentation_layer.refresh()

    def update_visible_layers(self):
        self.visible_layers = set()
        for layer in self.viewer.layers:
            if layer.visible:
                self.visible_layers.add(layer.name)