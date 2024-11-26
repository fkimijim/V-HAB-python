def find_long_paths(xInput, csCompletedUUIDs, csActiveUUIDs, bIsObject, iLevel, iMaxLevel, sPath):
    """
    Finds long paths in the simulation object hierarchy.

    This tool identifies where long object hierarchy paths exist in a simulation model,
    helping debug issues related to MATLAB's object hierarchy saving limitations.

    Parameters:
        xInput: The current object or structure to inspect.
        csCompletedUUIDs (list): List of completed UUIDs.
        csActiveUUIDs (list): List of active UUIDs.
        bIsObject (bool): Whether the input is an object.
        iLevel (int): Current level of recursion.
        iMaxLevel (int): Maximum level reached so far.
        sPath (str): Current path in the object hierarchy.

    Returns:
        csCompletedUUIDs, csActiveUUIDs, iMaxLevel
    """

    # Incrementing the level
    iLevel += 1

    # Printing the current level and path for the user
    print(f"Level: {iLevel}")
    print(sPath)

    # Update the maximum level
    iMaxLevel = max(iLevel, iMaxLevel)

    if bIsObject:
        # Check if the current object is already completed or active
        if xInput.sUUID in csCompletedUUIDs or xInput.sUUID in csActiveUUIDs:
            return csCompletedUUIDs, csActiveUUIDs, iMaxLevel

        # Add the object's UUID to the active list
        csActiveUUIDs.append(xInput.sUUID)

        # Inspect properties of the object
        csProperties = dir(xInput)
        for property_name in csProperties:
            sNewPath = f"{sPath}.{property_name}"
            try:
                prop_value = getattr(xInput, property_name)
                csCompletedUUIDs, csActiveUUIDs, iMaxLevel = find_long_paths(
                    prop_value, csCompletedUUIDs, csActiveUUIDs, False, iLevel, iMaxLevel, sNewPath
                )
            except AttributeError as e:
                if e.args[0] in [
                    "phase:mixture:invalidAccessPartialPressures",
                    "phase:mixture:invalidAccessHumidity",
                    "phase:mixture:invalidAccessPartsPerMillion",
                ]:
                    continue
                elif "MATLAB:structRefFromNonStruct" in str(e):
                    # Handle dependent properties
                    if hasattr(xInput, property_name) and hasattr(xInput, "__dict__"):
                        continue
                    else:
                        raise e
                else:
                    raise e

        # Move the object from active to completed
        csCompletedUUIDs.append(xInput.sUUID)
        csActiveUUIDs.remove(xInput.sUUID)

    else:
        # Check the type of input
        sReturn = check_type(xInput)

        if sReturn == "return":
            return csCompletedUUIDs, csActiveUUIDs, iMaxLevel
        elif sReturn == "struct":
            if isinstance(xInput, list):
                for i, item in enumerate(xInput):
                    sNewPath = f"{sPath}({i})"
                    csCompletedUUIDs, csActiveUUIDs, iMaxLevel = find_long_paths(
                        item, csCompletedUUIDs, csActiveUUIDs, False, iLevel, iMaxLevel, sNewPath
                    )
            else:
                for field_name in xInput.keys():
                    sNestedReturn = check_type(xInput[field_name])
                    sNewPath = f"{sPath}.{field_name}"
                    if sNestedReturn in ["struct", "cell"]:
                        csCompletedUUIDs, csActiveUUIDs, iMaxLevel = find_long_paths(
                            xInput[field_name], csCompletedUUIDs, csActiveUUIDs, False, iLevel, iMaxLevel, sNewPath
                        )
                    elif sNestedReturn == "base":
                        if isinstance(xInput[field_name], list):
                            for j, sub_item in enumerate(xInput[field_name]):
                                sBrandNewPath = f"{sNewPath}({j})"
                                csCompletedUUIDs, csActiveUUIDs, iMaxLevel = find_long_paths(
                                    sub_item, csCompletedUUIDs, csActiveUUIDs, True, iLevel, iMaxLevel, sBrandNewPath
                                )
                        else:
                            csCompletedUUIDs, csActiveUUIDs, iMaxLevel = find_long_paths(
                                xInput[field_name], csCompletedUUIDs, csActiveUUIDs, True, iLevel, iMaxLevel, sNewPath
                            )
        elif sReturn == "cell":
            for i, cell_item in enumerate(xInput):
                sNestedReturn = check_type(cell_item)
                sNewPath = f"{sPath}{{{i}}}"
                if sNestedReturn in ["struct", "cell"]:
                    csCompletedUUIDs, csActiveUUIDs, iMaxLevel = find_long_paths(
                        cell_item, csCompletedUUIDs, csActiveUUIDs, False, iLevel, iMaxLevel, sNewPath
                    )
                elif sNestedReturn == "base":
                    if isinstance(cell_item, list):
                        for j, sub_item in enumerate(cell_item):
                            sBrandNewPath = f"{sNewPath}({j})"
                            csCompletedUUIDs, csActiveUUIDs, iMaxLevel = find_long_paths(
                                sub_item, csCompletedUUIDs, csActiveUUIDs, True, iLevel, iMaxLevel, sBrandNewPath
                            )
                    else:
                        csCompletedUUIDs, csActiveUUIDs, iMaxLevel = find_long_paths(
                            cell_item, csCompletedUUIDs, csActiveUUIDs, True, iLevel, iMaxLevel, sNewPath
                        )
        elif sReturn == "base":
            for i, base_item in enumerate(xInput):
                if len(xInput) > 1:
                    sNewPath = f"{sPath}({i})"
                else:
                    sNewPath = sPath
                csCompletedUUIDs, csActiveUUIDs, iMaxLevel = find_long_paths(
                    base_item, csCompletedUUIDs, csActiveUUIDs, True, iLevel, iMaxLevel, sNewPath
                )
        else:
            try:
                sPath = f"{sPath}.{type(xInput).__name__}"
                csCompletedUUIDs, csActiveUUIDs, iMaxLevel = find_long_paths(
                    xInput, csCompletedUUIDs, csActiveUUIDs, True, iLevel, iMaxLevel, sPath
                )
            except Exception:
                raise RuntimeError("An unexpected error occurred.")

    return csCompletedUUIDs, csActiveUUIDs, iMaxLevel


def check_type(xInput):
    """
    Checks the type of the input and returns a string indicating the type.

    Returns:
        str: Type description ('return', 'struct', 'cell', 'base', 'unknown').
    """
    if isinstance(
        xInput, (str, int, float, bool, type(None), list, dict)
    ):
        return "return"
    elif isinstance(xInput, dict):
        return "struct"
    elif isinstance(xInput, list):
        return "cell"
    elif hasattr(xInput, "sUUID"):
        return "base"
    else:
        return "unknown"
