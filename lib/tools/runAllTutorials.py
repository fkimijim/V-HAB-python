import os
import datetime
import shutil
from pathlib import Path

def runAllTutorials():
    """
    Runs all tutorials and saves the figures to a folder.
    This function is a debugging helper.
    """
    # Initializing counters
    iSuccessfulTutorials = 0
    iSkippedTutorials = 0
    iAbortedTutorials = 0

    # Tutorials directory path
    sTutorialDirectory = os.path.join('user', '+tutorials')
    tTutorials = [entry for entry in os.scandir(sTutorialDirectory) if entry.is_dir()]
    mbIsTutorial = [entry.name.startswith('+') for entry in tTutorials]

    # Filter only valid tutorial directories
    tTutorials = [tTutorials[i] for i, is_tutorial in enumerate(mbIsTutorial) if is_tutorial]

    # Create a folder path for saving figures
    sFolderPath = createDataFolderPath()

    # Check for changes in core and library folders
    bCoreChanged = checkForChanges('core')
    bLibChanged = checkForChanges('lib')
    bVHABChanged = checkVHABFiles()

    if any([bCoreChanged, bLibChanged]):
        sCore = 'Core ' if bCoreChanged or bVHABChanged else ''
        sLib = 'Library ' if bLibChanged else ''
        sConjunction = 'and ' if bCoreChanged and bLibChanged else ''
        sVerb = 'have ' if bCoreChanged or bLibChanged else 'has '
        print(f"\n{sCore}{sConjunction}{sLib}{sVerb}changed. All tutorials will be executed!\n")
    else:
        print("\nCore and Library are both unchanged. Proceeding with tutorial execution.\n")

    # Run each tutorial
    for tutorial in tTutorials:
        tutorial_path = os.path.join(sTutorialDirectory, tutorial.name)
        setup_file = os.path.join(tutorial_path, 'setup.m')

        if checkForChanges(tutorial_path) or bLibChanged or bCoreChanged:
            print(f"\n\n======================================\n")
            print(f"Running {tutorial.name.replace('+', '')} Tutorial")
            print("======================================\n\n")

            if os.path.exists(setup_file):
                sExecString = f"tutorials.{tutorial.name.replace('+', '')}.setup"
                try:
                    # Simulate execution of the tutorial
                    oLastSimObj = vhab_exec(sExecString)  # Placeholder function
                    oLastSimObj.plot()  # Placeholder method
                    tools_saveFigures(sFolderPath, tutorial.name.replace('+', ''))  # Placeholder function
                    print(f"Successfully completed {tutorial.name}.\n")
                    iSuccessfulTutorials += 1
                except Exception as e:
                    print(f"\nEncountered an error in the simulation. Aborting.\n")
                    iAbortedTutorials += 1
                    tutorial.sStatus = 'Aborted'
                    tutorial.sErrorReport = str(e)
            else:
                print(f"The {tutorial.name.replace('+', '')} Tutorial does not have a 'setup.m' file. Skipping.")
                iSkippedTutorials += 1
        else:
            print(f"The {tutorial.name.replace('+', '')} Tutorial has not changed. Skipping.")
            iSkippedTutorials += 1

    # Summary report
    print("\n\n======================================\n")
    print("============== Summary ===============\n")
    print("======================================\n\n")
    print(f"Total Tutorials:       {len(tTutorials)}\n")
    print(f"Successfully executed: {iSuccessfulTutorials}")
    print(f"Aborted:               {iAbortedTutorials}")
    print(f"Skipped:               {iSkippedTutorials}")
    print("--------------------------------------")
    print("Detailed Summary:")
    for tutorial in tTutorials:
        status = getattr(tutorial, 'sStatus', 'Unknown')
        print(f"{tutorial.name.replace('+', '')}: {status}")
    print("--------------------------------------\n")

    # Print errors if any
    if iAbortedTutorials > 0:
        print("=======================================\n")
        print("=========== Error messages ============\n")
        print("=======================================\n\n")
        for tutorial in tTutorials:
            if getattr(tutorial, 'sStatus', '') == 'Aborted':
                print(f"=> {tutorial.name.replace('+', '')} Tutorial Error Message:\n\n")
                print(f"{getattr(tutorial, 'sErrorReport', 'No error report available.')}\n")
                print("--------------------------------------\n")

    print("======================================\n")
    print("===== Finished running tutorials =====\n")
    print("======================================\n\n")


