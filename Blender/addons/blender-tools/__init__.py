import bpy
from .scene_exporter import get_scene_data, export_scene
from collections import OrderedDict
from bpy.props import CollectionProperty, BoolProperty, StringProperty
from ws4py.client.threadedclient import WebSocketClient
import json

bl_info = {
    "name": "Blender Tools",
    "author": "",
    "version": (1, 0, 0),
    "blender": (2, 78, 0),
    "description": "",
    "warning": "",
    "category": "Development"
}

def make_RPC_data(params):
    data = OrderedDict()
    data['jsonrpc'] = "2.0"
    data["method"] = "render"
    data["params"] = params
    return data

def send_scene_data(ws):
    scene_data = get_scene_data()
    ws.send(json.dumps(make_RPC_data(scene_data), indent=4))

def write_scene_data():
    user_preferences = bpy.context.user_preferences
    pref = user_preferences.addons[__package__].preferences
    export_scene(pref.out_dir, 'scene.json')

class WSClient(WebSocketClient):
    def opened(self):
        print("Connected")

    def closed(self, code, reason):
        print(("Closed down", code, reason))

    def received_message(self, m):
        print("=> %d %s" % (len(m), str(m)))

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
g_ws = False
g_ws_connected = False
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
        global g_ws
        global g_ws_connected
        g_ws = WSClient('ws://localhost:8081/websocket',
                        protocols=['http-only', 'chat'])
        g_ws.daemon = False
        try:
            g_ws.connect()
            g_ws_connected = True
        except ConnectionRefusedError:
            print('Connection refused')
        g_exporting_scene = True
        g_dof_distance = -1
        g_fstop = -1

        print('start')
        if g_ws_connected:
            send_scene_data(g_ws)
        write_scene_data()
        bpy.app.handlers.scene_update_post.append(scene_update)
        return {'FINISHED'}

class StopExportButtonOperation(bpy.types.Operator):
    bl_idname = "export.stop"
    bl_label = "text"

    def execute(self, context):
        global g_exporting_scene
        global g_ws
        g_ws.close()

        g_exporting_scene = False
        print('stop')
        bpy.app.handlers.scene_update_post.remove(scene_update)
        return {'FINISHED'}

def scene_update(context):
    global g_dof_distance
    global g_fstop
    global g_ws
    global g_ws_connected
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
    print('scene was updated')
    if g_ws_connected:
        send_scene_data(g_ws)
    write_scene_data()

def register ():
    bpy.utils.register_class(ToolsPreferences)
    bpy.utils.register_module(__name__)

def unregister ():
    bpy.utils.unregister_class(ToolsPreferences)
    bpy.utils.unregister_module(__name__)
