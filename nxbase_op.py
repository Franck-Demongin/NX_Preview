import numpy as np
import mathutils
from math import radians
import os
import tempfile
import bpy
from bpy.props import (StringProperty, 
                       BoolProperty, 
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty)

class NXBase:
  scene_preview="NXPreviewScene"
  scene_asset="Scene"

  file_format={
    "format": "PNG",
    "ext": "png" 
  }

  path: StringProperty(
    name="",
    description="Path to Preview Output",
    default="",
    maxlen=1024,
    subtype='DIR_PATH'
  )
  preview_filepath: StringProperty(
    default=""
  )
  original_scene : StringProperty(
    default=""
  )
  original_object : StringProperty(
    default=""
  )
  mark_as_asset : BoolProperty(
    default=False
  )
  assign_preview : BoolProperty(
    default=True
  )
  use_backdrop : BoolProperty(
    default=False
  )
  backdrop_style : StringProperty(
    default=""
  )
  use_background : BoolProperty(
    default=False
  )
  background_color : FloatVectorProperty(
    subtype = "COLOR",
    default = (0.25,0.25,0.25,1.0),
    size = 4
  )
  world_strength : FloatProperty(
    default=0.5,
    min=0,
    max=10,
    soft_max=1
  )
  light_top_strength : FloatProperty(
    default=0.5,
    min=0,
    max=1
  )
  light_left_strength : FloatProperty(
    default=0.5,
    min=0,
    max=1
  )
  light_right_strength : FloatProperty(
    default=0.5,
    min=0,
    max=1
  )
  camera_focal : IntProperty(
    default=85,
    min=0,
    max=250
  )
  camera_align_h : StringProperty(
    default="RIGHT"
  )
  camera_align_v : StringProperty(
    default="CENTER"
  )
  save_in_file_folder : BoolProperty(
    default=False
  )
  save_asset : BoolProperty(
    default=False
  )
  library_id : IntProperty(
    default=0
  )
  apply_modifier : BoolProperty(
    default=False
  )

  @classmethod
  def poll(cls, context):
    return context.object
  
  def purge_orphan_data(self):
    print("====PURGE_ORPHAN_DATA====")

    meshes = [mesh for mesh in bpy.data.meshes if mesh.users == 0 and mesh.name != "Backdrop"]
    list(map(lambda mesh: bpy.data.meshes.remove(mesh, do_unlink=True), meshes))
    
    lights = [light for light in bpy.data.lights if light.users == 0 and 
              light.name not in ["Area_1","Area_2","Area_3"]]
    list(map(lambda light: bpy.data.lights.remove(light, do_unlink=True), lights))

    cams = [cam for cam in bpy.data.objects if cam.type == "CAMERA" and cam.users == 0]
    list(map(lambda cam: bpy.data.objects.remove(cam, do_unlink=True), cams))

    cams = [cam for cam in bpy.data.cameras if cam.users == 0 and cam.name != "CamPreview"]
    list(map(lambda cam: bpy.data.cameras.remove(cam, do_unlink=True), cams))
    
    ngs = [ng for ng in bpy.data.node_groups if ng.users == 0 and ng.name != "GNXBackdrop"]
    list(map(lambda ng: bpy.data.node_groups.remove(ng, do_unlink=True), ngs))

    worlds = [world for world in bpy.data.worlds if world.users == 0 and world.name != "WorldPreview"]
    list(map(lambda world: bpy.data.worlds.remove(world, do_unlink=True), worlds))

    imgs = [img for img in bpy.data.images if img.users == 0]
    list(map(lambda img: bpy.data.images.remove(img, do_unlink=True), imgs))
  
  def purge_scene(self, scene_name):
    '''Remove all objects in the scene'''
    for o in bpy.data.scenes[scene_name].objects:  
      bpy.data.objects.remove(o, do_unlink=True)

  def create_scene_and_switch_to(self, context, scene_name, switch_to=True):
    '''Create scene scene_name in not exist and switch to it'''
    if scene_name not in bpy.data.scenes:
      bpy.data.scenes.new(scene_name)    
    if switch_to:
      context.window.scene = bpy.data.scenes[scene_name]
  
  def copy_object(self, context):
    obj = bpy.data.objects[self.original_object]
    copy = obj.copy()
    copy.data = obj.data.copy()
    copy.name = "Preview"
    context.collection.objects.link(copy)
    context.view_layer.objects.active = copy
    copy.select_set(True)
    bpy.ops.object.convert(target="MESH")
    copy.location = (0,0,0)
    copy.rotation_euler = (0,0,0)
    copy.hide_render = False

    dims = [d for d in copy.dimensions]
    maxi = max(dims)
    index = dims.index(maxi)
    copy.dimensions[index] = 2
    copy.scale[0] = copy.scale[index]
    copy.scale[1] = copy.scale[index]
    copy.scale[2] = copy.scale[index]

  def add_cam(self, context):
    target = context.object
    
    if 'CamPreview' not in bpy.data.cameras:
        camData = bpy.data.cameras.new("CamPreview")
    else:
        camData = bpy.data.cameras['CamPreview']            
    cam = bpy.data.objects.new("CamPreview", camData)
    context.scene.collection.objects.link(cam)
    
    context.scene.camera = cam

    context.scene.render.resolution_x = 512
    context.scene.render.resolution_y = 512
    
    target_loc = mathutils.Vector(target.location)

    if self.camera_align_h == "RIGHT":
      x = 2.5
    elif self.camera_align_h == "CENTER":
      x = 0
    else:
      x = -2.5

    if self.camera_align_v == "CENTER":
      z = 2
    elif self.camera_align_v == "TOP":
      z = 7.5
    else:
      z = -5

    cam.location = target_loc + mathutils.Vector((x,-6,z))
    context.view_layer.update()
    loc_cam = cam.matrix_world.to_translation()
    direction = target.location - loc_cam
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam.rotation_euler = rot_quat.to_euler()
    cam.data.lens = self.camera_focal + 5    
    bpy.ops.view3d.camera_to_view_selected()    
    cam.data.lens = self.camera_focal
      
  def add_light(self, context, name, 
                type="AREA", loc=(0,0,0), rot=(0,0,0), size=0.25, energy=10, energy_max=100):
    if name not in bpy.data.lights:
        lgt = bpy.data.lights.new(name=name, type=type)
    else:
        lgt = bpy.data.lights[name]
    lgt.use_contact_shadow = True
    light = bpy.data.objects.new(name, lgt)
    context.scene.collection.objects.link(light)
        
    light.data.energy = np.interp(energy, [0,1], [0,energy_max])
    light.data.size = size
    light.location = loc
    light.rotation_euler = list(map(radians, rot))
  
  def add_world(self, context):
    if 'WorldPreview' not in bpy.data.worlds:
        bpy.data.worlds.new('WorldPreview')
    
    bpy.data.worlds['WorldPreview'].use_nodes = True
    context.scene.world = bpy.data.worlds['WorldPreview']
    
    node_tree = context.scene.world.node_tree
    tree_nodes = node_tree.nodes

    tree_nodes.clear()

    node_background = tree_nodes.new(type='ShaderNodeBackground')
    node_background.inputs[1].default_value = self.world_strength

    node_environment = tree_nodes.new('ShaderNodeTexEnvironment')
    if "city.exr" not in bpy.data.images:
      node_environment.image = bpy.data.images.load(context.preferences.studio_lights['city.exr'].path)
    else:
      node_environment.image = bpy.data.images['city.exr']
    node_environment.location = -300,0

    node_output = tree_nodes.new(type='ShaderNodeOutputWorld')   
    node_output.location = 200,0

    links = node_tree.links
    links.new(node_environment.outputs["Color"], node_background.inputs["Color"])
    links.new(node_background.outputs["Background"], node_output.inputs["Surface"])

  def add_material_backdrop(self, context):
    obj = bpy.data.objects["Backdrop"]

    if "MatBackdrop" not in bpy.data.materials:
      mat = bpy.data.materials.new(name="MatBackdrop")
    else:
      mat = bpy.data.materials["MatBackdrop"]
    
    mat.use_nodes = True
    if self.backdrop_style == "LIGHT":
      color = (0.8,0.8,0.8,1.0)
    elif self.backdrop_style == "DARK":
      color = (0.01,0.01,0.01,1.0)
    else:
      color = (0.25,0.25,0.25,1.0)
    mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
      
  def add_backdrop(self, context):
    if "GNX_Backdrop" not in bpy.data.node_groups:
      backgrop_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "GNX_Backdrop.blend")
      with bpy.data.libraries.load(backgrop_filepath, link=False) as (data_from, data_to):
        data_to.node_groups = [name for name in data_from.node_groups if name == "GNX_Backdrop"]

    if 'Backdrop' not in bpy.data.meshes:
      bck = bpy.data.meshes.new('Backdrop')
    else:
      bck = bpy.data.meshes['Backdrop']
    backdrop = bpy.data.objects.new('Backdrop', bck)
    context.scene.collection.objects.link(backdrop)
    
    depsgraph = context.evaluated_depsgraph_get()
    
    obj = context.scene.objects['Preview']
    obj_eval = obj.evaluated_get(depsgraph)
    scale = obj_eval.scale.z
    
    backdrop.location.z =  min([d[2] for d in obj_eval.bound_box]) * scale   

    self.add_material_backdrop(context)
    
    bck_mod = backdrop.modifiers.new('NX_Bck', type="NODES")
    bck_mod.node_group = bpy.data.node_groups['GNX_Backdrop']   
    bck_mod["Input_3"] = 5.0 
    bck_mod["Input_6"] = 0.5 
    bck_mod["Input_7"] = 6
    bck_mod["Input_13"] = 1
    bck_mod["Input_12"] = context.scene.camera
    bck_mod["Input_1"] = bpy.data.materials["MatBackdrop"]
   
  def add_background(self, context):
    scene = context.scene
    scene.use_nodes = True
    node_tree = scene.node_tree
    nodes = node_tree.nodes
    nodes.new(type="CompositorNodeImage")
    
    color = nodes.new(type="CompositorNodeRGB")
    color.location.x += 200
    color.outputs[0].default_value = self.background_color

    mixRGB = nodes.new(type="CompositorNodeMixRGB")
    mixRGB.location.x += 400
    
    nodes['Composite'].location.x += 600

    node_tree.links.new(nodes['Mix'].inputs[0], nodes['Render Layers'].outputs[1])
    node_tree.links.new(nodes['Mix'].inputs[2], nodes['Render Layers'].outputs[0])
    node_tree.links.new(nodes['Mix'].inputs[1], nodes['RGB'].outputs[0])
    node_tree.links.new(nodes['Composite'].inputs[0], nodes['Mix'].outputs[0])



  def render_preview(self, context):  
    p = self.path
    if self.save_in_file_folder and bpy.data.is_saved:
        p = os.path.dirname(bpy.data.filepath)
    elif len(self.path) == 0:
        p = tempfile.gettempdir()
    self.preview_filepath = os.path.join(p, self.original_object)

    context.scene.render.film_transparent = True
    context.scene.render.image_settings.file_format = self.file_format["format"]
    context.scene.render.filepath = self.preview_filepath

    context.scene.render.use_lock_interface = True
    bpy.ops.render.render(write_still = True)
 