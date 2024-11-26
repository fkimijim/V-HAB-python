class Plot:
    """
    Container for all information relating to a single plot.
    This class defines objects that store information regarding individual
    plots in a figure. Most importantly, they contain the `tPlotOptions`
    property, which can be modified directly by the user, influencing the
    appearance of plots even after creation.
    """

    def __init__(self, sTitle, aiIndexes, tPlotOptions=None):
        """
        Constructor method

        Parameters:
        sTitle (str): A string containing the plot title.
        aiIndexes (list of int): An array of integers containing the indexes
                                 of all plotted items in the log array.
        tPlotOptions (dict, optional): A dictionary containing plot options.
        """
        self.sTitle = sTitle  # A string containing the plot title
        self.aiIndexes = aiIndexes  # An array of integers for plot item indexes

        # tPlotOptions contains settings related to the plot's appearance.
        # If not provided, initialize it as an empty dictionary.
        self.tPlotOptions = tPlotOptions if tPlotOptions is not None else {}

# Example usage
if __name__ == "__main__":
    # Example indexes and plot options
    example_indexes = [1, 2, 3]
    plot_options = {
        "sTimeUnit": "seconds",
        "bLegend": True,
        "tLineOptions": {
            "lineStyle": "--",
            "color": "blue",
            "marker": "o"
        },
        "csUnitOverride": [["left_unit"], ["right_unit"]]
    }

    # Create a Plot instance
    my_plot = Plot("MyPlotTitle", example_indexes, plot_options)

    # Access attributes
    print("Plot Title:", my_plot.sTitle)
    print("Indexes:", my_plot.aiIndexes)
    print("Plot Options:", my_plot.tPlotOptions)
