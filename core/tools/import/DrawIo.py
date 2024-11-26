import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "matter")))
from matter.table.private.importNutrientData import NutrientImporter
from private.extractXML import extract_xml
from private.sanityCheckXML_import import sanity_check_xml_import
from private.associateComponents import associate_components
from private.convertBranches import convert_branches
from private.createFolders import create_folders
from private.createSetupFile import create_setup_file
from private.createSystemFiles import create_system_files

def DrawIo(filepath):
    """
    Main function to parse and generate V-HAB system from DrawIO XML.

    Args:
        filepath (str): Path to the XML file.
    """

    # TO DO: P2Ps, Subsystems (e.g., CHX, CCAA, CDRA, etc.), other F2F types, thermal
    # branches, thermal domain in general
    # To simplify adding custom P2Ps and F2Fs, the program could just create an
    # empty general P2P file fitting the current conditions (e.g., static or flow)
    # Add optional input for branches to specify the custom name.

    # Specify which types of XML objects can be translated into V-HAB
    csValidTypes = [
        "Store", "FoodStore", "Branch", "System", "Subsystem", "Input", "Output",
        "Setup", "P2P", "Manipulator", "HeatSource", "ThermalBranch", "ThermalResistance"
    ]

    # Add implemented phases
    csPhases = [
        "Gas", "Gas_Boundary", "Gas_Flow", "Liquid", "Liquid_Boundary", "Liquid_Flow",
        "Solid", "Solid_Boundary", "Solid_Flow", "Mixture", "Mixture_Boundary", "Mixture_Flow"
    ]

    # Add implemented library F2Fs
    csF2F = ["pipe", "fan_simple", "fan", "pump", "checkvalve", "valve"]

    csSystems = ["Human", "CDRA", "CCAA", "OGA", "SCRA", "Plants", "Subsystem"]

    csValidTypes.extend(csPhases)
    csValidTypes.extend(csF2F)
    csValidTypes.extend(csSystems)

    # Extract data from the XML
    tVHAB_Objects, tConvertIDs = extract_xml(filepath, csValidTypes)

    # Map system IDs to their labels
    tSystemIDtoLabel = {
        system["id"]: system["label"] for system in tVHAB_Objects["System"]
    }

    # Perform sanity check
    sanity_check_xml_import(tVHAB_Objects, tConvertIDs)

    # Associate the V-HAB components to the systems for simplified code definition
    tVHAB_Objects = associate_components(tVHAB_Objects, csPhases, csF2F, csSystems)

    # Transform DrawIO arrows into V-HAB branches
    tVHAB_Objects = convert_branches(tVHAB_Objects, csPhases, csF2F, csSystems, tConvertIDs)

    # Check system naming consistency
    for iSystem, system1 in enumerate(tVHAB_Objects["System"]):
        for jSystem, system2 in enumerate(tVHAB_Objects["System"]):
            if iSystem != jSystem and system1["label"] == system2["label"]:
                raise ValueError(
                    f"The system name {system2['label']} is used twice in this DrawIO V-HAB system. "
                    f"Please provide a different system name for one of the systems!"
                )

    # Create folders if they do not yet exist
    sSystemLabel, sPath = create_folders(filepath)

    # Find the root system (ParentID = 'p_1')
    for system in tVHAB_Objects["System"]:
        if system["ParentID"] == "p_1":
            sRootSystemLabel = system["label"]
            break

    sRootName = NutrientImporter.normalize_path(sRootSystemLabel)

    oMT = matter_table()

    # Create V-HAB code
    create_setup_file(tVHAB_Objects, sPath, sSystemLabel, sRootName, csPhases, csF2F, oMT, tSystemIDtoLabel)

    # Create system files
    sPath = os.path.join(sPath, "+systems")
    create_system_files(tVHAB_Objects, csPhases, csF2F, csSystems, sPath, sSystemLabel, tConvertIDs)

    print("Import Successful")
