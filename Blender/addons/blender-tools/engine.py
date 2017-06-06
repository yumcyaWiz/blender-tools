import bpy

g_img_data = [[0, 0, 0, 0]]

def update(img_data):
    global g_img_data
    g_img_data =  img_data

def create(engine, data, scene):
    return ToolsRenderPass(scene)

def render(engine):
    if hasattr(engine, 'render_pass'):
        engine.render_pass.render(engine)

class ToolsRenderPass:
    def __init__(self, scene):
        self.scene = scene

    def render(self, engine):
        global g_img_data
        render_info = self.scene.render
        image_scale = render_info.resolution_percentage / 100.0
        size_x = render_info.resolution_x
        size_y = render_info.resolution_y
        pixel_count = size_x * size_y

        result = engine.begin_result(0, 0, size_x, size_y)
        layer = result.layers[0].passes["Combined"]
        if pixel_count != len(g_img_data):
            layer.rect = [[0.0, 0.0, 1.0, 1.0]] * pixel_count
        else:
            layer.rect = g_img_data
        engine.end_result(result)
