import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

def combine_figures(chFigures, tOptionalInputs=None):
    """
    Combines separate matplotlib figures into one figure with subplots.

    Parameters:
    chFigures: list
        List of matplotlib figure objects.
    tOptionalInputs: dict, optional
        Dictionary containing optional inputs:
            - sName: Name of the new combined figure.
            - sPositioning: 'column' or 'row' for subplot arrangement.
            - miSubPlots: Tuple of (rows, cols) for subplot grid.
            - bOnlyOneLegend: If True, only the legend from the first figure is used.
            - bAddEmptySpace: If True, an empty subplot is added for custom use.
    Returns:
    hCombinedFigure: matplotlib.figure.Figure
        The combined figure object.
    """
    if tOptionalInputs is None:
        tOptionalInputs = {}

    # Use the name of the first figure if no name is specified
    sName = tOptionalInputs.get('sName', chFigures[0].get_label())
    hCombinedFigure = plt.figure(figsize=(12, 8), num=sName)

    # Determine subplot positioning
    sPositioning = tOptionalInputs.get('sPositioning', 'column')
    miSubPlots = tOptionalInputs.get('miSubPlots', None)
    bAddEmptySpace = tOptionalInputs.get('bAddEmptySpace', False)
    bOnlyOneLegend = tOptionalInputs.get('bOnlyOneLegend', False)

    # Collect subplot information
    iFigures = len(chFigures)
    chSubplots = [fig.get_axes() for fig in chFigures]
    miSubplots = [len(subplots) for subplots in chSubplots]
    iMaxSubplots = max(miSubplots)
    
    if bAddEmptySpace:
        iFiguresForSubplots = iFigures + 1
    else:
        iFiguresForSubplots = iFigures

    # Determine grid dimensions
    if miSubPlots:
        rows, cols = miSubPlots
    elif sPositioning == 'column':
        rows, cols = iFiguresForSubplots, iMaxSubplots
    else:  # 'row'
        rows, cols = iMaxSubplots, iFiguresForSubplots

    gs = GridSpec(rows, cols, figure=hCombinedFigure)

    # Combine subplots
    for iFigure, subplots in enumerate(chSubplots):
        for iSubplot, subplot in enumerate(subplots):
            # Add subplot to combined figure
            if sPositioning == 'column':
                position = (iFigure, iSubplot)
            else:
                position = (iSubplot, iFigure)
            ax = hCombinedFigure.add_subplot(gs[position])
            
            # Copy content from the original subplot
            for line in subplot.get_lines():
                ax.plot(line.get_xdata(), line.get_ydata(), label=line.get_label())

            # Set labels, title, and grid
            ax.set_xlabel(subplot.get_xlabel())
            ax.set_ylabel(subplot.get_ylabel())
            ax.set_title(subplot.get_title())
            ax.grid(True)

            # Rescale or recolor if specified
            if 'mrRescalePlots' in tOptionalInputs:
                ax.set_position([p * s for p, s in zip(ax.get_position().bounds, tOptionalInputs['mrRescalePlots'])])
            if 'mrLineColors' in tOptionalInputs:
                for line, color in zip(ax.get_lines(), tOptionalInputs['mrLineColors']):
                    line.set_color(color)

            # Add legend
            if not bOnlyOneLegend or (bOnlyOneLegend and iFigure == 0):
                ax.legend()

    return hCombinedFigure
