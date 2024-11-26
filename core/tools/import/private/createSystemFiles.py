import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "table")))
from private.importNutrientData import NutrientImporter
import create_stores, create_f2fs, create_branches, create_thermal_structure, create_solver_structure

def create_system_files(tVHAB_Objects, csPhases, csF2F, csSystems, sPath, sSystemLabel, tConvertIDs):
    """
    This function loops through all systems and defines the necessary V-HAB code for them.

    Args:
        tVHAB_Objects (dict): VHAB object structure.
        csPhases (list): List of phases.
        csF2F (list): List of face-to-face connections.
        csSystems (list): List of systems.
        sPath (str): Path to save system files.
        sSystemLabel (str): System label.
        tConvertIDs (dict): Conversion IDs.
    """
    for iSystem, tCurrentSystem in enumerate(tVHAB_Objects["System"]):
        sSystemName = NutrientImporter.normalize_path(tCurrentSystem["label"])
        sSystemFile = open(f"{sPath}/{sSystemName}.py", "w")

        sSystemFile.write(f"\nclass {sSystemName}(vsys):\n")
        sSystemFile.write("\n    def __init__(self, oParent, sName):\n")

        if "fTimeStep" in tCurrentSystem and tCurrentSystem["fTimeStep"]:
            sSystemFile.write(f"        super().__init__(oParent, sName, {tCurrentSystem['fTimeStep']})\n")
        else:
            sSystemFile.write("        super().__init__(oParent, sName)\n")

        # Add subsystems
        for sChild in tCurrentSystem.get("csChildren", []):
            sChildName = NutrientImporter.normalize_path(sChild["label"])
            sSystemFile.write(f"        DrawIoImport.{sSystemLabel}.systems.{sChildName}(self, '{sChildName}')\n")

        # Add humans
        for tHuman in tCurrentSystem.get("Human", []):
            sSystemFile.write(f"\n        # Human: {tHuman['label']}\n")
            sSystemFile.write("        for iCrewMember in range(1, {}):\n".format(tHuman["iNumberOfCrew"]))
            sSystemFile.write("            components.matter.DetailedHuman.Human(self, f'Human_{iCrewMember}', txCrewPlaner, 60)\n")

        # Plants
        if tCurrentSystem.get("Plants"):
            tPlants = tCurrentSystem["Plants"][0]
            sSystemFile.write("\n        # Plants\n")
            if tPlants["bMultiplyPlantAreaWithNumberOfCrew"] in ["true", "1"]:
                sSystemFile.write("        self.mfPlantArea *= self.iCrewMembers\n")
            sSystemFile.write("        tInput = {}\n")

            sSystemFile.write("        for iPlant, plant in enumerate(self.csPlants):\n")
            sSystemFile.write("            # Plant logic\n")
            # More plant-related initialization...

        # Components (CCAA, OGA, CDRA, SCRA, Subsystems)
        for component_type in ["CCAA", "OGA", "CDRA", "SCRA", "Subsystem"]:
            for tComponent in tCurrentSystem.get(component_type, []):
                if component_type == "CCAA":
                    sSystemFile.write(f"        components.matter.CCAA.CCAA(self, '{tComponent['label']}', {tComponent['fTimeStep']}, {tComponent['fCoolantTemperature']})\n")
                elif component_type == "OGA":
                    sSystemFile.write(f"        components.matter.OGA.OGA(self, '{tComponent['label']}', {tComponent['fTimeStep']}, {tComponent['fOutletTemperature']})\n")
                elif component_type == "CDRA":
                    sSystemFile.write(f"        components.matter.CDRA.CDRA(self, '{tComponent['label']}', [])\n")
                elif component_type == "SCRA":
                    sSystemFile.write(f"        components.matter.SCRA.SCRA(self, '{tComponent['label']}', {tComponent['fTimeStep']}, {tComponent['fCoolantTemperature']})\n")
                elif component_type == "Subsystem":
                    sInput = "tInput = {}\n"
                    for key, value in tComponent.items():
                        if key not in {"id", "label", "sSubsystemPath", "sType", "csToPlot", "csToLog", "ParentID", "fTimeStep", "Input", "Output"}:
                            if isinstance(value, str) and not value.isnumeric():
                                sInput += f"tInput['{key}'] = '{value}'\n"
                            else:
                                sInput += f"tInput['{key}'] = {value}\n"
                    sSystemFile.write(sInput)
                    sSystemFile.write(f"        {tComponent['sSubsystemPath']}(self, '{tComponent['label']}', {tComponent['fTimeStep']}, tInput)\n")

        # Create Matter Structure
        sSystemFile.write("\n    def create_matter_structure(self):\n")
        sSystemFile.write("        super().create_matter_structure()\n")
        create_stores(tCurrentSystem, csPhases, sSystemFile, tConvertIDs)
        create_f2fs(tCurrentSystem, csF2F, sSystemFile)
        create_branches(tCurrentSystem, tVHAB_Objects, csSystems, sSystemFile)
        create_thermal_structure(tCurrentSystem, csPhases, sSystemFile)
        create_solver_structure(tCurrentSystem, csPhases, sSystemFile)

        # Execution method
        sSystemFile.write("\n    def exec(self):\n")
        sSystemFile.write("        super().exec()\n")
        for exec_code in tCurrentSystem.get("exec", []):
            sSystemFile.write(f"        {exec_code}\n")

        sSystemFile.write("\n")
        sSystemFile.close()
