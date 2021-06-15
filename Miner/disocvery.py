from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.analysis import check_soundness
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.visualization.process_tree import visualizer as pt_visualizer
from pm4py.visualization.petrinet import visualizer as pn_visualizer
from pm4py.objects.petri import utils
from pm4py.objects.conversion.process_tree.variants.to_petri_net import clean_duplicate_transitions
from pm4py.objects.petri.petrinet import PetriNet, Marking
from pm4py.algo.evaluation.replay_fitness import evaluator as replay_fitness_evaluator
from pm4py.algo.evaluation.precision import evaluator as precision_evaluator
from Miner.helpers import *
import settings
import os
import main

# The main functions are here......

def import_event_log(log_path):
    EVENT_LOG = xes_importer.apply(log_path)
    return EVENT_LOG

def to_Petrinet(net, initial_marking, final_marking):
    parameters = {pn_visualizer.Variants.WO_DECORATION.value.Parameters.FORMAT: "PNG"}
    gviz = pn_visualizer.apply(net, initial_marking, final_marking, parameters=parameters)
    image_path = os.path.join(settings.NET_PATH, f"{settings.EVENT_LOG_NAME}.PNG")
    pn_visualizer.save(gviz, image_path)
    return image_path

def to_Processtree():
    parameters = {pt_visualizer.Variants.WO_DECORATION.value.Parameters.FORMAT: "PNG"}
    gviz = pt_visualizer.apply(settings.PROCESS_TREE, parameters=parameters)
    tree_path = os.path.join(settings.TREE_PATH, f"{settings.EVENT_LOG_NAME}.PNG")
    pt_visualizer.save(gviz, tree_path)
    return tree_path

def discover_processtree():
    tree = inductive_miner.apply_tree(settings.EVENT_LOG)
    settings.PROCESS_TREE = tree
    return tree

def discover_net():
    settings.PETRI_NET, settings.I_MARKS, settings.F_MARKS =  inductive_miner.apply(settings.EVENT_LOG)
    return settings.PETRI_NET, settings.I_MARKS, settings.F_MARKS
    
def to_PNG(graph):
    gviz = pt_visualizer.apply(graph)
    pt_visualizer.view(gviz)


def get_xor_pairs(tree):
    
    root = tree._get_root()
    parent = []
    xor_pairs = []
    parent.insert(0,root)
    settings.candidates = {}

    # get the XOR candidate tree for implicit dependency calculations
    settings.candidates = get_candidates_copy(tree, parent)
    #print(candidates)
    candidates = settings.candidates
    xor_list = []

    # Find LCA, for Sequence LCA, find combinations
    for idx,key in enumerate(candidates.keys()) :
        for idx2 in range(idx+1,len(list(candidates.keys()))) :
            #print("Node1", key)
            #print("Node2", list(candidates.keys())[idx2])
            xor_list.append(final_candidates(key,list(candidates.keys())[idx2]))

    xor_pairs = [item for sublist in xor_list for item in sublist]
    settings.xor_pairs = xor_pairs
    return xor_pairs

def discover_dependency_values():
    # apply inductive algorithm to discover tree
    tree = discover_processtree()
    
    # Discover corresponding petri net
    settings.PETRI_NET, settings.I_MARKS, settings.F_MARKS = discover_net()
    fitness = replay_fitness_evaluator.apply(settings.EVENT_LOG, settings.PETRI_NET, settings.I_MARKS, settings.F_MARKS, variant=replay_fitness_evaluator.Variants.TOKEN_BASED)
    prec = precision_evaluator.apply(settings.EVENT_LOG, settings.PETRI_NET, settings.I_MARKS, settings.F_MARKS, variant=precision_evaluator.Variants.ETCONFORMANCE_TOKEN)
    print("Fitness Before ", fitness)
    print("Precision Before", prec)
    print("Before Check Soundness", check_soundness(settings.PETRI_NET, settings.I_MARKS, settings.F_MARKS))
    # get XOR children pairs which will be candidate for implicit dependency
    xor_pairs = get_xor_pairs(tree)
    
    settings.support = {}
    settings.confidence = {}
    settings.lift = {}
    
    # Find Dependency Values for each xor_pairs
    settings.support, settings.confidence, settings.lift = findDependencyValue(xor_pairs)
    # settings.lift = dict(sorted(settings.lift.items(), key=lambda item: item[1], reverse=True))
    
    # settings.lift[list(settings.lift.keys())[1]] = 0.0
    # settings.lift[list(settings.lift.keys())[2]] = 2.0
    # settings.lift[list(settings.lift.keys())[2]] = 0.0
    # settings.lift[list(settings.lift.keys())[1]] = 0.0

    net_path = repair_petrinet(settings.PETRI_NET, xor_pairs)
    
    print("After Check Soundness", check_soundness(settings.PETRI_NET, settings.I_MARKS, settings.F_MARKS))
    
    print("Support", settings.support)
    print("Confidence", settings.confidence)
    print("Lift", settings.lift)
    
    return net_path

