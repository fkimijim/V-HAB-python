import math

def Bin_diff_coeff(Vapor, Inertgas, temp_Gas, pressure_Gas):
    """
    Calculates the Diffusion Coefficient for a binary gas mixture.
    Based on VDI-Waermeatlas, p. 170f, D1, 10.1, (115).
    
    Parameters:
        Vapor (str): The vapor type ('H2O' or 'Isopropanol').
        Inertgas (str): The inert gas type ('Air' or 'N2').
        temp_Gas (float): Gas temperature [K].
        pressure_Gas (float): Gas pressure [Pa].
    
    Returns:
        float: Diffusion coefficient in m^2/s.
    """
    # Conversion: Pa to Bar
    pressure_Gas_bar = pressure_Gas / 1e5

    # Properties of the vapor
    if Vapor == 'H2O':
        molMass_V = 18.01528  # [g/mol]
        diffVolume_V = 13.1   # [-]
    elif Vapor == 'Isopropanol':
        molMass_V = 60.1  # [g/mol]
        diffVolume_V = 3 * 15.9 + 8 * 2.31 + 6.11  # [-]
    else:
        print("fx: Diff_Coeff: Use Air as Gas_1.")
        return None

    # Properties of the inert gas
    if Inertgas == 'Air':
        molMass_I = 28.949  # [g/mol]
        diffVolume_I = 19.7  # [-]
    elif Inertgas == 'N2':
        molMass_I = 28  # [g/mol]
        diffVolume_I = 18.5  # [-]
    else:
        print("fx: Diff_Coeff: Use H2O as Gas_2.")
        return None

    # Diffusion coefficient calculation in cm^2/s
    D_12_cm2_s = (0.00143 * temp_Gas**1.75 * math.sqrt(1 / molMass_V + 1 / molMass_I)) / \
                 (pressure_Gas_bar * math.sqrt(2) * (diffVolume_V**(1/3) + diffVolume_I**(1/3))**2)

    # Conversion: cm^2/s to m^2/s
    D_12 = D_12_cm2_s / 10000

    return D_12
