import tifffile as tif
import numpy as np


def demo_data():
    # Create example image and segmentation data
    # read the data from folder
    data_path = "D:/Code/repos/napari-U01/data/"
    image_data = tif.imread(data_path + 'nuclei_img.tif')
    neuron_data = tif.imread(data_path + 'neuron_img.tif')
    segmentation_data = tif.imread(data_path + 'nuclei_labels.tif')
    return image_data, segmentation_data, neuron_data


def split_segmentation_into_classes(segmentation_data, classes):
    # get all labels
    labels = np.unique(segmentation_data)
    labels = labels[labels != 0]
    n_labels = len(labels)

    segmentation_classes = {}

    # for each class, get some random labels and
    # create a new image with these labels only
    # labels in different classes can not overlap
    for class_name in classes:
        segmentation_classes[class_name] = np.zeros_like(segmentation_data)
        n_labels_to_select = int(n_labels / len(classes))
        selected_labels = np.random.choice(labels, n_labels_to_select)
        for label in selected_labels:
            segmentation_classes[class_name][segmentation_data == label] = \
                label
        labels = np.setdiff1d(labels, selected_labels)

    return segmentation_classes


def prepare_demo3():
    # Create example image and segmentation data
    segmentation_file = 'D:/Code/repos/napari-U01/data/demo3/all_labels.tif'
    segmentation_data = tif.imread(segmentation_file)
    bg = np.min(segmentation_data)
    segmentation_data[segmentation_data == bg] = 0

    # split segmentation into classes
    classes_and_subclasses = ['neuron', 'glia',
                              'background', 'nuclei',
                              'excitatory', 'inhibitory']
    segmentation_classes = split_segmentation_into_classes(
        segmentation_data, classes_and_subclasses)

    # save the segmentation classes
    for class_name, segmentation_class in segmentation_classes.items():
        tif.imwrite('D:/Code/repos/napari-U01/data/'
                    'demo3/demo_' + class_name + '_labels.tif',
                    segmentation_class)


if __name__ == '__main__':
    prepare_demo3()
