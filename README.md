# NX_Preview

Blender addon for generate assets preview.

<img src="https://img.shields.io/badge/Blender-3.0.0-green" /> <img src="https://img.shields.io/badge/Python-3.10-blue" /> <img src="https://img.shields.io/badge/Addon-1.0.0.Beta-orange" /> 
[![GPLv3 license](https://img.shields.io/badge/License-GPLv3-blue.svg)](http://perso.crans.org/besson/LICENSE.html)

> *Addon under development. Some features can be deleted and others appear.  
> **Use with caution!***

## Installation

Download ZIP file on your system.

In Blender, install addon from _Preferences > Add-ons > Install_...  
Activate the addon

## Usage

In Object Mode **NX_Preview** is located in the _Sidebar (N) > NX_Tools_

Select an object of type _mesh_

You can see on the right of the object's name if it's an asset or not and easely toggle this state by pressing the icon  
![asset_off](https://user-images.githubusercontent.com/54265936/162628484-a74b5d16-3157-4e4a-a02b-86b981d3371f.png)
![asset_on](https://user-images.githubusercontent.com/54265936/162628486-445a40ef-ff8d-4f9e-b245-b068f44e2451.png)

If the option _Mark as Asset (Default False)_ is checked, the object selected will be mark as asset if it's not.  
It's a convenient way to mark object as asset and assign them a preview with a single operation.

The option _Assign Preview (default True)_ is available if the selected object is mark as asset or if the option _Mark as Asset_ is checked.  
If it's True, the preview will be use in the Asset Manager, if it's False the generated preview created by Blender will be use.

Generate the preview by clicking on _Render Preview_  
![render_preview](https://user-images.githubusercontent.com/54265936/162630062-2ed2624d-98c9-418d-be19-541220d33b36.png)

## Options

There are a few options to control how the preview are rendered :

- _add a background or a backdrop_
- _control the lighting_
- _change the point of view_
- _select the output folder_
- _save asset in library_ [![Generic badge](https://img.shields.io/badge/NEW-blue.svg)](https://shields.io/)

### Background

It's possible to choose between _Backdrop_ or _Background_  
If nothing is selected, the preview will be rendered on a transparent background.

#### Backdrop

![backdrop](https://user-images.githubusercontent.com/54265936/162631642-a81f8d07-5cb2-419e-86c0-72af783b73f3.png)

This option add a backdrop under the object.  
_Style_ can be set to _Neutral (Default)_, _Light_ or _Dark_  
Use a backdrop add soft shadows on and near the object.

![Suzanne_backdrop](https://user-images.githubusercontent.com/54265936/162631786-43b5fba3-73f1-4c56-8dc8-12bab6fb3973.png)

#### Background

![background](https://user-images.githubusercontent.com/54265936/162631649-02b0c98b-b4aa-4d2d-a056-bab1e0e917d0.png)

Add a background color after the render of the preview.  
_Color_ can be selected in a color selector.

![Suzanne_background](https://user-images.githubusercontent.com/54265936/162634565-8a528ef9-e3f4-4a9e-a2a8-037f2ad4c35a.png)

### Lighting

This section offer the possibilities to adjust the lighting of the scene used to create the preview.

![lighting](https://user-images.githubusercontent.com/54265936/162632321-f428df52-b758-48a4-a7fa-675edcf552a6.png)

_World_ adjust the strenght of the HDRI used for global illumination.  
Light _Top_, _Left_ and _Right_ adjust the power of each lights in the scene.

![Suzanne_lighting](https://user-images.githubusercontent.com/54265936/162634493-c9eb7d7a-52ca-43d6-b294-8f99b16d942d.png)

### Camera

Adjust the focal of the camera and the point of vue horizontally and vertically.

![camera](https://user-images.githubusercontent.com/54265936/162635311-89e225dc-c343-4d38-a119-bdcb38a24d64.png)

![Suzanne_camera](https://user-images.githubusercontent.com/54265936/162636201-6c6e7c67-f882-4ec6-b0e1-9a0912e93b0b.png)

### Output

Select a folder to save preview.

![output](https://user-images.githubusercontent.com/54265936/163257840-a923596f-7986-4c59-93ac-a12d2d5d9bca.png)

The _Save to File Folder_ option is displayed if the .blend file is saved. Once selected, the preview will be saved in its folder. [![Generic badge](https://img.shields.io/badge/NEW-blue.svg)](https://shields.io/)

The folder selector allows to choose a folder to save the previews.  
Let empty to use OS temp dir.

### Save Asset [![Generic badge](https://img.shields.io/badge/NEW-blue.svg)](https://shields.io/)

This option is allowed if the object is marked as asset or if the option _Mark as Asset_ is active and if a library exist and is selected.

![save_asset](https://user-images.githubusercontent.com/54265936/163256970-0da8411b-8f71-4557-beac-ea9193c8d2a1.png)

The libraries are selectable by clicking on their name, (double-click to edit it).  
The folder is also editable by clicking on the icon. Libraries could be deleted (files are not) and some new libraries can be add.

To save an asset, select one library, and render the preview, a .blend file will be registered in the appropriate folder with the name of the object (files with the same name will be remove).




