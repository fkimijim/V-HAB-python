import numpy as np

def find_log_indices(oLogger, csLogVariableNames):
    """
    Find the indices inside the logger for the provided labels.

    Parameters:
    oLogger: object
        Reference to the logger object which contains the log values.
        Assumes `tLogValues` and `tVirtualValues` are attributes of the logger,
        each containing a list of objects with an `sLabel` attribute.
    csLogVariableNames: list of str
        List of labels as strings. The output indices will be in the same
        order as this list.

    Returns:
    aiLogIndices: numpy.ndarray
        Array of indices corresponding to `tLogValues` in the logger.
    aiVirtualLogIndices: numpy.ndarray
        Array of indices corresponding to `tVirtualValues` in the logger.
    """
    aiLogIndices = np.full(len(csLogVariableNames), np.nan)
    aiVirtualLogIndices = np.full(len(csLogVariableNames), np.nan)

    for iLabel, sLabel in enumerate(csLogVariableNames):
        # Remove double quotes from the label if present
        sLabel = sLabel.replace('"', '')

        # Search in tLogValues
        for iLog, logValue in enumerate(oLogger.tLogValues):
            if logValue.sLabel == sLabel:
                aiLogIndices[iLabel] = iLog
                break

        # If not found, search in tVirtualValues
        if np.isnan(aiLogIndices[iLabel]):
            for iLog, virtualValue in enumerate(oLogger.tVirtualValues):
                if virtualValue.sLabel == sLabel:
                    aiVirtualLogIndices[iLabel] = iLog
                    break

    return aiLogIndices, aiVirtualLogIndices
