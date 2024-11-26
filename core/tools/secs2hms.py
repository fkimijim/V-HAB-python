def secs2hms(fSeconds):
    """
    Converts a time in seconds to a string giving the time in hours, minutes, and seconds.
    
    Args:
        fSeconds (float): The time in seconds to be converted.
        
    Returns:
        str: A string representation of the time in hours, minutes, and seconds.
    
    Examples:
        >>> secs2hms(7261)
        '2 hours, 1 min, 1.0 secs'
        
        >>> import time
        >>> start = time.time(); time.sleep(61); print(f"Program took {secs2hms(time.time() - start)}")
        'Program took 1 min, 1.0 secs'
    """
    # Initializing the return variable
    sString = ""
    
    # Initializing variables for the number of hours and minutes
    iHours = 0
    iMins = 0

    # Get the number of hours, if the duration is longer than one
    if fSeconds >= 3600:
        iHours = int(fSeconds // 3600)
        
        # Setting the hour string to the correct singular and plural
        if iHours > 1:
            sHourString = " hours, "
        else:
            sHourString = " hour, "
        
        # Concatenating the number and unit
        sString += f"{iHours}{sHourString}"

    # Get the number of minutes, if the duration is longer than one
    if fSeconds >= 60:
        iMins = int((fSeconds - 3600 * iHours) // 60)
        
        # Setting the minute string to the correct singular and plural
        if iMins > 1:
            sMinuteString = " mins, "
        else:
            sMinuteString = " min, "
        
        # Concatenating the number and unit with the string already containing the hours.
        sString += f"{iMins}{sMinuteString}"

    # The number of seconds is calculated via subtraction
    iSeconds = fSeconds - 3600 * iHours - 60 * iMins

    # And finally, we can add the seconds string to the end of our return variable.
    sString += f"{iSeconds:.1f} secs"

    return sString
