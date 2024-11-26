class configurationParameters:
    """
    Framework to provide configuration parameters for simulations.
    This class makes it easier to run multiple simulations in parallel, each
    using different parameters for vsys objects. Parameters are stored in a
    dictionary and can be accessed for individual systems.
    """

    def __init__(self, ptConfigParams):
        """
        Constructor for the configurationParameters class.

        Parameters:
        - ptConfigParams: A dictionary containing configuration parameters.
        """
        self.ptConfigParams = ptConfigParams

    def get(self, oVsys):
        """
        Extracts the configuration parameters for a specific system.

        Parameters:
        - oVsys: The system object to retrieve parameters for.

        Returns:
        - tParams: A dictionary containing the parameters for the system.
        - csKeys: A list of parameter keys.
        """
        # Extract the constructor name and system path
        sConstructor = oVsys.oMeta.Name
        sSystemPath = self._getSystemPath(oVsys)

        # Initialize the return dictionary
        tParams = {}

        # Match constructor path
        for sKey, value in self.ptConfigParams.items():
            if sKey == sConstructor:
                tParams.update(value)

        # Match system path
        for sKey, value in self.ptConfigParams.items():
            fullPath = self._convertShorthandToFullPath(sKey)
            if fullPath == sSystemPath:
                tParams.update(value)

        # Extract the field names (keys) for convenience
        csKeys = list(tParams.keys())

        return tParams, csKeys

    def configCode(self, oVsys):
        """
        Returns code that can be directly executed in the vsys object to set parameters.

        Parameters:
        - oVsys: The vsys object to set parameters for.

        Returns:
        - sCode: A string of executable code to set parameters.
        """
        sCode = (
            "[tParams, csKeys] = this.oRoot.oCfgParams.get(this)\n"
            "for iParameter in range(len(csKeys)):\n"
            "    key = csKeys[iParameter]\n"
            "    if '.' in key:\n"
            "        sA, sB = key.split('.', 1)\n"
            "        setattr(getattr(this, sA), sB, tParams[key])\n"
            "    else:\n"
            "        setattr(this, key, tParams[key])\n"
        )
        return sCode

    @staticmethod
    def _getSystemPath(oVsys):
        """
        Helper method to extract the full system path.

        Parameters:
        - oVsys: The system object.

        Returns:
        - The full path as a string.
        """
        # Placeholder for the logic to extract the system path
        return oVsys.getPath()

    @staticmethod
    def _convertShorthandToFullPath(sKey):
        """
        Helper method to convert shorthand system paths to full paths.

        Parameters:
        - sKey: The shorthand path.

        Returns:
        - The full path as a string.
        """
        # Placeholder for the logic to convert shorthand to full path
        return sKey.replace("/", ".toChildren.")
