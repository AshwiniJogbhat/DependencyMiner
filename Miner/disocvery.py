from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.visualization.process_tree import visualizer as pt_visualizer
from pm4py.visualization.petrinet import visualizer as pn_visualizer
from Miner.helpers import get_candidates, findDependencyValue, final_candidates
import settings
import os
import main

# The main functions are here......


def import_event_log(log_path):
    EVENT_LOG = xes_importer.apply(log_path)
    return EVENT_LOG

def to_Petrinet(log_name):
    net, initial_marking, final_marking = inductive_miner.apply(settings.EVENT_LOG)
    parameters = {pn_visualizer.Variants.WO_DECORATION.value.Parameters.FORMAT: "PNG"}
    gviz = pn_visualizer.apply(net, initial_marking, final_marking, parameters=parameters)
    image_path = os.path.join(settings.NET_PATH, f"{settings.EVENT_LOG_NAME}.PNG")
    pn_visualizer.save(gviz, image_path)
    return image_path

def to_Processtree():
    tree = inductive_miner.apply_tree(settings.EVENT_LOG)
    parameters = {pt_visualizer.Variants.WO_DECORATION.value.Parameters.FORMAT: "PNG"}
    gviz = pt_visualizer.apply(tree, parameters=parameters)
    tree_path = os.path.join(settings.TREE_PATH, f"{settings.EVENT_LOG_NAME}.PNG")
    pt_visualizer.save(gviz, tree_path)
    return tree_path

def to_PNG(graph):
    gviz = pt_visualizer.apply(graph)
    pt_visualizer.view(gviz)

def discover_dependency_value(tree):
    xor_pairs = get_xor_pairs(tree)
    support, confidence, lift = findDependencyValue(xor_pairs)
    print("Yet to write")

def discover_petrinet(net, sup_val=0.5, conf_val=0.5, lift_val=1):
    print("Discover")
    
    png_path = to_PNG(net)

# def get_rules(sup_th, conf_th, net):
#     global i 
#     for val,key in enumerate(confidence.keys()) :
#         if key in xor_pairs:
#             print(conf_th, sup_th)
#             if lift[key] > 1 and confidence[key] >= conf_th and support[key] >= sup_th:
#                 # add place in petrinet


def get_xor_pairs(tree):
    root = tree._get_root()
    parent.insert(0,root)

    # get the XOR candidate tree for implicit dependency calculations
    candidates = get_candidates(tree)
    #print(candidates)

    xor_list = []

    # Find LCA, for Sequence LCA, find combinations
    for idx,key in enumerate(candidates.keys()) :
        for idx2 in range(idx+1,len(list(candidates.keys()))) :
            #print("Node1", key)
            #print("Node2", list(candidates.keys())[idx2])
            xor_list.append(final_candidates(key,list(candidates.keys())[idx2]))

    xor_pairs = [item for sublist in xor_list for item in sublist]
    return xor_pairs
