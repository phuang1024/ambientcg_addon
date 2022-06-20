import bpy
from bpy.props import *


class ACGProps(bpy.types.PropertyGroup):
    test: BoolProperty(
        name="a",
    )
