import traceback

def log_error(e, message=None):
    """ Prints in the server logs (defaults to Apache if not specified) """
    try:
        print("-------------------")
        if message is not None: print(message)
        print("ERROR: " + str(e.__repr__()))
        print(traceback.format_exc())
        print("-------------------")
    except: print("ERROR IN log_error")


# TODO: Find places where this should be used.