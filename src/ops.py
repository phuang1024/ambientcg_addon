import os

import bpy
from bpy.props import *

from .material import *


class ACG_OT_LoadFiles(bpy.types.Operator):
    bl_idname = "acg.load_files"
    bl_label = "Load from files"
    bl_description = "Load material from images or zip."
    bl_options = {"UNDO"}

    filepath: StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        path = os.path.abspath(bpy.path.abspath(self.filepath))

        if os.path.isdir(path):
            maps = get_map_files(os.listdir(path))
            maps = {k: os.path.join(path, f) for k, f in maps.items()}
            load_material(os.path.basename(path), maps)

        elif os.path.isfile(path) and path.endswith(".zip"):
            pass

        else:
            self.report({"ERROR"}, "Please select zip file or directory.")
            return {"CANCELLED"}

        return {"FINISHED"}
