import bpy
import bmesh
import random
from mathutils import Vector
import math
import os
import time

# This enables GPU rendering.
# I'm running this on a MacBook Pro (2019) with an AMD RX 5600 XT eGPU.
# Note: Model generation is only uses the CPU
bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'METAL'
bpy.context.preferences.addons['cycles'].preferences.get_devices()
for device in bpy.context.preferences.addons['cycles'].preferences.devices:
    device.use = (device.type != 'CPU')

# Blender was crashing 🔥🤖🔥 So I've implemented a break taking strategy using a sleep factor. This will give
# the Blender server time to recover memory, CPU cycles etc. The higher the sleep factor the longer the breaks.
# Set to 0 to disable and increase if crashes are occuring.
SLEEP_FACTOR = 1

def take_a_break(length):
    time.sleep(SLEEP_FACTOR * length)


class MoonModel:
    def __init__(self, size=100):
        self.plane = self.create_plane(size=size)

    def create_plane(self, size=100, number_cuts=100, smoothness=1000):
        # This is currently producing a solid grey plane. This should be updated with texture images based on the
        # lunar surface.

        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_by_type(type='MESH')
        bpy.ops.object.delete()
        
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_by_type(type='LIGHT')
        bpy.ops.object.delete()

        bpy.ops.mesh.primitive_plane_add(size=size, enter_editmode=False, location=(0, 0, 0))
        plane = bpy.context.object
        material = bpy.data.materials.new(name="SolidGrey")
        material.diffuse_color = (0.8, 0.8, 0.8, 1.0)
        plane.data.materials.append(material)

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.subdivide(number_cuts=number_cuts, smoothness=smoothness)
        bpy.ops.object.mode_set(mode='OBJECT')

        return plane
        
    def add_rock(self, x, y, radius=0.1):
        # These "rocks" are currently just spheres and all one size. These rock models should be based on known
        # moon rocks instead.

        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=16,
            ring_count=16,
            radius=0.1,
            location=(x, y, 0)
        )

    def join_objects(self):
        bpy.ops.object.select_all(action='SELECT')
        bpy.context.view_layer.objects.active = self.plane
        bpy.ops.object.join()

    def save(self, filepath):
        bpy.ops.wm.save_as_mainfile(filepath=filepath)

    def load(self, filepath):
        bpy.ops.wm.open_mainfile(filepath=filepath)

    def add_undulation(self, x, y, radius, height):
        me = bpy.context.object.data
        bm = bmesh.new()
        bm.from_mesh(me)

        center = Vector((x, y, 0))

        for v in bm.verts:
            displacement = v.co.xy - center.xy
            distance = displacement.length
            
            if distance < radius:
                v.co.z += height * (1 - distance / radius)

        bm.to_mesh(me)
        bm.free()

    def add_crater(self, x, y, radius):
        # We can use existing 3D models of the moon's surface to determine what
        # realistic crater height to crater depressions should be.

        crater_height = radius / 3
        depression_height = crater_height * -1.5
        depression_radius = radius * 0.7

        self.add_undulation(x, y, radius, crater_height)
        self.add_undulation(x, y, depression_radius, depression_height)

    def surface_height(self, x=0, y=0):
        # This function returns the surface height for a given point which is useful
        # for rendering images from the surface. This is a pretty simple implementation
        # using closest point calculations, there is likely a better solution.

        closest_point = None
        closest_distance = math.inf

        mesh_name = "Plane"
        mesh = bpy.data.meshes[mesh_name]

        bm = bmesh.new()
        bm.from_mesh(mesh)

        for v in bm.verts:
            distance = ((v.co.x - x) ** 2 + (v.co.y - y) ** 2) ** 0.5
            if distance < closest_distance:
                closest_distance = distance
                closest_point = v.co

        bm.free()
        return closest_point[2]

    def render(self, output_path, sun_altitude=45, sun_azimuth=0, sun_intensity=1.0, reflectivity=0, x=0, y=0, z=1.5, camera_direction=0, camera_angle=90, resolution_x=512, resolution_y=512):
        scene = bpy.context.scene
        scene.render.resolution_x = resolution_x
        scene.render.resolution_y = resolution_y
        scene.render.resolution_percentage = 100

        # Set up the camera
        bpy.ops.object.camera_add(location=(x, y, z))
        camera = bpy.context.object
        camera.rotation_euler = (math.radians(camera_angle), 0, math.radians(camera_direction))
        camera.data.angle = math.radians(camera_angle)
        bpy.context.scene.camera = camera

        # Check if the sun object has already been added
        sun = None
        for obj in bpy.context.scene.objects:
            if obj.type == 'LIGHT' and obj.data.type == 'SUN':
                sun = obj
                break

        # Set up the sun if it doesn't already exist
        if sun is None:
            sun_distance = 100000  # Far enough to cast parallel shadows
            sun_x = sun_distance * math.sin(math.radians(sun_altitude)) * math.cos(math.radians(sun_azimuth))
            sun_y = sun_distance * math.sin(math.radians(sun_altitude)) * math.sin(math.radians(sun_azimuth))
            sun_z = sun_distance * math.cos(math.radians(sun_altitude))
            bpy.ops.object.light_add(type='SUN', location=(sun_x, sun_y, sun_z))
            sun = bpy.context.object

        # Set the intensity of the sun
        sun.data.energy = sun_intensity

        # Set up the world
        world = bpy.data.worlds.new("BlackWorld")
        world.use_nodes = True
        bg = world.node_tree.nodes['Background']
        bg.inputs[0].default_value = (0, 0, 0, 1)  # Black color
        bpy.context.scene.world = world

        # Set the reflectivity of the material
        material = self.plane.data.materials[0]
        material.specular_intensity = reflectivity

        # Render the scene
        bpy.context.scene.render.filepath = output_path
        bpy.ops.render.render(write_still=True)


