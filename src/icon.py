import os

import bpy
import bpy.utils.previews

texture_icons = None


def get_tex_icon(name):
    global texture_icons
    if texture_icons is None:
        return None
    return texture_icons.get(name)


def refresh_icons(textures):
    """
    After searching textures, call this to assign icons to each texture.

    :param textures: Mapping of name to directory path.
    """
    global texture_icons
    if texture_icons is not None:
        unregister_icons()

    texture_icons = bpy.utils.previews.new()
    for name, directory in textures.items():
        for f in os.listdir(directory):
            if "PREVIEW" in f:
                path = os.path.join(directory, f)
                texture_icons.load(name, path, "IMAGE")
                break


def unregister_icons():
    global texture_icons
    if texture_icons is not None:
        bpy.utils.previews.remove(texture_icons)
        texture_icons = None
