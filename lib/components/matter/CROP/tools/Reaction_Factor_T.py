def Reaction_Factor_T(tPmr, fT):
    """
    Function to add the temperature effect to the enzyme kinetics as described in section 4.2.3.7 in the thesis.

    Parameters:
        tPmr (dict): Enzyme kinetics rate constants structure.
        fT (float): Current temperature in degrees Celsius.

    Returns:
        dict: Updated tPmr with temperature effects applied.
    """
    # Denature temperature
    fTdenature = 40

    # Reference temperature
    fTref = 25

    # Calculate the temperature effect factor k_T
    if fT > fTdenature:
        rTemp_Factor = 2 ** (-(fT - fTref) / 10)
    else:
        rTemp_Factor = 2 ** ((fT - fTref) / 10)

    # Add the temperature effect factors to the rate constants
    for i in ['A', 'B', 'C']:
        for j in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']:
            tPmr[i][j]["fk_f"] *= rTemp_Factor
            tPmr[i][j]["fk_r"] *= rTemp_Factor

    tPmr["D"]["fk_f"] *= rTemp_Factor
    tPmr["D"]["fk_r"] *= rTemp_Factor

    return tPmr
