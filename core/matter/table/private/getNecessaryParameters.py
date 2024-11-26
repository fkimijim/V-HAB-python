import numpy as np

class MatterTable:
    def get_necessary_parameters(self, *args):
        """
        Determines necessary parameters for calculations based on phase, flow, or direct inputs.

        :param args: Either a single object (phase or flow) or a set of parameters (state, mass, etc.)
        :return: Tuple containing fTemperature, arPartialMass, csPhase, aiPhase, aiIndices,
                 afPartialPressures, tbReference, sMatterState, bUseIsobaricData
        """
        tbReference = {"bPhase": False, "bFlow": False, "bNone": False}

        if len(args) == 1:
            # Handle single object case
            obj = args[0]
            if obj.sObjectType == "phase":
                sMatterState = obj.sType
                oPhase = obj
                tbReference["bPhase"] = True

                if obj.fMass == 0:
                    arPartialMass = np.zeros(self.iSubstances)
                else:
                    arPartialMass = self.resolve_compound_mass(obj.arPartialMass, obj.arCompoundMass)
            elif obj.sObjectType == "flow":
                oPhase = obj.oBranch.get_in_exme().oPhase
                sMatterState = oPhase.sType
                tbReference["bFlow"] = True
                arPartialMass = self.resolve_compound_mass(obj.arPartialMass, obj.arCompoundMass)
            else:
                raise ValueError("If only one parameter is provided, it must be a matter.phase or matter.flow.")

            if not np.any(arPartialMass) and np.any(oPhase.afMass):
                arPartialMass = self.resolve_compound_mass(oPhase.afMass / np.sum(oPhase.afMass), oPhase.arCompoundMass)

            fTemperature = obj.fTemperature
            fPressure = obj.fPressure

            if sMatterState == "gas":
                afPartialPressures = self.calculate_partial_pressures(obj)
            elif sMatterState == "liquid":
                afPartialPressures = np.ones(self.iSubstances) * (fPressure or oPhase.fPressure)
            elif sMatterState == "mixture":
                if not oPhase.sPhaseType:
                    afPartialPressures = np.ones(self.iSubstances) * self.Standard["Pressure"]
                    aiPhase = self.determine_phase(arPartialMass, fTemperature, afPartialPressures)
                else:
                    aiPhase = self.determine_phase(arPartialMass, fTemperature, np.ones(self.iSubstances) * fPressure)
                    if oPhase.sPhaseType == "gas":
                        afMassGas = np.zeros(self.iSubstances)
                        afMassGas[aiPhase != 1] = oPhase.afMass[aiPhase != 1]
                        afPartialPressures = self.calculate_partial_pressures("gas", afMassGas, fPressure, fTemperature)
                        afPartialPressures[aiPhase == 1] = fPressure
                        aiPhase = self.determine_phase(arPartialMass, fTemperature, afPartialPressures)
                    else:
                        afPartialPressures = np.ones(self.iSubstances) * fPressure
            else:
                afPartialPressures = np.ones(self.iSubstances) * (fPressure or oPhase.fPressure)

            fTemperature = fTemperature or self.Standard["Temperature"]
            bUseIsobaricData = True

        else:
            # Handle parameter-based input
            sMatterState = args[0]
            xfMass = args[1]
            tbReference["bNone"] = True

            if isinstance(xfMass, dict):
                afMass = np.zeros(self.iSubstances)
                for substance, mass in xfMass.items():
                    afMass[self.tiN2I[substance]] = mass
            else:
                afMass = np.array(xfMass)

            arPartialMass = afMass / np.sum(afMass) if np.sum(afMass) > 0 else np.zeros(self.iSubstances)

            fTemperature = args[2] if len(args) > 2 else self.Standard["Temperature"]

            if len(args) > 3 and isinstance(args[3], (list, np.ndarray)) and len(args[3]) > 1:
                afPartialPressures = np.array(args[3])
            else:
                fPressure = self.Standard["Pressure"]
                if len(args) > 3 and isinstance(args[3], (float, int)):
                    fPressure = args[3]

                if sMatterState == "gas":
                    afPartialPressures = self.calculate_partial_pressures(sMatterState, afMass, fPressure, fTemperature)
                else:
                    afPartialPressures = np.ones(self.iSubstances) * fPressure

            bUseIsobaricData = args[4] if len(args) > 4 and args[4] is False else True

        aiIndices = np.where(arPartialMass > 0.001)[0]
        csPhase = ["solid", "liquid", "gas", "supercritical"]
        tiP2N = {"solid": 1, "liquid": 2, "gas": 3, "supercritical": 4}

        if sMatterState != "mixture":
            aiPhase = np.full(self.iSubstances, tiP2N[sMatterState])
        elif len(args) != 1:
            aiPhase = self.determine_phase(arPartialMass, fTemperature, afPartialPressures)

        return fTemperature, arPartialMass, csPhase, aiPhase, aiIndices, afPartialPressures, tbReference, sMatterState, bUseIsobaricData
