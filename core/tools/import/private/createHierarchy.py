def create_hierarchy(tVHAB_Objects, tSystemIDtoLabel):
    """
    Create hierarchy by organizing systems into their correct structure.

    Args:
        tVHAB_Objects (dict): Dictionary containing system objects.
        tSystemIDtoLabel (dict): Mapping of system IDs to their labels.

    Returns:
        tuple: Updated tVHAB_Objects and tSystems dictionaries.
    """
    # Initialize variables
    mbOrderedSystems = [False] * len(tVHAB_Objects["System"])
    tSystems = {}

    # Find the root system (ID 'p_1')
    iRootSystem = None
    for i, system in enumerate(tVHAB_Objects["System"]):
        if system["ParentID"] == "p_1":
            iRootSystem = i
            sRootSystemID = system["id"]
            root_label = tSystemIDtoLabel[sRootSystemID]
            tSystems[root_label] = system
            tVHAB_Objects["System"][i]["sFullPath"] = system["label"]
            mbOrderedSystems[i] = True
            tSystems[root_label]["Children"] = {}
            break

    if iRootSystem is None:
        raise ValueError("Root system with ParentID 'p_1' not found.")

    # Organize systems into a hierarchy
    while not all(mbOrderedSystems):
        for i, system in enumerate(tVHAB_Objects["System"]):
            if not mbOrderedSystems[i]:
                sID = system["id"]
                sSupraSystemID = system["ParentID"]
                sSupraSystemField = tSystemIDtoLabel[sSupraSystemID]

                bAbort = False
                while sSupraSystemID != sRootSystemID:
                    for j, supra_system in enumerate(tVHAB_Objects["System"]):
                        if supra_system["id"] == sSupraSystemID:
                            if not mbOrderedSystems[j]:
                                bAbort = True
                                break
                            else:
                                sSupraSystemField = f"{tSystemIDtoLabel[supra_system['ParentID']]}.Children.{sSupraSystemField}"
                                sSupraSystemID = supra_system["ParentID"]
                                break
                    if bAbort:
                        break

                if not bAbort:
                    # Assign the current system to its parent's Children field
                    sFullPath = f"{sSupraSystemField}.Children.{tSystemIDtoLabel[sID]}"
                    fields = sFullPath.split(".")
                    current_dict = tSystems
                    for field in fields[:-1]:
                        current_dict = current_dict.setdefault(field, {"Children": {}})
                    current_dict[fields[-1]] = system

                    tVHAB_Objects["System"][i]["sFullPath"] = sFullPath
                    mbOrderedSystems[i] = True

    return tVHAB_Objects, tSystems
