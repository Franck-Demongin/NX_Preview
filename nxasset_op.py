import os
import bpy
from bpy.types import Operator
from bpy.props import (StringProperty, 
                       BoolProperty, 
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty)

class NXBaseAsset:
  scene_asset="Scene"

  is_asset : BoolProperty(
    default=False
  )
  save_asset : BoolProperty(
    default=False
  )
  library_id : IntProperty(
    default=0
  )
  original_scene : StringProperty(
    default=""
  )
  original_object : StringProperty(
    default=""
  )
  filepath : StringProperty(
    default="",
    subtype="FILE_PATH"
  )
  assign_preview : BoolProperty(
    default=False
  )
  apply_modifiers : BoolProperty(
    default=False
  )

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
  
  def create_scene_and_switch_to(self, context, scene_name, switch_to=True):
    '''Create scene scene_name in not exist and switch to it'''
    if scene_name not in bpy.data.scenes:
      bpy.data.scenes.new(scene_name)    
    if switch_to:
      context.window.scene = bpy.data.scenes[scene_name]
                 

class ASSET_OT_NXAssetToggle(Operator):
  bl_idname = "asset.nx_asset_toggle"
  bl_label = "Toggle Asset"
  bl_description = "Mark as asset if it's not, clear asset if it's"
  bl_options = {"INTERNAL"}

  def execute(self, context):
    obj = context.object

    if obj.asset_data is not None:
      obj.asset_clear()
      msg = f"Data-block '{obj.name}' is no asset anymore"
    else:
      obj.asset_mark()
      msg = f"Data-block '{obj.name}' is now an asset"

    # needed to update scene
    bpy.ops.object.editmode_toggle()
    bpy.ops.object.editmode_toggle()

    self.report({'INFO'}, msg)
    return {'FINISHED'}


class ASSET_OT_NXAssetSave(Operator, NXBaseAsset):
  bl_idname = "asset.nx_asset_save"
  bl_label = "Save Asset"
  bl_description = "Save asset in library"
  bl_options = {"INTERNAL"}

  def execute(self, context):

    print("START SAVE ASSET", context.object.name)
    if self.save_asset:
      obj = bpy.data.objects[self.original_object]
      libraries = bpy.context.preferences.filepaths.asset_libraries
      if (self.library_id >= 0 and 
          self.library_id < len(libraries) and
          len(libraries[self.library_id].name) > 0 and
          os.path.isdir(libraries[self.library_id].path)
      ):
        path_ = os.path.join(libraries[self.library_id].path, f"{self.original_object}.blend")
        
        if bpy.data.is_saved:
          bpy.ops.file.make_paths_absolute()

        bpy.context.scene.name = f"{self.original_scene}_"
        self.create_scene_and_switch_to(bpy.context, self.scene_asset, True)

        o = obj
        if self.apply_modifiers:
          co = obj.copy()
          co.data = obj.data.copy()
          co.data.name = obj.data.name
          co.name = obj.name
          bpy.context.collection.objects.link(co)
          co.select_set(True)
          bpy.context.view_layer.objects.active = co
          bpy.ops.object.convert(target="MESH")
          o = co
          o.asset_mark()          
          if self.assign_preview:
            bpy.ops.ed.lib_id_load_custom_preview(
              {"id":o}, 
              filepath=self.filepath
            )
          else:
            pass
            # print('GENERATE_PREVIEW', o.name)
            # o.asset_generate_preview()
        else:
          bpy.context.collection.objects.link(o)
        data = {bpy.data.scenes[bpy.context.scene.name]}
        bpy.data.libraries.write(path_, data)
        bpy.data.scenes.remove(bpy.data.scenes[self.scene_asset])
        bpy.context.scene.name = self.original_scene
        if self.apply_modifiers:
          obj.data.name = o.data.name
          obj.name = o.name
          bpy.data.objects.remove(o, do_unlink=True)
        self.purge_orphan_data()
        
        if bpy.data.is_saved:
          bpy.ops.file.make_paths_relative()
      else:
        print('LIB NOT EXIST')

    else:
      print("DON'T SAVE_ASSET")
    
    return {'FINISHED'}


class ASSET_OT_NXLibraryAdd(Operator):
  bl_idname = "asset.nx_library_add"
  bl_label = "Add Lirary"
  bl_options = {"INTERNAL"}

  def execute(self, context):
    scene = context.scene
    bpy.ops.preferences.asset_library_add("INVOKE_DEFAULT")
    libraries = context.preferences.filepaths.asset_libraries
    scene.NXPreview.library_id = len(libraries)
    scene.NXPreview.last_library_id = len(libraries)

    return {"FINISHED"}


class ASSET_OT_NXLibraryRemove(Operator):
  bl_idname = "asset.nx_library_remove"
  bl_label = "Remove Lirary"
  bl_options = {"INTERNAL"}

  def execute(self, context):
    scene = context.scene

    library_id = scene.NXPreview.library_id
    bpy.ops.preferences.asset_library_remove("INVOKE_DEFAULT", index=library_id)
    
    library_id -= 1 if library_id > 0 else 0
    scene.NXPreview.library_id = library_id

    return {"FINISHED"}