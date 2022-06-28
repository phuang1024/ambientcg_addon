import os
import platform
import random
import requests
import shutil
import tempfile
from zipfile import ZipFile

import bpy
from bpy.props import *

from .icon import refresh_icons
from .material import do_action

REQUEST_ENDPOINT = "https://ambientcg.com/api/v2/full_json"


class ACG_OT_SearchTextures(bpy.types.Operator):
    """
    Search for textures in archive.
    Stores results in scene.acg.arc_textures.
    """
    bl_idname = "acg.search_textures"
    bl_label = "Search"
    bl_description = "Search for textures in the archive."
    bl_options = {"REGISTER"}

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        props = context.scene.acg
        props.arc_textures.clear()

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

        for name in sorted(textures.keys()):
            res, path = textures[name]

            p = props.arc_textures.add()
            p.name = name
            p.res = " ".join(str(r) for r in sorted(res))

        refresh_icons({n: i[1] for n, i in textures.items()})

        return {"FINISHED"}


class ACG_OT_QueryTextures(bpy.types.Operator):
    """
    Search for textures from website.
    Stores results in scene.acg.query_textures.
    """
    bl_idname = "acg.query_textures"
    bl_label = "Search"
    bl_description = "Search for textures from the website."
    bl_options = {"REGISTER"}

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        props = context.scene.acg
        props.query_textures.clear()

        r = requests.get(
            REQUEST_ENDPOINT,
            params={
                "type": "Material",
                "include": "downloadData,previewData",
                "limit": props.query_limit,
            },
            headers={"User-Agent": "blah"}
        )
        if r.status_code == 200:
            data = r.json()

            for asset in data["foundAssets"]:
                downloads = asset["downloadFolders"]["default"]["downloadFiletypeCategories"] \
                    ["zip"]["downloads"]

                ress = []
                for info in downloads:
                    res = int(info["attribute"].split("-")[0][:-1])
                    ress.append(res)

                p = props.query_textures.add()
                p.name = asset["assetId"]
                p.res = " ".join(map(str, sorted(ress)))

        else:
            self.report({"ERROR"}, "Failed to query website.")

        return {"FINISHED"}


class ACG_OT_LoadArchive(bpy.types.Operator):
    bl_idname = "acg.load_archive"
    bl_label = "Load From Archive"
    bl_description = "Load textures from archive."
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        props = context.scene.acg

        textures = props.arc_textures
        index = props.arc_textures_index
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

        copy_dir = bpy.path.abspath(props.copy_dir)
        local_dir = os.path.join(copy_dir, basename)
        os.makedirs(copy_dir, exist_ok=True)

        # More validate settings
        if props.file_action == "0" and platform.system() == "Windows":
            self.report({"ERROR"}, "Cannot create symlink on Windows.")
            return {"CANCELLED"}

        if props.file_action in ("0", "1") and os.path.exists(local_dir):
            self.report({"WARNING"}, "Local directory already exists, not updating local copy.")
        else:
            if props.file_action == "0":
                os.symlink(path, local_dir)
                path = local_dir
            elif props.file_action == "1":
                shutil.copytree(path, local_dir)
                path = local_dir
            elif props.file_action == "2":
                pass

        do_action(basename, path, props.action, self.report)

        return {"FINISHED"}


class ACG_OT_InstallToArc(bpy.types.Operator):
    bl_idname = "acg.install_to_arc"
    bl_label = "Install to Archive"
    bl_description = "Copy selected material to archive."
    bl_options = {"REGISTER"}

    filepath: StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        prefs = context.preferences.addons[__package__].preferences
        props = context.scene.acg

        path = os.path.abspath(bpy.path.abspath(self.filepath))
        # Remove file extension and "-JPG", "-PNG"
        name = os.path.basename(path).replace(".zip", "").rsplit("-", 1)[0]

        if os.path.exists(path):
            if os.path.isfile(path) and path.endswith(".zip"):
                # Extract zip and set path to tmp dir.
                tmp = tempfile.gettempdir()
                rand = random.randint(0, 1e9)
                tmpdir = os.path.join(tmp, f"ambientcg_addon_{rand}")
                os.makedirs(tmpdir)
                with ZipFile(path, "r") as f:
                    f.extractall(tmpdir)
                path = tmpdir

            shutil.copytree(path, os.path.join(prefs.arcpath, name))

        else:
            self.report({"ERROR"}, "Please select zip file or directory.")
            return {"CANCELLED"}

        return {"FINISHED"}
