from typing import List
from fastapi import FastAPI, Request, File, UploadFile, Form, status, Response, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
# from starlette.responses import RedirectResponse
from wsgiref.util import FileWrapper


import os


import settings
from Miner.eventLog import *
#from Miner.disocvery import import_event_log, to_Petrinet, to_Processtree, discover_dependency_values
from Miner.discoverModel import *

settings.init()
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


# @app.get("/", response_class=HTMLResponse)
# async def index(request: Request):
#     file_path = os.path.join(settings.EVENT_LOGS_PATH, 'EventLog.xes') 
#     settings.EVENT_LOG_PATH = file_path
#     log = import_event_log(file_path)
#     settings.EVENT_LOG = log
#     return templates.TemplateResponse("base.html", {"request": request})

@app.get("/", response_class=HTMLResponse)
async def eventLog(request: Request):
    eventLogs = get_event_log()
    return templates.TemplateResponse("eventlog.html", {"request": request, 'list_of_eventlogs': eventLogs, 'eventlog_name':settings.EVENT_LOG_NAME, 'log_attributes': log_attributes, 'log':settings.EVENT_LOG})

# @app.get("/eventlog", response_class=HTMLResponse)
# async def eventLog(request: Request):
#     eventLogs = get_event_log()
#     return templates.TemplateResponse("eventlog.html", {"request": request, 'list_of_eventlogs': eventLogs, 'eventlog_name':settings.EVENT_LOG_NAME, 'log_attributes':log_attributes})


@app.post("/", response_class=HTMLResponse)
async def upload_log(request: Request, file: UploadFile = File(...)):
    eventlogs = upload_event_log(file)
    return templates.TemplateResponse('eventlog.html', {"request": request, 'list_of_eventlogs': eventlogs })

@app.post("/eventlog", response_class=HTMLResponse)
async def form_data(request: Request, list_of_logs: str = Form(default=None), action: str = Form(default=None)):
    if action == "Set":
        eventlogs, attributes, log, tree, net, im, fm = set_event_log(list_of_logs)
        log_attributes = dict(attributes)
        settings.EVENT_LOG = log
        
    if action == "Delete":
        eventlogs, log_attributes = delete_event_log(list_of_logs)
        
    return templates.TemplateResponse('eventlog.html', {'request': request, 'list_of_eventlogs': eventlogs, 'eventlog_name':settings.EVENT_LOG_NAME, 'log_attributes':log_attributes})

######## Process Tree Page ####################
@app.get("/processtree")
async def discover_tree(request:Request):
    process_tree_path = display_process_tree()
    #rules_dicts, xor_tree = findAsociationRules()
    #settings.RULES_DICT = copy.deepcopy(rules_dicts)
    #settings.XOR_TREES = copy.deepcopy(xor_tree)
    
    return templates.TemplateResponse('process_tree.html', {"request": request, 'image_url': process_tree_path, 'rules': settings.RULES_DICT, 'xor_tree': settings.XOR_TREES})


####### Petri Net Page ###############
@app.get("/petrinet")
async def discover_net(request: Request):
    net_path = display_petri_net()
    fitness = get_fitness(settings.PETRI_NET, settings.I_MARKS_ORIG, settings.F_MARKS_ORIG)
    precision = get_precision(settings.PETRI_NET, settings.I_MARKS_ORIG, settings.F_MARKS_ORIG)
    # rules_dict = {}
    # xor_tree = []
    #rules_dicts, xor_tree = findAsociationRules()
    #settings.RULES_DICT = rules_dicts
    #settings.XOR_TREES = xor_tree
    pnml_path = export_pnml()
    return templates.TemplateResponse('petrinet.html', {"request": request, 'image_url': net_path, 'pnml_path': pnml_path, 'eventlog_name':settings.EVENT_LOG_NAME, 'rules':settings.RULES_DICT, 'fitness': round(fitness['average_trace_fitness'], 2), 'precision':round(precision,2), 'xor_trees':settings.XOR_TREES, 'Rules': settings.RULES})
    
@app.post("/petrinet")
async def process_net(request:Request, support: str = Form(default=None), confidence: str = Form(default=None), lift: str = Form(default=None), soundCheckbox: str = Form(default=None)):
    net_path, precision, fitness, rules = repair_petri_net(support, confidence, lift, soundCheckbox)
    return templates.TemplateResponse('petrinet.html', {'request': request, 'eventlog_name':settings.EVENT_LOG_NAME, 'rules':settings.RULES_DICT, 'support':support, 'confidence':confidence, 'soundCheckbox':soundCheckbox, 'lift':lift, 'image_url': net_path, 'fitness':fitness, 'precision':precision, 'Rules': rules})
    
    


    
    
    
    
    
   
    
     


