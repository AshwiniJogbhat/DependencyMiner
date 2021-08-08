from pm4py.objects.log.importer.xes import importer as xes_importer
import os
from os import listdir
from os.path import isfile, join
import shutil
import settings
from Miner.discoverModel import discover_process_tree, discover_petri_net
from Miner.discoverModel import findAsociationRules, export_pnml
import copy

log_attributes = {}
def import_event_log(log_path):
    """
    Given an event log, it improts and get the details for the log
    
    Parameter:
    log_path (str): Path of the log
    
    Returns:
    Event log (EventLog): Imported event log
    """
    EVENT_LOG = xes_importer.apply(log_path)
    return EVENT_LOG

def get_event_log():
    """
    Get all event logs uploaded to the tool
    
    Returns:
    list_of_logs (list): Imported event log list
    """
    return [f for f in listdir(settings.EVENT_LOGS_PATH) if isfile(join(settings.EVENT_LOGS_PATH, f))]

def upload_event_log(file):
    """
    Given a log file, it uploads the event log to the static/Event Log folder
    
    Parameter:
    log_file (file) : Event log file
    
    Returns:
    eventlogs (list): Uploaded event logs
    """
    upload_folder = open(os.path.join(settings.EVENT_LOGS_PATH, file.filename), 'wb+')
    file_object = file.file
    shutil.copyfileobj(file_object, upload_folder)
    upload_folder.close()
    eventlogs = [f for f in listdir(settings.EVENT_LOGS_PATH) if isfile(join(settings.EVENT_LOGS_PATH, f))]
    return eventlogs

def set_event_log(log_list):
    """
    Given an input event log, the function imports the log and returns discovered process tree 
    and petri net model along with the details of the log. 
    Parameters:
        file_path (str): Path of event log
        
    Returns:
        eventlogs (list): List of event logs
        log_attributes (dict): Details of the log
        log (EventLog) : Imported event log 
        tree (processtree): Discovered Process tree from the given event log
        net (PetriNet) : Discovered Petri net from the given event log
        im (Marking) : Initial marking of the generated Petri net
        fm (Marking) : Final marking of the generated Petri net
    """
    filename = log_list
    settings.EVENT_LOG_NAME = filename
    file_path = os.path.join(settings.EVENT_LOGS_PATH, filename) 
    settings.EVENT_LOG_PATH = file_path
    log = import_event_log(file_path)
    settings.EVENT_LOG = log
    no_traces = len(log)
    no_events = sum([len(trace) for trace in log])
    log_attributes['no_traces'] = no_traces
    log_attributes['no_events'] = no_events     
    
    #discover Tree
    tree = None
    tree = discover_process_tree(log)   
    
    #discover net
    net = None
    im = None
    fm = None
    settings.RULES_DICT = {}
    settings.RULES = {}
    settings.PRECISION = None
    settings.FITNESS = None
    net, im, fm = discover_petri_net(tree)
    
    
    pnml_path = export_pnml(net, im, fm)
    
    # disover rules
    rules_dict = {}
    xor_tree = []
    rules_dicts, xor_tree = findAsociationRules()
    settings.RULES_DICT = copy.deepcopy(rules_dicts)
    settings.XOR_TREES = copy.deepcopy(xor_tree)
    
    eventlogs = [f for f in listdir(settings.EVENT_LOGS_PATH) if isfile(join(settings.EVENT_LOGS_PATH, f))]
    return eventlogs, log_attributes, log, tree, net, im, fm
    
def delete_event_log(log_list): 
      
    filename = log_list
    if settings.EVENT_LOG_NAME == filename:
        settings.EVENT_LOG_NAME = ":notset:"
    eventlogs = [f for f in listdir(settings.EVENT_LOGS_PATH) if isfile(join(settings.EVENT_LOGS_PATH, f))]
    eventlogs.remove(filename)
    file_dir = os.path.join(settings.EVENT_LOGS_PATH, filename)
    os.remove(file_dir)
    log_attributes = {}
    return eventlogs, log_attributes
    