# Main algorithm or function
# First, it adds control places to all source and target XOR children pair.
# then it calls for adding dependency to petri net 
def repair_petrinet(net, pairs, lift_val = 2, conf_val = 0.8, sup_val=0):

    net = add_control_places(net, pairs)
    net = add_dependency(pairs, net)  
    settings.PETRI_NET = net
    
    # calculate fitness and precision of the net
    fitness = replay_fitness_evaluator.apply(settings.EVENT_LOG, net, settings.I_MARKS, settings.F_MARKS, variant=replay_fitness_evaluator.Variants.TOKEN_BASED)
    prec = precision_evaluator.apply(settings.EVENT_LOG, net, settings.I_MARKS, settings.F_MARKS, variant=precision_evaluator.Variants.ETCONFORMANCE_TOKEN)
    print("Fitness", fitness)
    print("Precision", prec)
    
    net_path = to_Petrinet(settings.PETRI_NET, settings.I_MARKS, settings.F_MARKS)
    return net_path
    
   
def add_dependency(pairs, net, threshold_up=False, lift_val = 2, conf_val = 0.4, sup_val=0.2 ):
    for pair in pairs:
        # create tau transition for that pair
        tau_t = PetriNet.Transition(f"tau_{pair[0]}{pair[1]}", None)
        # check threshold values
        if (settings.lift[pair] > lift_val and settings.confidence[pair] > conf_val and settings.support[pair] > sup_val):
                s_place = f"ps_{pair[0]}"
                t_place = f"pt_{pair[1]}"
                # if threshold meets, add tau transition to net.transition set
                trans_found = False
                # if threshold_up:
                #     for trans in net.transition:
                #         if str(trans) == str(tau_t):
                #             trans_found = True
                #     if not trans_found:
                #         net.transitions.add(tau_t)
                # else:
                #     net.transitions.add(tau_t)
                for trans in net.transitions:
                    if str(trans) == str(tau_t):
                        trans_found = True
                if not trans_found:
                    net.transitions.add(tau_t)
                if not trans_found:
                # get the control places which were added in previous step
                    for place in net.places:
                        if place.name == s_place:
                            # add arc to tau transition which is the dependency
                            utils.add_arc_from_to(place, tau_t, net)
                            # what if the place is already connected to the source transition? Hence, keep if check here 
                            # mainly if will be true for the first time 
                            # it serves the purpose of not adding more arc for upcoming pairs 
                            if len(place.in_arcs) == 0:
                                for trans in net.transitions:
                                    if str(trans) == str(pair[0]):
                                        utils.add_arc_from_to(trans, place, net)
                                        break
                        # similarly, do it for target                    
                        elif place.name == t_place:
                            utils.add_arc_from_to(tau_t, place, net)
                            if len(place.out_arcs) == 0: 
                                for trans in net.transitions:
                                    if str(trans) == str(pair[1]):
                                        utils.add_arc_from_to(place, trans, net)
                                        break
        
        # else :
        #     for trans in net.transitions:
        #         if str(trans) == str(tau_t):
        #             utils.remove_transition(trans)
        #              in_arcs = trans.in_arcs
    #net = get_sound_petrinet(net) 
    net = utils.remove_unconnected_components(net)
            
    return net             
    
def add_control_places(net, pairs):
    # part the pairs into source and target
    settings.source = get_source_child(pairs)
    settings.target = get_target_child(pairs)
    # add source 
    net = add_controlPlaces_toSource(settings.source, net)
    net = add_controlPlaces_totarget(settings.target, net)
    
    return net

# To preserve soundness, ---------     
def get_sound_petrinet(net):
    # sort lift in descending order so that highest dependent pair will be first
    # so, the source to add input arc to leftover control place of target will be decided
    # is the most dependent pair
    sorted_lift = dict(sorted(settings.lift.items(), key=lambda item: item[1], reverse=True))

    for (k, v) in sorted_lift.keys():
        if (settings.lift[(k,v)] != 0.0):
            t_place = f"pt_{v}" 
            for place in net.places:
                if place.name == t_place and len(place.in_arcs) == 0:
                    s_place = f"ps_{k}"
                    tau_t = PetriNet.Transition(f"tau_{k}{v}", None)
                    net.transitions.add(tau_t)
                    utils.add_arc_from_to(tau_t, place, net)
                    if len(place.out_arcs) == 0:
                        for trans in net.transitions:
                            if str(trans) == str(v):
                                utils.add_arc_from_to(place, trans, net)
                                break
                    for place in net.places:
                        if place.name == s_place:
                            utils.add_arc_from_to(place, tau_t, net)
                            if len(place.in_arcs) == 0:
                                for trans in net.transitions:
                                    if str(trans) == str(k):
                                        utils.add_arc_from_to(trans, place, net)
                                        break
                            break
                    break
    print("Trying to clean the duplicate transitions")
    net = clean_duplicate_transitions(net)
    return net          
            
    