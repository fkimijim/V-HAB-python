def add_crew_plotting(o_plotter, o_system, t_plot_options):
    """
    Adds crew-related plots to the plotter.

    Args:
        o_plotter: Plotter object for creating plots.
        o_system: System object containing crew member data.
        t_plot_options: Plot options for configuring the plots.
    """
    # Create list for Respiratory Coefficient plots
    cs_respiratory_coefficient = [f'"Respiratory Coefficient {i_human}"' for i_human in range(1, o_system.i_crew_members + 1)]

    # Initialize plot configuration
    co_plot = []

    # Define plots
    co_plot.append([
        o_plotter.define_plot(['"Effective CO_2 Flow Crew"', '"Effective O_2 Flow Crew"'], 'Crew Respiration Flowrates', t_plot_options),
        o_plotter.define_plot(cs_respiratory_coefficient, 'Crew Respiratory Coefficients', t_plot_options)
    ])
    co_plot.append([
        o_plotter.define_plot(['"Exhaled CO_2"', '"Inhaled O_2"'], 'Crew Cumulative Respiration', t_plot_options),
        o_plotter.define_plot(['"Respiration Water"', '"Perspiration Water"', '"Metabolism Water"', '"Urine Urea"'], 'Crew Cumulative Masses', t_plot_options)
    ])

    # Define the figure with the created plots
    o_plotter.define_figure(co_plot, 'Crew Values')
