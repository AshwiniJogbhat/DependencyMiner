import pandas as pd
import os
import settings
import Miner.to_petri_net_bordered as discover_net
from Miner.helper_functions import *

from pm4py.objects.log.importer.xes import importer as xes_importer
import pm4py.objects.process_tree as pt
from pm4py.analysis import check_soundness

from pm4py.algo.evaluation.precision import algorithm as precision_evaluator
from pm4py.algo.evaluation.replay_fitness import algorithm as replay_fitness_evaluator

from pm4py.visualization.petri_net import visualizer as pn_visualizer

from pm4py.objects.process_tree.obj import Operator as pt_op
from pm4py.objects.process_tree.utils import generic as util
from pm4py.objects.process_tree.utils import bottomup as b
from pm4py.objects.process_tree.utils import generic as g
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.visualization.process_tree import visualizer as pt_visualizer

from pm4py.objects.petri_net.exporter import exporter as pnml_exporter
from pm4py.objects.petri_net.importer import importer as pnml_importer
from pm4py.objects.petri_net.obj import PetriNet, Marking

#from pm4py.objects.petri_net import utils
# from pm4py.objects.petri import utils
from pm4py.objects.petri_net.utils import petri_utils as p_utils

from pm4py.statistics.traces.generic.log import case_statistics

def display_process_tree():
    #tree = inductive_miner.apply_tree(settings.EVENT_LOG, variant=inductive_miner.Variants.IM)
    parameters = {pt_visualizer.Variants.WO_DECORATION.value.Parameters.FORMAT: "SVG"}
    gviz = pt_visualizer.apply(settings.PROCESS_TREE, parameters=parameters)
    tree_path = os.path.join(settings.TREE_PATH, f"{settings.EVENT_LOG_NAME}.SVG")
    pt_visualizer.save(gviz, tree_path)
    return tree_path

def discover_process_tree(log):
    tree = inductive_miner.apply_tree(log)
    settings.PROCESS_TREE = tree
    return tree

def display_petri_net(net=None):
    if net == None :
        net = settings.PETRI_NET
        
    im = settings.I_MARKS_ORIG
    fm = settings.F_MARKS_ORIG
    parameters = {pn_visualizer.Variants.WO_DECORATION.value.Parameters.FORMAT: "SVG"}
    gviz = pn_visualizer.apply(net, im, fm, parameters=parameters)
    image_path = os.path.join(settings.NET_PATH, f"{settings.EVENT_LOG_NAME}.SVG")
    pn_visualizer.save(gviz, image_path)
    return image_path


def discover_petri_net(tree):
    orig_net = None
    im = None
    fm = None
    settings.sink_dict = {}
    settings.src_dict = {}
    
    orig_net, im, fm  = discover_net.apply(tree)
    
    settings.PETRI_NET_ORIG = orig_net
    settings.I_MARKS_ORIG = im 
    settings.F_MARKS_ORIG = fm
    
    settings.PETRI_NET = orig_net
    return orig_net, im, fm

def export_pnml(net_name=None):
    if net_name != None:
        net_name = net_name
    else:
        net_name = f"{settings.EVENT_LOG_NAME}.pnml"
    im = settings.I_MARKS_ORIG
    fm = settings.F_MARKS_ORIG
    pnml_path = os.path.join(settings.NET_PATH, net_name)
    pnml_exporter.apply(settings.PETRI_NET, im, pnml_path , final_marking=fm)
    
