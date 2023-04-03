
class LayerVisibilityController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def on_assign_clicked(self, row, key, layer_name):

        # if mapping existis,
        # remove it from the other use and unbind
        if key in self.model.key_to_layer_map:
            self.model.key_to_key_box[key].clear()
            self.view.viewer.bind_key(key, None)

        # in case we removed it from itself
        self.view.rows[row]['key'].setText(key)
        self.model.set_mapping(key, self.view.rows[row]['key'], layer_name)
        self.view.viewer.bind_key(key, lambda x: self.on_keyboard_input(key))

        # hide assign button
        self.view.rows[row]['assign'].hide()

        # update bindings
        self.update_bindings()

    def update_bindings(self):
        # ist of all keys in the widget
        view_keys = [
            self.view.rows[row]['key'].text() for row in self.view.rows]
        model_keys = list(self.model.key_to_layer_map.keys())

        # remove unused keys from model and viewer
        for key in model_keys:
            if key not in view_keys:
                self.model.remove_mapping(key)
                self.view.viewer.bind_key(key, None)

    def on_keyboard_input(self, key):
        layer_name = self.model.key_to_layer_map.get(key)
        # if not in the solo mode, remember the current state of the layers
        # and switch to the solo mode
        if self.model.solo_layer is None:
            self.model.visible_layers = [
                layer.name for layer in self.view.viewer.layers
                if layer.visible]

            if layer_name:
                self.model.solo_layer = layer_name
                self.view.show_only_layer(layer_name)
        # if in the solo mode, restore the previous state of the layers
        # or switch to another solo layer
        else:
            if layer_name == self.model.solo_layer:
                self.model.solo_layer = None
                self.view.restore_all_layers_visibility()
            else:
                self.model.solo_layer = layer_name
                self.view.show_only_layer(layer_name)