def createDataFolderPath():
    """
    Generate a name for a folder in 'data/'.
    """
    sTimeStamp = datetime.datetime.now().strftime('%Y%m%d')
    sBaseFolderPath = os.path.join('data', 'figures', 'Tutorials_Test')
    iFolderNumber = 1

    while True:
        sFolderPath = os.path.join(sBaseFolderPath, f"{sTimeStamp}_Test_Run_{iFolderNumber}")
        if not os.path.exists(sFolderPath):
            os.makedirs(sFolderPath)
            return sFolderPath
        iFolderNumber += 1

# Placeholder functions
def checkForChanges(path):
    # Simulate checking for file changes
    return False

def checkVHABFiles():
    # Simulate checking VHAB files
    return False

def vhab_exec(exec_string):
    # Placeholder for executing a tutorial
    class Simulation:
        def plot(self):
            print("Plotting simulation results.")
    return Simulation()

def tools_saveFigures(folder_path, tutorial_name):
    # Placeholder for saving figures
    print(f"Saving figures for {tutorial_name} in {folder_path}.")

import os
import re
import pickle
from pathlib import Path

def remove_illegal_files_and_folders(tInputStruct):
    """Remove illegal files and folders from the input struct."""
    abIllegals = [False] * len(tInputStruct)
    for iI, item in enumerate(tInputStruct):
        name = item['name']
        if name.startswith('.') or '~' in name or name == 'runAllTutorials.m':
            abIllegals[iI] = True
    return [item for iI, item in enumerate(tInputStruct) if not abIllegals[iI]]

def normalize_path(sInputPath, bUseNewSeparators=False):
    """Normalize the path to remove special characters."""
    if bUseNewSeparators:
        tSeparators = {'package': '__pkd_', 'class': '__clsd_', 'filesep': '__ds__'}
    else:
        tSeparators = {'package': '__', 'class': '_aaat_', 'filesep': '_p_'}
    
    sOutputName = sInputPath
    if not sOutputName.startswith(os.sep):
        sOutputName = os.sep + sOutputName
    
    sOutputName = sOutputName.replace(os.sep + '+', tSeparators['package'])
    sOutputName = sOutputName.replace(os.sep + '@', tSeparators['class'] + 'at_')
    sOutputName = re.sub(r'^[^a-z0-9]*', '', sOutputName, flags=re.IGNORECASE)
    sOutputName = sOutputName.replace(os.sep, tSeparators['filesep'])
    sOutputName = re.sub(r'\.(\w+)$', r'_\1_file', sOutputName)
    sOutputName = re.sub(r'[^a-z0-9_]', '_', sOutputName, flags=re.IGNORECASE)
    sOutputName = re.sub(r'^([^a-z])', r'p_\1', sOutputName, flags=re.IGNORECASE)
    return sOutputName, tSeparators

def check_for_changes(sFileOrFolderPath, save_path='data/FolderStatus.pkl'):
    """Check if the folder contains changed files."""
    save_path = Path(save_path)
    tSavedInfo = {}
    
    if save_path.exists():
        with open(save_path, 'rb') as f:
            tSavedInfo = pickle.load(f)
        
        sFileOrFolderString = normalize_path(sFileOrFolderPath)[0]
        csFieldNames = re.split(r'__|_aa|_p_', sFileOrFolderString)
        
        if len(csFieldNames) == 1:
            top_field = csFieldNames[0]
            if top_field not in tSavedInfo:
                tSavedInfo[top_field] = {}
                with open(save_path, 'wb') as f:
                    pickle.dump(tSavedInfo, f)
                
                tInfo = [dict(name=f.name, isdir=f.is_dir()) for f in os.scandir(sFileOrFolderPath)]
                tInfo = remove_illegal_files_and_folders(tInfo)
                for item in tInfo:
                    check_for_changes(os.path.join(sFileOrFolderPath, item['name']), save_path)
                return True
            else:
                tInfo = [dict(name=f.name, isdir=f.is_dir()) for f in os.scandir(sFileOrFolderPath)]
                tInfo = remove_illegal_files_and_folders(tInfo)
                abChanged = [check_for_changes(os.path.join(sFileOrFolderPath, item['name']), save_path) for item in tInfo]
                return any(abChanged)
    else:
        sFieldName = normalize_path(sFileOrFolderPath)[0]
        tSavedInfo = {sFieldName: {}}
        with open(save_path, 'wb') as f:
            pickle.dump(tSavedInfo, f)
        tInfo = [dict(name=f.name, isdir=f.is_dir()) for f in os.scandir(sFileOrFolderPath)]
        tInfo = remove_illegal_files_and_folders(tInfo)
        for item in tInfo:
            check_for_changes(os.path.join(sFileOrFolderPath, item['name']), save_path)
        return True
