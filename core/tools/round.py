class Round:
    """
    ROUND Static class providing rounding functionality.

    This class provides the `prec` method which rounds a given value 
    to a specified precision.
    """
    # Default decimal value. Masses in V-HAB are given in kg.
    # When using the `prec` method, a value of 5 results in rounding
    # to the nearest 10 mg (1 * 10^-5 kg).
    iDecimal = 5

    @staticmethod
    def prec(fRawValue, iDecimal=None):
        """
        Rounds the input value to the provided decimal precision.

        Parameters:
        fRawValue (float): The value to be rounded.
        iDecimal (int, optional): The number of decimal places to round to.
                                   Defaults to Round.iDecimal.

        Returns:
        float: The rounded value.
        """
        # If no decimal value is given, use the default
        if iDecimal is None:
            iDecimal = Round.iDecimal

        # Compute the multiplier for shifting decimal places
        iMultiplier = 10 ** iDecimal

        # Round the value to the desired precision
        fRoundedValue = round(fRawValue * iMultiplier) / iMultiplier
        return fRoundedValue
