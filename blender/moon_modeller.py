import bpy
import random
import math
from mathutils import Vector

class MoonModeller:
    def __init__(self):
        pass

    def generate(self, length=100, width=100, rock_density=75, crater_density=2):
        # Delete all existing meshes
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_by_type(type='MESH')
        bpy.ops.object.delete()

        self.length = length
        self.width = width
        self.rock_density = rock_density * 10
        self.crater_density = crater_density * 1

        # Create a plane for the moon surface
        bpy.ops.mesh.primitive_plane_add(size=self.length, enter_editmode=False, location=(0, 0, 0))
        self.moon_surface = bpy.context.object
        self.moon_surface.scale.y = self.width / self.length

        # Set color to moon grey
        self._set_color(self.moon_surface, (0.5, 0.5, 0.5, 1))  # RGBA

        # Generate rocks
        for _ in range(self.rock_density):
            x = random.uniform(-self.length / 2, self.length / 2)
            y = random.uniform(-self.width / 2, self.width / 2)
            self._create_rock((x, y, 0))

        # Generate craters
        for _ in range(self.crater_density):
            x = random.uniform(-self.length / 2, self.length / 2)
            y = random.uniform(-self.width / 2, self.width / 2)
            self._create_crater((x, y, 0))

    def _create_rock(self, location):
        # Create a high-resolution sphere
        bpy.ops.mesh.primitive_uv_sphere_add(segments=128, ring_count=48, location=location)  # Increase the number of segments and rings
        rock = bpy.context.object
        rock.scale = Vector((random.uniform(0.05, 0.2) for _ in range(3)))  # Make the rocks smaller

        # Set color to light grey and increase the roughness
        self._set_color(rock, (0.8, 0.8, 0.8, 1), 1.0)  # RGBA, roughness

        # Create a new texture for the Displace modifier
        tex = bpy.data.textures.new('RockTexture', 'CLOUDS')
        tex.noise_scale = 0.25

        # Add the Displace modifier to the rock
        mod = rock.modifiers.new('Displace', 'DISPLACE')
        mod.texture = tex
        mod.strength = 0.5

    def _create_crater(self, location):
        # Create a sphere for the main body of the crater
        bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, location=location)
        main_sphere = bpy.context.object
        main_sphere.scale = Vector((random.uniform(1, 3) for _ in range(3)))

        # Create a cylinder for the rim of the crater
        bpy.ops.mesh.primitive_cylinder_add(radius=main_sphere.scale.x * 1.1, depth=main_sphere.scale.z * 0.1, location=(location[0], location[1], location[2] - main_sphere.scale.z / 2))
        rim_cylinder = bpy.context.object

        # Use boolean modifier to subtract the main sphere from the moon surface
        mod_bool = self.moon_surface.modifiers.new('Modifier', 'BOOLEAN')
        mod_bool.operation = 'DIFFERENCE'
        mod_bool.object = main_sphere
        bpy.context.view_layer.objects.active = self.moon_surface
        bpy.ops.object.modifier_apply(modifier=mod_bool.name)

        # Use boolean modifier to add the rim cylinder to the moon surface
        mod_bool = self.moon_surface.modifiers.new('Modifier', 'BOOLEAN')
        mod_bool.operation = 'UNION'
        mod_bool.object = rim_cylinder
        bpy.context.view_layer.objects.active = self.moon_surface
        bpy.ops.object.modifier_apply(modifier=mod_bool.name)

        # Delete the spheres
        bpy.ops.object.select_all(action='DESELECT')
        main_sphere.select_set(True)
        rim_cylinder.select_set(True)
        bpy.ops.object.delete()

        # Set color to light grey
        self._set_color(self.moon_surface, (0.8, 0.8, 0.8, 1))  # RGBA

    def _set_color(self, obj, color, roughness=0.5):
        # Create a new material
        mat = bpy.data.materials.new(name="Material")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes["Principled BSDF"]

        # Set the color of the material
        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Roughness'].default_value = roughness

        # Assign the material to the object
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)

    def render(self, output_path, sun_height=45, sun_direction=0, rover_position=(0, 0, 0.5), rover_direction=0, camera_angle=90):
        # Set the world color to black
        bpy.context.scene.world.color = (0, 0, 0)

        # Set up the sun lamp
        bpy.ops.object.light_add(type='SUN', location=(0, 0, 0))
        sun = bpy.context.object
        sun.location = (math.sin(math.radians(sun_direction)) * 1000, math.cos(math.radians(sun_direction)) * 1000, math.tan(math.radians(sun_height)) * 1000)
        sun.data.energy = 0.1  # Increase the strength of the sun lamp

        # Set up the camera
        bpy.ops.object.camera_add(location=rover_position)
        camera = bpy.context.object
        camera.rotation_euler = (math.radians(camera_angle), 0, math.radians(rover_direction))
        bpy.context.scene.camera = camera

        # Set the output path for the rendered image
        bpy.context.scene.render.filepath = output_path

        # Render the scene
        bpy.ops.render.render(write_still=True)

    def save(self, filepath):
        bpy.ops.wm.save_as_mainfile(filepath=filepath)

    def load(self, filepath):
        bpy.ops.wm.open_mainfile(filepath=filepath)


# for moon_index in range(10):
#     moon = MoonModeller()
#     moon.generate(length=100, width=100, rock_density=10*moon_index, crater_density=20)
#     moon.save(f'renders/{moon_index}/Moon.blend')
#     for render_index in range(12):
#         moon.render(f'renders/{moon_index}/img{render_index}.png', sun_height=45, sun_direction=45, rover_position=(0, 0, 1.5), rover_direction=30*render_index, camera_angle=90)



moon = MoonModeller()
# # moon.load('Moon.blend')
moon.generate(length=100, width=100, rock_density=100, crater_density=20)
moon.render('moon.png', sun_height=75, sun_direction=45, rover_position=(0, 0, 1.5), rover_direction=180, camera_angle=90)
moon.save('Moon.blend')
