import bpy
from collections import OrderedDict
from mathutils import Vector, Matrix
import math
import json
from functools import reduce
import os


def vec2array(_vector):
    return [_vector.x, _vector.z, -_vector.y]


def unit(vec):
    vec_sq = [x for x in map(lambda x:x*x, vec)]
    length = math.sqrt(reduce(lambda x, y: x + y, vec_sq))
    return [x for x in map(lambda x: x / length, vec)]


def get_scene_data():
    scene_data = OrderedDict()
    scene_data['resolutionX'] = bpy.data.scenes['Scene'].render.resolution_x
    scene_data['resolutionY'] = bpy.data.scenes['Scene'].render.resolution_y
    scene_data['resolutionPercentage'] = bpy.data.scenes['Scene'].render.resolution_percentage
    scene_data.update(export_camera())
    scene_data.update(export_lights())
    scene_data.update(export_shapes())
    return scene_data


def pbrt_string(scene_data):
    camera = scene_data['camera']

    ret = ""
    # lookat transform
    ox = camera['location'][0]
    oy = camera['location'][1]
    oz = camera['location'][2]
    lx = camera['lookat'][0]
    ly = camera['lookat'][1]
    lz = camera['lookat'][2]
    ux = camera['up'][0]
    uy = camera['up'][1]
    uz = camera['up'][2]
    ret += "LookAt {0} {1} {2} {3} {4} {5} {6} {7} {8}\n".format(
        ox, oy, oz, lx, ly, lz, ux, uy, uz)

    # film
    resx = scene_data['resolutionX']
    resy = scene_data['resolutionY']
    filmx = 1e-3 * camera['sensorWidth']
    filmy = 1e-3 * camera['sensorHeight']
    diagonal = math.sqrt(filmx * filmx + filmy * filmy)
    ret += 'Film "image" "integer xresolution" [ {0} ] "integer yresolution" [ {1} ] "float diagonal" [ {2} ] "string filename" [ "pbrt.exr" ]\n'.format(
        resx, resy, diagonal)

    # camera
    fov = camera['fov']
    ret += 'Camera "perspective" "float fov" [ {0} ]\n'.format(fov)

    return ret


def export_scene(outdir, filename):
    scene_data = get_scene_data()

    # JSON output
    outfilename = os.path.join(outdir, filename + '.json')
    f = open(outfilename, "w")
    f.write(json.dumps(scene_data, indent=4))
    f.close()

    # PBRT output
    outfilename = os.path.join(outdir, filename + '.pbrt')
    f = open(outfilename, "w")
    f.write(pbrt_string(scene_data))
    f.close()


def export_camera():
    obj_camera = bpy.data.objects["Camera"]
    loc_camera = obj_camera.matrix_world.translation
    camera_param = OrderedDict()
    camera_param['location'] = vec2array(obj_camera.matrix_world.translation)
    camera_param['rotation'] = vec2array(obj_camera.rotation_euler)
    camera_param['lookat'] = vec2array(
        (obj_camera.matrix_world @ Vector((0, 0, -1, 1))).xyz)
    camera_param['fov'] = bpy.data.cameras['Camera'].angle * 180 / math.pi
    camera_param['lens'] = bpy.data.cameras['Camera'].lens
    camera_param['sensorWidth'] = bpy.data.cameras['Camera'].sensor_width
    camera_param['sensorHeight'] = bpy.data.cameras['Camera'].sensor_height
    camera_param['dofDistance'] = bpy.data.cameras['Camera'].dof.focus_distance
    camera_param['fStop'] = bpy.data.cameras['Camera'].dof.aperture_fstop
    camera_param['up'] = vec2array(
        (obj_camera.matrix_world @ Vector((0, 1, 0, 0))).xyz)

    camera_data = OrderedDict()
    camera_data['camera'] = camera_param
    return camera_data


def export_shapes():
    shapes = OrderedDict()
    shapes['shapes'] = []
    for obj in bpy.data.objects:
        obj_type = obj.type
        if obj_type != 'MESH':
            continue
        obj_data = OrderedDict()
        obj_data['name'] = obj.name
        if len(obj.material_slots) > 0:
            mat = obj.material_slots[0].material
            obj_data['material'] = OrderedDict()
            obj_data['material']['name'] = mat.name
            obj_data['material']['diffuseColor'] = [
                c for c in mat.diffuse_color]
        shapes['shapes'].append(obj_data)
    return shapes


def export_lights():
    lights = []
    for light in bpy.data.lights:
        light_data = OrderedDict()
        type_name = str(light.type)
        light_data['type'] = type_name
        if bpy.data.objects.find(light.name) == -1:
            continue
        light_obj = bpy.data.objects[light.name]
        if type_name == 'POINT':
            light_data['position'] = vec2array(light_obj.location)
            light_data['color'] = [c for c in light.color]
            light_data['energy'] = light.energy
        elif type_name == 'SPOT':
            position = vec2array(light_obj.location)
            light_data['position'] = position
            light_data['color'] = [c for c in light.color]
            light_data['energy'] = light.energy
            lookat = vec2array(
                (light_obj.matrix_world @ Vector((0, 0, -1, 1))).xyz)
#            direction = [x - y for (x, y) in zip(lookat, light_data['location'])]
#            light_data['direction'] = direction

            light_data['direction'] = unit(
                [d for d in map(lambda x, y: x - y, lookat, position)])
            light_data['spotSize'] = light.spot_size
            light_data['spotBlend'] = light.spot_blend
        elif type_name == 'SUN':
            light_data['type'] = 'DIRECTIONAL'
            light_data['color'] = [c for c in light.color]
            light_data['energy'] = light.energy
            lookat = vec2array(
                (light_obj.matrix_world @ Vector((0, 0, -1, 1))).xyz)
            position = vec2array(light_obj.location)
            light_data['direction'] = unit(
                [d for d in map(lambda x, y: x - y, lookat, position)])
        elif type_name == 'AREA':
            light_data['type'] = 'AREA'
            position = vec2array(light_obj.location)
            light_data['position'] = position
            light_data['color'] = [c for c in light.color]
            light_data['energy'] = light.energy
            lookat = vec2array(
                (light_obj.matrix_world @ Vector((0, 0, -1, 1))).xyz)
            light_data['direction'] = unit(
                [d for d in map(lambda x, y: x - y, lookat, position)])

            light_data['rotation'] = vec2array(light_obj.rotation_euler)
            light_data['size'] = light.size
        lights.append(light_data)

    data = OrderedDict()
    data['lights'] = lights
    return data
