import numpy as np

def resolve_compound_mass(self, af_mass, ar_compound_mass):
    """
    Resolves compound masses into their components and provides a resolved afMass vector 
    which only contains base matter.

    Args:
        af_mass (numpy.ndarray): Mass vector with compound masses.
        ar_compound_mass (numpy.ndarray): Array representing the composition of compounds in terms of base substances.

    Returns:
        numpy.ndarray: Resolved mass vector containing only base substances.
    """
    if np.any(af_mass[self.abCompound]):
        af_resolved_mass = af_mass[:, np.newaxis] * ar_compound_mass
        af_resolved_mass = np.sum(af_resolved_mass, axis=0)
        # Add masses of non-compound substances back to the resolved mass
        af_resolved_mass[~self.abCompound] += af_mass[~self.abCompound]
    else:
        af_resolved_mass = af_mass

    return af_resolved_mass
