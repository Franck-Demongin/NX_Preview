import bpy
from bpy.types import Panel, PropertyGroup, UIList

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

  @classmethod
  def poll(cls, context):
      obj = context.object
      return (context.mode == 'OBJECT' and
              obj is not None and
              obj.type in ['MESH',])


class NXPREVIEW_PT_control_panel(Panel, PreviewPanel):
  """Creates a Panel in the Object properties window"""
  bl_label = "Asset Preview"
  bl_idname = 'NXPREVIEW_PT_control_panel'
        
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
      
      is_asset = True if obj.asset_data is not None else False
      op = row.operator('asset.nx_asset_toggle', 
        text="", icon="ASSET_MANAGER", depress=is_asset)
            
      col.separator() 

      col.prop(scene.NXPreview, 'mark_as_asset', text="Mark as Asset")
      if obj.asset_data is not None or scene.NXPreview.mark_as_asset:
        col.prop(scene.NXPreview, 'assign_preview', text="Assign Preview")  
  
      col.separator()      
      col = layout.column()
      op = col.operator('object.nx_preview', text="Render Preview")
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
  bl_options = {"DEFAULT_CLOSED"}

  def draw_header(self, context):
    scene = context.scene
    layout = self.layout
    libraries = context.preferences.filepaths.asset_libraries
    
    col = layout.column()
    if (len(libraries) == 0 or 
        scene.NXPreview.library_id >= len(libraries) or
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
    col.operator('asset.nx_library_add', text="", icon="ADD")
    op = col.operator('asset.nx_library_remove', text="", icon="REMOVE")