def findAsociationRules():
    tree = settings.PROCESS_TREE 
    log = settings.EVENT_LOG 
    # Explore Log
    total_traces = 0
    xor_tree = {}
    rules_dict = {}
    
    
    variants_count = case_statistics.get_variant_statistics(log)
    variants_count = sorted(variants_count, key=lambda x: x['count'], reverse=True)
    print("Variants", variants_count)
    rules_values = {}
    
    for ele in variants_count:
        total_traces += ele['count']
    
    rule_dicti = {}
    ## Firstly, get all XOR tree list if it has no tau at the leaves.
    xor_tree = {}
    xor_tree = get_xor_trees(tree)
    print(xor_tree)
    
    ## find all valid XOR combinations
    for i in range(1, len(xor_tree)):
        for j in range(i+1, len(xor_tree)+1):
            max_v = 0
            rules_values = {}
            LCA = g.common_ancestor(xor_tree[f'X{i}'], xor_tree[f'X{j}'])
            if LCA.operator == pt_op.SEQUENCE and (pt_op.XOR not in get_ancestors_operator(xor_tree[f'X{i}'], LCA)) and (pt_op.XOR not in get_ancestors_operator(xor_tree[f'X{j}'], LCA)) and (pt_op.LOOP not in get_ancestors_operator(xor_tree[f'X{i}'], LCA)) and (pt_op.LOOP not in get_ancestors_operator(xor_tree[f'X{j}'], LCA)):
                xor_children = []
                source, target = get_candidates(xor_tree[f'X{i}'], xor_tree[f'X{j}'])
                for s in source:
                    for t in target:
                        values = []
                        support = get_support([s,t], variants_count, total_traces)
                        conf_value = round((support[tuple(s), tuple(t)]/support[tuple(s)]), 3)
                        lift_value = get_lift([s, t], conf_value, variants_count, total_traces)
                        
                        values.append(support[tuple(s), tuple(t)])
                        values.append(conf_value)
                        values.append(lift_value)
                        l = [s,t]
                        rules_values[(f"{s}", f"{t}")] = values
                        if values[2] > max_v:
                            max_v = values[2]
                rules_values['Max'] = max_v
                rule_dicti[(f"X{i}", f"X{j}")] = rules_values
    
    sorted_rule_dict = dict(sorted(rule_dicti.items(), key=lambda item: item[1]['Max'], reverse=True))
    return sorted_rule_dict, xor_tree

def soundness_at_XOR_tree(rules):
    sound_xor_rule = {}
    keys_to_be_removed = []
    key_copy = tuple(rules.keys())
    for i in range(len(rules.keys())):
        if len(rules.keys()) != 0:
            sound_xor_rule[next(iter(rules))] = rules[next(iter(rules))]
            for k,v in rules.items():
                if k[0] == list(sound_xor_rule.items())[len(sound_xor_rule)-1][0][0]:
                    keys_to_be_removed.append(k)
                elif k[1] == list(sound_xor_rule.items())[len(sound_xor_rule)-1][0][1]:
                    keys_to_be_removed.append(k)
            for k in keys_to_be_removed:
                if k in rules.keys():
                    del rules[k]
    return sound_xor_rule

def discover_sound_petrinet(rules_dict, net):
    for pair in rules_dict:
        trans_exist = 0
        #if the place already exists, We do not need to add new places, just use existing ones
        tau_t = PetriNet.Transition(f"tau_{pair[0]}{pair[1]}", None)
        for trans in net.transitions:
            if str(trans) == str(tau_t):
                trans_exist = 1
                break
        if(trans_exist == 0):
            net.transitions.add(tau_t)
            s_place = f"ps_{pair[0]}"
            t_place = f"pt_{pair[1]}"
            source_found = 0
            target_found = 0
            for place in net.places:
                if place.name == s_place:
                    source_found = 1
                    
                    p_utils.add_arc_from_to(place, tau_t, net)

                elif place.name == t_place:
                    target_found = 1
                    p_utils.add_arc_from_to(tau_t, place, net)

                if (source_found and target_found):
                    break
            
            ## Handle Source Side
            # Adding new place after source
            if (not source_found):
                source = PetriNet.Place(s_place)
                net.places.add(source)
                p_utils.add_arc_from_to(source, tau_t, net)
                #print("Sinc Dict", settings.sink_dict)
                for k,v in settings.sink_dict.items():
                    if all(elem in str(list(k)) for elem in str(pair[0])):
                        for t in net.transitions:
                            if str(t) == str(v):
                                #print("Added arc for source", t)
                                
                                p_utils.add_arc_from_to(t, source, net)
                                break
                        
                            
            if (not target_found):
                target = PetriNet.Place(t_place)
                net.places.add(target)
                p_utils.add_arc_from_to(tau_t, target, net)
                #print("sOURCE Dict", settings.src_dict)
                for k,v in settings.src_dict.items():
                    if all(elem in str(list(k)) for elem in str(pair[1])):
                        for t in net.transitions:
                            if str(t) == str(v):
                                #print("Added arc for target", t)
                                p_utils.add_arc_from_to(target, t, net)
                                break
            
    return net


