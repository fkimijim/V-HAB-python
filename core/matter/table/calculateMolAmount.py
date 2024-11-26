import numpy as np

def calculateMolAmount(self, *args):
    """
    Calculates the amount of matter in moles.

    This function calculates the amount of matter in a phase, flow, or a body of matter. 
    Input arguments must be either a `matter.phase` object, a `matter.flow` object, 
    or matter data formatted as described below. If the input argument is a flow, 
    the output will be a flow rate in [mol/s].

    Returns:
        fMolAmount: A float depicting the amount of matter in [mol] 
                    or the matter flow in [mol/s] if the input argument is a `matter.flow` object.
    """

    if args[0].sObjectType == 'phase':
        # Get data from object: `afMasses` array from `matter.phase` object
        afMasses = args[0].afMass

    elif args[0].sObjectType == 'flow':
        # Get data from object: `afMasses` array from `matter.flow` object
        # Return value will be in [mol/s]
        afMasses = args[0].arPartialMass * args[0].fFlowRate

    elif isinstance(args[0], (list, np.ndarray)):
        # Ensure the input has the expected size
        if len(args[0]) != len(self.afMolarMass):
            raise ValueError(
                "Input must be a row vector with the number of elements equal to the number of recognized substances."
            )
        # The given parameter is the masses array
        afMasses = args[0]

    else:
        raise TypeError(
            "Parameter must be of type `double`, `matter.phase`, or `matter.flow`."
        )

    # Calculate the (mole) amount of each substance and sum to get the total amount
    fMolAmount = sum(afMasses / self.afMolarMass)

    return fMolAmount
