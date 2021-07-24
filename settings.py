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
    
    global PNML_PATH 
    
    global TREE_PATH
    TREE_PATH = "./static/ProcessTrees/"
    
    global PROCESS_TREE
    PROCESS_TREE = None
    
    global PETRI_NET
    global I_MARKS
    global F_MARKS
    global PRECISE_NET
    PETRI_NET = None 
    I_MARKS = None
    F_MARKS = None
    PRECISE_NET = None
    
    global sink_dict
    global src_dict
    sink_dict = {}
    src_dict = {}
    
    global RULES_DICT
    global XOR_TREES
    global RULES
    RULES_DICT = {}
    XOR_TREES = {}
    RULES = {}
    
    global PETRI_NET_ORIG
    global I_MARKS_ORIG 
    global F_MARKS_ORIG
    PETRI_NET_ORIG = {}
    I_MARKS_ORIG = {}
    F_MARKS_ORIG = {}
    
    global PRECISION
    global FITNESS
    PRECISION = None
    FITNESS = None