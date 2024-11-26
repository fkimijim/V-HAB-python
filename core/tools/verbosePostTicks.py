def verbose_post_ticks(oTimer):
    """
    Helper to make the post-tick boolean matrix human-readable.

    This function translates the 3-dimensional boolean array
    `mbPostTickControl`, which controls post-tick execution, into a more
    verbose dictionary where indexing with the post-tick group names and
    levels is possible. Each post-tick level only contains as many post ticks
    as are actually bound to it (unlike the array).

    Args:
        oTimer: An object that contains post-tick groups, levels, and control matrices.

    Returns:
        dict: A nested dictionary representing post-tick control in a human-readable format.
    """
    tbPostTickControl = {}

    for iGroup in range(len(oTimer.csPostTickGroups)):
        group_name = oTimer.csPostTickGroups[iGroup]
        csLevel = oTimer.tcsPostTickLevel[group_name]

        for iLevel in range(len(csLevel)):
            level_name = csLevel[iLevel]
            cxPostTicks = oTimer.txPostTicks[group_name][level_name]

            if cxPostTicks:
                mbControl = oTimer.cabPostTickControl[iGroup][iLevel]
            else:
                mbControl = []

            if group_name not in tbPostTickControl:
                tbPostTickControl[group_name] = {}

            tbPostTickControl[group_name][level_name] = mbControl

    return tbPostTickControl
