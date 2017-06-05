import bpy
from .scene_exporter import get_scene_data, export_scene
from collections import OrderedDict
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

class ToolsRender(bpy.types.RenderEngine):
    bl_idname = 'TOOLS_RENDER'
    bl_label = 'Blender Tools Preview'
    bl_use_preview = True
    bl_use_save_buffers = True

    # Simple Render Engine Example
    # https://docs.blender.org/api/blender_python_api_current/bpy.types.RenderEngine.html
    def render(self, scene):
        scale = scene.render.resolution_percentage / 100.0
        self.size_x = int(scene.render.resolution_x * scale)
        self.size_y = int(scene.render.resolution_y * scale)

        self.render_scene(scene)

    def render_scene(self, scene):
        pixel_count = self.size_x * self.size_y

        blue_rect = [[0.0, 0.0, 1.0, 1.0]] * pixel_count

        result = self.begin_result(0, 0, self.size_x, self.size_y)
        layer = result.layers[0].passes["Combined"]
        layer.rect = blue_rect
        self.end_result(result)

def register ():
    from . import ui

    ui.register()
    bpy.utils.register_module(__name__)

def unregister ():
    from . import ui

    ui.unregister()
    bpy.utils.unregister_module(__name__)
