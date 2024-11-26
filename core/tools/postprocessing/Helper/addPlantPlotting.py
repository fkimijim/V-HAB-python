def addPlantPlotting(oPlotter, tPlotOptions, oSetup):
    """
    Adds plant-related plots to the plotter.

    Args:
        oPlotter: Plotter object to define and manage plots.
        tPlotOptions: Dictionary of plot options.
        oSetup: Setup object containing logging indexes for plants.
    """

    # Define plots for biomass
    coPlotBiomasses = [
        [oPlotter.definePlot(oSetup["tiLogIndexes"]["Plants"]["Biomass"], "Current Biomass", tPlotOptions),
         oPlotter.definePlot(oSetup["tiLogIndexes"]["Plants"]["EdibleBiomassCum"], "Cumulative Edible Biomass", tPlotOptions),
         oPlotter.definePlot(oSetup["tiLogIndexes"]["Plants"]["InedibleBiomassCum"], "Cumulative Inedible Biomass", tPlotOptions)],
        [oPlotter.definePlot(oSetup["tiLogIndexes"]["Plants"]["EdibleBiomass"], "Current Edible Biomass", tPlotOptions),
         oPlotter.definePlot(oSetup["tiLogIndexes"]["Plants"]["EdibleGrowthRate"], "Current Edible Growth Rate", tPlotOptions),
         oPlotter.definePlot(oSetup["tiLogIndexes"]["Plants"]["InedibleGrowthRate"], "Current Inedible Growth Rate", tPlotOptions)]
    ]

    # Define plots for exchange rates
    coPlotExchange = [
        [oPlotter.definePlot(oSetup["tiLogIndexes"]["Plants"]["WaterUptakeRate"], "Current Water Uptake", tPlotOptions),
         oPlotter.definePlot(oSetup["tiLogIndexes"]["Plants"]["TranspirationRate"], "Current Transpiration", tPlotOptions),
         oPlotter.definePlot(oSetup["tiLogIndexes"]["Plants"]["OxygenRate"], "Current Oxygen Production", tPlotOptions),
         oPlotter.definePlot(oSetup["tiLogIndexes"]["Plants"]["CO2Rate"], "Current CO_2 Consumption", tPlotOptions)],
        [oPlotter.definePlot(oSetup["tiLogIndexes"]["Plants"]["WaterUptake"], "Cumulative Water Uptake", tPlotOptions),
         oPlotter.definePlot(oSetup["tiLogIndexes"]["Plants"]["Transpiration"], "Cumulative Transpiration", tPlotOptions),
         oPlotter.definePlot(oSetup["tiLogIndexes"]["Plants"]["Oxygen"], "Cumulative Oxygen", tPlotOptions),
         oPlotter.definePlot(oSetup["tiLogIndexes"]["Plants"]["CO2"], "Cumulative CO_2", tPlotOptions)]
    ]

    # Define plots for nutrients
    coPlotNutrients = [
        [oPlotter.definePlot(oSetup["tiLogIndexes"]["Plants"]["NitrateStorageRate"], "Current Storage Nitrate Uptake", tPlotOptions),
         oPlotter.definePlot(oSetup["tiLogIndexes"]["Plants"]["NitrateStructureRate"], "Current Structure Nitrate Uptake", tPlotOptions),
         oPlotter.definePlot(oSetup["tiLogIndexes"]["Plants"]["NitrateEdibleRate"], "Current Edible Nitrate Uptake", tPlotOptions)],
        [oPlotter.definePlot(oSetup["tiLogIndexes"]["Plants"]["NitrateStorage"], "Cumulative Storage Nitrate", tPlotOptions),
         oPlotter.definePlot(oSetup["tiLogIndexes"]["Plants"]["Nitratestructure"], "Cumulative Structure Nitrate", tPlotOptions),
         oPlotter.definePlot(oSetup["tiLogIndexes"]["Plants"]["NitrateEdible"], "Cumulative Edible Nitrate", tPlotOptions)]
    ]

    # Define figures for each group of plots
    oPlotter.defineFigure(coPlotBiomasses, "Plant Biomass")
    oPlotter.defineFigure(coPlotExchange, "Plant Exchange Rates")
    oPlotter.defineFigure(coPlotNutrients, "Plant Nutrients")
