from math import radians
import bpy
from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator
from . nxpreview_base import NXPreview

class OBJECT_OT_NXToggleAsset(Operator, NXPreview):
  bl_idname = "object.nxtoggle_asset"
  bl_label = "Toggle Asset"
  bl_description = "Marh as asset if it's not, clear asset if it's"
  bl_options = {"INTERNAL"}

  is_asset : bpy.props.BoolProperty(
    name="is_asset",
    default=False
  )

  def execute(self, context):
    obj = context.object

    if self.is_asset:
      obj.asset_clear()
      msg = "Object asset is remove"
    else:
      obj.asset_mark()
      msg = "Obbject is marked as asset"

    # needed to update scene
    bpy.ops.object.editmode_toggle()
    bpy.ops.object.editmode_toggle()

    print(f"====={msg}=====")
    self.report({'INFO'}, msg)
    return {'FINISHED'}


class OBJECT_OT_NXPreview(Operator, NXPreview):
  bl_idname = "object.nxpreview"
  bl_label = "Render Preview"
  bl_options = {"INTERNAL"}

  def after_render_preview(self, scene, depsgraph):
    obj = bpy.data.objects[self.original_object]
    if self.mark_as_asset or obj.asset_data is not None:
      obj.asset_mark()
    
      if self.assign_preview:
        bpy.ops.ed.lib_id_load_custom_preview(
          {"id":obj}, 
          filepath=f"{self.filepath}.{self.file_format['ext']}"
        )
      else:
        obj.asset_generate_preview()
    
    scene.render.use_lock_interface = False
    self.purge_scene()
    bpy.data.scenes.remove(bpy.data.scenes[self.sc_name], do_unlink=True)
    self.purge_orphan_data()

    print("=====Preview rendered=====")
    self.report({'INFO'}, "Preview rendered")
    
    bpy.app.handlers.render_post.remove(self.after_render_preview)
  
  def execute(self, context):
    scene = context.scene
    self.original_scene = scene.name
    obj = context.object
    self.original_object = obj.name

    self.create_scene_and_switch_to(context)

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
