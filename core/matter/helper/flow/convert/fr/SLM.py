def SLM(oFlow, bSTP=True):
    """
    Convert fFlowRate on matter.flow to Standard Liters per Minute (SLM).

    Uses the molar mass and other parameters to convert to SLM.
    Assumes standard conditions (STP) by default.

    Parameters:
    - oFlow: Flow object or dictionary containing flow properties.
    - bSTP: If True, use standard temperature and pressure; otherwise, use flow-specific values.

    Returns:
    - fLiterPerMin: Flow rate in Standard Liters per Minute.
    """
    import numpy as np

    # Check input
    if not isinstance(oFlow, dict):
        raise ValueError("First parameter must be a dictionary containing flow data!")
    
    # Required keys
    required_keys = ['fFlowRate', 'fMolarMass']
    if not all(key in oFlow for key in required_keys):
        raise ValueError("Provided dictionary must contain 'fFlowRate' and 'fMolarMass'.")

    if not bSTP:
        if not all(key in oFlow for key in ['fTemperature', 'fPressure']):
            raise ValueError(
                "Non-standard temperature and pressure require 'fTemperature' and 'fPressure' in the dictionary."
            )

    # Get flow rate [kg/s] and convert to [kg/min]
    fFlowRate = oFlow['fFlowRate'] * 60

    # Temperature and pressure
    if bSTP:
        # Standard conditions: 20 deg C, 101325 Pa
        fTemperature = 273.15 + 20  # 20 deg C
        fPressure = 101325  # Pa
    else:
        fTemperature = oFlow['fTemperature']
        fPressure = oFlow['fPressure']

    # Ideal gas law: p * V = n * R * T = m / M * R * T
    # V = m / M * R * T / p
    R = 8.314472  # Universal gas constant, J/(mol K)
    fLiterPerMin = (fFlowRate / oFlow['fMolarMass'] * R * fTemperature / fPressure) * 1000  # Convert m^3 to liters

    return fLiterPerMin
