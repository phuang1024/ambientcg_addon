"""
Material loading, applying, searching, etc.
"""

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
    tree = bpy.data.node_groups.new(name, "ShaderNodeTree")

    # Inputs and outputs
    tree.inputs.new("NodeSocketVector", "Mapping")
    tree.inputs.new("NodeSocketFloat", "AO Strength")
    tree.inputs.new("NodeSocketFloat", "Min Roughness")
    tree.inputs.new("NodeSocketFloat", "Max Roughness")
    tree.inputs.new("NodeSocketFloat", "Bump Distance")
    tree.outputs.new("NodeSocketShader", "BSDF")

    tree.inputs[1].default_value = 1
    tree.inputs[2].default_value = 0
    tree.inputs[3].default_value = 1
    tree.inputs[4].default_value = 0.04
    for i in range(1, 5):
        tree.inputs[i].min_value = 0
        tree.inputs[i].max_value = 1

    # Input output shader nodes.
    inputs = tree.nodes.new("NodeGroupInput")
    inputs.location = (-50, -100)
    outputs = tree.nodes.new("NodeGroupOutput")
    outputs.location = (1300, 180)
    shader = tree.nodes.new("ShaderNodeBsdfPrincipled")
    shader.location = (950, 200)

    tree.links.new(outputs.inputs[0], shader.outputs[0])

    # Color and AO
    col_ao_mix = tree.nodes.new("ShaderNodeMixRGB")
    col_ao_mix.location = (750, 200)
    col_ao_mix.blend_type = "MULTIPLY"
    col_ao_mix.inputs[1].default_value = (1, 1, 1, 1)
    col_ao_mix.inputs[2].default_value = (1, 1, 1, 1)
    ao_reroute = tree.nodes.new("NodeReroute")
    ao_reroute.location = (200, 100)
    tree.links.new(ao_reroute.inputs[0], inputs.outputs[1])
    tree.links.new(col_ao_mix.inputs[0], ao_reroute.outputs[0])
    tree.links.new(shader.inputs[0], col_ao_mix.outputs[0])

    if "color" in maps:
        map_color = add_image_node(tree, maps["color"], non_color=False)
        map_color.location = (250, 75)
        tree.links.new(map_color.inputs[0], inputs.outputs[0])
        tree.links.new(col_ao_mix.inputs[1], map_color.outputs[0])

    if "ao" in maps:
        map_ao = add_image_node(tree, maps["ao"])
        map_ao.location = (250, 25)
        tree.links.new(map_ao.inputs[0], inputs.outputs[0])
        tree.links.new(map_ao.inputs[0], inputs.outputs[0])
        tree.links.new(col_ao_mix.inputs[2], map_ao.outputs[0])

    # Roughness
    rough_adj = tree.nodes.new("ShaderNodeMapRange")
    rough_adj.location = (750, -10)
    tree.links.new(rough_adj.inputs[3], inputs.outputs[2])
    tree.links.new(rough_adj.inputs[4], inputs.outputs[3])
    tree.links.new(shader.inputs[9], rough_adj.outputs[0])

    if "rough" in maps:
        map_rough = add_image_node(tree, maps["rough"])
        map_rough.location = (250, -100)
        tree.links.new(map_rough.inputs[0], inputs.outputs[0])
        tree.links.new(rough_adj.inputs[0], map_rough.outputs[0])

    # Bump and normal
    bump = tree.nodes.new("ShaderNodeBump")
    bump.location = (750, -300)
    nrm = tree.nodes.new("ShaderNodeNormalMap")
    nrm.location = (550, -450)
    nrm.hide = True
    tree.links.new(bump.inputs[1], inputs.outputs[4])
    tree.links.new(bump.inputs[3], nrm.outputs[0])
    tree.links.new(shader.inputs[22], bump.outputs[0])

    if "disp" in maps:
        map_disp = add_image_node(tree, maps["disp"])
        map_disp.location = (250, -400)
        tree.links.new(map_disp.inputs[0], inputs.outputs[0])
        tree.links.new(bump.inputs[2], map_disp.outputs[0])

    if "nrm" in maps:
        map_nrm = add_image_node(tree, maps["nrm"])
        map_nrm.location = (250, -450)
        tree.links.new(map_nrm.inputs[0], inputs.outputs[0])
        tree.links.new(nrm.inputs[1], map_nrm.outputs[0])


def create_material(name):
    """
    Assumes node group already created.
    """
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()

    output = tree.nodes.new("ShaderNodeOutputMaterial")
    output.location = (300, 0)

    shader = tree.nodes.new("ShaderNodeGroup")
    shader.node_tree = bpy.data.node_groups[name]
    shader.location = (100, 0)

    tree.links.new(output.inputs[0], shader.outputs[0])


def do_action(name, path, action, report):
    """
    Call this from operator to load material.

    :param action: props.action
    :param report: self.report
    """
    maps = get_map_files(os.listdir(path))
    maps = {k: os.path.join(path, f) for k, f in maps.items()}

    action = int(action)

    if action >= 0:
        # Create node group
        if name in bpy.data.node_groups:
            if action == 0:
                report({"WARNING"}, f"Node group {name} already exists, skipping.")
        else:
            create_node_group(name, maps)

    if action >= 1:
        # Create material
        if name in bpy.data.materials:
            if action == 1:
                report({"WARNING"}, f"Material {name} already exists, skipping.")
        else:
            create_material(name)

    if action >= 2:
        # Apply to active obj's slots.
        obj = bpy.context.object
        if obj is None:
            report({"WARNING"}, f"No active object, not applying material.")
        else:
            slots = obj.material_slots
            material = bpy.data.materials[name]
            if action == 2:
                # Apply to active
                if len(slots) == 0:
                    obj.data.materials.append(material)
                else:
                    slots[obj.active_material_index].material = material

            elif action == 3:
                # Apply to new slot
                obj.data.materials.append(material)
