import os
from math import radians
import bpy
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator
from . nxbase_op import NXBase

class OBJECT_OT_NXPreview(Operator, NXBase):
  bl_idname = "object.nx_preview"
  bl_label = "Render Preview"
  bl_options = {"INTERNAL"}

  def after_render_preview(self, scene, depsgraph):
    obj = bpy.data.objects[self.original_object]
    if self.mark_as_asset or obj.asset_data is not None:
      obj.asset_mark()
    
      if self.assign_preview:
        bpy.ops.ed.lib_id_load_custom_preview(
          {"id":obj}, 
          filepath=f"{self.preview_filepath}.{self.file_format['ext']}"
        )
      else:
        obj.asset_generate_preview()
    
    scene.render.use_lock_interface = False
    self.purge_scene(self.scene_preview)
    bpy.data.scenes.remove(bpy.data.scenes[self.scene_preview], do_unlink=True)
    self.purge_orphan_data()

    print("=====Preview rendered=====")

    bpy.ops.asset.nx_asset_save(
                                save_asset=self.save_asset,
                                filepath=f"{self.preview_filepath}.{self.file_format['ext']}",
                                assign_preview=self.assign_preview,
                                library_id=self.library_id,
                                original_scene=self.original_scene,
                                original_object=self.original_object,
                                apply_modifiers=self.apply_modifier
                              )
    # if self.save_asset:
    #   libraries = bpy.context.preferences.filepaths.asset_libraries
    #   if (self.library_id >= 0 and 
    #       self.library_id < len(libraries) and
    #       len(libraries[self.library_id].name) > 0 and
    #       os.path.isdir(libraries[self.library_id].path)
    #   ):
    #     path_ = os.path.join(libraries[self.library_id].path, f"{self.original_object}.blend")
        
    #     if bpy.data.is_saved:
    #       bpy.ops.file.make_paths_absolute()

    #     bpy.context.scene.name = f"{self.original_scene}_"
    #     self.create_scene_and_switch_to(bpy.context, self.scene_asset, True)

    #     o = obj
    #     loc = obj.location.copy()
    #     if self.apply_modifier:
    #       co = obj.copy()
    #       co.data = obj.data.copy()
    #       co.data.name = obj.data.name
    #       co.name = obj.name
    #       bpy.context.collection.objects.link(co)
    #       co.select_set(True)
    #       bpy.context.view_layer.objects.active = co
    #       bpy.ops.object.convert(target="MESH")
    #       o = co
    #       if self.mark_as_asset or obj.asset_data is not None:
    #         o.asset_mark()          
    #         if self.assign_preview:
    #           bpy.ops.ed.lib_id_load_custom_preview(
    #             {"id":o}, 
    #             filepath=f"{self.filepath}.{self.file_format['ext']}"
    #           )
    #         else:
    #           pass
    #           # print('GENERATE_PREVIEW', o.name)
    #           # o.asset_generate_preview()
    #     else:
    #       bpy.context.collection.objects.link(o)
    #     data = {bpy.data.scenes[bpy.context.scene.name]}
    #     bpy.data.libraries.write(path_, data)
    #     bpy.data.scenes.remove(bpy.data.scenes[self.scene_asset])
    #     bpy.context.scene.name = self.original_scene
    #     if self.apply_modifier:
    #       obj.data.name = o.data.name
    #       obj.name = o.name
    #       bpy.data.objects.remove(o, do_unlink=True)
    #     self.purge_orphan_data()
        
    #     if bpy.data.is_saved:
    #       bpy.ops.file.make_paths_relative()
    #   else:
    #     print('LIB NOT EXIST')

    self.report({'INFO'}, "Preview rendered")
    
    bpy.app.handlers.render_post.remove(self.after_render_preview)
  
  def execute(self, context):
    scene = context.scene
    self.original_scene = scene.name
    obj = context.object
    self.original_object = obj.name

    self.create_scene_and_switch_to(context, self.scene_preview)

    self.copy_object(context)

    self.add_cam(context)

    self.add_light(context, "Area_1", loc=(0,-1,3), rot=(18.7,0,0), size=2, 
                    energy=self.light_top_strength, energy_max=75)
    self.add_light(context, "Area_2", loc=(-2,-3,3), rot=(34.2,0,-58.6), size=0.25, 
                    energy=self.light_left_strength, energy_max=150)
    self.add_light(context, "Area_3", loc=(4,0,1), rot=(0,75,0), size=0.25, 
                    energy=self.light_right_strength, energy_max=100)

    self.add_world(context)

    if self.use_backdrop:
      self.add_backdrop(context)
    
    if self.use_background:
      self.add_background(context)

    self.render_preview(context)    
    context.window.scene = scene    

    return {'FINISHED'}

  def invoke(self, context, event):
    if self.after_render_preview not in bpy.app.handlers.render_post:
       bpy.app.handlers.render_post.append(self.after_render_preview)
    return self.execute(context)
