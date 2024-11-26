def sanity_check_xml_import(tVHAB_Objects, tConvertIDs):
    """
    Perform a sanity check on the imported XML data.

    Args:
        tVHAB_Objects (dict): Parsed V-HAB objects from the XML.
        tConvertIDs (dict): Conversion mapping for IDs to labels and types.

    Raises:
        ValueError: If there are errors in the XML structure.
    """
    sError = ""

    for iBranch in range(len(tVHAB_Objects["Branch"])):
        tBranch = tVHAB_Objects["Branch"][iBranch]

        if "SourceID" not in tBranch:
            if "sCustomName" in tBranch and tBranch["sCustomName"]:
                try:
                    sError += (
                        f"In system {tConvertIDs['tIDtoLabel'][tBranch['ParentID']]}, "
                        f"the branch with the name {tBranch['sCustomName']} has no source. "
                        f"It targets a {tConvertIDs['tIDtoType'][tBranch['TargetID']]} called "
                        f"{tConvertIDs['tIDtoLabel'][tBranch['TargetID']]}\n"
                    )
                except KeyError:
                    sError += (
                        f"In system {tConvertIDs['tIDtoLabel'][tBranch['ParentID']]}, "
                        f"the branch with the name {tBranch['sCustomName']} has no connected interface at all. "
                        f"Make sure that the arrows in draw IO actually connect with the components!\n"
                    )
            else:
                try:
                    sError += (
                        f"In system {tConvertIDs['tIDtoLabel'][tBranch['ParentID']]}, "
                        f"the branch with the id {tBranch['id']} has no source. "
                        f"It targets a {tConvertIDs['tIDtoType'][tBranch['TargetID']]} called "
                        f"{tConvertIDs['tIDtoLabel'][tBranch['TargetID']]}\n"
                    )
                except KeyError:
                    sError += (
                        f"In system {tConvertIDs['tIDtoLabel'][tBranch['ParentID']]}, "
                        f"the branch with the id {tBranch['id']} has no connected interface at all. "
                        f"Make sure that the arrows in draw IO actually connect with the components!\n"
                    )
        elif "TargetID" not in tBranch:
            if "sCustomName" in tBranch and tBranch["sCustomName"]:
                try:
                    sError += (
                        f"In system {tConvertIDs['tIDtoLabel'][tBranch['ParentID']]}, "
                        f"the branch with the name {tBranch['sCustomName']} has no target. "
                        f"It originates from a {tConvertIDs['tIDtoType'][tBranch['SourceID']]} called "
                        f"{tConvertIDs['tIDtoLabel'][tBranch['SourceID']]}\n"
                    )
                except KeyError:
                    sError += (
                        f"In system {tConvertIDs['tIDtoLabel'][tBranch['ParentID']]}, "
                        f"the branch with the name {tBranch['sCustomName']} has no connected interface at all. "
                        f"Make sure that the arrows in draw IO actually connect with the components!\n"
                    )
            else:
                try:
                    sError += (
                        f"In system {tConvertIDs['tIDtoLabel'][tBranch['ParentID']]}, "
                        f"the branch with the id {tBranch['id']} has no target. "
                        f"It originates from a {tConvertIDs['tIDtoType'][tBranch['SourceID']]} called "
                        f"{tConvertIDs['tIDtoLabel'][tBranch['SourceID']]}\n"
                    )
                except KeyError:
                    sError += (
                        f"In system {tConvertIDs['tIDtoLabel'][tBranch['ParentID']]}, "
                        f"the branch with the id {tBranch['id']} has no connected interface at all. "
                        f"Make sure that the arrows in draw IO actually connect with the components!\n"
                    )

    # Add checks for subsystem inputs/outputs if necessary
    # TODO: Check if the subsystems still have the correct number of Inputs/Outputs.

    if sError:
        raise ValueError(sError)
