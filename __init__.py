# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
  "name" : "NX_Preview",
  "author" : "Franck Demongin",
  "description" : "Render preview for Asset Browser",
  "blender" : (3, 0, 0),
  "version" : (1, 0, 0),
  "location" : "View 3D > Sidebar > NX_Tools",
  "warning" : "Beta",
  "doc_url" : "https://github.com/Franck-Demongin/NX_Preview",
  "category" : "Render"
}

import tempfile
import bpy
from bpy.props import (StringProperty,
                       PointerProperty,
                       BoolProperty,
                       EnumProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty)
from bpy.types import Panel, PropertyGroup, UIList
from . nxpreview_op import (OBJECT_OT_NXToggleAsset, 
                            OBJECT_OT_NXPreview, 
                            ASSET_OT_NXAddLibrary,
                            ASSET_OT_NXRemoveLibrary)

def update_backdrop(self, context):
  if self.use_backdrop:
    self.use_background = False

def update_background(self, context):
  if self.use_background:
    self.use_backdrop = False  

def library_id_update(self, context):
  default_id = self.bl_rna.properties.get('library_id').default
  id = self.library_id
  
  libraries_len = len(context.preferences.filepaths.asset_libraries)

  if (libraries_len == 0 or
      len(context.preferences.filepaths.asset_libraries[id].name) == 0
  ):
    self.save_asset = False

tempD = tempfile.gettempdir()

class MXPreviewProperties(PropertyGroup):
  path : StringProperty(
      name="path",
      description=f"Path to preview output.\nLet empty to save in tempdir: {tempD}",
      default="",
      maxlen=1024,
      subtype='DIR_PATH'
  )
  mark_as_asset : BoolProperty(
      name="mark_as_asset",
      description="Mark object as asset if it's not when render preview",
      default=False
  )
  assign_preview : BoolProperty(
      name="asign_preview",
      description="Assign preview to asset",
      default=True
  )
  use_backdrop : BoolProperty(
      name="use_backdrop",
      description="Add a backdrop",
      default=False,
      update=update_backdrop
  )
  backdrop_style : EnumProperty(
      name="Backdrop Style",
      description="Choose backdrop style",
      items={
        ('NEUTRAL', 'neutral', 'Neutral'),
        ('LIGHT', 'light', 'Light'),
        ('DARK', 'dark', 'Dark')
      },
      default="NEUTRAL"
  )
  use_background : BoolProperty(
    name="use_background",
    description="Add a background",
    default=False,
    update=update_background
  )
  background_color : FloatVectorProperty(
    name="Background Color",
    description="Color used for the background",
    subtype="COLOR",
    default=(0.25,0.25,0.25),
    min=0,
    max=1,
    size=3
  )
  show_lighting : BoolProperty(
    name="Show Lighting",
    description="Display lighting options",
    default=False
  )
  world_strength : FloatProperty(
    name="World Strength",
    description="Adjust the strength of the world",
    default=0.5,
    min=0,
    max=1,
    step=10
  )
  light_top_strength : FloatProperty(
    name="Light Top Strength",
    description="Adjust the strength of the top light",
    default=0.5,
    min=0,
    max=1,
    step=10
  )
  light_left_strength : FloatProperty(
    name="Light Left Strength",
    description="Adjust the strength of the left light",
    default=0.5,
    min=0,
    max=1,
    step=10
  )
  light_right_strength : FloatProperty(
    name="Light Right Strength",
    description="Adjust the strength of the Right light",
    default=0.5,
    min=0,
    max=1,
    step=10
  )
  camera_focal : IntProperty(
    name="Camera Focal",
    description="Adjust the focal length",
    default=85,
    min=24,
    max=250
  )
  camera_align_h : EnumProperty(
      name="Horizontal Alignement",
      description="Choose camera horizontal alignement",
      items={
        ('LEFT', 'left', 'Left'),
        ('CENTER', 'center', 'Center'),
        ('RIGHT', 'right', 'Right')
      },
      default="RIGHT"
  )
  camera_align_v : EnumProperty(
      name="Vertical Alignement",
      description="Choose camera vertical alignement",
      items={
        ('TOP', 'top', 'Top'),
        ('CENTER', 'center', 'Center'),
        ('BOTTOM', 'bottom', 'Bottom')
      },
      default="CENTER"
  )
  save_in_file_folder : BoolProperty(
    name="Save in File Folder",
    description="Save preview in .blend folder",
    default=False
  )
  save_asset : BoolProperty(
    name="Save Asset",
    description="Save asset in selected library",
    default=False
  )
  library_id : IntProperty(default=0, min=0, update=library_id_update)
  apply_modifiers : BoolProperty(
    name="Apply Modifiers",
    description="Apply all modifiers before save asset in library",
    default=False
  )


