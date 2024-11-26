import matplotlib.pyplot as plt
import numpy as np

def overlay_figures(csFigures, csLegendEntries=None):
    """
    Overlays multiple figures into one figure, provided they share a common time frame
    and the same layout of subplots.

    Parameters:
        csFigures (list of str): List of file paths to the saved figures.
        csLegendEntries (list of str, optional): List of legend entries for the combined figure.
    """
    iTotalFigures = len(csFigures)
    coFigures = []
    coAxes = []
    coDataObjects = []

    for csFigure in csFigures:
        # Open each figure
        fig = plt.figure()
        ax = fig.add_subplot(111)
        fig.canvas.set_window_title(csFigure)
        data = np.load(csFigure, allow_pickle=True).item()

        coFigures.append(fig)
        coAxes.append(ax)
        coDataObjects.append(data)

    # Determine overall x and y limits
    fOverallLowerLimit_X = float('inf')
    fOverallUpperLimit_X = float('-inf')

    fOverallLowerLimit_Y = float('inf')
    fOverallUpperLimit_Y = float('-inf')

    for data in coDataObjects:
        for line_data in data['lines']:
            x_data = line_data['x']
            y_data = line_data['y']

            fOverallLowerLimit_X = max(fOverallLowerLimit_X, np.min(x_data))
            fOverallUpperLimit_X = min(fOverallUpperLimit_X, np.max(x_data))

            fOverallLowerLimit_Y = min(fOverallLowerLimit_Y, np.min(y_data))
            fOverallUpperLimit_Y = max(fOverallUpperLimit_Y, np.max(y_data))

    # Create a new figure for the overlay
    fig_overlay = plt.figure()
    ax_overlay = fig_overlay.add_subplot(111)

    line_styles = ['-', '-.', '--', ':']
    csBaseColors = ['#e41a1c', '#4daf4a', '#984ea3', '#ff7f00', '#a65628', '#f781bf', '#999999']

    for iFigure, data in enumerate(coDataObjects):
        line_style = line_styles[min(iFigure, len(line_styles) - 1)]

        for i, line_data in enumerate(data['lines']):
            x_data = line_data['x']
            y_data = line_data['y']
            color = csBaseColors[i % len(csBaseColors)]

            ax_overlay.plot(
                x_data, y_data, linestyle=line_style, color=color, label=f"{csFigures[iFigure]} Line {i + 1}"
            )

    ax_overlay.set_xlim(fOverallLowerLimit_X, fOverallUpperLimit_X)
    ax_overlay.set_ylim(fOverallLowerLimit_Y, fOverallUpperLimit_Y)

    # Add legends if provided
    if csLegendEntries:
        ax_overlay.legend(csLegendEntries)

    plt.show()

# Example usage
if __name__ == "__main__":
    # Simulating saved figure data
    csFigures = ["figure1.npz", "figure2.npz"]

    # Generate and save example data for testing
    for i, file_name in enumerate(csFigures):
        x = np.linspace(0, 10, 100)
        y = np.sin(x + i)
        data = {'lines': [{'x': x, 'y': y}]}
        np.savez(file_name, **data)

    csLegendEntries = ["Figure 1", "Figure 2"]
    overlay_figures(csFigures, csLegendEntries)
