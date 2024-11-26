from colorama import Fore, Back, Style, init

# Initialize colorama for styled console output
init(autoreset=True)

def cprintf(style, format_string, *args):
    """
    Displays styled formatted text in the terminal.

    Parameters:
        style (str or tuple): The style or RGB tuple for the text.
                              Predefined styles include:
                              'Text', 'Keywords', 'Comments', 'Strings', 'Errors', etc.
                              Additional options:
                              - Prefix with '-' or '_' for underline.
                              - Prefix with '*' for bold.
        format_string (str): The format string for text output.
        *args: Additional arguments for text formatting.
    Returns:
        int: The number of characters written.
    """
    # Mapping predefined styles to colorama attributes
    styles = {
        "text": Fore.RESET,
        "keywords": Fore.BLUE,
        "comments": Fore.GREEN,
        "strings": Fore.MAGENTA,
        "errors": Fore.RED,
        "hyperlinks": Style.UNDERLINE + Fore.BLUE,
        "black": Fore.BLACK,
        "cyan": Fore.CYAN,
        "magenta": Fore.MAGENTA,
        "blue": Fore.BLUE,
        "green": Fore.GREEN,
        "red": Fore.RED,
        "yellow": Fore.YELLOW,
        "white": Fore.WHITE,
    }

    underline_flag = False
    bold_flag = False

    # Process style for underline and bold
    if isinstance(style, str):
        if style.startswith("-") or style.startswith("_"):
            underline_flag = True
            style = style[1:]
        if style.startswith("*"):
            bold_flag = True
            style = style[1:]

    # Determine the selected style
    selected_style = styles.get(style.lower(), Fore.RESET)

    # Apply underline and bold flags
    if underline_flag:
        selected_style = Style.UNDERLINE + selected_style
    if bold_flag:
        selected_style = Style.BRIGHT + selected_style

    # Format the string with the provided arguments
    formatted_string = format_string.format(*args)

    # Print the styled string
    styled_string = selected_style + formatted_string
    print(styled_string, end="")  # Avoid extra newline

    return len(styled_string)

# Example usage
if __name__ == "__main__":
    cprintf('text', 'This is regular text.\n')
    cprintf('keywords', 'This is a keyword.\n')
    cprintf('comments', 'This is a comment.\n')
    cprintf('strings', 'This is a string.\n')
    cprintf('errors', 'This is an error.\n')
    cprintf('-blue', 'This is underlined blue text.\n')
    cprintf('*green', 'This is bold green text.\n')
    cprintf('*-magenta', 'This is bold and underlined magenta text.\n')