class PREFERENCE_UL_asset_library(UIList):
   
  def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
    self.lib_id = index
    library = item
    row = layout.row(align=False)

    if self.layout_type in {'DEFAULT', 'COMPACT'}:
      row.alert = not library.name
      row.prop(library, "name", text="Name", emboss=False)
      row.alert = False
      row.prop(library, "path", text="", icon_only=True, icon="ADD", emboss=False)
        
    elif self.layout_type in {'GRID'}:
      layout.alignment = 'CENTER'
      layout.label(text="", icon_value=icon)


class PreviewPanel:
  bl_space_type = 'VIEW_3D'
  bl_region_type = 'UI'
  bl_category = 'NX_Tools'


class NXPREVIEW_PT_control_panel(Panel, PreviewPanel):
  """Creates a Panel in the Object properties window"""
  bl_label = "Asset Preview"
  bl_idname = 'NXPREVIEW_PT_control_panel'
        
  @classmethod
  def poll(cls, context):
      obj = context.object
      return (context.mode == 'OBJECT' and
              obj is not None and
              obj.type in ['MESH',]
              )

  def draw(self, context):
    scene = context.scene
    obj = context.object
    layout = self.layout
    layout.use_property_split = False
    layout.use_property_decorate = False

    col = layout.column()

    if scene.name == "NXPreviewScene":
      col.label(text="Render Preview")
    else:
      row = col.row(align=False)
      row.label(text=context.object.name)
      
      is_asset = False
      msg = "Mark as Asset"

      if obj.asset_data is not None:
        msg = "Clear Asset"
        is_asset = True
      op = row.operator('object.nxtoggle_asset', text="", icon="ASSET_MANAGER", depress=is_asset)
      op.is_asset = is_asset
      
      col.separator() 

      col.prop(scene.NXPreview, 'mark_as_asset', text="Mark as Asset")
      if obj.asset_data is not None or scene.NXPreview.mark_as_asset:
        col.prop(scene.NXPreview, 'assign_preview', text="Assign Preview")  
  
      col.separator()      
      col = layout.column()
      op = col.operator('object.nxpreview', text="Render Preview")
      op.path = scene.NXPreview.path
      op.original_scene = scene.name
      op.original_object = obj.name
      op.mark_as_asset = scene.NXPreview.mark_as_asset
      op.assign_preview = scene.NXPreview.assign_preview
      op.use_backdrop = scene.NXPreview.use_backdrop
      op.backdrop_style = scene.NXPreview.backdrop_style
      op.use_background = scene.NXPreview.use_background
      color = scene.NXPreview.background_color
      op.background_color = (color.r, color.g, color.b, 1.0)
      op.world_strength = scene.NXPreview.world_strength
      op.light_top_strength = scene.NXPreview.light_top_strength
      op.light_left_strength = scene.NXPreview.light_left_strength
      op.light_right_strength = scene.NXPreview.light_right_strength
      op.camera_focal = scene.NXPreview.camera_focal
      op.camera_align_h = scene.NXPreview.camera_align_h
      op.camera_align_v = scene.NXPreview.camera_align_v
      op.save_in_file_folder = scene.NXPreview.save_in_file_folder
      op.save_asset = scene.NXPreview.save_asset
      op.library_id = scene.NXPreview.library_id
      op.apply_modifier = scene.NXPreview.apply_modifiers


class NXPREVIEW_PT_Background(Panel, PreviewPanel):
  bl_label = "Background"
  bl_parent_id = "NXPREVIEW_PT_control_panel"
  bl_options = {"DEFAULT_CLOSED"}

  def draw(self, context):
    scene = context.scene
    layout = self.layout
    layout.use_property_split = False
    layout.use_property_decorate = False

    col = layout.column()
    col.prop(scene.NXPreview, 'use_backdrop', text="Use Backdrop")
    
    if scene.NXPreview.use_backdrop:
      layout.use_property_split = True
      col = layout.column()  
      col.prop(scene.NXPreview, 'backdrop_style', text="Style")
    
    layout.use_property_split = False
    col = layout.column()
    col.prop(scene.NXPreview, 'use_background', text="Use Background")
    if scene.NXPreview.use_background:
      layout.use_property_split = True
      col = layout.column()
      col.prop(scene.NXPreview, 'background_color', text="Color")


