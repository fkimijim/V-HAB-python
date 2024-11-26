import os
from datetime import datetime
import matplotlib.pyplot as plt

def saveFigures(sFolderName, sFileName, aoFigures=None):
    """
    SAVEFIGURES Saves all open figures into a folder.
    
    This function saves all currently open matplotlib figures or a specified list of figures. 
    It creates a folder with `sFolderName` as the folder name. Then the figures are saved in a single 
    timestamped file with `sFileName` as the file name.

    Parameters:
    sFolderName (str): The name of the folder where figures will be saved.
    sFileName (str): The base file name for saving the figures.
    aoFigures (list, optional): List of matplotlib figure objects to save. 
                                If None, saves all currently open figures.
    """
    if aoFigures is None or len(aoFigures) == 0:
        # Get all currently open figures
        aoFigures = [plt.figure(i) for i in plt.get_fignums()]
    
    # Generate the timestamp
    sTimeStamp = datetime.now().strftime('%Y%m%d%H%M')
    
    # Ensure the folder exists
    if not os.path.isdir(sFolderName):
        os.makedirs(sFolderName)
    
    # Construct the file path
    sFilePath = os.path.join(sFolderName, f"{sTimeStamp}_{sFileName}.pdf")
    
    # Save the figures as a multi-page PDF
    with plt.backends.backend_pdf.PdfPages(sFilePath) as pdf:
        for fig in aoFigures:
            pdf.savefig(fig)
    
    print(f"Files saved here: {sFilePath}")
