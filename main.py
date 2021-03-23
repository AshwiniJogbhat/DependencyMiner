from typing import List
from fastapi import FastAPI, Request, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
import shutil

import os
from os import listdir
from os.path import isfile, join

import settings
from Miner.disocvery import import_event_log, to_Petrinet, to_Processtree

settings.init()
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

log_attributes = {}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})

@app.get("/eventlog", response_class=HTMLResponse)
async def eventLog(request: Request):
    eventlogs = [f for f in listdir(settings.EVENT_LOGS_PATH) if isfile(join(settings.EVENT_LOGS_PATH, f))]
    return templates.TemplateResponse("eventlog.html", {"request": request, 'list_of_eventlogs': eventlogs, 'eventlog_name':settings.EVENT_LOG_NAME, 'log_attributes':log_attributes})


@app.post("/eventlog", response_class=HTMLResponse)
async def upload_log(request: Request,file: UploadFile = File(...)):
    upload_folder = open(os.path.join(settings.EVENT_LOGS_PATH, file.filename), 'wb+')
    file_object = file.file
    shutil.copyfileobj(file_object, upload_folder)
    upload_folder.close()
    eventlogs = [f for f in listdir(settings.EVENT_LOGS_PATH) if isfile(join(settings.EVENT_LOGS_PATH, f))]
    return templates.TemplateResponse('eventlog.html', {"request": request, 'list_of_eventlogs': eventlogs })

@app.post("/eventLog", response_class=HTMLResponse)
async def form_data(request: Request, list_of_logs: str = Form(default=None), action: str = Form(default=None)):
    if action == "Set":
        filename = list_of_logs
        settings.EVENT_LOG_NAME = filename
        file_path = os.path.join(settings.EVENT_LOGS_PATH, filename) 
        settings.EVENT_LOG_PATH = file_path
        log = import_event_log(file_path)
        settings.EVENT_LOG = log
        no_traces = len(log)
        no_events = sum([len(trace) for trace in log])
        log_attributes['no_traces'] = no_traces
        log_attributes['no_events'] = no_events
        eventlogs = [f for f in listdir(settings.EVENT_LOGS_PATH) if isfile(join(settings.EVENT_LOGS_PATH, f))]
        return templates.TemplateResponse('eventlog.html', {'request': request, 'list_of_eventlogs': eventlogs, 'eventlog_name':settings.EVENT_LOG_NAME, 'log_attributes':log_attributes})
    if action == "Deleted":
        print(list_of_logs)
        # delete the event log and update the table
    if action == "Download":
        # download corresponding event log
        print(list_of_logs)

@app.get("/petrinet")
async def discover_net(request: Request):
    net_path = to_Petrinet(settings.EVENT_LOG_NAME)
    return templates.TemplateResponse('petrinet.html', {"request": request, 'image_url': net_path})

@app.get("/processtree")
async def discover_tree(request:Request):
    process_tree_path = to_Processtree()
    return templates.TemplateResponse('process_tree.html', {"request": request, 'image_url': process_tree_path})
    
    
    
    
    
    
    
   
    
     


