"""
Material loading, applying, searching, etc.
"""

__all__ = (
    "get_map_files",
    "load_material",
)

import os

import bpy


def get_map_files(files):
    """
    Returns dict of map name to file path.
    """
    maps = {}

    for f in files:
        name = os.path.basename(f).lower()
        if "color" in name:
            maps["color"] = f
        elif "ambientocclusion" in name:
            maps["ao"] = f
        elif "displacement" in name:
            maps["disp"] = f
        elif "normalgl" in name:
            maps["nrm"] = f
        elif "roughness" in name:
            maps["rough"] = f

    return maps


def load_material(name, maps):
    print(name)
    print(maps)
