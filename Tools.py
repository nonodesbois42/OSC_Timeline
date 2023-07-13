import sys
import os
import re


def absolute_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller
    This function allows the .exe of the program to run properly
    """
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def create_css_absolute_path(css_file_path):
    """
    Replace all paths in the css file by the absolute path
    This function allows the .exe of the program to run properly
    """
    with open(css_file_path, "r") as file:
        css_content = file.read()

    # Define the regular expression pattern to match the url() function and its path
    pattern = r"url\((.*?)\)"

    # Find all matches of the pattern in the CSS content
    matches = re.findall(pattern, css_content)

    # Iterate over the matches and modify the paths
    for path in matches:
        new_path = absolute_path(path)
        new_path = new_path.replace("\\", "/")
        css_content = css_content.replace(path, new_path)

    return css_content
