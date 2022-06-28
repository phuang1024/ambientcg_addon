import os

import bpy

from .icon import get_tex_icon


class ACG_UL_ArcTextures(bpy.types.UIList):
    """
    Draws textures from archive.
    """

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        tex_icon = get_tex_icon(item.name)
        icon_id = icon if tex_icon is None else tex_icon.icon_id
        layout.label(text=item.name, icon_value=icon_id)


class ACG_UL_QueryTextures(bpy.types.UIList):
    """
    Draws textures from search query.
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
    bl_label = "AmbientCG"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        pass


class ACG_PT_LoadMats(bpy.types.Panel, BasePanel):
    bl_parent_id = "ACG_PT_Main"
    bl_label = "Load Materials"

    def draw(self, context):
        prefs = context.preferences.addons[__package__].preferences
        props = context.scene.acg
        layout = self.layout

        if os.path.isdir(prefs.arcpath):
            col = layout.column(align=True)

            # Above list.
            row = col.row(align=True)
            row.operator("acg.search_textures", text="Refresh", icon="FILE_REFRESH")

            # List showing materials found.
            col.template_list("ACG_UL_ArcTextures", "",
                props, "arc_textures", props, "arc_textures_index", rows=3)
            layout.prop(props, "resolution", expand=True)

            # Below list.
            col = layout.column(align=True)
            col.prop(props, "ui_options", toggle=True,
                icon="TRIA_DOWN" if props.ui_options else "TRIA_RIGHT")

            if props.ui_options:
                box = col.box()
                box.prop(props, "action")
                box.prop(props, "file_action")
                if props.file_action in ("0", "1"):
                    box.prop(props, "copy_dir", text="Folder")

            layout.operator("acg.load_archive", text="Load Material", icon="IMPORT")

        else:
            box.label(text="Archive path is not set. See preferences.", icon="ERROR")


class ACG_PT_Archive(bpy.types.Panel, BasePanel):
    bl_parent_id = "ACG_PT_Main"
    bl_label = "Archive"

    def draw(self, context):
        prefs = context.preferences.addons[__package__].preferences
        props = context.scene.acg
        layout = self.layout

        if os.path.isdir(prefs.arcpath):
            layout.operator("acg.install_to_arc", text="Install Files to Archive", icon="IMPORT")

        else:
            layout.label(text="Archive path is not set. See preferences.", icon="ERROR")


class ACG_PT_Website(bpy.types.Panel, BasePanel):
    bl_parent_id = "ACG_PT_Main"
    bl_label = "Website"

    def draw(self, context):
        prefs = context.preferences.addons[__package__].preferences
        props = context.scene.acg
        layout = self.layout

        layout.operator("wm.url_open", text="Open AmbientCG", icon="URL").url = \
            "https://www.ambientcg.com"

        if os.path.isdir(prefs.arcpath):
            col = layout.column(align=True)

            # Above list.
            row = col.row(align=True)
            row.operator("acg.query_textures", text="Search", icon="FILE_REFRESH")

            # List showing materials found.
            col.template_list("ACG_UL_QueryTextures", "",
                props, "query_textures", props, "query_textures_index", rows=3)

            # Below list.
            col = layout.column(align=True)
            col.prop(props, "query_options", toggle=True,
                icon="TRIA_DOWN" if props.query_options else "TRIA_RIGHT")

            if props.query_options:
                box = col.box()
                box.prop(props, "query_limit")

        else:
            box.label(text="Archive path is not set. See preferences.", icon="ERROR")
