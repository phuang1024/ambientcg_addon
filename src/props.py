import bpy
from bpy.props import *


def get_resolutions(self, context):
    """
    Used by EnumProperty "resolution" in props.
    Returns options for selected texture.
    """
    index = context.scene.acg.found_textures_index
    if index >= len(context.scene.acg.found_textures):
        return []

    items = []
    for res in context.scene.acg.found_textures[index].res.split():
        items.append((res, f"{res}K", f"{res}K resolution"))

    return items


class ACG_Texture(bpy.types.PropertyGroup):
    """
    Represents one texture in the list of found textures.
    Has a name, directory path, and available resolutions.
    """
    name: StringProperty()
    path: StringProperty()
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

    action: EnumProperty(
        name="Action",
        description="What to do with selected textures.",
        items=(
            ("0", "Node Group", "Create node group of material."),
            ("1", "Material", "Create but don't apply material datablock."),
            ("2", "Apply to Active", "Apply material to active material slot."),
            ("3", "Apply to New", "Apply material to new material slot."),
        )
    )

    # Internal use
    found_textures: CollectionProperty(type=ACG_Texture)
    found_textures_index: IntProperty()
