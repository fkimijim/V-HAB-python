import matplotlib.pyplot as plt

def plotSolverFlowRates(mfFlowRates, branchNames):
    """
    Plots flow rates for all iterations in a multi-branch solver.
    
    Parameters:
    mfFlowRates (2D array): Matrix of flow rates, where each column corresponds to a branch, 
                            and each row is an iteration.
    branchNames (list of str): Names of the branches corresponding to the columns of mfFlowRates.
    """
    # Plot the flow rates
    plt.plot(mfFlowRates)
    plt.title('Multi-Branch Solver Flow Rates')
    plt.legend(branchNames, loc='upper right', fontsize='small', frameon=False)
    plt.ylabel('Flow Rate [kg/s]')
    plt.xlabel('Iteration')
    
    # Add a Save button
    from matplotlib.widgets import Button
    
    def saveFigureAs(event):
        """Callback function to save the figure."""
        filename = input("Enter filename to save the figure (e.g., 'plot.png'): ")
        plt.savefig(filename)
        print(f"Figure saved as {filename}")
    
    ax_button = plt.axes([0.01, 0.01, 0.1, 0.05])  # Position of the button
    save_button = Button(ax_button, 'Save', color='lightgrey', hovercolor='grey')
    save_button.on_clicked(saveFigureAs)
    
    # Show the plot
    plt.show()
