import os
import random
import tempfile
from zipfile import ZipFile

import bpy
from bpy.props import *

from .material import do_action


class ACG_OT_LoadFiles(bpy.types.Operator):
    bl_idname = "acg.load_files"
    bl_label = "Load From Files"
    bl_description = "Load material from images or zip."
    bl_options = {"UNDO"}

    filepath: StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        props = context.scene.acg

        path = os.path.abspath(bpy.path.abspath(self.filepath))
        name = os.path.basename(path).replace(".zip", "")

        if os.path.exists(path):
            if os.path.isfile(path) and path.endswith(".zip"):
                # Extract zip and set path to tmp dir.
                tmp = tempfile.gettempdir()
                rand = random.randint(0, 1e9)
                tmpdir = os.path.join(tmp, f"ambientcg_utils_{rand}")
                os.makedirs(tmpdir)
                with ZipFile(path, "r") as f:
                    f.extractall(tmpdir)
                path = tmpdir

            do_action(name, path, props.action, self.report)

        else:
            self.report({"ERROR"}, "Please select zip file or directory.")
            return {"CANCELLED"}

        return {"FINISHED"}
