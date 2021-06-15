from pm4py.objects.conversion.process_tree.variants.to_petri_net import clean_duplicate_transitions
import settings
from pm4py.analysis import check_soundness
import os
from pm4py.objects.petri.petrinet import PetriNet, Marking
from pm4py.objects.petri import utils
from pm4py.objects.petri.utils import remove_transition, remove_place, add_arc_from_to

sacredNodes = []

def reduce_silent_transition(net):
    net = apply_fst(net)

def prepare_net(net):
    sacredNodes= [t for t in net.transitions if not t.label is None ]
    
def apply_fst(net):
    for place in net.places:
        if place in sacredNodes:
            continue
        
        preset = place.in_arcs
        if len(preset) != 1:
            continue
        
        inputTransition = list(place.in_arcs)[0].source
        #print(inputTransition)
        
        postset = place.out_arcs
        if len(postset) != 1:
            continue
        
        outputTransition = list(place.out_arcs)[0].target
        preset = outputTransition.in_arcs
        if (len(preset) != 1):
            continue
            
        if (inputTransition == outputTransition):
            continue
        
        if not outputTransition in sacredNodes:
            print(outputTransition)
            postset = outputTransition.out_arcs
            target_place = list(outputTransition.out_arcs)[0].target
            print(target_place)
            for arc in postset:
                add_arc_from_to(inputTransition, target_place, net)
            remove_transition(net, outputTransition)
            remove_place(net, place)
            
        elif not inputTransition in sacredNodes and (outputTransition.label is None or len(inputTransition.out_arcs) == 1):
            preset = inputTransition.in_arcs
            source_place = list(inputTransition.in_arcs)[0].source
            print(source_place)
            for arc in preset:
                add_arc_from_to(source_place, outputTransition, net)
            
            postset = inputTransition.out_arcs
            for arc in postset:
                add_arc_from_to(outputTransition, arc.target, net)
            remove_transition(net, inputTransition)
            remove_place(net, place)
    return net

def apply_fsp(net):
    for trans in net.transitions:
        if trans in sacredNodes:
            continue
            
        preset = trans.in_arcs
        if len(preset) != 1:
            continue
            
        inputPlace = list(trans.in_arcs)[0].source
        postset = inputPlace.out_arcs
        if len(postset) != 1:
            continue
        
        postset = trans.out_arcs
        if len(postset) != 1:
            continue
            
        outputPlace = list(trans.out_arcs)[0].target
        
        if inputPlace == outputPlace:
            continue
            
        if not inputPlace in sacredNodes:
            preset = inputPlace.in_arcs
            for arc in preset:
                add_arc_from_to(arc.source, outputPlace, net)
            remove_transition(net,trans)
            remove_place(net, inputPlace)
            
        elif not outputPlace in sacredNodes:
            preset = outputPlace.in_arcs
            for arc in preset:
                add_arc_from_to(arc.source, inputPlace, net)
            postset = outputPlace.out_arcs
            for arc in postset:
                add_arc_from_to(inputPlace, arc.target, net)
            remove_transition(net, trans)
            remove_place(net, outputPlace)
    return net
           
        
            
    
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
            

def simplify(net):
    net = reduce_silent_transition(net)
    
    if not check_soundness(settings.PETRI_NET, settings.I_MARKS, settings.F_MARKS):
        petri_net = get_sound_petrinet(net)
    
    return net

