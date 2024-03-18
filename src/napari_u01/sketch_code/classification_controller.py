from PyQt5.QtWidgets import QWidget, \
    QVBoxLayout, QListWidget, QLabel, QFileDialog
import csv


class LabelClassificationController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def on_label_selection(self, label):
        if label != 0:
            self.view.highlight_label(label)
            self.model.select_label(label)

    def on_keyboard_input(self, key):
        # hide 'unclassified', 'neuron', 'glia', 'background' layers
        if key == 's':
            if self.view.segmentation_hidden:
                self.view.restore_layers_visibility()
            else:
                self.view.hide_segmentation_layers()

        # classify label
        label = self.model.selected
        if label is not None:
            if key == 'g':
                old_class_name = self.model.classify_label(label, 'glia')
            elif key == 'n':
                old_class_name = self.model.classify_label(label, 'neuron')
            elif key == 'e':
                old_class_name = self.model.classify_label(label, 'neuron',
                                                           'excitatory')
            elif key == 'i':
                old_class_name = self.model.classify_label(label, 'neuron',
                                                           'inhibitory')
            elif key == 'Delete':
                old_class_name = self.model.classify_label(label, 'background')
            # if escape, deselect label
            elif key == 'Escape':
                self.model.deselect_label()
                self.view.unhighlight_label()

            if key in ['g', 'n', 'e', 'i', 'Delete']:
                # Update the view
                self.view.update_label_layers(label, old_class_name)
                self.view.update_classified_labels_list()

    def on_double_click_label(self, item):
        # when label is double-clicked in the table
        label = self.view.label_list.get_selected_id()

        # Update the view
        self.view.move_viewer_to_label(label)
        self.view.highlight_label(label)
        self.model.select_label(label)

    def on_save_button_click(self):
        filename, _ = QFileDialog.getSaveFileName(self.view.label_list,
                                                  'Save to CSV', '',
                                                  'CSV Files (*.csv)')
        if filename:
            self.model.save_classified_labels(filename)
