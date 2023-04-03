class LayerVisibilityModel:
    def __init__(self):
        self.key_to_layer_map = {}
        self.layer_to_key_map = {}

        self.key_to_key_box = {}

        self.solo_layer = None

        self.visible_layers = []

    def set_mapping(self, key, key_box, layer_name):
        self.key_to_layer_map[key] = layer_name
        self.layer_to_key_map[layer_name] = key
        self.key_to_key_box[key] = key_box

    def remove_mapping(self, key):
        layer_name = self.key_to_layer_map[key]
        del self.layer_to_key_map[layer_name]
        del self.key_to_layer_map[key]
        del self.key_to_key_box[key]
