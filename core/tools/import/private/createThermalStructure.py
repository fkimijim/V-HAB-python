def create_thermal_structure(tCurrentSystem, csPhases, sSystemFile):
    """
    Create thermal structure for the given system.

    Args:
        tCurrentSystem (dict): Current system data.
        csPhases (list): List of phases.
        sSystemFile (file object): File object to write the system definition.
    """
    sSystemFile.write("\n")
    sSystemFile.write("    def create_thermal_structure(self):\n")
    sSystemFile.write("        super().create_thermal_structure()\n")
    
    # Create heat sources
    for tStore in tCurrentSystem["Stores"]:
        for sPhase in csPhases:
            for tPhase in tStore.get(sPhase, []):
                for iHeatSource, tHeatSource in enumerate(tPhase.get("HeatSource", []), start=1):
                    sSystemFile.write("\n")
                    if not tHeatSource["label"]:
                        tHeatSource["label"] = f"{tPhase['label']}_HeatSource_{iHeatSource}"

                    if tHeatSource["sHeatSourceType"] == "components.thermal.heatsources.ConstantTemperature":
                        sSystemFile.write(f"        oHeatSource = {tHeatSource['sHeatSourceType']}('{tHeatSource['label']}')\n")
                    else:
                        sSystemFile.write(f"        oHeatSource = {tHeatSource['sHeatSourceType']}('{tHeatSource['label']}', {tHeatSource['fHeatFlow']})\n")
                    sSystemFile.write(f"        self.toStores.{tStore['label']}.toPhases.{tPhase['label']}.oCapacity.add_heat_source(oHeatSource)\n")

    sSystemFile.write("\n")

    # Add thermal interface for humans
    for tHuman in tCurrentSystem.get("Human", []):
        sSystemFile.write(f"        oCabinPhase = {tHuman['toInterfacePhases']['oCabin']}\n")
        sSystemFile.write("        for iHuman in range(1, self.iCrewMembers + 1):\n")
        sSystemFile.write("            # Add thermal IF for humans\n")
        sSystemFile.write("            thermal.procs.exme(oCabinPhase.oCapacity, f'SensibleHeatOutput_Human_{iHuman}')\n")
        sSystemFile.write("            thermal.branch(self, f'SensibleHeatOutput_Human_{iHuman}', {}, f'{oCabinPhase.oStore.sName}.SensibleHeatOutput_Human_{iHuman}', f'SensibleHeatOutput_Human_{iHuman}')\n")
        sSystemFile.write("            self.toChildren[f'Human_{iHuman}'].set_thermal_if(f'SensibleHeatOutput_Human_{iHuman}')\n")
        sSystemFile.write("\n")

    sSystemFile.write("\n")

    # Add reference phase for CDRA
    for tCDRA in tCurrentSystem.get("CDRA", []):
        csReference = tCDRA["ReferencePhase"].split(".")
        sSystemFile.write(f"        self.toChildren.{tCDRA['label']}.set_reference_phase(self.toStores.{csReference[0]}.toPhases.{csReference[1]})\n")

    sSystemFile.write("\n")
    sSystemFile.write("    # End of thermal structure creation\n")
