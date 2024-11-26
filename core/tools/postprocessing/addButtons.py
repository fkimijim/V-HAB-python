import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import numpy as np

def add_buttons(oFigure):
    """
    Adds buttons to the given figure for interacting with subplots.

    Parameters:
        oFigure: Matplotlib Figure object.
    """
    # Get all axes (subplots) in the figure
    aoAxes = oFigure.get_axes()
    iNumberOfPlots = len(aoAxes)

    # Store subplot positions
    ciPositions = [(ax.get_position().x0, ax.get_position().y0) for ax in aoAxes]

    iColumns = len(set([pos[0] for pos in ciPositions]))
    iRows = len(set([pos[1] for pos in ciPositions]))

    # Add buttons for saving or undocking subplots
    if iNumberOfPlots == 1:
        ax_save_button = oFigure.add_axes([0.01, 0.01, 0.1, 0.05])
        save_button = Button(ax_save_button, 'Save')

        def save_callback(event):
            file_name = input("Enter file name to save the figure: ")
            oFigure.savefig(file_name)
            print(f"Figure saved as {file_name}")

        save_button.on_clicked(save_callback)
    else:
        # Create panel for buttons
        fPanelYSize = 0.12
        fPanelXSize = 0.065

        # Panel for undocking buttons
        panel = plt.figure(figsize=(fPanelXSize * 10, fPanelYSize * 10))
        panel_ax = panel.add_subplot(111)
        panel_ax.axis('off')
        panel_ax.set_title('Undock Subplots')

        # Save button for the entire figure
        ax_save_button = oFigure.add_axes([0.01, 0.13, 0.1, 0.05])
        save_button = Button(ax_save_button, 'Save Figure')

        def save_figure_callback(event):
            file_name = input("Enter file name to save the figure: ")
            oFigure.savefig(file_name)
            print(f"Figure saved as {file_name}")

        save_button.on_clicked(save_figure_callback)

        # Create toggle legends button
        ax_toggle_button = oFigure.add_axes([0.01, 0.18, 0.1, 0.05])
        toggle_button = Button(ax_toggle_button, 'Toggle Legends')

        def toggle_legends_callback(event):
            for ax in aoAxes:
                legend = ax.get_legend()
                if legend:
                    legend.set_visible(not legend.get_visible())
            oFigure.canvas.draw_idle()

        toggle_button.on_clicked(toggle_legends_callback)

        # Calculate button dimensions
        fButtonYSize = (14 - (iRows - 1)) / iRows / 16
        fButtonXSize = (14 - (iColumns - 1)) / iColumns / 16

        fHorizontalSpacing = fButtonXSize + 1 / 16
        fVerticalSpacing = fButtonYSize + 1 / 16

        afHorizontal = np.arange(0, 1, fHorizontalSpacing)[:iColumns]
        afVertical = np.flip(np.arange(0, 1, fVerticalSpacing)[:iRows])

        coButtons = []

        iSubPlotCounter = 0
        for iRow, y in enumerate(afVertical):
            for iCol, x in enumerate(afHorizontal):
                if iSubPlotCounter < iNumberOfPlots:
                    ax_button = panel.add_axes([x, y, fButtonXSize, fButtonYSize])
                    button = Button(ax_button, str(iSubPlotCounter + 1))

                    def undock_subplot(event, ax=aoAxes[iSubPlotCounter]):
                        new_fig = plt.figure()
                        new_ax = new_fig.add_subplot(111)
                        for line in ax.get_lines():
                            new_ax.plot(line.get_xdata(), line.get_ydata(), label=line.get_label())
                        new_ax.legend()
                        new_ax.set_title(ax.get_title())
                        new_ax.set_xlabel(ax.get_xlabel())
                        new_ax.set_ylabel(ax.get_ylabel())
                        plt.show()

                    button.on_clicked(undock_subplot)
                    coButtons.append(button)
                    iSubPlotCounter += 1

    plt.show()

# Example usage
if __name__ == "__main__":
    fig, axes = plt.subplots(2, 2)
    for i, ax in enumerate(axes.flatten(), start=1):
        ax.plot(range(10), range(10), label=f'Line {i}')
        ax.legend()
        ax.set_title(f'Subplot {i}')

    add_buttons(fig)