def create_moon_model(size=100, rocks=1000, hills=10, depressions=10, craters=50, small_craters=100):
    moon = MoonModel(size)

    # rocks
    for i in range(rocks):
        take_a_break(0.01)
        moon.add_rock(
            x=random.uniform(-50, 50),
            y=random.uniform(-50, 50),
            radius=random.uniform(0.01, 0.2)
        )

    moon.join_objects()

    # hills
    for i in range(hills):
        take_a_break(0.1)
        x = random.uniform(-50, 50)
        y = random.uniform(-50, 50)

        radius = random.uniform(5, 10)
        height = radius * random.uniform(0.1, 0.5)
        moon.add_undulation(x=x, y=y, radius=radius, height=height)

    # depressions
    for i in range(depressions):
        take_a_break(0.1)
        x = random.uniform(-50, 50)
        y = random.uniform(-50, 50)

        radius = random.uniform(5, 10)
        height = -radius * random.uniform(0.1, 0.3)
        moon.add_undulation(x=x, y=y, radius=radius, height=height)
    
    # We're adding two types of craters here, regular and small. In reality we should use existing 3D lunar
    # models to determine the size, density, and depression characteristics for the specific area we're
    # modelling.  

    # craters
    for i in range(craters):
        take_a_break(0.05)
        x = random.uniform(-50, 50)
        y = random.uniform(-50, 50)
        radius = random.uniform(1, 15)

        moon.add_crater(x, y, radius)

    # small craters (hopefully this will add more realistic texturing)
    for i in range(small_craters):
        take_a_break(0.05)
        x = random.uniform(-50, 50)
        y = random.uniform(-50, 50)
        radius = random.uniform(0.1, 1)

        moon.add_crater(x, y, radius)

    return moon

renders_directory = 'renders'
os.makedirs(renders_directory, exist_ok=True)

# Generates models with different crater densities to compare to reference photo for optimizaiton
for number_of_craters in [5, 10, 20, 40, 80]:
    # Generates 5 versions for comparrison
    for version in range(5):
        directory = f'{renders_directory}/model_with_{number_of_craters:02d}_craters_v{version}'
        os.makedirs(directory, exist_ok=True)
        moon = create_moon_model(craters=number_of_craters)
        take_a_break(10)

        # Rendering images from 5 locations on the model
        for location in [(0,0), (10,10), (10,-10), (-10,-10), (-10,10)]:
            x = location[0]
            y = location[1]

            # This height should match the reference image's height
            camera_altitude = 1.5
            elevation = moon.surface_height(x, y)
            z = elevation + camera_altitude

            # Rendering 8 images facing in different directions from each location.
            for camera_direction in [0, 45, 90, 135, 180, 225, 270, 315]:
                # Resolution is set to 512x512 which is the resolution of the reference image used for comparrison.
                # Ideally the sun_altitude, sun_azimuth, direction, and camera_angle would also match the reference
                # image. I've just set some basic defaults for now.

                moon.render(
                    output_path=f'{directory}/location_{x:02d}.{y:02d}_camera_direction_{camera_direction:03d}.png',
                    sun_altitude=45,
                    sun_azimuth=0,
                    sun_intensity=1.0,
                    reflectivity=0,
                    x=x,
                    y=y,
                    z=z,
                    camera_direction=camera_direction,
                    camera_angle=90,
                    resolution_x=512,
                    resolution_y=512
                )

        moon.save(f'{directory}/moon_surface.blend')
