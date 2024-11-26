def convert_branches(tVHAB_Objects, csPhases, csF2F, csSystems, tConvertIDs):
    """
    Convert drawio branches to V-HAB branches.
    This function converts the drawio arrows and their associated components into a V-HAB-conform structure.

    Args:
        tVHAB_Objects (dict): Dictionary containing all V-HAB objects.
        csPhases (list): List of phase types.
        csF2F (list): List of F2F component types.
        csSystems (list): List of subsystem types.
        tConvertIDs (dict): Mapping of IDs to labels.

    Returns:
        dict: Updated tVHAB_Objects with converted branches.
    """
    for system in tVHAB_Objects["System"]:
        system["csBranches"] = []
        system["cVHABBranches"] = []
        system["csSolvers"] = []
        system["csBranchNames"] = []
        system["csInterfaces"] = []
        system["csInterfaceIDs"] = []

    for tBranch in tVHAB_Objects["Branch"]:
        sLeftSideBranch = None
        sRightSideBranch = None
        sLeftSideSystemID = None
        sRightSideSystemID = None
        sLeftSideInterface = None
        sRightSideInterface = None
        csF2FinBranches = []
        sCustomName = tBranch.get("sCustomName", None)

        # Match branches to phases in stores
        for tStore in tVHAB_Objects["Store"]:
            for sPhase in csPhases:
                for tPhase in tStore[sPhase]:
                    if tPhase["id"] == tBranch["SourceID"]:
                        sLeftSideBranch = f"this.toStores.{normalize_path(tStore['label'])}.toPhases.{normalize_path(tPhase['label'])}"
                        sLeftSideSystemID = tStore["ParentID"]
                        sLeftSideInterface = f"'{tConvertIDs['tIDtoLabel'][sLeftSideSystemID]}_{normalize_path(tStore['label'])}_{normalize_path(tPhase['label'])}'"
                        sSolver = tBranch.get("sSolver", None)
                        tLeftBranch = tBranch
                    elif tPhase["id"] == tBranch["TargetID"]:
                        sRightSideBranch = f"this.toStores.{normalize_path(tStore['label'])}.toPhases.{normalize_path(tPhase['label'])}"
                        sRightSideSystemID = tStore["ParentID"]
                        sRightSideInterface = f"'{tConvertIDs['tIDtoLabel'][sRightSideSystemID]}_{normalize_path(tStore['label'])}_{normalize_path(tPhase['label'])}'"

        bLeftSideInterface = False
        bSpecialBranch = False

        if sLeftSideBranch is None:
            # Handle subsystems as sources or targets
            for subsystem_type in csSystems:
                for tSubsystem in tVHAB_Objects[subsystem_type]:
                    for tOutput in tSubsystem["Output"]:
                        if tOutput["id"] == tBranch["SourceID"]:
                            if subsystem_type == "Human":
                                # Handle special Human subsystem cases
                                if tOutput["label"] == "Air":
                                    tSubsystem["toInterfacePhases"]["oCabin"] = sRightSideBranch
                                elif tOutput["label"] == "Urine":
                                    tSubsystem["toInterfacePhases"]["oUrine"] = sRightSideBranch
                                elif tOutput["label"] == "Feces":
                                    tSubsystem["toInterfacePhases"]["oFeces"] = sRightSideBranch
                                bSpecialBranch = True
                            elif subsystem_type == "Plants":
                                # Handle special Plant subsystem cases
                                if tOutput["label"] == "Air":
                                    tSubsystem["toInterfacePhases"]["oCabin"] = sRightSideBranch
                                elif tOutput["label"] == "Nutrient":
                                    tSubsystem["toInterfacePhases"]["oNutrient"] = sRightSideBranch
                                elif tOutput["label"] == "Biomass":
                                    tSubsystem["toInterfacePhases"]["oBiomass"] = sRightSideBranch
                                bSpecialBranch = True
                            else:
                                sLeftSideInterface = f"'{tSubsystem['label']}_{tOutput['label']}_Out'"
                                sLeftSideBranch = sLeftSideInterface
                                sLeftSideSystemID = tSubsystem["ParentID"]
                                bLeftSideInterface = True

                    for tInput in tSubsystem["Input"]:
                        if tBranch["TargetID"] == tInput["id"] and subsystem_type == "Human":
                            if tInput["label"] == "Food":
                                for tFoodStore in tVHAB_Objects["FoodStore"]:
                                    if tFoodStore["id"] == tBranch["SourceID"]:
                                        tSubsystem["toInterfacePhases"]["oFoodStore"] = tFoodStore["label"]
                            bSpecialBranch = True

        if bSpecialBranch:
            continue

        # Define branch within a single system
        if sLeftSideBranch and sRightSideBranch:
            if sLeftSideSystemID == sRightSideSystemID:
                for system in tVHAB_Objects["System"]:
                    if system["id"] == sLeftSideSystemID:
                        sBranch = f"matter.branch(this, {sLeftSideBranch}, {{}}, {sRightSideBranch}, '{sCustomName}');"
                        system["csBranches"].append(sBranch)
                        if bLeftSideInterface:
                            system["csSolvers"].append(None)
                        else:
                            system["csSolvers"].append(sSolver)
                            system["cVHABBranches"].append(tLeftBranch)
                        system["csBranchNames"].append(sCustomName)

            # Define interface branches between systems
            else:
                for system in tVHAB_Objects["System"]:
                    if system["id"] == sLeftSideSystemID:
                        sBranch = f"matter.branch(this, {sLeftSideBranch}, {{}}, {sRightSideInterface}, '{sCustomName}');"
                        system["csBranches"].append(sBranch)
                        if bLeftSideInterface:
                            system["csSolvers"].append(None)
                        else:
                            system["csSolvers"].append(sSolver)
                            system["cVHABBranches"].append(tLeftBranch)
                        system["csBranchNames"].append(sCustomName)
                        system["csInterfaceIDs"].append((sLeftSideSystemID, sRightSideSystemID))
                        system["csInterfaces"].append((sLeftSideInterface, sRightSideInterface))

                    elif system["id"] == sRightSideSystemID:
                        sBranch = f"matter.branch(this, {sLeftSideInterface}, {{}}, {sRightSideBranch}, '{sCustomName}');"
                        system["csBranches"].append(sBranch)
                        system["csSolvers"].append(None)
                        system["csBranchNames"].append(sCustomName)
                        system["csInterfaceIDs"].append((sLeftSideSystemID, sRightSideSystemID))
                        system["csInterfaces"].append((sLeftSideInterface, sRightSideInterface))

    # Assign `toInterfacePhases` to subsystems
    for system in tVHAB_Objects["System"]:
        for human in system.get("Human", []):
            for ref in tVHAB_Objects["Human"]:
                if human["id"] == ref["id"]:
                    human["toInterfacePhases"] = ref["toInterfacePhases"]

        for plant in system.get("Plants", []):
            for ref in tVHAB_Objects["Plants"]:
                if plant["id"] == ref["id"]:
                    plant["toInterfacePhases"] = ref["toInterfacePhases"]

    return tVHAB_Objects
