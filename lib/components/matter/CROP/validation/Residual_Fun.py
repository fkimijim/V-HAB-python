import os
import numpy as np
from suyi.CROP.tools import (
    Set_Parameter_in_Fitting,
    Settings_DataSeries_in_Fitting,
    data_zero_filter,
    Pick_Sim_Data
)
from suyi.CROP.validation import Data_Experiment
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..")))
from vhab import Vhab

Vhab = Vhab()


def Residual_Fun(afPmr_Estimate):
    """
    This function creates the residual function for the data fitting process
    as described in section 4.3.2 in the thesis.
    
    Parameters:
    -----------
    afPmr_Estimate : numpy.ndarray
        The estimated parameter set.

    Returns:
    --------
    f : numpy.ndarray
        The residuals of all data series concatenated.
    """
    # Load the experimental data from the data file "Data_Experiment.mat"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, 'Data_Experiment.mat')
    Data_Modified = Data_Experiment.load(data_path)

    # Execute the simulation for each data series (from 3.5% to 100%) and calculate residuals
    afResiduals = {}

    for sSeries in ['C', 'H', 'I', 'D', 'E', 'F']:
        # Set parameter in each data series
        Set_Parameter_in_Fitting(afPmr_Estimate, sSeries)

        # Execute the simulation for each data series
        oLastSimObj = Vhab.exec('suyi.CROP.setup')

        # Get the simulation results from the log object "oLogger"
        oLogger = oLastSimObj.toMonitors.oLogger

        # Molar mass array, tank volume, and matter table indices
        afMolMass = oLastSimObj.oSimulationContainer.oMT.afMolarMass
        fVolume_Tank = 30
        tiN2I = oLastSimObj.oSimulationContainer.oMT.tiN2I

        # Time array in days
        afTime_Series = oLogger.afTime / (3600 * 24)

        _, aiNr_DataSet = Settings_DataSeries_in_Fitting(sSeries)
        tTestData = Data_Modified[sSeries]

        # Experimental data of NH4OH, HNO2, HNO3, and pH value
        afTestData_NH4OH = data_zero_filter(tTestData['b'][:, aiNr_DataSet] / 1000)
        afTestData_HNO2 = data_zero_filter(tTestData['c'][:, aiNr_DataSet] / 1000)
        afTestData_HNO3 = data_zero_filter(tTestData['d'][:, aiNr_DataSet] / 1000)
        afTestData_pH = data_zero_filter(tTestData['PH'][:, aiNr_DataSet])

        # Get simulation results of NH4OH, HNO2, HNO3, and pH from the logger
        afSimData_NH4OH = Pick_Sim_Data(
            tTestData['b'][:, 0],
            afTime_Series,
            oLogger.mfLog[:, 13] / (afMolMass[tiN2I['NH4OH']] * fVolume_Tank),
            afTestData_NH4OH
        )
        afSimData_HNO2 = Pick_Sim_Data(
            tTestData['c'][:, 0],
            afTime_Series,
            oLogger.mfLog[:, 16] / (afMolMass[tiN2I['HNO2']] * fVolume_Tank),
            afTestData_HNO2
        )
        afSimData_HNO3 = Pick_Sim_Data(
            tTestData['d'][:, 0],
            afTime_Series,
            oLogger.mfLog[:, 17] / (afMolMass[tiN2I['HNO3']] * fVolume_Tank),
            afTestData_HNO3
        )
        afSimData_pH = Pick_Sim_Data(
            tTestData['PH'][:, 0],
            afTime_Series,
            oLogger.mfLog[:, 18],
            afTestData_pH
        )

        # Residuals of NH4OH, HNO2, HNO3, and pH value
        afDiff_NH4OH = afSimData_NH4OH - afTestData_NH4OH
        afDiff_HNO2 = afSimData_HNO2 - afTestData_HNO2
        afDiff_HNO3 = afSimData_HNO3 - afTestData_HNO3
        afDiff_pH = 0.01 * (afSimData_pH - afTestData_pH)  # Weighted residual for pH

        # Integration of the residuals for a data series
        afResiduals[sSeries] = np.concatenate(
            [afDiff_NH4OH, afDiff_HNO2, afDiff_HNO3, afDiff_pH]
        )

    # Integration of the residuals of all data series
    f = np.concatenate(
        [afResiduals['C'], afResiduals['H'], afResiduals['I'], 
         afResiduals['D'], afResiduals['E'], afResiduals['F']]
    )

    return f
