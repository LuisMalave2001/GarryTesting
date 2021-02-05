"""
Created on Jan 28, 2020

@author: LuisMora
"""

def format_name(first_name, middle_name, last_name):

    first_name = first_name if first_name else ""
    middle_name = middle_name if middle_name else ""
    last_name = last_name if last_name else ""

    return f"{last_name} {first_name} {middle_name}"