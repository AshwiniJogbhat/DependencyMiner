from typing import List
from fastapi import FastAPI, Request, File, UploadFile, Form, status, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
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

log_attributes = {}

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
    print(log_attributes)
    return templates.TemplateResponse("eventlog.html", {"request": request, 'list_of_eventlogs': eventLogs, 'eventlog_name':settings.EVENT_LOG_NAME, 'log_attributes': log_attributes, 'log':settings.EVENT_LOG})

# @app.get("/eventlog", response_class=HTMLResponse)
# async def eventLog(request: Request):
#     eventLogs = get_event_log()
#     return templates.TemplateResponse("eventlog.html", {"request": request, 'list_of_eventlogs': eventLogs, 'eventlog_name':settings.EVENT_LOG_NAME, 'log_attributes':log_attributes})


@app.post("/", response_class=HTMLResponse)
async def upload_log(request: Request, file: UploadFile = File(...)):
    eventlogs = upload_event_log(file)
    return templates.TemplateResponse('eventlog.html', {"request": request, 'list_of_eventlogs': eventlogs })

@app.post("/eventlog-form", response_class=HTMLResponse)
async def form_data(request: Request, list_of_logs: str = Form(default=None), action: str = Form(default=None)):
    eventlogs, attributes, log, tree = set_delete_download_eventlogs(list_of_logs, action)
    log_attributes = dict(attributes)
    settings.EVENT_LOG = log
    settings.PROCESS_TREE = tree
    return templates.TemplateResponse('eventlog.html', {'request': request, 'list_of_eventlogs': eventlogs, 'eventlog_name':settings.EVENT_LOG_NAME, 'log_attributes':log_attributes})

######## Process Tree Page ####################
@app.get("/processtree")
async def discover_tree(request:Request):
    #settings.PROCESS_TREE = discover_process_tree(settings.EVENT_LOG)
    process_tree_path = display_process_tree()
    return templates.TemplateResponse('process_tree.html', {"request": request, 'image_url': process_tree_path})


####### Petri Net Page ###############
@app.get("/petrinet")
async def discover_net(request: Request):
    settings.PETRI_NET, settings.I_MARKS, settings.F_MARKS = discover_petri_net(settings.PROCESS_TREE)
    net_path = display_petri_net()
    rules_dict, xor_tree = findAsociationRules()
    settings.RULES = rules_dict
    settings.XOR_TREES = xor_tree
    return templates.TemplateResponse('petrinet.html', {"request": request, 'image_url': net_path, 'eventlog_name':settings.EVENT_LOG_NAME, 'rules':settings.RULES, 'xor_trees':settings.XOR_TREES})
    
@app.post("/petrinet")
async def process_net(request:Request, support: str = Form(default=None), confidence: str = Form(default=None), lift: str = Form(default=None), soundCheckbox: str = Form(default=None)):
    net_path = repair_petri_net(support, confidence, lift, soundCheckbox)
    # response = RedirectResponse(url='/petrinet', status_code=status.HTTP_302_FOUND)
    # return response
    print(support)
    return templates.TemplateResponse('petrinet.html', {'request': request, 'eventlog_name':settings.EVENT_LOG_NAME, 'rules':settings.RULES, 'support':support, 'confidence':confidence, 'sound':soundCheckbox, 'lift':lift, 'image_url': net_path})
    
    

    
    
    
    
    
   
    
     


