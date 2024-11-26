class Figure:
    """
    Container for all information relating to a single figure.
    This class defines objects that store information regarding individual
    figure objects. Most importantly, they contain the `tFigureOptions`
    property, which can be changed directly by the user, influencing the
    appearance of figures even after they have been created.
    """

    def __init__(self, sName, coPlots, tFigureOptions=None):
        """
        Constructor method

        Parameters:
        sName (str): A string containing the figure's name.
        coPlots (list): A list of objects containing plot objects.
        tFigureOptions (dict, optional): A dictionary containing figure options.
        """
        self.sName = sName  # A string containing the figure's name
        self.coPlots = coPlots  # A list of objects containing plot objects

        # tFigureOptions contains settings related to the figure's appearance.
        # If not provided, initialize it as an empty dictionary.
        self.tFigureOptions = tFigureOptions if tFigureOptions is not None else {}

# Example usage
if __name__ == "__main__":
    # Example plot objects (can be any object related to plotting)
    example_plots = ["plot1", "plot2"]

    # Example figure options
    figure_options = {
        "bPlotTools": True,
        "bTimePlot": False
    }

    # Create a Figure instance
    my_figure = Figure("MyFigure", example_plots, figure_options)

    # Access attributes
    print("Figure Name:", my_figure.sName)
    print("Plots:", my_figure.coPlots)
    print("Figure Options:", my_figure.tFigureOptions)