def repair_Model(s_net, rules_dict, support, confidence, lift, sound=1):
    rules = {}
    #print("Repairing Model")
    rules_dict = dict(sorted(rules_dict.items(), key=lambda item: item[1]))
    for pair, value in rules_dict.items():
        trans = None
        if str(value[2]) < lift or str(value[0]) < support or str(value[1]) < confidence:
            tau_t = f"tau_{pair[0]}{pair[1]}"
            for t in s_net.transitions:
                s_place_valid = 0
                t_place_valid = 0
                if str(t) == str(tau_t):
                    trans = t
                    source_places = set([x.source for x in t.in_arcs])
                    for p in source_places:
                        s_place = f"ps_{pair[0]}"
                        if str(p) == s_place:
                            if sound == 'on' and len(p.out_arcs) > 1:
                                s_place_valid = 1
                            elif sound == None:
                                s_place_valid = -1
                                if len(p.out_arcs) == 1:
                                    p_utils.remove_place(s_net, p)
                    target_places =  set([x.target for x in t.out_arcs])   
                    for p in target_places:
                        t_place = f"pt_{pair[1]}"
                        if str(p) == t_place:
                            if sound == 'on' and len(p.in_arcs) > 1:
                                t_place_valid = 1
                            elif sound== None:
                                t_place_valid = -1
                                if len(p.in_arcs) == 1:
                                    p_utils.remove_place(s_net, p)
                            
                            if sound == 'on' and len(p.in_arcs) == 1:
                                rules[pair] = value
                    if s_place_valid==1 and t_place_valid==1:
                        s_net = p_utils.remove_transition(s_net, trans)
                        break
                    elif s_place_valid == -1 and t_place_valid == -1:
                        s_net = p_utils.remove_transition(s_net, trans)
                        break
        else:
            rules[pair] = value
    return s_net, rules

def get_soundness():
    return check_soundness(settings.PETRI_NET, settings.I_MARKS_ORIG, settings.F_MARKS_ORIG)
    

def get_precision(pn_net, im, fm):
    log = settings.EVENT_LOG
    prec = precision_evaluator.apply(log, pn_net, im, fm, variant=precision_evaluator.Variants.ALIGN_ETCONFORMANCE)
    return prec

def get_fitness(net, im, fm):
    log = settings.EVENT_LOG
    fitness = replay_fitness_evaluator.apply(log, net, im, fm, variant=replay_fitness_evaluator.Variants.ALIGNMENT_BASED)
    return fitness
    
    
def repair_petri_net(support, confidence, lift, sound):
    
    p_net = None
    im = None
    fm = None
    p_net, im, fm = discover_petri_net(settings.PROCESS_TREE)

    rules_dict = dict(settings.RULES_DICT)
       
    if sound == 'on':
        print("we need sound model") 
        rules_dict_sound = soundness_at_XOR_tree(rules_dict)
        print(rules_dict_sound)
    else:
        print("we do not need sound model") 
        rules_dict_sound = rules_dict
        print(rules_dict_sound)
        
    rules_dicti = {}
    if rules_dict_sound != {}:
        for pair, value in rules_dict_sound.items():
            rules_dicti.update(value)
        del rules_dicti['Max']

    # Repair net,
    # firstly try adding all arcs and secondly remove those which does not meet the threshold.
    sound_net = discover_sound_petrinet(rules_dicti, p_net)
    repaired_net, rules = repair_Model(sound_net, rules_dicti, support, confidence, lift, sound)
    
    settings.PETRI_NET = None
    settings.PETRI_NET = repaired_net
    settings.RULES = rules
    
    precision = get_precision(settings.PETRI_NET ,im, fm)
    fitness = get_fitness(settings.PETRI_NET, im, fm)
    net_path = display_petri_net(settings.PETRI_NET)
    
    if sound == 'on':
        check_soundness(settings.PETRI_NET, im, fm)
        
    print(im, fm)
    print("Precision after", precision)
    return net_path, round(precision,2), round(fitness['average_trace_fitness'], 2), rules
 
    
    
    