import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "table")))
from private.importNutrientData import NutrientImporter

def create_stores(tCurrentSystem, csPhases, sSystemFile, tConvertIDs):
    """
    Create Stores and Phases

    Args:
        tCurrentSystem (dict): Current system data.
        csPhases (list): List of phase types.
        sSystemFile (file object): Output file for the system definition.
        tConvertIDs (dict): Conversion IDs for mapping.
    """
    sSystemFile.write("        # Creating the Stores and Phases\n")
    tCurrentSystem["csComponentIDs"] = []

    for tStore in tCurrentSystem["Stores"]:
        fields = tStore["label"].split("<")
        label = fields[0]
        sStoreName = NutrientImporter.normalize_path(label)

        if "fVolume" in tStore and tStore["fVolume"]:
            fVolume = tStore["fVolume"]
        else:
            raise ValueError(f"In system {tCurrentSystem['label']} in store {sStoreName} the property fVolume was not defined!")

        sSystemFile.write(f"        matter.store(self, '{sStoreName}', {fVolume})\n")

        for sPhase in csPhases:
            if sPhase not in tStore:
                continue

            for tPhase in tStore[sPhase]:
                sPhaseName = NutrientImporter.normalize_path(tPhase["label"])
                sSystemName = tCurrentSystem["label"]

                if "fTemperature" in tPhase:
                    fTemperature = tPhase["fTemperature"]
                else:
                    raise ValueError(f"In system {sSystemName} in store {sStoreName} in phase {sPhaseName} the property fTemperature was not defined!")

                if "Gas" in sPhase:
                    # Gas Phase
                    if "fVolume" in tPhase and tPhase["fVolume"]:
                        fPhaseVolume = tPhase["fVolume"]
                    else:
                        raise ValueError(f"In system {sSystemName} in store {sStoreName} in phase {sPhaseName} the property fVolume was not defined!")

                    if "rRelHumidity" in tPhase and tPhase["rRelHumidity"]:
                        rRelativeHumidity = tPhase["rRelHumidity"]
                    else:
                        raise ValueError(f"In system {sSystemName} in store {sStoreName} in phase {sPhaseName} the property rRelHumidity was not defined!")

                    # Partial pressure structure
                    sPressureStruct = {}
                    for attr, value in tPhase.items():
                        if attr.startswith("fPressure"):
                            substance = attr[10:]
                            sPressureStruct[substance] = value

                    if "Boundary" in sPhase:
                        sSystemFile.write(f"        self.toStores['{sStoreName}'].create_phase('gas', 'boundary', '{sPhaseName}', {fPhaseVolume}, {sPressureStruct}, {fTemperature}, {rRelativeHumidity})\n")
                    elif "Flow" in sPhase:
                        sSystemFile.write(f"        self.toStores['{sStoreName}'].create_phase('gas', 'flow', '{sPhaseName}', {fPhaseVolume}, {sPressureStruct}, {fTemperature}, {rRelativeHumidity})\n")
                    else:
                        sSystemFile.write(f"        self.toStores['{sStoreName}'].create_phase('gas', '{sPhaseName}', {fPhaseVolume}, {sPressureStruct}, {fTemperature}, {rRelativeHumidity})\n")

                elif "Solid" in sPhase:
                    # Solid Phase
                    sMassStruct = {}
                    for attr, value in tPhase.items():
                        if attr.startswith("fMass"):
                            substance = attr[6:]
                            sMassStruct[substance] = value

                    if "Boundary" in sPhase:
                        sSystemFile.write(f"        matter.phases.boundary.solid(self.toStores['{sStoreName}'], '{sPhaseName}', {sMassStruct}, {fTemperature})\n")
                    elif "Flow" in sPhase:
                        sSystemFile.write(f"        matter.phases.flow.solid(self.toStores['{sStoreName}'], '{sPhaseName}', {sMassStruct}, {fTemperature})\n")
                    else:
                        sSystemFile.write(f"        matter.phases.solid(self.toStores['{sStoreName}'], '{sPhaseName}', {sMassStruct}, {fTemperature})\n")

                elif "Liquid" in sPhase:
                    # Liquid Phase
                    if "fPressure" in tPhase and tPhase["fPressure"]:
                        fPressure = tPhase["fPressure"]
                    else:
                        raise ValueError(f"In system {sSystemName} in store {sStoreName} in phase {sPhaseName} the property fPressure was not defined!")

                    sMassStruct = {}
                    for attr, value in tPhase.items():
                        if attr.startswith("fMass"):
                            substance = attr[6:]
                            sMassStruct[substance] = value

                    if "Boundary" in sPhase:
                        sSystemFile.write(f"        matter.phases.boundary.liquid(self.toStores['{sStoreName}'], '{sPhaseName}', {sMassStruct}, {fTemperature}, {fPressure})\n")
                    elif "Flow" in sPhase:
                        sSystemFile.write(f"        matter.phases.flow.liquid(self.toStores['{sStoreName}'], '{sPhaseName}', {sMassStruct}, {fTemperature}, {fPressure})\n")
                    else:
                        sSystemFile.write(f"        matter.phases.liquid(self.toStores['{sStoreName}'], '{sPhaseName}', {sMassStruct}, {fTemperature}, {fPressure})\n")

                elif "Mixture" in sPhase:
                    # Mixture Phase
                    if "sPhaseType" in tPhase and tPhase["sPhaseType"]:
                        sPhaseType = tPhase["sPhaseType"]
                    else:
                        raise ValueError(f"In system {sSystemName} in store {sStoreName} in phase {sPhaseName} the property sPhaseType was not defined!")

                    if "fPressure" in tPhase and tPhase["fPressure"]:
                        fPressure = tPhase["fPressure"]
                    else:
                        raise ValueError(f"In system {sSystemName} in store {sStoreName} in phase {sPhaseName} the property fPressure was not defined!")

                    sMassStruct = {}
                    for attr, value in tPhase.items():
                        if attr.startswith("fMass"):
                            substance = attr[6:]
                            sMassStruct[substance] = value

                    if "Boundary" in sPhase:
                        sSystemFile.write(f"        matter.phases.boundary.mixture(self.toStores['{sStoreName}'], '{sPhaseName}', '{sPhaseType}', {sMassStruct}, {fTemperature}, {fPressure})\n")
                    elif "Flow" in sPhase:
                        sSystemFile.write(f"        matter.phases.flow.mixture(self.toStores['{sStoreName}'], '{sPhaseName}', '{sPhaseType}', {sMassStruct}, {fTemperature}, {fPressure})\n")
                    else:
                        sSystemFile.write(f"        matter.phases.mixture(self.toStores['{sStoreName}'], '{sPhaseName}', '{sPhaseType}', {sMassStruct}, {fTemperature}, {fPressure})\n")

                tCurrentSystem["csComponentIDs"].append(tPhase["id"])

    # Add Food stores
    for tFoodStore in tCurrentSystem["FoodStores"]:
        sMassStruct = {}
        for attr, value in tFoodStore.items():
            if attr.startswith("fMass"):
                substance = attr[6:]
                sMassStruct[substance] = value

        sSystemFile.write(f"        components.matter.FoodStore(self, '{tFoodStore['label']}', {tFoodStore['fVolume']}, {sMassStruct})\n")
