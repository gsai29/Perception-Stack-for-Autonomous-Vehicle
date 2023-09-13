import bpy
import numpy as np
import mathutils
import math
import json
import re
import os

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()

# Get the active scene
scene = bpy.context.scene


#########################################   FUNCTIONS  #############################################
def mega_purge():
    orphan_ob = [o for o in bpy.data.objects if not o.users]
    while orphan_ob:
        bpy.data.objects.remove(orphan_ob.pop())
        
    orphan_mesh = [m for m in bpy.data.meshes if not m.users]
    while orphan_mesh:
        bpy.data.meshes.remove(orphan_mesh.pop())
        
    orphan_mat = [m for m in bpy.data.materials if not m.users]
    while orphan_mat:
        bpy.data.materials.remove(orphan_mat.pop())

    def purge_node_groups():   
        orphan_node_group = [g for g in bpy.data.node_groups if not g.users]
        while orphan_node_group:
            bpy.data.node_groups.remove(orphan_node_group.pop())
        if [g for g in bpy.data.node_groups if not g.users]: purge_node_groups()
    purge_node_groups()
        
    orphan_texture = [t for t in bpy.data.textures if not t.users]
    while orphan_texture:
        bpy.data.textures.remove(orphan_texture.pop())

    orphan_images = [i for i in bpy.data.images if not i.users]
    while orphan_images:
        bpy.data.images.remove(orphan_images.pop())

    orphan_cameras = [c for c in bpy.data.cameras if not c.users]
    while orphan_cameras :
        bpy.data.cameras.remove(orphan_cameras.pop())


def spawn_objects(filepath, location, rotation, type):
    with bpy.data.libraries.load(filepath) as (data_from, data_to):
        data_to.objects = data_from.objects

    spawned_objects = []
    for obj in data_to.objects:
        new_obj = obj.copy()
        new_obj.data = obj.data.copy()
        if type == 'truck':
            new_obj.scale = (0.002, 0.002, 0.002)
        if type == 'person':
            new_obj.scale = (0.0005, 0.0005, 0.0005)
        if type == 'traffic_light':
            new_obj.scale = (0.7, 0.7, 0.7)
        else:    
            new_obj.scale = (0.03, 0.03, 0.03)
        new_obj.animation_data_clear()
        new_obj.location = location
        new_obj.rotation_euler = rotation
        bpy.context.scene.collection.objects.link(new_obj)
        spawned_objects.append(new_obj)
        
    for obj in bpy.context.selected_objects:
        obj.select_set(False)

    for obj in spawned_objects:
        obj.select_set(True)

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    override = {'area': area, 'region': region, 'edit_object': bpy.context.edit_object}
                    bpy.ops.view3d.view_selected(override)
#                    bpy.context.temp_override()
                    break
                
                
def spawn_perspective_camera(lens, location, rotation):
    # create a new camera object
    cam_data = bpy.data.cameras.new('PerspectiveCamera')
    cam_obj = bpy.data.objects.new('PerspectiveCamera', cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)

    # set camera properties
    cam_data.lens = lens
    cam_obj.location = location
    cam_obj.rotation_euler = rotation
    cam_obj.scale = (1, 1, 1)

    # hide all other cameras in the viewport
    for obj in bpy.data.objects:
        if obj.type == 'CAMERA' and obj != cam_obj:
            obj.hide_viewport = True
            obj.data.sensor_width = 0.0

    # activate this camera
    cam_obj.hide_viewport = False
    bpy.context.scene.camera = cam_obj
    cam_obj.data.sensor_width = 36.0

    return cam_obj


def spawnAssets(assets, depth_scale, width_scale):
    
    for asset in assets:
        if 'type' in asset.keys():
            if asset['type'] == 'sedan':
                location = (depth_scale * asset['z'] - 30, width_scale * (256 - asset['u']), 0)
                rotation = (0, 0, -asset['yaw'])
                spawn_objects(sedan_blend_path, location, rotation, 'sedan')
            
            elif asset['type'] == 'compact':
                location = (depth_scale * asset['z'] - 30, width_scale * (256 - asset['u']), 0)
                rotation = (0, 0, -asset['yaw'])
                spawn_objects(sedan_blend_path, location, rotation, 'sedan')
            
            elif asset['type'] == 'SUV':
                location = (depth_scale * asset['z'] - 30, width_scale * (256 - asset['u']), 0)
                rotation = (0, 0, -asset['yaw'])
                spawn_objects(SUV_blend_path, location, rotation, 'SUV')
            
#            else:
#                location = (depth_scale * asset['z'] - 30, width_scale * (256 - asset['u']), 0)
#                rotation = (0, 0, -asset['yaw'])
#                spawn_objects(truck_blend_path, location, rotation, 'truck')
        
        elif 'name' in asset.keys():
            if asset['name'] == 'traffic light':
                location = (depth_scale * asset['z'] - 5, width_scale * (256 - asset['x']), 10.4)
                rotation = (1.57, 0, 3.14)
                spawn_objects(traffic_light_blend_path, location, rotation, 'traffic_light')
            
            elif asset['name'] == 'person':
                pass
#                location = (depth_scale * asset['z'] - 5, width_scale * (256 - asset['x'] + 27), 0)
#                rotation = (1.57, 0, -1.57)
#                spawn_objects(pedestrian_blend_path, location, rotation, 'person')

######################################       PATHS     #####################################################

print('\n\n\n')

