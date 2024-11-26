import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "table")))
from private.importNutrientData import NutrientImporter

def create_folders(filepath):
    """
    Create folders if they do not yet exist.

    Args:
        filepath (str): Path to the file used for naming folders.

    Returns:
        tuple: sSystemLabel (system label without '+'), sPath (path to the created folder).
    """
    # Current working directory
    sCurrentFolder = os.getcwd()

    # Define user and DrawIo folder paths
    sUserFolder = os.path.join(sCurrentFolder, "user")
    sDrawIoFolder = "+DrawIoImport"

    # Create the DrawIoImport folder if it doesn't exist
    if not os.path.exists(os.path.join(sUserFolder, sDrawIoFolder)):
        os.makedirs(os.path.join(sUserFolder, sDrawIoFolder))

    sPath = os.path.join(sUserFolder, sDrawIoFolder)

    # Extract the file name without extension
    sFileName = os.path.splitext(os.path.basename(filepath))[0]
    sFileName = NutrientImporter.normalize_path(sFileName)  # Assume tools.normalize_path is defined
    sSystemLabel = f"+{sFileName}"

    # Check if folder already exists and increment name if necessary
    if os.path.exists(os.path.join(sPath, sSystemLabel)):
        sOldSystemLabel = sSystemLabel
        while os.path.exists(os.path.join(sPath, sSystemLabel)):
            sLastThreeDigits = sSystemLabel[-3:]
            if sLastThreeDigits.isdigit():
                iCurrentNumber = int(sLastThreeDigits) + 1
                sSystemLabel = f"{sSystemLabel[:-3]}{iCurrentNumber:03}"
            else:
                sSystemLabel = f"{sSystemLabel}_001"
        print(f"\nYou already have an imported draw io V-HAB system with the name {sOldSystemLabel}!")
        print(f"Increased number increment and created a new folder called {sSystemLabel} for this import\n")

    # Create the system folder
    sPath = os.path.join(sPath, sSystemLabel)
    os.makedirs(sPath, exist_ok=True)

    # Remove the '+' from the label for dot-referencing
    sSystemLabel = sSystemLabel[1:]

    # Create the "+systems" subfolder
    systems_folder = os.path.join(sPath, "+systems")
    os.makedirs(systems_folder, exist_ok=True)

    return sSystemLabel, sPath
