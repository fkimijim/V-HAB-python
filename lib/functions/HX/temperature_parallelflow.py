import math

def temperature_parallelflow(fArea, fU, fHeat_Cap_Flow_c, fHeat_Cap_Flow_h, fEntry_Temp_c, fEntry_Temp_h):
    """
    Returns the outlet temperatures of a parallel flow heat exchanger in K.

    Parameters:
    fArea: float
        Area of the heat exchanger in m^2.
    fU: float
        Heat exchange coefficient in W/m^2K.
    fHeat_Cap_Flow_c: float
        Heat capacity flow of cold stream in W/K.
    fHeat_Cap_Flow_h: float
        Heat capacity flow of hot stream in W/K.
    fEntry_Temp_c: float
        Inlet temperature of cold fluid in K.
    fEntry_Temp_h: float
        Inlet temperature of hot fluid in K.

    Returns:
    tuple
        fOutlet_Temp_c, fOutlet_Temp_h: Outlet temperatures in K.
    """
    # Number of Transfer Units
    fNTU = (fU * fArea) / min(fHeat_Cap_Flow_c, fHeat_Cap_Flow_h)
    
    # Ratio of heat capacity flows
    fHeat_Cap_Flow_Ratio = min(fHeat_Cap_Flow_c, fHeat_Cap_Flow_h) / max(fHeat_Cap_Flow_c, fHeat_Cap_Flow_h)

    # Check which fluid has the higher heat capacity flow
    if fHeat_Cap_Flow_c < fHeat_Cap_Flow_h:
        # Dimensionless temperature for the cold fluid
        fTheta_c = (1 - math.exp(-fNTU * (1 + fHeat_Cap_Flow_Ratio))) / (1 + fHeat_Cap_Flow_Ratio)
        
        # Dimensionless temperature for the hot fluid
        fTheta_h = fHeat_Cap_Flow_Ratio * fTheta_c
    else:
        # Dimensionless temperature for the hot fluid
        fTheta_h = (1 - math.exp(-fNTU * (1 + fHeat_Cap_Flow_Ratio))) / (1 + fHeat_Cap_Flow_Ratio)
        
        # Dimensionless temperature for the cold fluid
        fTheta_c = fHeat_Cap_Flow_Ratio * fTheta_h

    # Outlet temperature of the cold fluid
    fOutlet_Temp_c = fEntry_Temp_c + (fEntry_Temp_h - fEntry_Temp_c) * fTheta_c

    # Outlet temperature of the hot fluid
    fOutlet_Temp_h = fEntry_Temp_h - (fEntry_Temp_h - fEntry_Temp_c) * fTheta_h

    return fOutlet_Temp_c, fOutlet_Temp_h
