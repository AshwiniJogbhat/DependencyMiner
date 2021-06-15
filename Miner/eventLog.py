from pm4py.objects.log.importer.xes import importer as xes_importer
import os
from os import listdir
from os.path import isfile, join
import shutil
import settings
from Miner.discoverModel import discover_process_tree, discover_petri_net
from Miner.discoverModel import findAsociationRules

def import_event_log(log_path):
    EVENT_LOG = xes_importer.apply(log_path)
    return EVENT_LOG

def get_event_log():
    return [f for f in listdir(settings.EVENT_LOGS_PATH) if isfile(join(settings.EVENT_LOGS_PATH, f))]

def upload_event_log(file):
    upload_folder = open(os.path.join(settings.EVENT_LOGS_PATH, file.filename), 'wb+')
    file_object = file.file
    shutil.copyfileobj(file_object, upload_folder)
    upload_folder.close()
    eventlogs = [f for f in listdir(settings.EVENT_LOGS_PATH) if isfile(join(settings.EVENT_LOGS_PATH, f))]
    return eventlogs

def set_delete_download_eventlogs(log_list, action):
    log_attributes = {}
    if action == "Set":
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
        
        # discover Tree
        tree = discover_process_tree(log)
        
        eventlogs = [f for f in listdir(settings.EVENT_LOGS_PATH) if isfile(join(settings.EVENT_LOGS_PATH, f))]
        
    if action == "Delete":
        filename = log_list
        if settings.EVENT_LOG_NAME == filename:
            settings.EVENT_LOG_NAME = ":notset:"
        eventlogs = [f for f in listdir(settings.EVENT_LOGS_PATH) if isfile(join(settings.EVENT_LOGS_PATH, f))]
        eventlogs.remove(filename)
        file_dir = os.path.join(settings.EVENT_LOGS_PATH, filename)
        os.remove(file_dir)
    if action == "Download":
        # download corresponding event log
        filename = log_list
    
    return eventlogs, log_attributes, log, tree
    