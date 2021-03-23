from pm4py.objects.process_tree import pt_operator as pt_op
from pm4py.statistics.traces.log import case_statistics

import settings


def getOperator(treeList):
    op_list = []
    for tree in treeList:
        op_list.append(tree.operator)
    return op_list

def get_leaves(tree):
    root = tree
    leaves = root
    if root._get_children != list():
        leaves = root._get_children()
        change_of_leaves = True
        while change_of_leaves:
            leaves_to_replace = list()
            new_leaves = list()
            for leaf in leaves:
                if leaf._get_children() != list():
                    leaves_to_replace.append(leaf)
                else:
                    new_leaves.append(leaf)
            if leaves_to_replace != list():
                for leaf in leaves_to_replace:
                    for el in leaf.children:
                        new_leaves.append(el)
                leaves = new_leaves
            else:
                change_of_leaves = False
    return leaves

def check_subtree(tree):
    is_subtree = False
    for child in tree.children:
        if child.operator is None:
            continue
        else: 
            is_subtree = True
    return is_subtree

def combinations(node1, node2):
    xor_list = []
    children1 = node1._get_children()
    children2 = node2._get_children()
    
    for felement in children1:
        for selement in children2:
            if(felement.label is not None and selement.label is not None):
                xor_list.append((felement,selement))
    return xor_list

def get_children(tree):
    children_list = []
    if tree.operator != None:
        if(len(tree.children) > 0 and not check_subtree(tree)):
            children_list.append(tree.children)
        else:
            for node in tree.children:
                get_children(node)
    return children_list

def get_candidates(pt, parent, candidates):
    for node in pt.children:
        if node.operator != None and pt.operator != None:
            parent.append(node)
        if node.operator == pt_op.Operator.XOR:
            if(len(node._get_children()) >= 2 and not check_subtree(node)):
                candidates[node] = parent.copy()
                parent.pop(len(parent)-1)
            else:
                get_candidates(node)             
        else: 
            get_candidates(node)
    return candidates


def final_candidates(node1, node2, candidates):
    # candidates[key] , list(candidates.keys())[idx2], as nodes
    path1 = getOperator(candidates[node1])
    path2 = getOperator(candidates[node2])
    
    n = 0
    if len(path1) < len(path2): 
        n = len(path1)
        trim_length = len(path2) - len(path1)
        del path2[-trim_length:]

    elif len(path1) > len(path2):
        n = len(path2)
        trim_length = len(path1) - len(path2)
        del path1[-trim_length:]

    elif len(path1) == len(path2):
        n = len(path1)
    
    xor_final = []   
    
    # Find the LCA
    for i in range(n):
        found = False
        if(len(path1) > 0 and len(path2) > 0):
            # check for same operator from two paths
            if(path1[i] == path2[i]):
                # if find check whether it is sequence
                if(path1[i] == pt_op.Operator.SEQUENCE):
                    
                    # if it is sequence then confirming by checking children 
                    # get children of node
                    children1 = node1.children;
                    children2 = node2.children;
                    
                    # get leaves of two sequence operator
                    leaves1 = get_leaves(candidates[node1][i])
                    leaves2 = get_leaves(candidates[node2][i])
                    
                    # cross verify whether sequence node leaves has both children
                    # Example,leaves of sequence node of node1 has children of node2
                    # leaves of sequence node of node2 has children of node1
                    res1 = all(elem in leaves1 for elem in children2)
                    res2 = all(elem in leaves2 for elem in children1)

                    # if yes, we foung LCA else continue
                    if(res1 and res2):
                        xor_final = combinations(node1, node2)
                        
                        #dynamically find dependency value threshold? 
                        # dep_threshold = find_threshold(log)
                        #try finding dependency value here for each XOR_final list.
                        #if(get_dependency_strength(xor_final) > min_dep_value):
                        
                        found = True 
        if(found == True): 
            break
    return xor_final

def findDependencyValue(pairs):
    # find total traces in log
    total_traces = 0
    variants_count = case_statistics.get_variant_statistics(log)
    variants_count = sorted(variants_count, key=lambda x: x['count'], reverse=True)
    print("Variants of the Log \n",variants_count,"\n")
    
    for ele in variants_count:
        total_traces += ele['count']
    
    print("Trace length of the Log", total_traces, "\n")
    sup = {}
    conf = {}
    lift = {}
    for pair in pairs:
        sup, conf = get_sup_conf(pair, variants_count, total_traces)
        lift = get_lift(pair,variants_count, total_traces, sup, conf)
    
    return sup, conf, lift

def get_sup_conf(pair_list, log, total_trace):
    sup_dict = {}
    conf = {}
    lhs_c = 0
    pair_c = 0
    for item in log:
        if repr(pair_list[0]) in item['variant']:
            lhs_c += item['count']
            count_dict[pair_list[0]] = lhs_c
            sup_dict[pair_list[0]] = round((lhs_c / total_trace),3)
            if repr(pair_list[1]) in item['variant']:
                pair_c += item['count']
                count_dict[pair_list[0], pair_list[1]] = pair_c
                sup_dict[pair_list[0], pair_list[1]] = round((pair_c / total_trace), 3)
                conf[pair_list[0], pair_list[1]] = sup_dict[pair_list[0], pair_list[1]]/sup_dict[pair_list[0]]
                conf[pair_list[0], pair_list[1]] = round(conf[pair_list[0], pair_list[1]], 3)
            else:
                count_dict[pair_list[0], pair_list[1]] = pair_c
                sup_dict[pair_list[0], pair_list[1]] = round((pair_c / total_trace),3)
                conf[pair_list[0], pair_list[1]] = sup_dict[pair_list[0], pair_list[1]]/sup_dict[pair_list[0]]
                conf[pair_list[0], pair_list[1]] = round(conf[pair_list[0], pair_list[1]], 3)
                
    return sup_dict, conf  

def get_lift(pair,log, total, sup, conf):
    lift = {}
    rhs_c = 0
    for item in log:
        if repr (pair[1]) in item['variant']:
            rhs_c += item['count']
            count_dict[pair[1]] = rhs_c
            sup[pair[1]] = round((rhs_c / total),3)
            lift[pair] = round(conf[pair] / sup[pair[1]], 3)
    return lift