# paths for the blend files
sedan_blend_path = "C:/Uday/WPI/Courses/Computer Vision/Assignments/P3_EinsteinVision/P3Data/Assets/Vehicles/SedanAndHatchback.blend"
SUV_blend_path = "C:/Uday/WPI/Courses/Computer Vision/Assignments/P3_EinsteinVision/P3Data/Assets/Vehicles/SUV.blend"
truck_blend_path = "C:/Uday/WPI/Courses/Computer Vision/Assignments/P3_EinsteinVision/P3Data/Assets/Vehicles/Truck.blend"
sign_blend_path = "C:/Uday/WPI/Courses/Computer Vision/Assignments/P3_EinsteinVision/P3Data/Assets/SpeedLimitSign.blend"
pedestrian_blend_path = "C:/Uday/WPI/Courses/Computer Vision/Assignments/P3_EinsteinVision/P3Data/Assets/Pedestrain.blend"
traffic_light_blend_path = "C:/Uday/WPI/Courses/Computer Vision/Assignments/P3_EinsteinVision/P3Data/Assets/TrafficSignal.blend"


data_folder = "C:/Uday/WPI/Courses/Computer Vision/Assignments/P3_EinsteinVision/P3Data/blender_data/scene_11/input_frames"
render_folder = "C:/Uday/WPI/Courses/Computer Vision/Assignments/P3_EinsteinVision/P3Data/blender_data/scene_11/render"

vehicle_test_path = "C:/Uday/WPI/Courses/Computer Vision/Assignments/P3_EinsteinVision/P3Data/blender_data/scene_11/vehicles_with_depth/vehicles_with_depth001.json"
vehicle_json_path = "C:/Uday/WPI/Courses/Computer Vision/Assignments/P3_EinsteinVision/P3Data/blender_data/scene_11/vehicles_with_depth"

assets_test_path = "C:/Uday/WPI/Courses/Computer Vision/Assignments/P3_EinsteinVision/P3Data/blender_data/scene_11/assets_with_depth/assets_with_depth001.json"
assets_json_path = "C:/Uday/WPI/Courses/Computer Vision/Assignments/P3_EinsteinVision/P3Data/blender_data/scene_11/assets_with_depth"

output_path = "C:/Uday/WPI/Courses/Computer Vision/Assignments/P3_EinsteinVision/P3Data/scene1_front/output"
try:
    os.makedirs(output_path)
except:
    pass


output_width = 512
output_height = 256
output_frame_rate = 5

camera_location = (0.0, 0.0, 1.4)
camera_rot_mat = np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]])
camera_angles = (1.5708, 0, -1.5708)


# Set render settings
bpy.context.scene.render.resolution_x = output_width
bpy.context.scene.render.resolution_y = output_height
bpy.context.scene.render.fps = output_frame_rate
bpy.context.scene.render.image_settings.file_format = 'PNG'


# Render each Blender scene
for i, frame_name in enumerate(sorted(os.listdir(data_folder))):
#    mega_purge()
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    frame_number = int(re.findall(r'\d+', frame_name)[0])
    if frame_number < 432:
        padded_file_number = str(frame_number).zfill(3)
        spawn_perspective_camera(20.0, camera_location, camera_angles)
        print(frame_number)
        
        vehicle_json = os.path.join(vehicle_json_path, f'vehicles_with_depth{padded_file_number}.json')
        
        f_v = open(vehicle_json)
        cars = [json.load(f_v)]
        cars = [json.loads(idx.replace("'", '"')) for idx in cars]
        cars = cars[0]
        
        assets_json = os.path.join(assets_json_path, f'assets_with_depth{padded_file_number}.json')
        
        f_a = open(assets_json)
        assets = [json.load(f_a)]
        assets = [json.loads(idx.replace("'", '"')) for idx in assets]
        assets = assets[0]
        
        spawnAssets(cars, 12, 0.15)
        spawnAssets(assets, 4, 0.015)
        spawn_perspective_camera(20.0, camera_location, camera_angles)
        bpy.context.scene.render.filepath = os.path.join(render_folder, f"render{padded_file_number}")
        bpy.ops.render.render(write_still=True)


# Create a sequencer instance
sequencer = bpy.context.scene.sequence_editor_create()



current_frame = 1

for i, frame_name in enumerate(sorted(os.listdir(render_folder))):
    
    frame_number = int(re.findall(r'\d+', frame_name)[0])
    padded_file_number = str(frame_number).zfill(3)
    image_path = os.path.join(render_folder, f"render{padded_file_number}.png")
    
    sequencer.sequences.new_image(name=f"Image {padded_file_number}", filepath=image_path, channel=1, frame_start=current_frame)
    current_frame += 1


# Set render properties for final video
bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
bpy.context.scene.render.film_transparent = True
bpy.context.scene.render.ffmpeg.format = 'MPEG4'
bpy.context.scene.render.filepath = output_path

# Render the combined video
#bpy.ops.object.camera_add(location=(0, 0, 1.4), 
#                          rotation=(1.5708, 0, -1.5708))
#scene.camera = bpy.context.object
bpy.ops.render.render(animation=True)

    
########################################################################################################################
        
sign_location = (75, -20, 0)
sign_rotation = (0, 0, 0)
#spawn_objects

#spawn_objects(sign_path, sign_location, sign_rotation)

#########################################################################################################################

        
#print('\n\n\n')
#f_v = open(vehicle_test_path)
#cars = [json.load(f_v)]
#cars = [json.loads(idx.replace("'", '"')) for idx in cars]
#cars = cars[0]

#f_a = open(assets_test_path)
#assets = [json.load(f_a)]
#assets = [json.loads(idx.replace("'", '"')) for idx in assets]
#assets = assets[0]
#print(assets)

#mega_purge()
#spawnAssets(cars, 12, 0.15)
#spawnAssets(assets, 4, 0.015)
#spawn_perspective_camera(20.0, camera_location, camera_angles)