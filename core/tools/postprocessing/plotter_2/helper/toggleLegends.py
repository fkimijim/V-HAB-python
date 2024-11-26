import matplotlib.pyplot as plt

def toggle_legends(hButton):
    """
    Toggles all legends in a multi-plot figure.
    This function assumes `hButton` is connected to a matplotlib figure.

    Parameters:
        hButton: matplotlib button or any object that provides a `figure` attribute.
    """
    # Getting the handle of the parent figure
    hFigure = hButton.figure

    # Finding all legend objects in the figure
    aoLegends = [child for child in hFigure.get_children() if isinstance(child, plt.Legend)]

    # Getting the current visibility status of each legend
    csCurrentStatus = [legend.get_visible() for legend in aoLegends]

    # Toggling the visibility status
    csNewStatus = [not status for status in csCurrentStatus]

    # Applying the new visibility status to each legend
    for legend, new_status in zip(aoLegends, csNewStatus):
        legend.set_visible(new_status)

    # Redraw the figure to reflect changes
    hFigure.canvas.draw()

# Example usage
if __name__ == "__main__":
    # Create a sample plot with multiple legends
    fig, ax = plt.subplots()
    line1, = ax.plot([1, 2, 3], [1, 4, 9], label="Line 1")
    line2, = ax.plot([1, 2, 3], [9, 4, 1], label="Line 2")

    # Add legends
    legend1 = ax.legend(handles=[line1], loc="upper left")
    legend2 = ax.legend(handles=[line2], loc="upper right")

    # Add a button to toggle legends
    from matplotlib.widgets import Button

    ax_button = plt.axes([0.7, 0.01, 0.1, 0.075])
    toggle_button = Button(ax_button, "Toggle Legends")

    def on_button_click(event):
        toggle_legends(toggle_button)

    toggle_button.on_clicked(on_button_click)

    plt.show()
