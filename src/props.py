import platform

import bpy
from bpy.props import *


def get_resolutions(self, context):
    """
    Used by EnumProperty "resolution" in props.
    Returns options for selected texture.
    """
    index = context.scene.acg.arc_textures_index
    if index >= len(context.scene.acg.arc_textures):
        return []

    items = []
    for res in context.scene.acg.arc_textures[index].res.split():
        items.append((res, f"{res}K", f"{res}K resolution"))

    return items


class ACG_Texture(bpy.types.PropertyGroup):
    """
    Represents one texture in the list of found textures.
    Has a name, directory path, and available resolutions.
    """
    name: StringProperty()
    res: StringProperty()  # Space separated list of resolutions.


class ACG_Prefs(bpy.types.AddonPreferences):
    bl_idname = __package__

    arcpath: StringProperty(
        name="Archive Path",
        description="Path to textures archive.",
        subtype="DIR_PATH",
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "arcpath")


class ACG_Props(bpy.types.PropertyGroup):
    resolution: EnumProperty(
        name="Resolution",
        description="Resolution to use for selected texture.",
        items=get_resolutions,
    )

    ui_options: BoolProperty(
        name="Show More Options",
        description="Show more options.",
        default=False,
    )

    action: EnumProperty(
        name="Action",
        description="What to do with selected textures.",
        items=(
            ("0", "Create Node Group", "Create node group of material."),
            ("1", "Create Material", "Create but don't apply material datablock."),
            ("2", "Apply to Active Slot", "Apply material to active material slot."),
            ("3", "Apply to New Slot", "Apply material to new material slot."),
        ),
        default="2",
    )

    file_action: EnumProperty(
        name="File Action",
        description="How to handle files.",
        items=(
            ("0", "Symlink to Project",
                "Create a symlink from the current directory to the archive."),
            ("1", "Copy to Project", "Copy from archive to the current directory."),
            ("2", "Reference Archive", "Load images referenced to the archive."),
        ),
        default="1" if platform.system() == "Windows" else "0",
    )

    copy_dir: StringProperty(
        name="Copy Directory",
        description="Directory to copy files to.",
        subtype="DIR_PATH",
        default="//",
    )

    query_options: BoolProperty(
        name="Show More Options",
        description="Show more options.",
        default=False,
    )

    query_limit: IntProperty(
        name="Query Limit",
        description="Max number of textures to query.",
        default=20,
        min=1,
        max=100,
    )

    # Internal use

    # Textures from the archive.
    arc_textures: CollectionProperty(type=ACG_Texture)
    arc_textures_index: IntProperty()

    # Textures from website query.
    query_textures: CollectionProperty(type=ACG_Texture)
    query_textures_index: IntProperty()
