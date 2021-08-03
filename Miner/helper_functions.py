from pm4py.objects.process_tree.obj import Operator as pt_op
from pm4py.objects.process_tree.utils import generic as g

def check_subtree(tree):
    is_subtree = False
    for child in tree.children:
        if child.operator is None:
            continue
        else: 
            is_subtree = True
            break
    return is_subtree

def get_xor_leaves(xor_tree, leaves=None):
    tau_exist = 0
    leaves = leaves if leaves is not None else []
    if len(xor_tree.children) == 0:
        if xor_tree.label is not None:
            leaves.append(xor_tree)
    else:
        for c in xor_tree.children:
            leaves = get_xor_leaves(c, leaves)
    return leaves

def get_ancestors_operator(t, until, include_until = True):
    ancestors = list()
    if t == until:
        return ancestors
    parent = t.parent
    while parent != until:
        ancestors.append(parent.operator)
        parent = parent.parent
        if parent is None:
            return None
    if include_until:
        ancestors.append(until.operator)
    return ancestors

def is_xor_exists(node):
    if node.operator == pt_op.XOR:
        return True
    else:
        for child in node.children:
            return is_xor_exists(child)
    return False

def get_xor_children(node, xor_list=None):
    xor_list = xor_list if xor_list is not None else {}
    for child in node.children:
        if len(get_xor_leaves(child)) > 0:
            xor_list.append((child, get_xor_leaves(child)))
    return xor_list

def get_xor_children_copy(node, xor_list=None):
    xor_list = xor_list if xor_list is not None else {}
    for child in node.children:
        if len(get_xor_leaves(child)) > 0:
            xor_list.append(get_xor_leaves(child))
    return xor_list

def check_for_tau(tree):
    # leaves = g.get_leaves(tree)
    # for leaf in leaves:
    #     if g.is_tau_leaf(leaf):
    #         print("Tau Exists", leaf)
    #         return True
    for node in tree.children:
        leaves = g.get_leaves(node)
        if len(leaves) == 1:
            for leaf in leaves:
                if g.is_tau_leaf(leaf):
                    return True
        
def get_xor_trees(pt, xor_tree = None):
    xor_tree = xor_tree if xor_tree is not None else {}
    if pt.operator != None:
        for node in pt.children:
            if node.operator != None and node.operator == pt_op.XOR and not check_for_tau(node):
                xor_tree[f'X{len(xor_tree)+1}'] = node
            else:
                xor_tree = get_xor_trees(node, xor_tree)
                                               
    return xor_tree

def get_candidates(node1, node2):
    XOR_source = []
    XOR_target = []
    if g.common_ancestor(node1, node2).operator == pt_op.SEQUENCE:
        XOR_source = get_xor_children_copy(node1, XOR_source)
        XOR_target = get_xor_children_copy(node2, XOR_target)
        
    return XOR_source, XOR_target


def get_support(pair, variants, total):
    lhs_c = 0
    rule_count = 0
    sup = {}
    
    for item in variants:
        for i in range(0, len(pair[0])):
            if not repr(pair[0][i]) in item['variant']:
                continue
            else:
                lhs_c += item['count']
                for j in range(0, len(pair[1])):
                    if not repr(pair[1][j]) in item['variant']:
                        continue
                    else:
                        rule_count += item['count']
                        break
                break
    sup[tuple(pair[0])] = round((lhs_c / total), 3)
    sup[tuple(pair[0]), tuple(pair[1])] = round((rule_count / total), 3)
    
    return sup
                  
def get_lift(pair, confidence, variants, total):
    rhs_c = 0
    for item in variants:
        for i in range(0, len(pair[1])):
            if not repr(pair[1][i]) in item['variant']: 
                continue
            else:
                rhs_c += item['count']
                break
    sup_c = round((rhs_c / total),3)
    lift = round((confidence / sup_c), 3)
    return lift

def get_support_updated(pair, variants, total, source, target):
    lhs_c = 0
    rule_count = 0
    l_found = 0
    r_found = 0
    sup = {}
    for item in variants:
        trace = item['variant'].split(",")
        #added line
        temp_src = [str(i) for i in pair[0]]
        temp_tgt = [str(i) for i in pair[1]]
        
        for i in range(0, len(trace)):
            if not str(trace[i]) in temp_src:#repr(pair[0]):
                continue
            else:
                l_found = 1
                track = 0
                for j in range(i, len(trace)):
                    track = j
                    if str(trace[j]) in temp_tgt:#repr(pair[1]):
                        if l_found:
                            r_found = 1
                            rule_count += item['count']
                            i = j
                            break
                    else:
                        if str(trace[j]) in list(str(source)) and str(trace[j]) not in temp_src: #repr(pair[0]):
                            l_found = 0
                            break
                 
                if track == len(trace) - 1:
                    break

            if l_found and r_found:
                break
                               
    
    #sup[tuple(pair[0])] = round((lhs_c / total), 3)
    sup[tuple(pair[0]), tuple(pair[1])] = round((rule_count / total), 3) 
    return sup

def get_confidence(pair, sup, variants, total):
    lhs_c = 0
    for item in variants:
        trace = item['variant'].split(",")
        for i in range(0, len(pair[0])):
            if not repr(pair[0][i]) in trace:#item['variant']: 
                continue
            else:
                lhs_c += item['count']
                break
    sup_c = round((lhs_c / total),3)
    conf = round((sup / sup_c), 3)
    return conf