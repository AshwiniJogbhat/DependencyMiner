# We have all global vars here:

def init():
    global EVENT_LOG_NAME
    EVENT_LOG_NAME = ""

    global EVENT_LOG
    EVENT_LOG = None
    
    global EVENT_LOGS_PATH
    EVENT_LOGS_PATH = ("./static/EventLogs/")
    
    global NET_PATH
    NET_PATH = "./static/PetriNet/"
    
    global TREE_PATH
    TREE_PATH = "./static/ProcessTrees/"
    
    global candidates
    candidates = {}
    
    global parent
    parent = []
