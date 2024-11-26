import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Pool, Event
import os

def convergence():
    miCells = [2, 5] + list(range(10, 100, 10))
    results = []

    # Creating a matter table object
    oMT = matter_table()

    # Create a control figure with a STOP button
    stop_event = Event()

    def stop_all_sims():
        stop_event.set()
        print("Simulations stopped.")

    # Parallel pool for running simulations
    with Pool() as pool:
        for iCells in miCells:
            print(f"Starting simulation with {iCells} cells")
            result = pool.apply_async(run_sim, args=(iCells, oMT, stop_event))
            results.append((iCells, result))

        pool.close()
        pool.join()

    # Process results
    tData = {
        "cfTimeStep": [],
        "cfPartialPressureCO2_Torr": [],
        "cfCO2InletFlow": [],
        "cfH2OInletFlow": [],
        "cfCO2OutletFlow": [],
        "cfH2OOutletFlow": [],
        "mfAveragedCO2Outlet": [],
        "mfMaxDiff": [],
        "mfMinDiff": [],
        "mfMeanDiff": [],
        "mrPercentualError": [],
        "mfMeanSquaredError": [],
    }

    for iCells, result in results:
        if stop_event.is_set():
            print(f"Simulation for {iCells} cells was stopped.")
            break
        try:
            value = result.get()
            print(f"Completed simulation for {iCells} cells")
            for key in tData:
                tData[key].append(value[key])
        except Exception as e:
            print(f"Error in simulation for {iCells} cells: {e}")

    # Save results
    np.save("ConvergenceData.npy", tData)

    # Plotting results
    plt.figure("Convergence")
    plt.plot(miCells, tData["mfAveragedCO2Outlet"])
    plt.ylabel("Averaged CO2 Outlet Flow / kg/s")
    plt.xlabel("Cell Number per Bed / -")
    plt.savefig("Convergence.png")
    plt.show()

def run_sim(iCells, oMT, stop_event):
    if stop_event.is_set():
        return None

    # Simulate the run
    print(f"Running simulation with {iCells} cells")
    oLastSimObj = vhab_sim(
        "examples.CDRA.setup",
        {
            "ParallelExecution": (oMT,),
            "tInitialization": {
                "Zeolite13x": {"iCellNumber": iCells},
                "Sylobead": {"iCellNumber": iCells},
                "Zeolite5A": {"iCellNumber": iCells},
            },
        },
    )

    # Actually running the simulation
    oLastSimObj.run()
    oLogger = oLastSimObj.toMonitors.oLogger

    # Extract simulation data
    csLogVariableNames = [
        "Timestep",
        "Partial Pressure CO2 Torr",
        "CDRA CO2 InletFlow",
        "CDRA H2O InletFlow",
        "CDRA CO2 OutletFlow",
        "CDRA H2O OutletFlow",
    ]

    # Assuming we have helper methods to extract log data
    log_data = extract_log_data(oLogger, csLogVariableNames)

    # Process results
    interpolated_test_data, time_series = interpolate_test_data()

    partial_pressure = log_data["Partial Pressure CO2 Torr"]
    partial_pressure = partial_pressure[~np.isnan(interpolated_test_data)]
    interpolated_test_data = interpolated_test_data[~np.isnan(interpolated_test_data)]

    return {
        "afTimeStep": log_data["Timestep"],
        "mfPartialPressureCO2_Torr": partial_pressure,
        "mfCO2InletFlow": log_data["CDRA CO2 InletFlow"],
        "mfH2OInletFlow": log_data["CDRA H2O InletFlow"],
        "mfCO2OutletFlow": log_data["CDRA CO2 OutletFlow"],
        "mfH2OOutletFlow": log_data["CDRA H2O OutletFlow"],
        "fAveragedCO2Outlet": np.sum(log_data["CDRA CO2 OutletFlow"] * log_data["Timestep"]) / np.sum(log_data["Timestep"]),
        "fMaxDiff": np.max(np.abs(partial_pressure - interpolated_test_data)),
        "fMinDiff": np.min(np.abs(partial_pressure - interpolated_test_data)),
        "fMeanDiff": np.mean(partial_pressure - interpolated_test_data),
        "rPercentualError": 100 * np.mean(partial_pressure - interpolated_test_data) / np.mean(interpolated_test_data),
        "fMeanSquaredError": np.mean((partial_pressure - interpolated_test_data) ** 2),
    }

def interpolate_test_data():
    # Example interpolation logic
    test_data = np.loadtxt("CDRA_Test_Data.csv", delimiter=",")
    test_data[:, 0] -= 30.7
    test_data = test_data[test_data[:, 0] >= 0]
    time_series = np.linspace(0, 100, len(test_data))
    return np.interp(time_series, test_data[:, 0], test_data[:, 1]), time_series

# Placeholder implementations for dependencies
class matter_table:
    pass

class vhab_sim:
    def __init__(self, setup_name, params):
        self.setup_name = setup_name
        self.params = params

    def run(self):
        print("Simulating...")

    @property
    def toMonitors(self):
        return self

    @property
    def oLogger(self):
        return {"mfLog": np.random.random((100, 6))}

def extract_log_data(oLogger, csLogVariableNames):
    return {name: oLogger["mfLog"][:, i] for i, name in enumerate(csLogVariableNames)}
