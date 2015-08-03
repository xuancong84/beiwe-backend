def checkbox_to_boolean(list_checkbox_params, dict_all_params):
    """ Takes a list of strings that are to be processed as checkboxes on a post
        parameter, (checkboxes supply some arbitrary value in a post if they are
        checked, and no value at all if they are not checked.), and a dict of
        parameters and their values to update.
        returns a dictionary with modified/added values containing appropriate
        booleans."""
    for param in list_checkbox_params:
        if param not in dict_all_params:
            dict_all_params[param] = False
        else:
            dict_all_params[param] = True
    return dict_all_params


def string_to_int(list_int_params, dict_all_params):
    for key in list_int_params:
        dict_all_params[key] = int(dict_all_params[key])
    return dict_all_params


def combined_multi_dict_to_dict(cmd):
    """ converts an ImmutableMultiDict to a mutable python Dict. """
    return { key: value for key, value in cmd.items() }