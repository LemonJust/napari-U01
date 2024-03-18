import csv
import numpy as np
import yaml
from napari.layers import Labels


# Model
class LabelClassificationModel:
    def __init__(self, layers, config_path=None):

        self.config = {}
        if config_path is not None:
            self.load_config(config_path)

        # segmentation data in format:
        # {class_name: np.ndarray, ...}
        # will put all labels in layers into segmentation data
        self.segmentation_data = {}
        # summary image of all labels: all labels in one array
        self.segmentation_summary_image = None
        self.init_segmentation_data(layers)

        # label value of the currently selected label
        self.selected = None

        # class-related information
        self.group_names = []
        self.class_names = []
        self.classes_per_group = {}
        self.class_per_key = {}

        # label-related information
        self.labels_per_class = {}
        # {label: {'class': 'neuron', 'subclass': 'excitatory'}, ...}
        self.class_per_label = {}

        # color information
        self.class_colors = {}
        self.class_colormaps = {}

        self.init_class_info()
        self.init_labels_per_class()
        self.init_class_per_label()
        self.init_class_colormaps()
        self.init_segmentation_summary_image()

    def load_config(self, config_path):
        with open(config_path, 'r') as config_file:
            config = yaml.unsafe_load(config_file)
        self.config = config

    def init_class_info(self):
        for group in self.config['classifications']:
            for classification in group['classes']:
                name = classification['name']
                color = classification['color']
                key = classification['key']

                self.class_names.append(name)
                self.class_per_key[key] = name
                self.class_colors[name] = color

                if 'subclasses' in classification:
                    for subclass in classification['subclasses']:
                        sub_name = f"{name}:{subclass['name']}"
                        sub_color = subclass['color']
                        sub_key = subclass['key']

                        self.class_names.append(sub_name)
                        self.class_per_key[sub_key] = sub_name
                        if sub_color is not None:
                            self.class_colors[sub_name] = sub_color
                        else:
                            self.class_colors[sub_name] = color

    def init_segmentation_data(self, layers):
        for layer in layers:
            if isinstance(layer, Labels):
                self.segmentation_data[layer.name] = layer.data

    def init_segmentation_summary_image(self):
        class_name = self.class_names[0]
        self.segmentation_summary_image = np.zeros(
            self.segmentation_data[class_name].shape, dtype=np.uint16)

        for class_name in self.class_names:
            class_data = self.segmentation_data[class_name]
            # assert that segmentation labels do not overlap between classes
            assert np.sum(
                self.segmentation_summary_image[class_data > 0]) == 0, \
                "Segmentation labels overlap between classes!"
            # add labels to summary image
            self.segmentation_summary_image += class_data

    def init_labels_per_class(self):
        for class_name in self.class_names:
            if class_name in self.segmentation_data:
                self.labels_per_class[class_name] = set(
                    np.unique(self.segmentation_data[class_name]))
            else:
                self.labels_per_class[class_name] = set()

    def init_class_per_label(self):
        for class_name in self.class_names:
            for label in self.labels_per_class[class_name]:
                self.class_per_label[label] = {'class': class_name}

    def init_class_colormaps(self):
        for class_name in self.class_names:
            self.class_colormaps[class_name] = {}
            for label in self.labels_per_class[class_name]:
                self.class_colormaps[class_name][label] = self.class_colors[
                    class_name]
            self.class_colormaps[class_name][0] = 'transparent'

    def update_class_colormap(self, class_name, label):
        # adds a new label to the class colormap
        self.class_colormaps[class_name][label] = self.class_colors[
            class_name]

    def classify_label(self, label, class_name):
        print(f"Classifying label {label} as {class_name}.")
        print(f"Old class: {self.class_per_label[label]['class']}.")

        # first remove it from the old class
        old_class_name = self.class_per_label[label]['class']
        self.labels_per_class[old_class_name].remove(label)

        # now change classification
        self.class_per_label[label] = {'class': class_name}
        self.labels_per_class[class_name].add(label)

        print(f"New class: {self.class_per_label[label]['class']}.")

        return old_class_name

    def save_classified_labels(self, filename='classified_labels.csv'):
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['ID', 'Class', 'Subclass'])
            for label, classification in self.class_per_label.items():
                class_name = classification['class']
                subclass_name = ''
                if ":" in class_name:
                    class_name, subclass_name = class_name.split(":")
                writer.writerow([label, class_name, subclass_name])

    def select_label(self, label):
        self.selected = label

    def deselect_label(self):
        self.selected = None
