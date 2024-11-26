def associate_components(tVHAB_Objects, csPhases, csF2F, csSystems):
    """
    Associate store, phases, branches, and other V-HAB components to their corresponding systems.

    Args:
        tVHAB_Objects (dict): Dictionary of V-HAB objects containing systems, stores, phases, etc.
        csPhases (list): List of phase types.
        csF2F (list): List of F2F component types.
        csSystems (list): List of subsystem types.

    Returns:
        dict: Updated tVHAB_Objects with associations.
    """

    # Initialize child systems for each system
    for system in tVHAB_Objects["System"]:
        system["csChildren"] = []

    # Initialize phase parameters for stores
    for store in tVHAB_Objects["Store"]:
        for phase_type in csPhases:
            store[phase_type] = []

    # Associate phases with stores and add manipulators and heat sources
    for phase_type in csPhases:
        for phase in tVHAB_Objects.get(phase_type, []):
            phase["Manipulators"] = []
            for manip in tVHAB_Objects.get("Manipulator", []):
                if phase["id"] == manip["ParentID"]:
                    phase["Manipulators"].append(manip)

            phase["HeatSource"] = []
            for heat_source in tVHAB_Objects.get("HeatSource", []):
                if phase["id"] == heat_source["ParentID"]:
                    phase["HeatSource"].append(heat_source)

            for store in tVHAB_Objects["Store"]:
                if phase["ParentID"] == store["id"]:
                    store[phase_type].append(phase)

    # Add stores to systems
    for system in tVHAB_Objects["System"]:
        system["Stores"] = []

    for store in tVHAB_Objects["Store"]:
        store["P2Ps"] = []
        for p2p in tVHAB_Objects.get("P2P", []):
            if store["id"] == p2p["ParentID"]:
                store["P2Ps"].append(p2p)

        for system in tVHAB_Objects["System"]:
            if store["ParentID"] == system["id"]:
                system["Stores"].append(store)

    # Add food stores to systems
    for system in tVHAB_Objects["System"]:
        system["FoodStores"] = []

    for food_store in tVHAB_Objects.get("FoodStore", []):
        for system in tVHAB_Objects["System"]:
            if food_store["ParentID"] == system["id"]:
                system["FoodStores"].append(food_store)

    # Add branches to systems
    for system in tVHAB_Objects["System"]:
        system["Branches"] = []

    for branch in tVHAB_Objects.get("Branch", []):
        for system in tVHAB_Objects["System"]:
            if branch["ParentID"] == system["id"]:
                system["Branches"].append(branch)

    # Add thermal branches to systems
    for system in tVHAB_Objects["System"]:
        system["ThermalBranches"] = []

    for thermal_branch in tVHAB_Objects.get("ThermalBranch", []):
        for system in tVHAB_Objects["System"]:
            if thermal_branch["ParentID"] == system["id"]:
                system["ThermalBranches"].append(thermal_branch)

    # Associate F2F components with systems
    for system in tVHAB_Objects["System"]:
        for f2f_type in csF2F:
            system[f2f_type] = []

    for f2f_type in csF2F:
        for f2f in tVHAB_Objects.get(f2f_type, []):
            for system in tVHAB_Objects["System"]:
                if f2f["ParentID"] == system["id"]:
                    for existing_f2f in system[f2f_type]:
                        if f2f["label"] == existing_f2f["label"]:
                            label = f2f["label"]
                            if label[-3:].isdigit():
                                current_number = int(label[-3:]) + 1
                                label = f"{label[:-3]}{current_number:03}"
                            else:
                                label = f"{label}_001"
                            f2f["label"] = label
                    system[f2f_type].append(f2f)

    # Connect inputs and outputs to corresponding library subsystems
    for system in tVHAB_Objects["System"]:
        for subsystem_type in csSystems:
            system[subsystem_type] = []

    for subsystem_type in csSystems:
        for subsystem in tVHAB_Objects.get(subsystem_type, []):
            subsystem["Input"] = []
            subsystem["Output"] = []

            for inp in tVHAB_Objects.get("Input", []):
                if subsystem["id"] == inp["ParentID"]:
                    subsystem["Input"].append(inp)

            for out in tVHAB_Objects.get("Output", []):
                if subsystem["id"] == out["ParentID"]:
                    subsystem["Output"].append(out)

    # Link systems to their parent systems and subsystems
    for system in tVHAB_Objects["System"]:
        for supra_system in tVHAB_Objects["System"]:
            if system["ParentID"] == supra_system["id"]:
                supra_system["csChildren"].append(system)

        for subsystem_type in csSystems:
            for subsystem in tVHAB_Objects.get(subsystem_type, []):
                if system["id"] == subsystem["ParentID"]:
                    if subsystem_type not in system:
                        system[subsystem_type] = []
                    system[subsystem_type].append(subsystem)

    return tVHAB_Objects
