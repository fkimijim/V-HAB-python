import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Pool
from functools import partial
import scipy.io as sio

def run_ccaa_sim(fBroadness, fLength, iSimTicks, Data, oMT, iSim):
    """
    Function to run the CCAA simulation for a given set of parameters.
    """
    # Placeholder function to simulate the behavior of vhab.sim
    # Replace this with the actual simulation logic
    oLastSimObj = simulate_ccaa(fBroadness, fLength, iSimTicks, Data, oMT)

    oLogger = oLastSimObj['logger']

    mfAirOutletTemperature = np.zeros((oLogger['log_index'], 6))
    mfMixedAirOutletTemperature = np.zeros((oLogger['log_index'], 6))
    mfCoolantOutletTemperature = np.zeros((oLogger['log_index'], 6))
    mfCondensateFlow = np.zeros((oLogger['log_index'], 6))

    for iLog, log in enumerate(oLogger['log_values']):
        for iProtoflightTest in range(6):
            label = f'CCAA_{iProtoflightTest + 1}'
            if log['label'] == f'{label} Air Outlet Temperature':
                mfAirOutletTemperature[:, iProtoflightTest] = log['data']
            elif log['label'] == f'{label} Mixed Air Outlet Temperature':
                mfMixedAirOutletTemperature[:, iProtoflightTest] = log['data']
            elif log['label'] == f'{label} Coolant Outlet Temperature':
                mfCoolantOutletTemperature[:, iProtoflightTest] = log['data']
            elif log['label'] == f'{label} Condensate Flow Rate':
                mfCondensateFlow[:, iProtoflightTest] = log['data']

    mfAirTemperatureDifference = (
        mfMixedAirOutletTemperature[3, :] - Data['ProtoflightTestData']['AirOutletTemperature']
    )
    mfCoolantTemperatureDifference = (
        mfCoolantOutletTemperature[3, :] - Data['ProtoflightTestData']['CoolantOutletTemperature']
    )
    mfCondensateDifference = (
        mfCondensateFlow[3, :] * 3600 - Data['ProtoflightTestData']['CondensateMassFlow']
    )

    return {
        'fAirOutletDiff': np.mean(mfAirTemperatureDifference),
        'fCoolantOutletDiff': np.mean(mfCoolantTemperatureDifference),
        'fWaterProduced': np.mean(mfCondensateDifference),
    }

def optimization():
    mfLength = np.arange(0.2, 0.41, 0.01)
    mfBroadness = np.arange(0.2, 0.41, 0.01)

    mfAirOutletDiff = np.zeros((len(mfLength), len(mfBroadness)))
    mfCoolantOutletDiff = np.zeros((len(mfLength), len(mfBroadness)))
    mfWaterProduced = np.zeros((len(mfLength), len(mfBroadness)))

    Data = sio.loadmat('user/+examples/+CCAA/+TestData/ProtoflightData.mat')

    iSimTicks = 4
    oMT = {}  # Placeholder for matter table object
    results = []

    for iLength, fLength in enumerate(mfLength):
        print(f'Currently calculating Length: {fLength}')
        
        with Pool(processes=len(mfBroadness)) as pool:
            partial_run_sim = partial(run_ccaa_sim, fLength=fLength, iSimTicks=iSimTicks, Data=Data, oMT=oMT)
            results = pool.map(partial_run_sim, mfBroadness)

        for iBroadness, result in enumerate(results):
            mfAirOutletDiff[iLength, iBroadness] = result['fAirOutletDiff']
            mfCoolantOutletDiff[iLength, iBroadness] = result['fCoolantOutletDiff']
            mfWaterProduced[iLength, iBroadness] = result['fWaterProduced']

    # Mesh plot data preparation
    X, Y = np.meshgrid(mfLength, mfBroadness, indexing="ij")

    # Air Outlet Temperature Difference
    fig1 = plt.figure('Air Outlet Temperature Difference')
    ax1 = fig1.add_subplot(111, projection='3d')
    ax1.plot_surface(X, Y, mfAirOutletDiff, cmap='viridis')
    ax1.set_xlabel('Length / m')
    ax1.set_ylabel('Broadness / m')
    ax1.set_zlabel('Air Outlet Temperature Difference / K')
    plt.show()

    # Coolant Outlet Temperature Difference
    fig2 = plt.figure('Coolant Outlet Temperature Difference')
    ax2 = fig2.add_subplot(111, projection='3d')
    ax2.plot_surface(X, Y, mfCoolantOutletDiff, cmap='viridis')
    ax2.set_xlabel('Length / m')
    ax2.set_ylabel('Broadness / m')
    ax2.set_zlabel('Coolant Outlet Temperature Difference / K')
    plt.show()

    # Condensate Flow Difference
    fig3 = plt.figure('Condensate Flow Difference')
    ax3 = fig3.add_subplot(111, projection='3d')
    ax3.plot_surface(X, Y, mfWaterProduced, cmap='viridis')
    ax3.set_xlabel('Length / m')
    ax3.set_ylabel('Broadness / m')
    ax3.set_zlabel('Condensate Flow Difference / kg/h')
    plt.show()

def simulate_ccaa(fBroadness, fLength, iSimTicks, Data, oMT):
    """
    Simulate the CCAA system. Placeholder for the actual simulation logic.
    """
    # Simulated logger for demonstration purposes
    return {
        'logger': {
            'log_index': 10,
            'log_values': [
                {
                    'label': f'CCAA_1 Air Outlet Temperature',
                    'data': np.random.rand(10),
                },
                {
                    'label': f'CCAA_1 Mixed Air Outlet Temperature',
                    'data': np.random.rand(10),
                },
                {
                    'label': f'CCAA_1 Coolant Outlet Temperature',
                    'data': np.random.rand(10),
                },
                {
                    'label': f'CCAA_1 Condensate Flow Rate',
                    'data': np.random.rand(10),
                },
            ],
        }
    }

if __name__ == "__main__":
    optimization()
