"""
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.  

// SPDX-License-Identifier: CC-BY-NC-4.0
"""
from anytree import AnyNode

def build_parent_group_mapping(toks):
    '''
    Utility function to construct a mapping for the start index to end index
    for every (sub-)tree in the `toks` list. Example the input `toks` list:
    ['(','(ORDER', '(', 'PIZZAORDER', '(', 'NUMBER', '1', ')', '(', 'TOPPING', 'HAM', ')',
        '(', 'COMPLEX_TOPPING', '(', 'TOPPING', 'ONIONS', ')', '(', 'QUANTITY', 'EXTRA',')',
         ')', ')', ')']

    :param toks: (list) List of tokens in the tokenized EXR-format flat string
    :return: (dict) Mapping of start index to end index for every (sub-)tree 
        in the `toks` list.
    '''
    i, N = 0, len(toks)
    stack = []
    parent_group_mapping = {}

    while i < N:
        if toks[i] == '(':
            stack.append(i)
        if toks[i] == ')':
            parent_group_mapping[stack.pop()] = i
        i += 1
    return parent_group_mapping

def parse_sexp(toks, start_index, end_index, parent_group_mapping):
    '''
    This is a utility function to convert the EXR-format flat string into a tree format

    Example the input `toks` list:
    ['(','(ORDER', '(', 'PIZZAORDER', '(', 'NUMBER', '1', ')', '(', 'TOPPING', 'HAM', ')',
        '(', 'COMPLEX_TOPPING', '(', 'TOPPING', 'ONIONS', ')', '(', 'QUANTITY', 'EXTRA',')',
         ')', ')', ')']

    :param toks: (list) List of tokens in the tokenized EXR-format flat string
    :param start_index: (int) Starting index in the `toks` list.
    :param end_index: (int) End index in the `toks` list 
    :param parent_group_mapping: (dict) Mapping of start index to end index 
        for every (sub-)tree in the `toks` list.

    :return: (AnyNode) A node specifying the root of a (sub-)tree constructed 
        from a subsequence in `toks` list.
    '''
    if toks[start_index] != '(':
        return AnyNode(id=toks[start_index])
    else:
        root_node = toks[start_index+1]
        args = []
        # Points to the beginning of the first leftmost sub-tree
        i = start_index+2
        # We run a loop to construct a sub-tree from a sub-sequence in the
        # `toks` list.
        while i < end_index-1:
            j = parent_group_mapping[i]+1 if toks[i] == '(' else i+1
            # Construct a node from the sub-sequence for which 
            # streches from index {i,...,j-1}.
            child = parse_sexp(toks, i, j, parent_group_mapping)
            args.append(child)
            i = j
        return AnyNode(id=root_node,children=args)
