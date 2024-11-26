
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "exme")))
import ExMe

MatterProcsExMe = ExMe()

class LiquidExMe(MatterProcsExMe):
    """
    LiquidExMe: An EXME that interfaces with a liquid phase.

    This class supports gravity-driven flows and calculates pressure 
    based on the liquid level, acceleration, and density.
    """

    def __init__(self, oPhase, sName, fAcceleration=0, fHeightExMe=0):
        """
        Initialize the LiquidExMe.

        Args:
            oPhase (object): The phase the EXME is attached to.
            sName (str): The name of the processor.
            fAcceleration (float, optional): The current acceleration acting 
                on the liquid in m/s^2. Default is 0.
            fHeightExMe (float, optional): The height of the EXME from the 
                bottom in meters. Default is 0.
        """
        super().__init__(oPhase, sName)
        self.fAcceleration = fAcceleration
        self.fHeightExMe = fHeightExMe

        tTankGeomParams = oPhase.oStore.tGeometryParameters
        fVolumeTank = oPhase.oStore.fVolume
        fVolumeLiquid = oPhase.fVolume

        if tTankGeomParams["Shape"].lower() == "box":
            fAreaTank = tTankGeomParams["Area"]
            fHeightTank = fVolumeTank / fAreaTank

            if fHeightTank < self.fHeightExMe:
                raise ValueError("The height of the EXME is larger than the height of the tank.")

            fLiquidLevelTank = fVolumeLiquid / fAreaTank

            if (fLiquidLevelTank - self.fHeightExMe) >= 0:
                self.fLiquidLevel = fLiquidLevelTank - self.fHeightExMe
        else:
            raise ValueError("Invalid store geometry. Check the geometry name.")

        # Calculate pressure based on acceleration and liquid level
        if self.fAcceleration != 0:
            self.fPressure = (
                oPhase.fPressure + self.fLiquidLevel * self.fAcceleration * oPhase.fDensity
            )
        else:
            self.fPressure = oPhase.fPressure

        self.fTemperature = oPhase.fTemperature

    def getExMeProperties(self):
        """
        Returns the EXME properties.

        Returns:
            tuple:
                - fExMePressure (float): Pressure at the EXME in Pa.
                - fExMeTemperature (float): Temperature at the EXME in K.
        """
        fExMePressure = self.fPressure if self.fPressure is not None else self.oPhase.fPressure
        fExMeTemperature = self.fTemperature
        return fExMePressure, fExMeTemperature

    def setPortAcceleration(self, fAcceleration):
        """
        Set the acceleration acting on the EXME.

        Args:
            fAcceleration (float): Acceleration in m/s^2.
        """
        self.fAcceleration = fAcceleration

    def update(self):
        """
        Update the properties of the EXME.

        Recalculates the pressure and temperature based on the liquid level,
        acceleration, and density of the liquid.
        """
        if self.fAcceleration != 0:
            tTankGeomParams = self.oPhase.oStore.tGeometryParameters
            fVolumeTank = self.oPhase.oStore.fVolume
            fVolumeLiquid = self.oPhase.fVolume
            fPressureTank = self.oPhase.fPressure
            fMassTank = self.oPhase.fMass

            self.fTemperature = self.oPhase.fTemperature
            fDensityLiquid = fMassTank / fVolumeLiquid

            if tTankGeomParams["Shape"].lower() == "box":
                fAreaTank = tTankGeomParams["Area"]
                fHeightTank = fVolumeTank / fAreaTank

                if fHeightTank < self.fHeightExMe:
                    raise ValueError("The height of the EXME is larger than the height of the tank.")

                fLiquidLevelTank = fVolumeLiquid / fAreaTank

                if (fLiquidLevelTank - self.fHeightExMe) >= 0:
                    self.fLiquidLevel = fLiquidLevelTank - self.fHeightExMe
            else:
                raise ValueError("Invalid store geometry. Check the geometry name.")

            # Recalculate pressure based on gravity
            self.fPressure = (
                fPressureTank + self.fLiquidLevel * self.fAcceleration * fDensityLiquid
            )
        else:
            self.fPressure = self.oPhase.fPressure

        self.fTemperature = self.oPhase.fTemperature
