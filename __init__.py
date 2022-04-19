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
from bpy.types import PropertyGroup
from . nxpreview_op import OBJECT_OT_NXPreview
from . nxasset_op import (ASSET_OT_NXAssetToggle,
                          ASSET_OT_NXAssetSave,
                          ASSET_OT_NXLibraryAdd,
                          ASSET_OT_NXLibraryRemove)
from . nxpreview_UI import (PREFERENCE_UL_asset_library,
                            NXPREVIEW_PT_control_panel,
                            NXPREVIEW_PT_Background,
                            NXPREVIEW_PT_Lighting,
                            NXPREVIEW_PT_Camera,
                            NXPREVIEW_PT_Output,
                            NXPREVIEW_PT_SaveAsset)
                            
def update_backdrop(self, context):
  if self.use_backdrop:
    self.use_background = False

def update_background(self, context):
  if self.use_background:
    self.use_backdrop = False  

def update_library_id(self, context):
  id = self.library_id
  
  libraries_len = len(context.preferences.filepaths.asset_libraries)

  if (libraries_len == 0 or
      id >= libraries_len or
      len(context.preferences.filepaths.asset_libraries[id].name) == 0
  ):
    self.save_asset = False
  
  if id > 0 and id >= libraries_len:
    self.library_id = self.last_library_id

  self.last_library_id = self.library_id

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
  library_id : IntProperty(
    default=0, 
    min=0, 
    update=update_library_id
  )
  last_library_id : IntProperty(
    default=0
  )
  apply_modifiers : BoolProperty(
    name="Apply Modifiers",
    description="Apply all modifiers before save asset in library",
    default=False
  )


classes = [
  MXPreviewProperties,
  PREFERENCE_UL_asset_library,
  NXPREVIEW_PT_control_panel,
  NXPREVIEW_PT_Background,
  NXPREVIEW_PT_Lighting,
  NXPREVIEW_PT_Camera,
  NXPREVIEW_PT_Output,
  NXPREVIEW_PT_SaveAsset,
  OBJECT_OT_NXPreview,
  ASSET_OT_NXAssetToggle,
  ASSET_OT_NXAssetSave,
  ASSET_OT_NXLibraryAdd,
  ASSET_OT_NXLibraryRemove,
]

def register():
  for cls in classes:
    bpy.utils.register_class(cls)

  bpy.types.Scene.NXPreview= PointerProperty(type=MXPreviewProperties)
    

def unregister():
  for cls in classes:
    bpy.utils.unregister_class(cls)

  del bpy.types.Scene.NXPreview
