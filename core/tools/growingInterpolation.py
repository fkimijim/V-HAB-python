import numpy as np
import pickle


class GrowingInterpolation:
    """
    GrowingInterpolation
    Dynamically stores output values of a function for given inputs to avoid recalculation.
    Uses nearest-neighbor interpolation based on user-defined relative or absolute limits.
    """

    def __init__(self, oParent, sName, hFunction, arRelativeInputDeviationLimits, afAbsoluteInputDeviationLimits=None):
        """
        Initialize the GrowingInterpolation class.

        Parameters:
            oParent: The parent object for this interpolation (e.g., CHX).
            sName: Identifier for this interpolation object.
            hFunction: Handle to the function for interpolation, taking a vector as input and returning a vector as output.
            arRelativeInputDeviationLimits: Percentual deviation limits for input reuse.
            afAbsoluteInputDeviationLimits: Absolute deviation limits for input reuse (optional).
        """
        self.oParent = oParent
        self.sName = sName
        self.hFunction = hFunction
        self.arRelativeInputDeviationLimits = arRelativeInputDeviationLimits
        self.afAbsoluteInputDeviationLimits = afAbsoluteInputDeviationLimits
        self.iInputs = None
        self.iOutputs = None
        self.mfMeanInputData = None
        self.mfStoredInputData = np.empty((0, len(arRelativeInputDeviationLimits)))
        self.mfStoredOutputData = np.empty((0,))

    def calculate_outputs(self, mfInputs, bForceNewCalculation=False):
        """
        Calculate outputs for the given inputs using the stored function or previously stored data points.

        Parameters:
            mfInputs: Input vector for the function.
            bForceNewCalculation: Force a new calculation (default: False).

        Returns:
            mfClosestOutputs: Output vector, either interpolated or calculated.
            bFoundMatch: Boolean indicating if a valid match was found.
            fRSS: Residual sum of squares for the selected interpolation point.
        """
        if not bForceNewCalculation:
            bFoundMatch = self.check_match(mfInputs)
        else:
            bFoundMatch = False

        if bFoundMatch and not bForceNewCalculation:
            mfClosestOutputs, fRSS = self.find_closest_match(mfInputs)
        else:
            fRSS = 0
            mfClosestOutputs = self.hFunction(mfInputs)
            self.add_data_point(mfInputs, mfClosestOutputs)

        return mfClosestOutputs, bFoundMatch, fRSS

    def adjust_limits(self, arRelativeInputDeviationLimits, afAbsoluteInputDeviationLimits=None):
        """
        Adjust the deviation limits for input reuse.

        Parameters:
            arRelativeInputDeviationLimits: New percentual deviation limits.
            afAbsoluteInputDeviationLimits: New absolute deviation limits (optional).
        """
        self.arRelativeInputDeviationLimits = arRelativeInputDeviationLimits
        self.afAbsoluteInputDeviationLimits = afAbsoluteInputDeviationLimits

    def load_stored_data(self, tData):
        """
        Load previously stored interpolation data.

        Parameters:
            tData: Dictionary with 'Input' and 'Output' keys for stored data.
        """
        self.mfStoredInputData = np.array(tData['Input'])
        self.mfStoredOutputData = np.array(tData['Output'])
        self.iInputs = self.mfStoredInputData.shape[1]
        self.iOutputs = self.mfStoredOutputData.shape[1]
        self.mfMeanInputData = np.mean(self.mfStoredInputData, axis=0)

    def store_data(self, sFileName=None):
        """
        Save the interpolation data to a file.

        Parameters:
            sFileName: File name to save the data (optional).
        """
        if sFileName is None:
            sFileName = self.sName

        tData = {
            'Input': self.mfStoredInputData.tolist(),
            'Output': self.mfStoredOutputData.tolist()
        }

        with open(sFileName, 'wb') as f:
            pickle.dump(tData, f)

    def add_data_point(self, mfInputs, mfOutputs):
        """
        Add a new data point to the stored interpolation data.

        Parameters:
            mfInputs: Input vector for the calculated data point.
            mfOutputs: Output vector for the calculated data point.
        """
        if self.iInputs is None:
            self.iInputs = len(mfInputs)
            self.iOutputs = len(mfOutputs)

        self.mfStoredInputData = np.vstack([self.mfStoredInputData, mfInputs])
        self.mfStoredOutputData = np.vstack([self.mfStoredOutputData, mfOutputs])
        self.mfMeanInputData = np.mean(self.mfStoredInputData, axis=0)

    def check_match(self, mfInputs):
        """
        Check if any stored data point matches the input within defined limits.

        Parameters:
            mfInputs: Input vector to check against stored data.

        Returns:
            bMatch: Boolean indicating if a valid match was found.
        """
        if self.mfStoredInputData.size == 0:
            return False

        mfAbsoluteDeviation = np.abs(self.mfStoredInputData - mfInputs)
        abAbsolute = (
            np.all(mfAbsoluteDeviation < self.afAbsoluteInputDeviationLimits, axis=1)
            if self.afAbsoluteInputDeviationLimits is not None
            else True
        )
        abRelative = (
            np.all((mfAbsoluteDeviation / np.abs(mfInputs)) < self.arRelativeInputDeviationLimits, axis=1)
            if self.arRelativeInputDeviationLimits is not None
            else True
        )

        return np.any(abAbsolute & abRelative)

    def find_closest_match(self, mfInputs):
        """
        Find the closest matching stored data point to the input.

        Parameters:
            mfInputs: Input vector to match against stored data.

        Returns:
            mfClosestOutputs: Output vector for the closest matching data point.
            fRSS: Residual sum of squares for the match.
        """
        mfRSS = np.sum(((self.mfStoredInputData - mfInputs) / self.mfMeanInputData) ** 2, axis=1)
        aiClosestMatch = np.where(mfRSS == np.min(mfRSS))[0]

        mfClosestOutputs = np.mean(self.mfStoredOutputData[aiClosestMatch], axis=0)
        fRSS = np.mean(mfRSS[aiClosestMatch])

        return mfClosestOutputs, fRSS
