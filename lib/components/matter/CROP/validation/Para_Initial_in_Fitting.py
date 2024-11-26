import numpy as np

def Para_Initial_in_Fitting():
    """
    This function is used to set the initial parameter set in each data series for data fitting.

    Returns:
    --------
    afPmr_Estimate_Initial : numpy.ndarray
        The initial parameter set as a numpy array of length 98.
    """
    # Initialize the array with zeros
    afPmr_Estimate_Initial = np.zeros(98)

    # Set specific values for the initial parameters
    afPmr_Estimate_Initial[0] = 0.05
    afPmr_Estimate_Initial[1] = 1
    afPmr_Estimate_Initial[2] = 0.05
    afPmr_Estimate_Initial[3] = 1
    afPmr_Estimate_Initial[4] = 0.0001
    afPmr_Estimate_Initial[5] = 0.0003
    afPmr_Estimate_Initial[6] = 0.0003
    afPmr_Estimate_Initial[7] = 0.0005

    afPmr_Estimate_Initial[8] = 0.05
    afPmr_Estimate_Initial[9] = 1
    afPmr_Estimate_Initial[10] = 0.05
    afPmr_Estimate_Initial[11] = 1
    afPmr_Estimate_Initial[12] = 0.0001
    afPmr_Estimate_Initial[13] = 0.0003
    afPmr_Estimate_Initial[14] = 0.0003
    afPmr_Estimate_Initial[15] = 0.0005

    afPmr_Estimate_Initial[16] = 0.05
    afPmr_Estimate_Initial[17] = 1
    afPmr_Estimate_Initial[18] = 0.05
    afPmr_Estimate_Initial[19] = 1
    afPmr_Estimate_Initial[20] = 0.0001
    afPmr_Estimate_Initial[21] = 0.0003
    afPmr_Estimate_Initial[22] = 0.0003
    afPmr_Estimate_Initial[23] = 0.0005

    afPmr_Estimate_Initial[24] = 0.005
    afPmr_Estimate_Initial[25] = 0.1

    # Set values in a loop for specified ranges
    for i in range(6):
        afPmr_Estimate_Initial[26 + 12 * i] = 0.1
        afPmr_Estimate_Initial[27 + 12 * i] = 0
        afPmr_Estimate_Initial[28 + 12 * i] = 0
        afPmr_Estimate_Initial[29 + 12 * i] = 0
        afPmr_Estimate_Initial[30 + 12 * i] = 0
        afPmr_Estimate_Initial[31 + 12 * i] = 0.1
        afPmr_Estimate_Initial[32 + 12 * i] = 0.1
        afPmr_Estimate_Initial[33 + 12 * i] = 0.1
        afPmr_Estimate_Initial[34 + 12 * i] = 0.01
        afPmr_Estimate_Initial[35 + 12 * i] = 0.01
        afPmr_Estimate_Initial[36 + 12 * i] = 0.01
        afPmr_Estimate_Initial[37 + 12 * i] = 0

    return afPmr_Estimate_Initial
