import bpy
from .scene_exporter import export_scene
from bpy.props import CollectionProperty, BoolProperty, StringProperty

bl_info = {
    "name": "Blender Tools",
    "author": "",
    "version": (1, 0, 0),
    "blender": (2, 78, 0),
    "description": "",
    "warning": "",
    "category": "Development"
}

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

g_exporting_scene = False
# dof_distance and fstop are not detected by is_updated.
# So we have to check whether the variables are updated
g_dof_distance = -1
g_fstop = -1
class Panel(bpy.types.Panel):
    bl_label = "blender-tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOL_PROPS"

    def draw(self, context):
        global g_exporting_scene
        if g_exporting_scene:
            self.layout.operator("export.stop",
                                 text="Stop Scene Exporter",
                                 icon='CANCEL')
        else:
            self.layout.operator("export.start",
                                 text="Start Scene Exporter",
                                 icon='PLAY')

class StartExportButtonOperation(bpy.types.Operator):
    bl_idname = "export.start"
    bl_label = "text"

    def execute(self, context):
        global g_exporting_scene
        global g_dof_distance
        global g_fstop
        g_exporting_scene = True
        g_dof_distance = -1
        g_fstop = -1

        print('start')
        user_preferences = bpy.context.user_preferences
        pref = user_preferences.addons[__package__].preferences
        export_scene(pref.out_dir, 'scene.json')
        bpy.app.handlers.scene_update_post.append(scene_update)
        return {'FINISHED'}

class StopExportButtonOperation(bpy.types.Operator):
    bl_idname = "export.stop"
    bl_label = "text"

    def execute(self, context):
        global g_exporting_scene
        g_exporting_scene = False
        print('stop')
        bpy.app.handlers.scene_update_post.remove(scene_update)
        return {'FINISHED'}

def scene_update(context):
    global g_dof_distance
    global g_fstop

    is_updated = False
    if bpy.data.objects.is_updated:
        for ob in bpy.data.objects:
            if ob.is_updated or ob.is_updated_data:
                is_updated = True
        for ob in bpy.data.lamps:
            if ob.is_updated or ob.is_updated_data:
                is_updated = True
        for ob in bpy.data.cameras:
            if ob.is_updated or ob.is_updated_data:
                is_updated = True

    if g_dof_distance != bpy.data.cameras['Camera'].dof_distance:
        is_updated = True
        g_dof_distance = bpy.data.cameras['Camera'].dof_distance
    if g_fstop != bpy.data.cameras['Camera'].gpu_dof.fstop:
        is_updated = True
        g_fstop = bpy.data.cameras['Camera'].gpu_dof.fstop


    if is_updated == False:
        return;
    print('update')
    user_preferences = bpy.context.user_preferences
    pref = user_preferences.addons[__package__].preferences
    export_scene(pref.out_dir, 'scene.json')

def register ():
    bpy.utils.register_class(ToolsPreferences)
    bpy.utils.register_module(__name__)

def unregister ():
    bpy.utils.unregister_class(ToolsPreferences)
    bpy.utils.unregister_module(__name__)
