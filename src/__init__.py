bl_info = {
    "name": "AmbientCG Utils",
    "description": "Utilities for using AmbientCG assets. Not related to AmbientCG.",
    "author": "Patrick Huang",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "Properties > Material > AmbientCG Utils",
    "doc_url": "https://github.com/phuang1024/ambientcg_utils",
    "bug_url": "https://github.com/phuang1024/ambientcg_utils/issues",
    "category": "Material",
}

import bpy

from .ops import ACG_OT_LoadFiles
from .props import ACGProps
from .ui import ACG_PT_Main


classes = (
    ACGProps,
    ACG_OT_LoadFiles,
    ACG_PT_Main,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.acg = bpy.props.PointerProperty(type=ACGProps)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.acg


if __name__ == "__main__":
    register()
