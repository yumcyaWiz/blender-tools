import bpy
from .scene_exporter import get_scene_data, export_scene
from collections import OrderedDict
from ws4py.client.threadedclient import WebSocketClient
import ws4py.messaging
import json
import threading
from io import BytesIO
import struct
from . import engine

bl_info = {
    "name": "Blender Tools",
    "author": "",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
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
        if isinstance(m, ws4py.messaging.TextMessage):
            print("=> %d %s" % (len(m), str(m)))
        elif isinstance(m, ws4py.messaging.BinaryMessage):
            print("=> binary")
            out = BytesIO(m.data)
            img_data = []
            index = 0
            rgba = []
            b = out.read(4)
            while b:
                rgba.append(struct.unpack("f", b)[0])
                if index % 3 == 2:
                    rgba.append(1)
                    img_data.append(rgba)
                    rgba = []
                b = out.read(4)
                index += 1
#            print(img_data)
            out.close()
            # engine.update(img_data)
            th_me = threading.Thread(
                target=bpy.ops.render.render, name="th_me")
            th_me.start()


g_exporting_scene = False
# dof_distance and fstop are not detected by is_updated.
# So we have to check whether the variables are updated
g_dof_distance = -1
g_fstop = -1
g_ws = False
g_ws_connected = False


class TOOLS_PT_Panel(bpy.types.Panel):
    bl_label = "blender-tools"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"

    @classmethod
    def poll(cls, context):
        renderer = context.scene.render
        return renderer.engine == "TOOLS_RENDER"

    def draw(self, context):
        global g_exporting_scene
        if context.scene.render.engine != "TOOLS_RENDER":
            return
        if g_exporting_scene:
            self.layout.operator("export.stop",
                                 text="Stop Scene Exporter",
                                 icon='CANCEL')
        else:
            self.layout.operator("export.start",
                                 text="Start Scene Exporter",
                                 icon='PLAY')


class TOOLS_OT_StartExportButtonOperation(bpy.types.Operator):
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
        g_ws.daemon = True
        try:
            g_ws.connect()
            g_ws_connected = True
        except ConnectionRefusedError:
            print('Connection refused')
        g_exporting_scene = True
        g_dof_distance = -1
        g_fstop = -1

        bpy.app.handlers.depsgraph_update_post.append(scene_update)
        return {'FINISHED'}


class TOOLS_OT_StopExportButtonOperation(bpy.types.Operator):
    bl_idname = "export.stop"
    bl_label = "text"

    def execute(self, context):
        global g_exporting_scene
        global g_ws
        global g_ws_connected
        if g_ws_connected:
            g_ws.close()
        g_ws_connected = False
        g_exporting_scene = False
        print('stop')
        bpy.app.handlers.depsgraph_update_post.remove(scene_update)
        return {'FINISHED'}


g_update_timer = None


def scene_update(context):
    global g_dof_distance
    global g_fstop
    global g_ws
    global g_ws_connected
    global g_update_timer
    is_updated = False

    is_updated = (bpy.data.objects.is_updated or
                  bpy.data.materials.is_updated or
                  bpy.data.lamps.is_updated or
                  bpy.data.cameras.is_updated)

    if g_dof_distance != bpy.data.cameras['Camera'].dof_distance:
        is_updated = True
        g_dof_distance = bpy.data.cameras['Camera'].dof_distance
    if g_fstop != bpy.data.cameras['Camera'].gpu_dof.fstop:
        is_updated = True
        g_fstop = bpy.data.cameras['Camera'].gpu_dof.fstop

    if is_updated == False:
        return
    print('scene was updated')

    def export_data():
        if g_ws_connected:
            send_scene_data(g_ws)
        write_scene_data()

    if g_update_timer is not None:
        g_update_timer.cancel()
    g_update_timer = threading.Timer(0.5, export_data)
    g_update_timer.start()


class ToolsRender(bpy.types.RenderEngine):
    bl_idname = 'TOOLS_RENDER'
    bl_label = 'Blender Tools Preview'
    bl_use_preview = True
    bl_use_save_buffers = True

    def __init__(self):
        self.render_pass = None

    def __del__(self):
        pass
        # if hasattr(engine, 'render_pass') and self.render_pass is not None:
        # del self.render_pass

    def update(self, data, scene):
        print('update')
        # if not self.render_pass:
        # self.render_pass = engine.create(self, data, scene)

    def render(self, scene):
        print('start rendering')
        # if self.render_pass is not None:
        # engine.render(self)


classes = [
    TOOLS_PT_Panel,
    TOOLS_OT_StartExportButtonOperation,
    TOOLS_OT_StopExportButtonOperation,
    ToolsRender
]


def register():
    from . import ui
    ui.register()
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    from . import ui
    ui.unregister()
    for c in classes:
        bpy.utils.unregister_class(c)
