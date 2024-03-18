import csv
import numpy as np


# Model
class LabelClassificationModel:
    def __init__(self):
        self.image_data = {}  # {image_name: image_data, ...}
        self.segmentation_data = {}  # {class_name: segmentation_data, ...}

        # label value of the currently selected label
        self.selected = None

        # class-related information
        self.classes = []
        self.labels_per_class = {}
        self.class_colors = None
        self.class_colormaps = {}
        # classification for each label in format:
        # {label: {'class': 'neuron', 'subclass': 'excitatory'}, ...}
        self.classifications = {}

        self.initialize_class_info()

    def initialize_class_info(self):
        # TODO: load this from config file
        self.classes = ['neuron', 'glia', 'background', 'unclassified']

        # initialize labels_per_class dictionary by adding
        # labels from the segmentation data to the corresponding class set
        for class_ in self.classes:
            if class_ in self.segmentation_data:
                self.labels_per_class[class_] = set(
                    np.unique(self.segmentation_data[class_]))
            else:
                self.labels_per_class[class_] = set()

        # initialise classififcations
        for class_ in self.labels_per_class:
            for label in self.labels_per_class[class_]:
                self.classifications[label] = {'class': class_}

        # TODO: load this from config file
        self.class_colors = {
            'neuron': (213 / 255, 0, 249 / 255),
            'glia': (0, 229 / 255, 1),
            'background': (1, 23 / 255, 68 / 255),
            'unclassified': (1, 1, 1)
        }

        for class_ in self.class_colors:
            self.class_colormaps[class_] = {0: 'transparent'}

    @property
    def segmentation_data(self):
        return self._segmentation_data

    @segmentation_data.setter
    def segmentation_data(self, data):
        self._segmentation_data = data
        self.selected = None
        self.classifications = {}

    def classify_label(self, label, class_name, subclass_name=None):
        # if label is already classified first remove it from the
        # labels_per_class dictionary and remove subclass if it exists
        old_class_name = None
        if label in self.classifications:
            old_class_name = self.classifications[label]['class']
            self.labels_per_class[old_class_name].remove(label)
            if 'subclass' in self.classifications[label]:
                del self.classifications[label]['subclass']

        # now change classification
        self.classifications[label] = {'class': class_name}
        self.labels_per_class[class_name].add(label)
        if subclass_name:
            self.classifications[label]['subclass'] = subclass_name

        return old_class_name

    def select_label(self, label):
        self.selected = label

    def deselect_label(self):
        self.selected = None

    def save_classified_labels(self, filename='classified_labels.csv'):
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['ID', 'Class', 'Subclass'])
            for label, classification in self.classifications.items():
                class_name = classification['class']
                subclass_name = classification.get('subclass', '')
                writer.writerow([label, class_name, subclass_name])
