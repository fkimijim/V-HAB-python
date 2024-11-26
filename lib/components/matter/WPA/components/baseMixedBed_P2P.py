import numpy as np
from scipy.integrate import solve_ivp

class BaseMixedBedP2P:
    """
    Mixed Bed = P2P performing ion exchange in the Multifiltration beds.
    """

    def __init__(self, oStore, oDesorptionP2P):
        self.oDesorptionP2P = oDesorptionP2P
        self.bCationResin = oStore.oContainer.bCationResin
        self.rVoidFraction = oStore.oContainer.rVoidFraction
        self.fResinMass = oStore.oContainer.fResinMass / oStore.oContainer.iCells
        self.fCellVolume = oStore.oContainer.fVolume / oStore.oContainer.iCells
        self.fEmptyBedContactTime = oStore.oContainer.fEmptyBedContactTime / oStore.oContainer.iCells

        self.afSeperationFactors = np.zeros(oStore.oMT.iSubstances)
        if self.bCationResin:
            self.afSeperationFactors[oStore.oMT.tiN2I["Hplus"]] = 1
            self.afSeperationFactors[oStore.oMT.tiN2I["Naplus"]] = 1.68
            self.afSeperationFactors[oStore.oMT.tiN2I["Kplus"]] = 2.15
            self.afSeperationFactors[oStore.oMT.tiN2I["Ca2plus"]] = 72.7
            self.afSeperationFactors[oStore.oMT.tiN2I["NH4"]] = 1.9
            self.iPresaturant = oStore.oMT.tiN2I["Hplus"]
        else:
            self.afSeperationFactors[oStore.oMT.tiN2I["OH"]] = 1
            self.afSeperationFactors[oStore.oMT.tiN2I["CMT"]] = 214
            self.afSeperationFactors[oStore.oMT.tiN2I["Clminus"]] = 16.7
            self.afSeperationFactors[oStore.oMT.tiN2I["C4H7O2"]] = 3.21
            self.afSeperationFactors[oStore.oMT.tiN2I["C2H3O2"]] = 1.99
            self.afSeperationFactors[oStore.oMT.tiN2I["HCO3"]] = 4.99
            self.afSeperationFactors[oStore.oMT.tiN2I["SO4"]] = 149
            self.afSeperationFactors[oStore.oMT.tiN2I["C3H5O3"]] = 2.266
            self.iPresaturant = oStore.oMT.tiN2I["OH"]

        self.abIons = self.afSeperationFactors != 0
        self.mfSeperationFactors = np.zeros((oStore.oMT.iSubstances, oStore.oMT.iSubstances))
        self.mfSeperationFactors[np.ix_(self.abIons, self.abIons)] = (
            self.afSeperationFactors[self.abIons][:, None] / self.afSeperationFactors[self.abIons]
        )
        np.fill_diagonal(self.mfSeperationFactors, 0)

        self.afEquivalentInletFlows = np.zeros(sum(self.abIons))
        self.afCurrentLoading = np.zeros(sum(self.abIons))
        self.afPreviousFlowRates = np.zeros(oStore.oMT.iSubstances)

        self.tOdeOptions = {"rtol": 1e-3, "atol": 1e-4}

    def calculateLoadingChangeRate(self, t, afCurrentLoading):
        abZeroLoading = afCurrentLoading == 0
        afCurrentLoading[abZeroLoading] = 1e-12

        afSeperationFactorSumValues = np.sum(
            self.mfSeperationFactors[np.ix_(self.abIons, self.abIons)] * afCurrentLoading, axis=1
        )

        afSeperationFactorSumWithoutSelf = afSeperationFactorSumValues.copy()

        dqdt = (
            self.afEquivalentInletFlows
            - self.fTotalEquivalentFlows
            * (afCurrentLoading / afSeperationFactorSumValues)
            / (
                self.fResinMass
                + self.rVoidFraction
                * self.fCellVolume
                * (self.fTotalEquivalentFlows / self.fVolumetricFlowRate)
                * afSeperationFactorSumWithoutSelf
                / afSeperationFactorSumValues**2
            )
        )

        dqdt[dqdt < 0 & abZeroLoading] = 0
        if self.bCationResin:
            iLocalPresaturant = sum(self.abIons[: self.iPresaturant + 1])
            dqdt[iLocalPresaturant] = 0
            dqdt[iLocalPresaturant] = -np.sum(dqdt)
        else:
            iLocalPresaturant = sum(self.abIons[: self.iPresaturant + 1])
            dqdt[iLocalPresaturant] = 0
            dqdt[iLocalPresaturant] = -np.sum(dqdt)

        return dqdt

    def calculateExchangeRates(self, afPartialInFlows):
        afNewEquivalentInletFlows = (
            afPartialInFlows[self.abIons]
            / self.oMT.afMolarMass[self.abIons]
            * np.abs(self.oMT.aiCharge[self.abIons])
        )
        self.fTotalEquivalentFlows = np.sum(afNewEquivalentInletFlows)

        fDensity = self.oIn.oPhase.fDensity
        self.fVolumetricFlowRate = np.sum(afPartialInFlows) / fDensity

        afNewLoading = (
            self.oOut.oPhase.afMass[self.abIons]
            * np.abs(self.oMT.aiCharge[self.abIons])
            / (self.fResinMass * self.oMT.afMolarMass[self.abIons])
        )

        arChangeInletConcentrations = np.abs(
            (self.afEquivalentInletFlows - afNewEquivalentInletFlows) / afNewEquivalentInletFlows
        )
        arChangeLoading = np.abs((self.afCurrentLoading - afNewLoading) / afNewLoading)

        if np.any(arChangeInletConcentrations > 0.02) or np.any(arChangeLoading > 0.02):
            self.afCurrentLoading = afNewLoading
            self.afEquivalentInletFlows = afNewEquivalentInletFlows

            result = solve_ivp(
                self.calculateLoadingChangeRate,
                [self.oTimer.fTime, self.oTimer.fTime + self.fEmptyBedContactTime],
                self.afCurrentLoading,
                **self.tOdeOptions,
            )

            afSolutionLoading = result.y[:, -1]
            afSeperationFactorSumValues = np.sum(
                self.mfSeperationFactors[np.ix_(self.abIons, self.abIons)] * afSolutionLoading, axis=1
            )

            afOutletConcentrations = self.fTotalEquivalentFlows * (afSolutionLoading / afSeperationFactorSumValues)

            afOutletFlows = (
                afOutletConcentrations
                * self.oMT.afMolarMass[self.abIons]
                / np.abs(self.oMT.aiCharge[self.abIons])
                * self.fVolumetricFlowRate
            )

            afPartialFlowRates = np.zeros_like(self.afPreviousFlowRates)
            afPartialFlowRates[self.abIons] = afPartialInFlows[self.abIons] - afOutletFlows

            self.afPreviousFlowRates = afPartialFlowRates
        else:
            afPartialFlowRates = self.afPreviousFlowRates

        abLimitFlows = afPartialFlowRates > afPartialInFlows
        afPartialFlowRates[abLimitFlows] = afPartialInFlows[abLimitFlows]

        afEquivalentFlows = np.zeros_like(self.afPreviousFlowRates)
        afEquivalentFlows[self.abIons] = (
            np.abs(self.oMT.aiCharge[self.abIons]) / self.oMT.afMolarMass[self.abIons]
        ) * afPartialFlowRates[self.abIons]

        if self.oOut.oPhase.afMass[self.iPresaturant] < 1e-12:
            afPartialFlowRates[afEquivalentFlows > 0] = 0
            afEquivalentFlows[afEquivalentFlows > 0] = 0

        afEquivalentFlows[self.iPresaturant] = 0
        afPartialFlowRates[self.iPresaturant] = -np.sum(afEquivalentFlows) * self.oMT.afMolarMass[self.iPresaturant]

        return afPartialFlowRates
