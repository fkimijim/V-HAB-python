import matplotlib.pyplot as plt
from matplotlib.widgets import Button

def undock_subplot(oSubPlot, oLegend=None):
    """
    Undocks a subplot from the main figure.
    Creates a new figure containing only the specified subplot.

    Parameters:
        oSubPlot: The Axes object to undock.
        oLegend: The Legend object associated with the subplot, if any.
    """
    # Create a new figure for the undocked subplot
    hFigure = plt.figure()
    hFigure.canvas.manager.set_window_title(oSubPlot.get_title())
    
    # Store original parent and positions for restoration
    hFigure.user_data = {
        "OldParent": oSubPlot.figure,
        "OldAxesPosition": oSubPlot.get_position(),
        "OldLegendPosition": oLegend.get_bbox_to_anchor() if oLegend else None,
    }
    
    # Transfer subplot to the new figure
    new_axes = hFigure.add_subplot(111)
    for line in oSubPlot.get_lines():
        new_axes._add_line(line)
    new_axes.set_title(oSubPlot.get_title())
    new_axes.set_xlim(oSubPlot.get_xlim())
    new_axes.set_ylim(oSubPlot.get_ylim())
    new_axes.set_xlabel(oSubPlot.get_xlabel())
    new_axes.set_ylabel(oSubPlot.get_ylabel())
    
    # Restore legend in the new figure
    if oLegend:
        new_axes.legend(oLegend.get_lines(), [t.get_text() for t in oLegend.texts], loc="best")

    # Create a save button in the new figure
    ax_button = hFigure.add_axes([0.8, 0.01, 0.1, 0.05])
    save_button = Button(ax_button, "Save")
    
    def save_callback(event):
        file_path = input("Enter file name to save the figure: ")
        hFigure.savefig(file_path, dpi=300, bbox_inches='tight')
        print(f"Figure saved as {file_path}")
    
    save_button.on_clicked(save_callback)

    # Add delete callback to restore the subplot when the new figure is closed
    hFigure.canvas.mpl_connect('close_event', lambda event: restore_figure(event, oSubPlot, hFigure))

    plt.show()

def restore_figure(event, oSubPlot, hFigure):
    """
    Restores the subplot to its original figure.

    Parameters:
        event: The close event triggering the restoration.
        oSubPlot: The Axes object to restore.
        hFigure: The temporary figure containing the undocked subplot.
    """
    user_data = hFigure.user_data
    old_parent = user_data["OldParent"]
    old_position = user_data["OldAxesPosition"]
    old_legend_position = user_data["OldLegendPosition"]
    
    # Restore subplot to its original parent and position
    oSubPlot.figure = old_parent
    oSubPlot.set_position(old_position)
    
    # Restore legend, if it existed
    if old_legend_position:
        legend = oSubPlot.get_legend()
        if legend:
            legend.set_bbox_to_anchor(old_legend_position)

    print("Subplot restored to original figure.")

# Example usage
if __name__ == "__main__":
    fig, ax = plt.subplots()
    line1, = ax.plot([1, 2, 3], [1, 4, 9], label="Line 1")
    legend = ax.legend()

    # Button to undock the subplot
    ax_button = plt.axes([0.7, 0.01, 0.1, 0.05])
    undock_button = Button(ax_button, "Undock")

    def undock_callback(event):
        undock_subplot(ax, legend)

    undock_button.on_clicked(undock_callback)

    plt.show()
