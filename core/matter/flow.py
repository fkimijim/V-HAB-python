import MatterBranch
from store.store import Store
from procs.f2f.f2f import F2F
from procs.exme.exme import ExMe

MatterBranch = MatterBranch()
MatterStore = Store()
F2FProcessor = F2F()
ExmeProcessor = ExMe()

class Flow:
    """
    Flow: A class describing the flow of matter.
    Represents a homogenous flow of matter at an interface between components of the simulation.
    """

    def __init__(self, oCreator=None):
        """
        Initialize the flow object.
        
        Args:
            oCreator: The object that creates the flow, either a branch or a store.
        """
        self.fFlowRate = 0  # [kg/s]
        self.fPressure = 0  # [Pa]
        self.fTemperature = 293  # [K]
        self.fMolarMass = 0  # [kg/mol]
        self.fDensity = None  # [kg/m^3]
        self.fDynamicViscosity = None  # [Pa/s]
        self.arPartialMass = None  # Partial masses as a vector
        self.arCompoundMass = None  # Compound masses for multi-substance matter
        self.oMT = None  # Matter table reference
        self.oTimer = None  # Timer reference
        self.oBranch = None  # Branch this flow belongs to
        self.oStore = None  # Store this flow belongs to if used as a P2P processor
        self.fDiameter = 0  # Diameter of the flow
        self.oIn = None  # Input processor
        self.oOut = None  # Output processor
        self.iFlow = 0  # Flow index within the branch
        self.bSealed = False  # Indicates if the flow is sealed
        self.bInterface = False  # Indicates if this is an interface flow
        self.tfPropertiesAtLastMassPropertySet = {
            "fTemperature": -1,
            "fPressure": -1,
            "arPartials": None,
        }
        self.sObjectType = "flow"  # Object type identifier
        self.thRemoveCBs = {"in": None, "out": None}  # Callbacks for removal

        if oCreator:
            self.oMT = oCreator.oMT
            self.oTimer = oCreator.oTimer
            self.arPartialMass = [0] * self.oMT.iSubstances
            self.arCompoundMass = [[0] * self.oMT.iSubstances for _ in range(self.oMT.iSubstances)]

            if isinstance(oCreator, MatterBranch):
                self.oBranch = oCreator
            elif isinstance(oCreator, MatterStore):
                self.oStore = oCreator

    def seal(self, bIf=False, oBranch=None):
        """
        Seals the flow object and provides the setData function handle.
        
        Args:
            bIf (bool): Indicates if this flow is an interface flow.
            oBranch: The branch in which the flow is located.
        
        Returns:
            setData (function): Function handle to set data for the flow.
            hRemoveIfProc (function): Function handle to remove an interface processor.
        """
        if self.bSealed:
            raise RuntimeError("Flow is already sealed!")

        self.bSealed = True
        hRemoveIfProc = None
        setData = lambda oThis, *args: oThis.setData(*args)

        if bIf and self.oIn and not self.oOut:
            self.bInterface = True
            hRemoveIfProc = self.removeIfProc

        if oBranch:
            self.oBranch = oBranch

        # Initialize properties for non-interface flows
        if not bIf:
            if self.oBranch.abIf[0]:
                oPhase = self.oBranch.coExmes[1].oPhase
            else:
                aoPhases = [exme.oPhase for exme in self.oBranch.coExmes]
                oPhase = max(aoPhases, key=lambda phase: phase.fMass)

            if oPhase.fMass != 0:
                self.arPartialMass = oPhase.arPartialMass
                self.fMolarMass = oPhase.fMolarMass
                self.arCompoundMass = oPhase.arCompoundMass

        return setData, hRemoveIfProc

    def remove(self):
        """
        Removes the flow from connected processors.
        """
        if self.oIn and self.thRemoveCBs["in"]:
            self.thRemoveCBs["in"]()
        if self.oOut and self.thRemoveCBs["out"]:
            self.thRemoveCBs["out"]()

        self.oIn = None
        self.oOut = None

    def getDensity(self):
        """
        Returns the density of the flow.
        """
        if self.fDensity is None:
            self.fDensity = self.oMT.calculateDensity(self)
        return self.fDensity

    def getDynamicViscosity(self):
        """
        Returns the dynamic viscosity of the flow.
        """
        if self.fDynamicViscosity is None:
            self.fDynamicViscosity = self.oMT.calculateDynamicViscosity(self)
        return self.fDynamicViscosity

    @property
    def afPartialPressure(self):
        """
        Returns the partial pressures of the matter in the flow.
        """
        return self.oMT.calculatePartialPressures(self)

    @property
    def fSpecificHeatCapacity(self):
        """
        Returns the specific heat capacity of the flow.
        """
        try:
            if self.iFlow == 0:
                return self.fSpecificHeatCapacityP2P
            if self.fFlowRate >= 0:
                iConductor = self.iFlow - 1
            else:
                iConductor = self.iFlow + 1
            return self.oBranch.oThermalBranch.coConductors[iConductor].fSpecificHeatCapacity
        except AttributeError:
            return 0

    def addProc(self, oProc, removeCallBack):
        """
        Adds a processor to the flow.
        
        Args:
            oProc: Processor to be added.
            removeCallBack: Callback function to remove the flow from the processor.
        
        Returns:
            iSign (int): -1 if added to oIn, 1 if added to oOut.
        """
        if not isinstance(oProc, (F2FProcessor, ExmeProcessor)):
            raise TypeError("Provided processor is not a valid F2F or Exme processor!")

        if self.bSealed and (not self.bInterface or self.oIn is None):
            raise RuntimeError("Cannot modify sealed flow!")

        if self.oIn is None:
            self.oIn = oProc
            self.thRemoveCBs["in"] = removeCallBack
            return -1
        elif self.oOut is None:
            self.oOut = oProc
            self.thRemoveCBs["out"] = removeCallBack
            return 1
        else:
            raise RuntimeError("Both input and output processors are already set!")

    def calculateVolumetricFlowRate(self, fFlowRate=None):
        """
        Calculates the volumetric flow rate in m^3/s.
        
        Args:
            fFlowRate (float): Mass flow rate in kg/s. Defaults to the flow's own rate.
        
        Returns:
            fVolumetricFlowRate (float): Volumetric flow rate in m^3/s.
        """
        if fFlowRate is None:
            fFlowRate = self.fFlowRate

        if fFlowRate != 0:
            density = self.getDensity()
            return fFlowRate / density
        return 0

    def setData(self, aoFlows, oExme, fFlowRate, afPressures):
        """
        Sets the data for this flow based on provided parameters.
        """
        # Logic for updating flow properties...
        pass
