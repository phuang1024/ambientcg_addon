bl_info = {
    "name": "AmbientCG",
    "description": "Utilities for using AmbientCG assets.",
    "author": "Patrick Huang",
    "version": (0, 0, 3),
    "blender": (2, 80, 0),
    "location": "Properties > Material > AmbientCG Utils",
    "doc_url": "https://github.com/phuang1024/ambientcg_addon/wiki",
    "tracker_url": "https://github.com/phuang1024/ambientcg_addon/issues",
    "category": "Material",
}

import bpy

from .icon import unregister_icons
from .ops import *
from .props import *
from .ui import *


classes = (
    ACG_Texture,
    ACG_Prefs,
    ACG_Props,
    ACG_OT_SearchTextures,
    ACG_OT_QueryTextures,
    ACG_OT_LoadArchive,
    ACG_OT_InstallToArc,
    ACG_UL_ArcTextures,
    ACG_UL_QueryTextures,
    ACG_PT_Main,
    ACG_PT_LoadMats,
    ACG_PT_Archive,
    ACG_PT_Website,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.acg = bpy.props.PointerProperty(type=ACG_Props)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    unregister_icons()
    del bpy.types.Scene.acg


if __name__ == "__main__":
    register()
