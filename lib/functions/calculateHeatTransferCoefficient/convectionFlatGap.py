import numpy as np

def convectionFlatGap(fD_Hydraulic, fLength, fFlowSpeed, fDyn_Visc, fDensity, fThermal_Conductivity, fC_p, fConfig):
    """
    Returns the convection coefficient alpha for a flow in a flat gap (two plates with distance h).
    
    Parameters:
        fD_Hydraulic: float
            Hydraulic diameter (2 times the distance between the plates).
        fLength: float
            Length of the gap over which heat exchange takes place.
        fFlowSpeed: float
            Flow speed of the fluid in m/s.
        fDyn_Visc: list
            Dynamic viscosity of the fluid in kg/(m s).
        fDensity: list
            Density of the fluid in kg/m³.
        fThermal_Conductivity: list
            Thermal conductivity of the fluid in W/(m K).
        fC_p: list
            Heat capacity of the fluid in J/K.
        fConfig: int
            Configuration parameter:
            - 0: Disturbed flow.
            - 1: Non-disturbed flow.
    
    Returns:
        tuple:
            - fConvection_alpha: float
                Convection coefficient in W/m²K.
            - tDimensionlessQuantities: dict
                Dictionary containing dimensionless quantities (fNu, fRe, fPr).
    """
    
    # Definition of the kinematic viscosity
    fKin_Visc = fDyn_Visc[0] / fDensity[0]
    
    fFlowSpeed = abs(fFlowSpeed)
    
    # Definition of the Reynolds number
    fRe = (fFlowSpeed * fD_Hydraulic) / fKin_Visc
    
    # Definition of the Prandtl number
    fPr = (fDyn_Visc[0] * fC_p[0]) / fThermal_Conductivity[0]
    
    # Calculate the Nusselt number
    fNu = calculateNusseltFlatGap(fRe, fPr, fD_Hydraulic, fLength, fConfig)
    
    # Calculate the convection coefficient
    fConvection_alpha = (fNu * fThermal_Conductivity[0]) / fD_Hydraulic
    
    # Store dimensionless quantities in a dictionary
    tDimensionlessQuantities = {
        'fNu': fNu,
        'fRe': fRe,
        'fPr': fPr
    }
    
    return fConvection_alpha, tDimensionlessQuantities


def calculateNusseltFlatGap(fRe, fPr, fD_Hydraulic, fLength, fConfig):
    """
    Calculates the Nusselt number for a flat gap based on the Reynolds number, Prandtl number,
    hydraulic diameter, length, and configuration.
    
    Parameters:
        fRe: float
            Reynolds number.
        fPr: float
            Prandtl number.
        fD_Hydraulic: float
            Hydraulic diameter.
        fLength: float
            Length of the gap.
        fConfig: int
            Configuration parameter:
            - 0: Disturbed flow.
            - 1: Non-disturbed flow.
    
    Returns:
        float:
            Nusselt number.
    """
    # Add your Nusselt number calculation logic here based on the given configuration.
    # Placeholder for now:
    fNu = 5.0  # Example constant value for testing.
    
    return fNu
