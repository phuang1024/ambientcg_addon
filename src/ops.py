import os
import platform
import random
import shutil
import tempfile
from zipfile import ZipFile

import bpy
from bpy.props import *

from .icon import refresh_icons
from .material import do_action


class ACG_OT_SearchTextures(bpy.types.Operator):
    """
    Search for textures in archive.
    Stores results in scene.acg.found_textures.
    """
    bl_idname = "acg.search_textures"
    bl_label = "Search"
    bl_description = "Search for textures in the archive."
    bl_options = {"REGISTER"}

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        props = context.scene.acg
        props.found_textures.clear()

        textures = {}  # Map of {name: (resolutions, path)}
        for f in os.listdir(prefs.arcpath):
            path = os.path.join(prefs.arcpath, f)
            if os.path.isdir(path):
                name, res_str = f.rsplit("_", 1)
                res_str = res_str[:-1]  # Remove "K"
                if res_str.isdigit():
                    res = int(res_str)
                    if name not in textures:
                        textures[name] = ([], path)
                    textures[name][0].append(res)

        for name, (res, path) in textures.items():
            p = props.found_textures.add()
            p.name = name
            p.res = " ".join(str(r) for r in sorted(res))

        refresh_icons({n: i[1] for n, i in textures.items()})

        return {"FINISHED"}


class ACG_OT_LoadArchive(bpy.types.Operator):
    bl_idname = "acg.load_archive"
    bl_label = "Load From Archive"
    bl_description = "Load textures from archive."
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        props = context.scene.acg

        textures = props.found_textures
        index = props.found_textures_index
        res = props.resolution

        # Validate settings
        if index < 0 or index >= len(textures):
            self.report({"ERROR"}, "Invalid texture selected.")
            return {"CANCELLED"}
        if not res.isdigit():
            self.report({"ERROR"}, "Invalid resolution selected.")
            return {"CANCELLED"}

        res = int(res)
        tex = textures[index]
        basename = f"{tex.name}_{res}K"
        path = os.path.join(prefs.arcpath, basename)
        local_dir = os.path.join(bpy.path.abspath(props.copy_dir), basename)

        # More validate settings
        if props.file_action == "0" and platform.system() == "Windows":
            self.report({"ERROR"}, "Cannot create symlink on Windows.")
            return {"CANCELLED"}
        if props.file_action in ("0", "1") and os.path.exists(local_dir):
            self.report({"ERROR"}, "Local directory already exists.")
            return {"CANCELLED"}

        if props.file_action == "0":
            os.symlink(path, local_dir)
            path = local_dir
        elif props.file_action == "1":
            shutil.copytree(path, local_dir)
            path = local_dir
        elif props.file_action == "2":
            pass

        do_action(tex.name, path, props.action, self.report)

        return {"FINISHED"}


class ACG_OT_LoadFiles(bpy.types.Operator):
    bl_idname = "acg.load_files"
    bl_label = "Load From Files"
    bl_description = "Load material from images or zip."
    bl_options = {"REGISTER", "UNDO"}

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
