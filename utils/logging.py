import traceback

def log_error(e, message=None):
    try:
        print("-------------------")
        if message is not None: print(message)
        print("ERROR: " + str(e.__repr__()))
        print(traceback.format_exc())
        print("-------------------")
    except: print("ERROR IN log_error")
