import math

def temperature_counterflow(fArea, fU, fHeat_Cap_Flow_c, fHeat_Cap_Flow_h, fEntry_Temp_c, fEntry_Temp_h):
    """
    Returns the outlet temperatures of a counterflow heat exchanger in K.
    
    Parameters:
    fArea : float
        Area of the heat exchanger in m²
    fU : float
        Heat exchange coefficient W/m²K
    fHeat_Cap_Flow_c : float
        Heat capacity flow of cold stream in W/K
    fHeat_Cap_Flow_h : float
        Heat capacity flow of hot stream in W/K
    fEntry_Temp_c : float
        Inlet temperature of cold fluid in K
    fEntry_Temp_h : float
        Inlet temperature of hot fluid in K

    Returns:
    fOutlet_Temp_c : float
        Outlet temperature of the cold fluid in K
    fOutlet_Temp_h : float
        Outlet temperature of the hot fluid in K
    """
    # Number of Transfer Units
    fNTU = (fU * fArea) / min(fHeat_Cap_Flow_c, fHeat_Cap_Flow_h)  # Equation from [1] page 174 equation (8.4)

    # Ratio of heat capacity flows
    fHeat_Cap_Flow_Ratio = min(fHeat_Cap_Flow_c, fHeat_Cap_Flow_h) / max(fHeat_Cap_Flow_c, fHeat_Cap_Flow_h)  # Equation from [1] page 174 equation (8.5)

    # Determine which fluid has the higher heat capacity flow
    if fHeat_Cap_Flow_c < fHeat_Cap_Flow_h:
        # Dimensionless temperature for the cold fluid
        fTheta_c = (1 - math.exp(-fNTU * (1 - fHeat_Cap_Flow_Ratio))) / \
                   (1 - fHeat_Cap_Flow_Ratio * math.exp(-fNTU * (1 - fHeat_Cap_Flow_Ratio)))  # Equation from [1] page 178 equation (8.15)

        # Dimensionless temperature for the hot fluid
        fTheta_h = fHeat_Cap_Flow_Ratio * fTheta_c  # Equation from [1] page 176 equation (8.1)
    else:
        # Dimensionless temperature for the hot fluid
        fTheta_h = (1 - math.exp(-fNTU * (1 - fHeat_Cap_Flow_Ratio))) / \
                   (1 - fHeat_Cap_Flow_Ratio * math.exp(-fNTU * (1 - fHeat_Cap_Flow_Ratio)))  # Equation from [1] page 178 equation (8.16)

        # Dimensionless temperature for the cold fluid
        fTheta_c = fHeat_Cap_Flow_Ratio * fTheta_h  # Equation from [1] page 176 equation (8.1)

    # Outlet temperature of the cold fluid
    fOutlet_Temp_c = fEntry_Temp_c + (fEntry_Temp_h - fEntry_Temp_c) * fTheta_c  # Equation from [1] page 174 equation (8.3)

    # Outlet temperature of the hot fluid
    fOutlet_Temp_h = fEntry_Temp_h - (fEntry_Temp_h - fEntry_Temp_c) * fTheta_h  # Equation from [1] page 174 equation (8.2)

    return fOutlet_Temp_c, fOutlet_Temp_h
