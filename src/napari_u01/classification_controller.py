from PyQt5.QtWidgets import QWidget, \
    QVBoxLayout, QListWidget, QLabel, QFileDialog
import csv


class LabelClassificationController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def on_label_selection(self, coordinates):
        label = self.model.segmentation_summary_image[tuple(coordinates)]
        print(f'Label selected: {label} at {coordinates}')
        if label == 0:
            self.view.unhighlight_label()
            self.model.deselect_label()
        else:
            # highlight the row with the corresponding ID in the table
            self.view.label_list.select_label(label)
            # update the view and model
            self.view.highlight_label(label)
            self.model.select_label(label)

    def on_keyboard_input(self, key):
        print(f'Key pressed: {key}')
        label = self.model.selected
        if label is not None:
            # if escape, deselect label
            if key == 'Escape':
                self.model.deselect_label()
                self.view.unhighlight_label()
            else:
                class_name = self.model.class_per_key[key]
                old_class_name = self.model.classify_label(label, class_name)

            if key in list(self.model.class_per_key.keys()):
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
