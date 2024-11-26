import math

def conductionResistance(fThermal_Cond_solid, fConfig, fRadius_in, fRadius_out, fLength):
    """
    Calculates the thermal resistivity resulting from conduction in the heat exchanger material.

    Parameters:
    fThermal_Cond_solid: Thermal conductivity of the pipe material in W/(m K)
    fConfig: Configuration of the thermal resistor:
             0: round pipe
             1: quadratic pipe
             2: plate
    fRadius_in: Inner radius (for quadratic pipes: inner edge length) in m
    fRadius_out: Outer radius (for quadratic pipes: outer edge length) in m
    fLength: Length of the pipe in m (or for plates, other parameters as described below)
    
    Returns:
    fResist_Cond: Thermal resistivity in K/W
    """

    if fConfig == 0:
        # Thermal resistivity of a pipe
        fResist_Cond = 1 / (2 * math.pi * fLength * fThermal_Cond_solid) * math.log(fRadius_out / fRadius_in)
    
    elif fConfig == 1:
        # Form factor for a quadratic pipe
        if fRadius_out / fRadius_in > 1.4:
            fForm_Factor = (2 * math.pi) / (0.93 * math.log(fRadius_out / fRadius_in) - 0.05202)
        else:
            fForm_Factor = (2 * math.pi) / (0.785 * math.log(fRadius_out / fRadius_in))
        
        fResist_Cond = 1 / (fThermal_Cond_solid * fForm_Factor * fLength)
    
    elif fConfig == 2:
        # Thermal resistivity of a plate
        # For a plate, fRadius_in = fArea and fRadius_out = fThickness
        fResist_Cond = fRadius_out / (fThermal_Cond_solid * fRadius_in)
    
    else:
        raise ValueError("Invalid input for fConfig in fResist_Cond")
    
    return fResist_Cond
