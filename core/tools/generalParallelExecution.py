import os
import datetime
import multiprocessing as mp
from multiprocessing import Manager
import time
import threading
import pickle

def general_parallel_execution(
    sSimulationPath, cmInputs, csSimulationNames=None, iTicksBetweenUpdateWaitBar=1, 
    sContinueFromFolder=None, fAdvanceTo=None
):
    """
    Executes simulations in parallel with different parameters.
    
    Parameters:
        sSimulationPath (str): Path to the simulation definition.
        cmInputs (list of dict): Parameters for each simulation as dictionaries.
        csSimulationNames (list of str, optional): Names of the simulations for display and saving.
        iTicksBetweenUpdateWaitBar (int, optional): Number of ticks between wait bar updates.
        sContinueFromFolder (str, optional): Folder to continue simulations from.
        fAdvanceTo (float, optional): Time to advance to when continuing simulations.
    """
    iSimulations = len(cmInputs)

    if csSimulationNames is None:
        csSimulationNames = [str(i + 1) for i in range(iSimulations)]

    # Create a unique storage directory
    fCreated = datetime.datetime.now()
    sStorageDirectory = f"{fCreated.strftime('%Y-%m-%d_%H-%M-%S_%f')}_ParallelExecution"

    if not os.path.exists(f"data/runs/{sStorageDirectory}"):
        os.makedirs(f"data/runs/{sStorageDirectory}")

    # Initialize global storage
    global sStorageDirectory_global
    sStorageDirectory_global = sStorageDirectory

    # Use a Manager for shared data structures
    manager = Manager()
    abActiveSimulations = manager.list([False] * iSimulations)
    abErrorResults = manager.list([False] * iSimulations)
    bCancelled = manager.Value('b', False)

    # Create a dictionary to track progress
    progress_dict = manager.dict({sim: 0 for sim in range(iSimulations)})

    # Define a function for worker execution
    def worker(sim_idx):
        try:
            sim_input = cmInputs[sim_idx]
            sim_name = csSimulationNames[sim_idx]
            print(f"Starting Simulation: {sim_name}")

            if sContinueFromFolder:
                # Continue from existing simulation
                sim_file = f"data/runs/{sContinueFromFolder}/oLastSimObj_{sim_name}.pkl"
                with open(sim_file, 'rb') as f:
                    oLastSimObj = pickle.load(f)
                
                oLastSimObj.set_parallel_send_interval(iTicksBetweenUpdateWaitBar)
                oLastSimObj.advance_to(fAdvanceTo)
            else:
                # Start a new simulation
                oLastSimObj = run_simulation(sSimulationPath, sim_input, iTicksBetweenUpdateWaitBar)
            
            # Save the result
            sim_file = f"data/runs/{sStorageDirectory}/oLastSimObj_{sim_name}.pkl"
            with open(sim_file, 'wb') as f:
                pickle.dump(oLastSimObj, f)

            print(f"Completed Simulation: {sim_name}")
            progress_dict[sim_idx] = 100
        except Exception as e:
            print(f"Error in Simulation {csSimulationNames[sim_idx]}: {e}")
            abErrorResults[sim_idx] = True

    # Create and start the pool of workers
    with mp.Pool(processes=mp.cpu_count()) as pool:
        for sim_idx in range(iSimulations):
            pool.apply_async(worker, args=(sim_idx,))

        # Monitor progress
        def monitor_progress():
            while True:
                if bCancelled.value:
                    print("Stopping all simulations...")
                    pool.terminate()
                    break
                time.sleep(1)
                for sim_idx, progress in progress_dict.items():
                    print(f"Simulation {csSimulationNames[sim_idx]} Progress: {progress}%")
        
        monitor_thread = threading.Thread(target=monitor_progress, daemon=True)
        monitor_thread.start()

        # Wait for all workers to complete
        pool.close()
        pool.join()

        # Wait for monitor thread to finish
        monitor_thread.join()

    print("All simulations completed.")

# Supporting function for running simulations
def run_simulation(sSimulationPath, sim_input, iTicksBetweenUpdateWaitBar):
    """
    Run a single simulation.

    Parameters:
        sSimulationPath (str): Path to the simulation definition.
        sim_input (dict): Input parameters for the simulation.
        iTicksBetweenUpdateWaitBar (int): Ticks between updates.

    Returns:
        Simulation object or result.
    """
    # Placeholder for simulation initialization logic
    print(f"Initializing simulation at {sSimulationPath} with inputs: {sim_input}")
    # Simulate execution
    for tick in range(1, 101):
        time.sleep(0.1)  # Simulate work
        if tick % iTicksBetweenUpdateWaitBar == 0:
            print(f"Tick {tick} progress...")
    return {"status": "completed"}

# Example usage
if __name__ == "__main__":
    # Example inputs for testing
    sSimulationPath = "simulations.ISS.setup"
    cmInputs = [
        {"tbCases": {"ACLS": False, "PlantChamber": False}, "sPlantLocation": "", "fSimTime": 300},
        {"tbCases": {"ACLS": False, "PlantChamber": True}, "sPlantLocation": "Columbus", "fSimTime": 300},
    ]
    csSimulationNames = ["Sim1", "Sim2"]
    general_parallel_execution(sSimulationPath, cmInputs, csSimulationNames)
