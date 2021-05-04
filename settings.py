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
    
    global PROCESS_TREE
    PROCESS_TREE = None
    
    global candidates
    candidates = {}
    
    global xor_pairs
    xor_pairs = []
    
    global parent
    parent = []
    
    global count_dict
    count_dict = {}
    
    global sup_dict
    sup_dict = {}
    
    global conf 
    conf = {}

    global lift
    lift = {}
    
    global support
    support = {}
    
    global confidence
    confidence = {}
    
    global source
    source = set()
    
    global target
    target = set()
    
    global PETRI_NET
    global I_MARKS
    global F_MARKS
    PETRI_NET = None 
    I_MARKS = None
    F_MARKS = None