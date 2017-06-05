import bpy

def create(engine, data, scene):
    return ToolsRenderPass(scene)

def render(engine):
    if hasattr(engine, 'render_pass'):
        engine.render_pass.render(engine)

class ToolsRenderPass:
    def __init__(self, scene):
        self.scene = scene

    def render(self, engine):
        render_info = self.scene.render
        image_scale = render_info.resolution_percentage / 100.0
        size_x = render_info.resolution_x
        size_y = render_info.resolution_y
        pixel_count = size_x * size_y

        blue_rect = [[0.0, 0.0, 1.0, 1.0]] * pixel_count

        result = engine.begin_result(0, 0, size_x, size_y)
        layer = result.layers[0].passes["Combined"]
        layer.rect = blue_rect
        engine.end_result(result)
