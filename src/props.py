import bpy
from bpy.props import *


class ACGProps(bpy.types.PropertyGroup):
    directory: StringProperty(
        name="Directory",
        description="Directory containing texture files.",
        subtype="DIR_PATH",
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
