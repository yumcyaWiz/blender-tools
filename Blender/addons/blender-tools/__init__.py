import bpy
from .scene_exporter import export_camera, export_lights

bl_info = {
    "name": "Blender tools",
    "author": "",
    "version": (1, 0, 0),
    "blender": (2, 78, 0),
    "location": "Info Header, render engine menu",
    "description": "",
    "warning": "",
    "category": "Render"
}

class Panel(bpy.types.Panel):
    bl_label = "blender-tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOL_PROPS"

    def draw(self, context):
        self.layout.operator("tools.export",
                             text="Start Export",
                             icon='PLAY')

class ExportButtonOperation(bpy.types.Operator):
    bl_idname = "tools.export"
    bl_label = "text"
    def execute(self, context):
        bpy.app.handlers.scene_update_post.append(scene_update)
        return {'FINISHED'}

def scene_update(context):
    print('update')

def register ():
    bpy.utils.register_module(__name__)

def unregister ():
    bpy.utils.unregister_module(__name__)
