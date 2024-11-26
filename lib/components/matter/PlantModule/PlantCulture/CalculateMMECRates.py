def calculate_MMECRates(self, fInternalTime, fPressureAtmosphere, fDensityAtmosphere, 
                        fRelativeHumidityAtmosphere, fHeatCapacityAtmosphere, fDensityH2O, fCO2):
    """
    Calculate MMECRates based on the MMEC model for plant growth.
    """
    # Determine if it is day or night for the current culture
    if fInternalTime % 86400 < (self.txInput["fPhotoperiod"] * 3600):
        bI = 1
        if self.bLight == 0:
            self.fLightTimeFlag = self.oTimer.fTime
            self.bLight = 1
    else:
        bI = 0
        if self.bLight == 1:
            self.fLightTimeFlag = self.oTimer.fTime
            self.bLight = 0

    # Calculate 24-hour Carbon Use Efficiency (CUE_24)
    if self.txPlantParameters["bLegume"] == 1:
        if fInternalTime <= (self.txPlantParameters["fT_Q"] * 86400):
            fCUE_24 = self.txPlantParameters["fCUE_Max"]
        elif (self.txPlantParameters["fT_Q"] * 86400) < fInternalTime <= (self.txPlantParameters["fT_M"] * 86400):
            fCUE_24 = self.txPlantParameters["fCUE_Max"] - (
                (self.txPlantParameters["fCUE_Max"] - self.txPlantParameters["fCUE_Min"])
                * ((fInternalTime / 86400) - self.txPlantParameters["fT_Q"])
                / (self.txPlantParameters["fT_M"] - self.txPlantParameters["fT_Q"])
            )
    else:
        fCUE_24 = self.txPlantParameters["fCUE_Max"]

    # Calculate time of canopy closure (T_A)
    fT_A = (
        [1 / fCO2, 1, fCO2, fCO2 ** 2, fCO2 ** 3]
        @ self.txPlantParameters["mfMatrix_T_A"]
        @ [1 / self.txInput["fPPFD"], 1, self.txInput["fPPFD"], self.txInput["fPPFD"] ** 2, self.txInput["fPPFD"] ** 3]
        * 86400
    )

    # Fraction of PPFD absorbed by canopy (A)
    if fInternalTime < fT_A:
        fA = self.txPlantParameters["fA_Max"] * (fInternalTime / fT_A) ** self.txPlantParameters["fN"]
    else:
        fA = self.txPlantParameters["fA_Max"]

    # Maximum Canopy Quantum Yield (CQY_Max)
    fCQY_Max = (
        [1 / fCO2, 1, fCO2, fCO2 ** 2, fCO2 ** 3]
        @ self.txPlantParameters["mfMatrix_CQY"]
        @ [1 / self.txInput["fPPFD"], 1, self.txInput["fPPFD"], self.txInput["fPPFD"] ** 2, self.txInput["fPPFD"] ** 3]
    )

    # Canopy Quantum Yield (CQY)
    if fInternalTime <= (self.txPlantParameters["fT_Q"] * 86400):
        fCQY = fCQY_Max
    elif self.txPlantParameters["fT_Q"] < (fInternalTime / 86400) <= self.txPlantParameters["fT_M"]:
        fCQY = fCQY_Max - (
            (fCQY_Max - self.txPlantParameters["fCQY_Min"])
            * ((fInternalTime / 86400) - self.txPlantParameters["fT_Q"])
            / (self.txPlantParameters["fT_M"] - self.txPlantParameters["fT_Q"])
        )
    else:
        fCQY = 0

    fCQY = max(min(fCQY, fCQY_Max), self.txPlantParameters["fCQY_Min"])

    # Hourly Carbon Gain (HCG)
    fHCG = (
        self.txPlantParameters["fAlpha"]
        * fCUE_24
        * fA
        * fCQY
        * self.txInput["fPPFD"]
        * bI
        / 3600
    )

    # Hourly Crop Growth Rate (dry) HCGR
    fHCGR = (
        fHCG
        * self.oMT["afMolarMass"][self.oMT["tiN2I"]["C"]]
        / self.txPlantParameters["fBCF"]
    )

    # Hourly Wet Crop Growth Rate (HWCGR)
    if fInternalTime >= (self.txPlantParameters["fT_E"] * 86400):
        fHWCGR = fHCGR / (1 - self.txPlantParameters["fWBF_Edible"])
    else:
        fHWCGR = fHCGR / (1 - self.txPlantParameters["fWBF_Inedible"])

    # Hourly Oxygen Production (HOP)
    fHOP = (
        fHCG
        / fCUE_24
        * self.txPlantParameters["fOPF"]
        * self.oMT["afMolarMass"][self.oMT["tiN2I"]["O2"]]
    )

    # Hourly Oxygen Consumption (HOC)
    fHOC = (
        (self.txPlantParameters["fAlpha"] * fCUE_24 * fA * fCQY * self.txInput["fPPFD"] / 3600)
        * (1 - fCUE_24)
        / fCUE_24
        * self.txPlantParameters["fOPF"]
        * self.oMT["afMolarMass"][self.oMT["tiN2I"]["O2"]]
        * self.txInput["fPhotoperiod"]
        / 24
    )

    # Hourly CO2 Consumption (HCO2C)
    fHCO2C = (
        fHOP
        * self.oMT["afMolarMass"][self.oMT["tiN2I"]["CO2"]]
        / self.oMT["afMolarMass"][self.oMT["tiN2I"]["O2"]]
    )

    # Hourly CO2 Production (HCO2P)
    fHCO2P = (
        fHOC
        * self.oMT["afMolarMass"][self.oMT["tiN2I"]["CO2"]]
        / self.oMT["afMolarMass"][self.oMT["tiN2I"]["O2"]]
    )

    # Hourly Nutrient Consumption (HNC)
    fHNC = (
        fHCGR
        * self.txPlantParameters["fDRY_Fraction"]
        * self.txPlantParameters["fNC_Fraction"]
    )

    # Hourly Transpiration Rate (HTR)
    fHTR = (
        fDensityH2O
        * self.txInput["fPhotoperiod"]
        / 24
    )

    # Hourly Water Consumption (HWC)
    fHWC = fHTR + fHOP + fHCO2P - fHOC - fHCO2C - fHNC

    # Write Return Parameters
    tfMMECRates = {
        "fWC": fHWC,
        "fTR": fHTR,
        "fOC": fHOC,
        "fOP": fHOP,
        "fCO2C": fHCO2C,
        "fCO2P": fHCO2P,
        "fNC": fHNC,
        "fCGR": fHCGR,
        "fWCGR": fHWCGR,
    }

    return tfMMECRates
