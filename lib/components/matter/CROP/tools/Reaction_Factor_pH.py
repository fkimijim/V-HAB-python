def Reaction_Factor_pH(tPmr, tpH_Diagram, fpH):
    """
    Function to add the pH effect to the enzyme kinetics as described in section 4.2.3.8 in the thesis.

    Parameters:
        tPmr (dict): Enzyme kinetics rate constants structure.
        tpH_Diagram (dict): pH diagram structure with pH values and effect factors.
        fpH (float): Current pH value.
    Returns:
        dict: Updated tPmr with pH effects applied.
    """
    trpH_Factor = {}

    for j in ['A', 'B', 'C']:
        # Use linear interpolation to calculate the pH effect factors
        if fpH <= tpH_Diagram[j]["fpH"][0] or fpH >= tpH_Diagram[j]["fpH"][10]:
            trpH_Factor[j] = 0
        else:
            for i in range(10):  # Loop through indices 0 to 9
                if tpH_Diagram[j]["fpH"][i] <= fpH < tpH_Diagram[j]["fpH"][i + 1]:
                    trpH_Factor[j] = (
                        (fpH - tpH_Diagram[j]["fpH"][i])
                        * (tpH_Diagram[j]["rFactor"][i + 1] - tpH_Diagram[j]["rFactor"][i])
                        / (tpH_Diagram[j]["fpH"][i + 1] - tpH_Diagram[j]["fpH"][i])
                        + tpH_Diagram[j]["rFactor"][i]
                    )
                    break

        # Add the pH effect factors to the rate constants
        for k in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']:
            tPmr[j][k]["fk_f"] *= trpH_Factor[j]
            tPmr[j][k]["fk_r"] *= trpH_Factor[j]

    return tPmr
