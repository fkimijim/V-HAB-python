def calculateJouleThomson(self, *args):
    """
    Calculates the Joule-Thomson coefficient of the matter in a phase or flow.

    Examples:
        fJouleThomson = calculateJouleThomson(oFlow)
        fJouleThomson = calculateJouleThomson(oPhase)
        fJouleThomson = calculateJouleThomson(sType, afMass, fTemperature, afPartialPressures)

    Returns:
        fJouleThomson: Joule-Thomson coefficient in K/Pa
    """

    (
        fTemperature,
        arPartialMass,
        csPhase,
        aiPhase,
        aiIndices,
        afPartialPressures,
        _,
        _,
        bUseIsobaricData,
    ) = self.getNecessaryParameters(*args)

    # Here, decision logic for alternative calculations can be added if needed
    # (see calculateDensity function as an example)

    fJouleThomson = self.calculateProperty(
        "Joule Thomson",
        fTemperature,
        arPartialMass,
        csPhase,
        aiPhase,
        aiIndices,
        afPartialPressures,
        bUseIsobaricData,
    )

    return fJouleThomson
