def extract_xml(filepath, csValidTypes):
    """
    Extract XML data and convert to a structured, human-readable format for V-HAB components.

    Args:
        filepath (str): Path to the XML file.
        csValidTypes (list): List of valid V-HAB object types.

    Returns:
        tuple: tVHAB_Objects (dict), tConvertIDs (dict)
    """
    import tools  # Assuming 'tools' contains helper functions like 'parseXML' and 'normalizePath'

    # Parse the XML file and locate the relevant section
    DrawIoXML = tools.parseXML(filepath)
    try:
        XML_VSYS = DrawIoXML["Children"][2]["Children"][2]["Children"][2]["Children"]
    except IndexError:
        raise ValueError("Could not load the XML file. Did you save it without compression? "
                         '(Use "Export As", choose "XML" and deselect the "Compressed" flag)')

    # Initialize data structures
    tVHAB_Objects = {type_: [] for type_ in csValidTypes}
    tConvertIDs = {"tIDtoLabel": {}, "tIDtoType": {}}

    # Loop through XML elements to extract relevant V-HAB components
    for element in XML_VSYS:
        tStruct = {}
        csToPlot = []
        csToLog = []

        # Extract attributes
        for attribute in element.get("Attributes", []):
            name = attribute["Name"]
            value = attribute["Value"]
            
            if name in ["id", "label"]:
                try:
                    # Clean up unnecessary formatting
                    if "<div>" in value:
                        value = value.replace("<div>", "").replace("</div>", "")
                    value = tools.normalizePath(value.split("<")[0])
                except Exception:
                    value = tools.normalizePath(value)
                tStruct[name] = value
            else:
                if "PLOT_" in value:
                    csToPlot.append(name)
                elif "LOG_" in value:
                    csToLog.append(name)
                tStruct[name] = value

        tStruct["csToPlot"] = csToPlot
        tStruct["csToLog"] = csToLog

        # Extract child attributes
        for child in element.get("Children", []):
            for attribute in child.get("Attributes", []):
                name = attribute["Name"]
                if name == "parent":
                    tStruct["ParentID"] = tools.normalizePath(attribute["Value"])
                elif name == "source":
                    tStruct["SourceID"] = tools.normalizePath(attribute["Value"])
                elif name == "target":
                    tStruct["TargetID"] = tools.normalizePath(attribute["Value"])

        # Check if the struct is a valid V-HAB component
        if "sType" in tStruct:
            if tStruct["sType"] in csValidTypes:
                tVHAB_Objects[tStruct["sType"]].append(tStruct)
                tConvertIDs["tIDtoLabel"][tStruct["id"]] = tStruct["label"]
                tConvertIDs["tIDtoType"][tStruct["id"]] = tStruct["sType"]
            else:
                raise ValueError(f"Unknown type {tStruct['sType']} in the XML definition! "
                                 f"Valid types: {csValidTypes}")

        # Check if the component is an exec
        if element["Name"] == "mxCell":
            sExec = "noExec"
            for attribute in element.get("Attributes", []):
                if attribute["Name"] == "id":
                    CurrentExecID = tools.normalizePath(attribute["Value"])
                elif attribute["Name"] == "parent":
                    CurrentExecParentID = tools.normalizePath(attribute["Value"])
                elif attribute["Name"] == "value":
                    sExec = attribute["Value"]

            if sExec.lower() == "exec":
                csExecCode = []

                # Find other elements of the exec
                for check_element in XML_VSYS:
                    if check_element["Name"] == "mxCell":
                        OtherParentID = None
                        for attribute in check_element.get("Attributes", []):
                            if attribute["Name"] == "parent":
                                OtherParentID = tools.normalizePath(attribute["Value"])
                            elif attribute["Name"] == "value":
                                csExecCode.append(attribute["Value"])

                        if CurrentExecID == OtherParentID:
                            csExecCode.append(attribute["Value"])

                # Add exec to the corresponding system
                for system in tVHAB_Objects["System"]:
                    if CurrentExecParentID == system["id"]:
                        system["exec"] = csExecCode

    return tVHAB_Objects, tConvertIDs
