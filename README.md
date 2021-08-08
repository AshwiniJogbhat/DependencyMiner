# Creating Precise Models by Discovering Long-term Dependencies in Process Trees

Given a log path and set of parameters, the dependency_miner algorithm is responsible for discovering long-term dependencies between the events and results into a precise Petri net by repairing the free-choice Petri net which includes the discovered rules. Added set of rules and computed evaluation metrics are returned.

## Requirements
- Windows 10/WS2016/WS2019
- [PM4Py](https://pm4py.fit.fraunhofer.de/) 2.2.8
  - $ pip install pm4py=2.2.8
- [FastAPI](https://fastapi.tiangolo.com/tutorial/) 0.63.0 
- In a virtual environment, FastAPI can be downloaded as  
   - $pip install fastapi 
   - $pip install uvicorn 


## Installation Instruction
- Check out the source code using git: git clone https://github.com/AshwiniJogbhat/DependencyMiner.git
- Execute the following command: git init
- Install Requirements: $pip install -r requirement.txt
- Check for two folders PetriNet and ProcessTrees in <path>\DependencyMiner\static
- If not exists, create one with the same name
### 

## Run the code base
- uvicorn main:app --reload
- web application starts at http://127.0.0.1:8000

## Long-term dependency miner
1. Upload event log and set the event log
2. Petri net can be viewed in Petri net view page
3. Process tree can be viewed in Process tree view page

The generated Petri net and Process trees are saved in 
- <path>\DependencyMiner\static\PetriNet
- <path>\DependencyMiner\static\ProcessTrees

