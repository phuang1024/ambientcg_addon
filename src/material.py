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


def add_image_node(group, path, non_color=True, hide=True):
    img = bpy.data.images.load(path)
    if non_color:
        img.colorspace_settings.name = "Non-Color"

    node = group.nodes.new("ShaderNodeTexImage")
    node.image = img
    if hide:
        node.hide = True

    return node


def create_node_group(name, maps):
    mat = bpy.data.node_groups.new(name, "ShaderNodeTree")

    # Inputs and outputs
    mat.inputs.new("NodeSocketVector", "Mapping")
    mat.inputs.new("NodeSocketFloat", "AO Strength")
    mat.inputs.new("NodeSocketFloat", "Min Roughness")
    mat.inputs.new("NodeSocketFloat", "Max Roughness")
    mat.inputs.new("NodeSocketFloat", "Bump Distance")
    mat.outputs.new("NodeSocketShader", "BSDF")

    mat.inputs[1].default_value = 1
    mat.inputs[2].default_value = 0
    mat.inputs[3].default_value = 1
    mat.inputs[4].default_value = 0.1
    for i in range(1, 5):
        mat.inputs[i].min_value = 0
        mat.inputs[i].max_value = 1

    # Input output shader nodes.
    inputs = mat.nodes.new("NodeGroupInput")
    inputs.location = (-50, -100)
    outputs = mat.nodes.new("NodeGroupOutput")
    outputs.location = (1300, 180)
    shader = mat.nodes.new("ShaderNodeBsdfPrincipled")
    shader.location = (950, 200)

    mat.links.new(outputs.inputs[0], shader.outputs[0])

    # Color and AO
    col_ao_mix = mat.nodes.new("ShaderNodeMixRGB")
    col_ao_mix.location = (750, 200)
    col_ao_mix.blend_type = "MULTIPLY"
    col_ao_mix.inputs[1].default_value = (1, 1, 1, 1)
    col_ao_mix.inputs[2].default_value = (1, 1, 1, 1)
    ao_reroute = mat.nodes.new("NodeReroute")
    ao_reroute.location = (200, 100)
    mat.links.new(ao_reroute.inputs[0], inputs.outputs[1])
    mat.links.new(col_ao_mix.inputs[0], ao_reroute.outputs[0])
    mat.links.new(shader.inputs[0], col_ao_mix.outputs[0])

    if "color" in maps:
        map_color = add_image_node(mat, maps["color"], non_color=False)
        map_color.location = (250, 75)
        mat.links.new(map_color.inputs[0], inputs.outputs[0])
        mat.links.new(col_ao_mix.inputs[1], map_color.outputs[0])

    if "ao" in maps:
        map_ao = add_image_node(mat, maps["ao"])
        map_ao.location = (250, 25)
        mat.links.new(map_ao.inputs[0], inputs.outputs[0])
        mat.links.new(map_ao.inputs[0], inputs.outputs[0])
        mat.links.new(col_ao_mix.inputs[2], map_ao.outputs[0])

    # Roughness
    rough_adj = mat.nodes.new("ShaderNodeMapRange")
    rough_adj.location = (750, -10)
    mat.links.new(rough_adj.inputs[3], inputs.outputs[2])
    mat.links.new(rough_adj.inputs[4], inputs.outputs[3])
    mat.links.new(shader.inputs[9], rough_adj.outputs[0])

    if "rough" in maps:
        map_rough = add_image_node(mat, maps["rough"])
        map_rough.location = (250, -100)
        mat.links.new(map_rough.inputs[0], inputs.outputs[0])
        mat.links.new(rough_adj.inputs[0], map_rough.outputs[0])

    # Bump and normal
    bump = mat.nodes.new("ShaderNodeBump")
    bump.location = (750, -300)
    nrm = mat.nodes.new("ShaderNodeNormalMap")
    nrm.location = (550, -450)
    nrm.hide = True
    mat.links.new(bump.inputs[1], inputs.outputs[4])
    mat.links.new(bump.inputs[3], nrm.outputs[0])
    mat.links.new(shader.inputs[22], bump.outputs[0])

    if "disp" in maps:
        map_disp = add_image_node(mat, maps["disp"])
        map_disp.location = (250, -400)
        mat.links.new(map_disp.inputs[0], inputs.outputs[0])
        mat.links.new(bump.inputs[2], map_disp.outputs[0])

    if "nrm" in maps:
        map_nrm = add_image_node(mat, maps["nrm"])
        map_nrm.location = (250, -450)
        mat.links.new(map_nrm.inputs[0], inputs.outputs[0])
        mat.links.new(nrm.inputs[1], map_nrm.outputs[0])


def load_material(name, maps):
    create_node_group(name, maps)
