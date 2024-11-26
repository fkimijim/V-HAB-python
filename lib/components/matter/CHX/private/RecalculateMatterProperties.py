import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))
import Bin_diff_coeff
from functions.calculateHeatTransferCoefficient.convectionFlatGap import convectionFlatGap
from functions.calculateHeatTransferCoefficient.calculateNusseltFlatGap import calculateNusseltFlatGap

def RecalculateMatterProperties(oMT, tInput, iFluid, tFluid):
    """
    RecalculateMatterProperties:
    Function used in the CHX to recalculate all required matter properties if necessary.
    """
    # Define some required inputs
    fSurfaceTemperatureInitialization = (tInput['fTemperatureGas'] + tInput['fTemperatureCoolant']) / 2
    afMolarMass = tInput['arPartialMassesGas'] / oMT.afMolarMass
    afPartialPressures = tInput['fPressureGas'] * afMolarMass / sum(afMolarMass)

    arVapor = [0] * oMT.iSubstances
    arVapor[oMT.tiN2I[tInput['Vapor']]] = afPartialPressures[oMT.tiN2I[tInput['Vapor']]]
    afPressureCoolant = oMT.calculatePartialPressures(tInput['oFlowCoolant'])

    if iFluid == 2:
        # Matter Properties of coolant
        try:
            tInput['fDynamicViscosityFilm'] = oMT.calculateDynamicViscosity('liquid', arVapor, fSurfaceTemperatureInitialization)
            tInput['fDensityFilm'] = oMT.calculateDensity('liquid', arVapor, fSurfaceTemperatureInitialization)
            tInput['fSpecificHeatCapacityFilm'] = oMT.calculateSpecificHeatCapacity('liquid', arVapor, fSurfaceTemperatureInitialization)
            tInput['fThermalConductivityFilm'] = oMT.calculateThermalConductivity('liquid', arVapor, fSurfaceTemperatureInitialization)
            tInput['fSpecificHeatCapacityCoolant'] = oMT.calculateSpecificHeatCapacity(
                'liquid', afPressureCoolant, tInput['fTemperatureCoolant'], afPressureCoolant
            )

            if tInput['fDynamicViscosityFilm'] == 0:
                # Default to water properties if no film exists
                tInput['fDynamicViscosityFilm'] = 8.9e-4
                tInput['fDensityFilm'] = 998
                tInput['fSpecificHeatCapacityFilm'] = 4184
                tInput['fThermalConductivityFilm'] = 0.6
                tInput['fSpecificHeatCapacityCoolant'] = 4184

        except Exception:
            # Default to water properties on failure
            tInput['fDynamicViscosityFilm'] = 8.9e-4
            tInput['fDensityFilm'] = 998
            tInput['fSpecificHeatCapacityFilm'] = 4184
            tInput['fThermalConductivityFilm'] = 0.6
            tInput['fSpecificHeatCapacityCoolant'] = 4184

        _, tInput['tDimensionlessQuantitiesCoolant'] = convectionFlatGap(
            tInput['fHeight_2'] * 2, tInput['fBroadness'], tFluid['fFlowSpeed_Fluid'],
            tFluid['fDynamic_Viscosity'], tFluid['fDensity'], tFluid['fThermal_Conductivity'],
            tFluid['fSpecificHeatCapacity'], 1
        )

    else:
        # Matter Properties of gas
        try:
            tInput['fDensityGas'] = oMT.calculateDensity('gas', tInput['arPartialMassesGas'], tInput['fTemperatureGas'], afPartialPressures)
            tInput['fDynamicViscosityGas'] = oMT.calculateDynamicViscosity('gas', tInput['arPartialMassesGas'], tInput['fTemperatureGas'], afPartialPressures)
            tInput['fKinematicViscosityGas'] = tInput['fDynamicViscosityGas'] / tInput['fDensityGas']
            tInput['fSpecificHeatCapacityGas'] = oMT.calculateSpecificHeatCapacity('gas', tInput['arPartialMassesGas'], tInput['fTemperatureGas'], afPartialPressures)
            tInput['fThermalConductivityGas'] = oMT.calculateThermalConductivity('gas', tInput['arPartialMassesGas'], tInput['fTemperatureGas'], afPartialPressures)
            tInput['fMolarFractionGas'] = 1 - tInput['fMolarFractionVapor']

        except Exception:
            # Default to mixture properties on failure
            tInput['fDensityGas'] = oMT.calculateDensity('mixture', tInput['arPartialMassesGas'], tInput['fTemperatureGas'], afPartialPressures)
            tInput['fDynamicViscosityGas'] = oMT.calculateDynamicViscosity('mixture', tInput['arPartialMassesGas'], tInput['fTemperatureGas'], afPartialPressures)
            tInput['fKinematicViscosityGas'] = tInput['fDynamicViscosityGas'] / tInput['fDensityGas']
            tInput['fSpecificHeatCapacityGas'] = oMT.calculateSpecificHeatCapacity('mixture', tInput['arPartialMassesGas'], tInput['fTemperatureGas'], afPartialPressures)
            tInput['fThermalConductivityGas'] = oMT.calculateThermalConductivity('mixture', tInput['arPartialMassesGas'], tInput['fTemperatureGas'], afPartialPressures)
            tInput['fMolarFractionGas'] = 1 - tInput['fMolarFractionVapor']

        DiffCoeff_Gas = Bin_diff_coeff(tInput['Vapor'], tInput['Inertgas'], tInput['fTemperatureGas'], tInput['fPressureGas'])

        _, tInput['tDimensionlessQuantitiesGas'] = calculateNusseltFlatGap(
            tInput['fHeight_1'] * 2, tInput['fLength'], tFluid['fFlowSpeed_Fluid'],
            tFluid['fDynamic_Viscosity'], tFluid['fDensity'], tFluid['fThermal_Conductivity'],
            tFluid['fSpecificHeatCapacity'], 1
        )

        tInput['tDimensionlessQuantitiesGas']['fSc'] = tInput['fKinematicViscosityGas'] / DiffCoeff_Gas

        if tInput['tDimensionlessQuantitiesGas']['fRe'] < 10**4 and tInput['tDimensionlessQuantitiesGas']['fSc'] < 0.6:
            if tInput['tDimensionlessQuantitiesGas']['fSc'] > 0.55:
                tInput['tDimensionlessQuantitiesGas']['fSc'] = 0.6 + 1e-8
            else:
                warn("The Sherwood number in a CHX became too low during transient calculations. Redesign heat exchanger or check other values!")
                tInput['tDimensionlessQuantitiesGas']['fSc'] = 0.6

        tInput['tDimensionlessQuantitiesGas']['fSh'] = calculateNusseltFlatGap(
            tInput['tDimensionlessQuantitiesGas']['fRe'], tInput['tDimensionlessQuantitiesGas']['fSc'], 
            tInput['fHeight_1'] * 2, tInput['fLength'], 1
        )

        tInput['tDimensionlessQuantitiesGas']['beta_Gas_0'] = (
            tInput['tDimensionlessQuantitiesGas']['fSh'] * DiffCoeff_Gas / (tInput['fHeight_1'] * 2)
        )

    return tInput
