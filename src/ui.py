import bpy


class BasePanel:
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
    bl_options = {"DEFAULT_CLOSED"}


class ACG_PT_Main(bpy.types.Panel, BasePanel):
    bl_idname = "ACG_PT_Main"
    bl_label = "AmbientCG Utils"

    def draw(self, context):
        props = context.scene.acg
        layout = self.layout

        layout.prop(props, "directory")
        layout.prop(props, "action")

        layout.operator("acg.load_files")