class NXPREVIEW_PT_Lighting(Panel, PreviewPanel):
  bl_label = "Lighting"
  bl_parent_id = "NXPREVIEW_PT_control_panel"
  bl_options = {"DEFAULT_CLOSED"}

  def draw(self, context):
    scene = context.scene
    layout = self.layout
    layout.use_property_split = True
    layout.use_property_decorate = False
    col = layout.column()
    col.prop(scene.NXPreview, "world_strength", text="World")
    col = layout.column(align=True)
    col.prop(scene.NXPreview, "light_top_strength", text="Light Top")
    col.prop(scene.NXPreview, "light_left_strength", text="Left")
    col.prop(scene.NXPreview, "light_right_strength", text="Right")


class NXPREVIEW_PT_Camera(Panel, PreviewPanel):
  bl_label = "Camera"
  bl_parent_id = "NXPREVIEW_PT_control_panel"
  bl_options = {"DEFAULT_CLOSED"}

  def draw(self, context):
    scene = context.scene
    layout = self.layout
    layout.use_property_split = True
    layout.use_property_decorate = False

    col = layout.column()

    col.prop(scene.NXPreview, "camera_focal", text="Focal")
    col.separator()
    col = layout.column()
    row = col.row(align=True)
    row.prop(scene.NXPreview, "camera_align_h", text="Alignement H", expand=True)
    col = layout.column()
    row = col.row(align=True)
    row.prop(scene.NXPreview, "camera_align_v", text="V", expand=True)


class NXPREVIEW_PT_Output(Panel, PreviewPanel):
  bl_label = "Output"
  bl_parent_id = "NXPREVIEW_PT_control_panel"
  bl_options = {"DEFAULT_CLOSED"}

  def draw(self, context):
    scene = context.scene
    obj = context.object
    layout = self.layout
    layout.use_property_split = False
    layout.use_property_decorate = False

    col = layout.column()
    col.label(text="Preview Output")

    if bpy.data.is_saved:
      col.prop(scene.NXPreview, "save_in_file_folder", text="Save in File Folder")
    
    if not scene.NXPreview.save_in_file_folder:
      col.label(text="Select Folder")
      col.prop(scene.NXPreview, "path", text="")


class NXPREVIEW_PT_SaveAsset(Panel, PreviewPanel):
  bl_label = "Save Asset"
  bl_parent_id = "NXPREVIEW_PT_control_panel"
  # bl_options = {"DEFAULT_CLOSED"}

  def draw_header(self, context):
    scene = context.scene
    layout = self.layout
    libraries = context.preferences.filepaths.asset_libraries
    
    col = layout.column()
    if (len(libraries) == 0 or 
        len(libraries[scene.NXPreview.library_id].name) == 0 or
        (context.object.asset_data is None and not scene.NXPreview.mark_as_asset)
    ):
      col.enabled = False
    col.prop(scene.NXPreview, 'save_asset', text="")
  
  def draw(self, context):
    scene = context.scene
    layout = self.layout
    layout.use_property_split = False
    layout.use_property_decorate = False

    col = layout.column()
    col.prop(scene.NXPreview, 'apply_modifiers', text="Apply Modifiers")
    row = layout.row(align=False)

    fp = context.preferences.filepaths
    col = row.column(align=True)
    col.template_list(
      "PREFERENCE_UL_asset_library", 
      "", 
      fp, 
      "asset_libraries", 
      scene.NXPreview, 
      "library_id", 
      type="DEFAULT"
    )
    col = row.column(align=True)
    col.operator('asset.nxadd_library', text="", icon="ADD")
    op = col.operator('asset.nxremove_library', text="", icon="REMOVE")


classes = [
  PREFERENCE_UL_asset_library,
  MXPreviewProperties,
  NXPREVIEW_PT_control_panel,
  NXPREVIEW_PT_Background,
  NXPREVIEW_PT_Lighting,
  NXPREVIEW_PT_Camera,
  NXPREVIEW_PT_Output,
  NXPREVIEW_PT_SaveAsset,
  OBJECT_OT_NXToggleAsset,
  OBJECT_OT_NXPreview,
  ASSET_OT_NXAddLibrary,
  ASSET_OT_NXRemoveLibrary,
]

def register():
  for cls in classes:
    bpy.utils.register_class(cls)

  bpy.types.Scene.NXPreview= PointerProperty(type=MXPreviewProperties)
    

def unregister():
  for cls in classes:
    bpy.utils.unregister_class(cls)

  del bpy.types.Scene.NXPreview
