import os

import bpy

from .icon import get_tex_icon


class ACG_UL_Textures(bpy.types.UIList):
    """
    Drawer for texture choices in the UI.
    """
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        tex_icon = get_tex_icon(item.name)
        icon_id = icon if tex_icon is None else tex_icon.icon_id
        layout.label(text=item.name, icon_value=icon_id)


class BasePanel:
    """
    Defines common properties for panels.
    """
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"


class ACG_PT_Main(bpy.types.Panel, BasePanel):
    bl_idname = "ACG_PT_Main"
    bl_label = "AmbientCG Utils"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        pass


class ACG_PT_Archive(bpy.types.Panel, BasePanel):
    bl_parent_id = "ACG_PT_Main"
    bl_label = "Archive"

    def draw(self, context):
        prefs = context.preferences.addons[__package__].preferences
        props = context.scene.acg
        layout = self.layout

        if os.path.isdir(prefs.arcpath):
            col = layout.column(align=True)

            # Buttons above list.
            row = col.row(align=True)
            row.operator("acg.search_textures", text="Refresh", icon="FILE_REFRESH")

            # List showing materials found.
            col.template_list("ACG_UL_Textures", "",
                props, "found_textures", props, "found_textures_index", rows=5)

            # Buttons below list.
            layout.prop(props, "resolution", expand=True)
            layout.prop(props, "action")
            layout.prop(props, "file_action")
            if props.file_action in ("0", "1"):
                layout.prop(props, "copy_dir", text="Folder")

            layout.operator("acg.load_archive", text="Load Material", icon="IMPORT")

        else:
            box.label(text="Archive path is not set. See preferences.", icon="ERROR")

        layout.separator()
