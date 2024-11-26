def create_f2fs(tCurrentSystem, csF2F, sSystemFile):
    """
    Adds the code for all F2Fs into the system file.

    Args:
        tCurrentSystem (dict): Current system dictionary containing F2F definitions.
        csF2F (list): List of F2F types.
        sSystemFile (file): File object for writing system definitions.

    Returns:
        dict: Updated tCurrentSystem with added component IDs.
    """
    sSystemFile.write("         % Creating the F2F processors\n")

    # Define input values for different F2F types
    csInputValues = {
        "pipe": ["fLength", "fDiameter", "fRoughness"],
        "fan_simple": ["fMaxDeltaP", "bReverse"],
        "fan": ["fSpeedSetpoint", "sDirection"],
        "pump": ["fFlowRateSP"],
        "checkvalve": ["bReversed", "fPressureDropCoefficient"],
        "valve": ["bOpen"]
    }

    # Process each F2F type
    for sF2F in csF2F:
        if sF2F in tCurrentSystem:
            for tF2F in tCurrentSystem[sF2F]:
                F2FName = tools.normalize_path(tF2F["label"])

                # Build input string
                sInput = ""
                for sInputName in csInputValues[sF2F]:
                    if sInputName in tF2F and tF2F[sInputName] is not None:
                        sInput += f", {tF2F[sInputName]}"
                    else:
                        raise ValueError(
                            f"In system {tCurrentSystem['name']} in {sF2F} {F2FName}, "
                            f"the property {sInputName} was not defined in draw.io!"
                        )

                # Write F2F creation code
                sSystemFile.write(
                    f"          components.matter.{sF2F}(this, '{F2FName}'{sInput});\n"
                )

                # Append the component ID to the system
                tCurrentSystem.setdefault("csComponentIDs", []).append(tF2F["id"])

        sSystemFile.write("\n")

    return tCurrentSystem
