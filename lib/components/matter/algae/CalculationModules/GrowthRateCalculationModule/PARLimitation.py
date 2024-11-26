class PARLimitation:
    """
    PARLimitation calculates the relative growth due to the limitation of
    photosynthetically active radiation (PAR) in the photobioreactor volume.
    """

    def __init__(self, oGrowthPhase):
        """
        Initializes the PARLimitation object.

        :param oGrowthPhase: Growth medium
        """
        self.oGrowthPhase = oGrowthPhase
        self.oPARModule = None  # Reference to be set later from Chlorella system
        self.rLinearGrowthFactor = 0  # Unitless
        self.rSaturatedGrowthFactor = 0  # Unitless
        self.rPARRelativeGrowth = 0  # Unitless, passed back to growth calculation module

    def UpdatePARRelativeGrowth(self):
        """
        Updates the relative growth rate due to PAR limitation.

        :return: The updated PAR relative growth factor (unitless)
        """
        # Saturated growth zone factor
        self.rSaturatedGrowthFactor = (
            self.oPARModule.fSaturatedGrowthVolume / self.oPARModule.fWaterVolume
        )

        # Linear growth zone factor
        self.rLinearGrowthFactor = (
            (self.oPARModule.fAveragePPFDLinearGrowth / self.oPARModule.fSaturationPPFD)
            * (self.oPARModule.fLinearGrowthVolume / self.oPARModule.fWaterVolume)
        )

        # Total PAR relative growth factor
        self.rPARRelativeGrowth = (
            self.rSaturatedGrowthFactor + self.rLinearGrowthFactor
        )

        # Cap the growth factor at 1 (due to slight computational overflows)
        if self.rPARRelativeGrowth > 1:
            self.rPARRelativeGrowth = 1

        return self.rPARRelativeGrowth
