def calculateMolarMass(self, afMasses):
    """
    Calculate total molar mass from partial masses.
    
    This function takes a vector of masses (its elements are the masses
    of each substance in the examined mixture; the order of elements
    must comply with the order of substances in the matter table) and
    calculates the total molar mass of the mixture using the molar mass
    of each substance from the matter table.

    Using the definition of the molar mass M = m / n:
        n[i] = m[i] / M[i]
        n = SUM( n[i] ) = SUM( m[i] / M[i] )
        ===> M = m / SUM( m[i] / M[i] )

    Returns:
        fMolarMass (float): Molar mass of mass/substance mix, in kg/mol.
    """

    fTotalMass = sum(afMasses)

    if fTotalMass == 0:
        return 0

    fMolarMass = fTotalMass / (sum(afMasses / self.afMolarMass))

    return fMolarMass
