import bpy

# enable default ui for Scene settings
import bl_ui.properties_render as properties_render
properties_render.RENDER_PT_render.COMPAT_ENGINES.add('TOOLS_RENDER')
properties_render.RENDER_PT_dimensions.COMPAT_ENGINES.add('TOOLS_RENDER')

## enable default ui for Material
import bl_ui.properties_material as properties_material
properties_material.MATERIAL_PT_context_material.COMPAT_ENGINES.add('TOOLS_RENDER')
#properties_material.MATERIAL_PT_preview.COMPAT_ENGINES.add('TOOLS_RENDER')
properties_material.MATERIAL_PT_diffuse.COMPAT_ENGINES.add('TOOLS_RENDER')
#properties_material.MATERIAL_PT_custom_props.COMPAT_ENGINES.add('TOOLS_RENDER')
del properties_material

## enable default ui for Textures
import bl_ui.properties_texture as properties_texture
properties_texture.TEXTURE_PT_context_texture.COMPAT_ENGINES.add('TOOLS_RENDER')
properties_texture.TEXTURE_PT_preview.COMPAT_ENGINES.add('TOOLS_RENDER')
properties_texture.TEXTURE_PT_image.COMPAT_ENGINES.add('TOOLS_RENDER')

# enable default ui for Lamp
import bl_ui.properties_data_lamp as properties_data_lamp
properties_data_lamp.DATA_PT_context_lamp.COMPAT_ENGINES.add('TOOLS_RENDER')
properties_data_lamp.DATA_PT_spot.COMPAT_ENGINES.add('TOOLS_RENDER')
properties_data_lamp.DATA_PT_area.COMPAT_ENGINES.add('TOOLS_RENDER')
properties_data_lamp.DATA_PT_lamp.COMPAT_ENGINES.add('TOOLS_RENDER')
#properties_data_lamp.DATA_PT_sun.COMPAT_ENGINES.add('TOOLS_RENDER')

## enable default ui for camera
import bl_ui.properties_data_camera as properties_data_camera
properties_data_camera.DATA_PT_camera.COMPAT_ENGINES.add('TOOLS_RENDER')
properties_data_camera.DATA_PT_lens.COMPAT_ENGINES.add('TOOLS_RENDER')
properties_data_camera.DATA_PT_camera_dof.COMPAT_ENGINES.add('TOOLS_RENDER')

from bpy.props import CollectionProperty, BoolProperty, StringProperty

def Tools_menu(self, context):
    if context.scene.render.engine != "TOOLS_RENDER":
        return
    self.layout.separator()

class ToolsPreferences (bpy.types.AddonPreferences):
    bl_idname = __package__
    out_dir = StringProperty(
        name = "Path to scene file folder",
        description = "Path to scene file folder",
        subtype = "DIR_PATH",
        default='/tmp/'
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "out_dir")


class ToolsRenderPanelBase(object):
    bl_context = "render"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render
        return renderer.engine == "TOOLS_RENDER"

class ToolsRenderSettingsPanel(bpy.types.Panel, ToolsRenderPanelBase):
    COMPAT_ENGINES = { 'TOOLS_RENDER' }
    bl_label = "Settings"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

def register():
    bpy.types.INFO_MT_render.append(Tools_menu)
    bpy.utils.register_class(ToolsPreferences)
    bpy.utils.register_class(ToolsRenderSettingsPanel)

def unregister():
    bpy.utils.unregister_class(ToolsPreferences)
    bpy.utils.unregister_class(ToolsRenderSettingsPanel)
