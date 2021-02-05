# -*- coding: utf-8 -*-

def switch_statement(cases, value):
    """ Simulate a swithc statement """
    return cases[value] if value in cases else cases["default"] if "default" in cases else False


def extract_value_from_dict(parameter: str, values: dict):
    """ Extract a value from values dict
    Args:
        parameter (str): What we want to extract
        values(dict): Where we want to extract
    Return:
        values[parameter] if is in values, if not return False        
    """
    return values[parameter] if parameter in values else False