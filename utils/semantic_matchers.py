"""
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.  

// SPDX-License-Identifier: CC-BY-NC-4.0
"""
from trees import TopSemanticTree, ExpressSemanticTree


def make_tree_if_possible(flat_string, semantic_tree_constructor):
    '''
    :param flat_string: (str) input flat string to construct a tree
    :param semantic_tree_constructor:
        (TopSemanticTree/ExpressSemanticTree) A tree class

    :return: (TopSemanticTree/ExpressSemanticTree) Return an object of Tree class
        if the tree can be constructed else None
    '''
    try:
        return semantic_tree_constructor(flat_string=flat_string)
    except:
        print('An exception occurred when creating a tree object from '
              f'the string "{flat_string}": make_if_possible returns None')
    return None


def tree_factory(flat_string, origin_type):
    '''
    :param flat_string: (str) input flat string to construct a tree
    :param origin_type: (str) origin of the string, i.e. EXR or TOP

    :return: (TopSemanticTree/ExpressSemanticTree) Return an object of Tree class
        if the tree can be constructed else None
    '''
    return make_tree_if_possible(flat_string, TopSemanticTree) if origin_type == 'TOP' \
        else make_tree_if_possible(flat_string, ExpressSemanticTree)


def is_unordered_exact_match(string_1, string_2, origin_type):
    '''
    Function to check if two strings have an unordered EM or not. This
    function returns False if either of the two input strings aren't
    in valid formats using which a tree can be constructed.

    :param string_1: input string 1
    :param string_2: input string 2
    :param origin_type: origin of the string, i.e. EXR or TOP

    :return: (bool) A bool value indicating if string 1 and string 2 are
        semantics only unordered EM or not
    '''
    tree_1 = tree_factory(string_1, origin_type)
    tree_2 = tree_factory(string_2, origin_type)

    # Check if either of the trees are storing a `None` value.
    # If yes, then return False for not an exact match
    if not tree_1 or not tree_2:
        return False

    return tree_1 and tree_2 and tree_1.is_unordered_exact_match(tree_2)


def is_semantics_only_unordered_exact_match(string_1, string_2):
    '''
    Function to check if two strings have an unordered EM or not,
    without the non-semantic nodes. This function is only applicable for
    TOP format strings. This function returns False if either of the two
    input strings aren't in valid formats using which a tree can be constructed.

    :param string_1: input string 1
    :param string_2: input string 2

    :return: (bool) A bool value indicating if string 1 and string 2 are
        semantics only unordered EM or not
    '''

    tree_semantics_only_1 = None
    tree_semantics_only_2 = None

    tree_1 = tree_factory(string_1, 'TOP')
    if tree_1:
        tree_semantics_only_1 = TopSemanticTree.get_semantics_only_tree(tree_1.tree_rep)
    tree_2 = tree_factory(string_2, 'TOP')
    if tree_2:
        tree_semantics_only_2 = TopSemanticTree.get_semantics_only_tree(tree_2.tree_rep)

    # Check if either of the trees are storing a `None` value.
    # If yes, then return False for not an exact match
    if not tree_semantics_only_1 or not tree_semantics_only_2:
        return False

    return tree_semantics_only_1 and tree_semantics_only_2 and \
           tree_semantics_only_1.is_unordered_exact_match(tree_semantics_only_2)


def is_unordered_exact_match_post_ER(string_1, string_2, resolver):
    '''
    Function to check if two strings have an unordered EM or not. Entity
    resolution step will be performed on the loaded tree representation for
    string_1. Once this is done the obtained tree will be
    compared to the tree obtained from loading string_2 as EXR-formatted string.
    This function returns False if either of the two input strings aren't
    in valid formats using which a tree can be constructed.

    :param string_1: input string 1, TOP format, will undergo ER and removal of non-semantic nodes
    :param string_2: input string 2, EXR format, will NOT undergo ER
    :param resolver: a resolver object from entity_resolution.py

    :return: (bool) A bool value indicating if string 1 and string 2 are
        semantics only unordered EM or not after entity resolution is performed
        the tree obtained from string 1.
    '''

    tree_1 = tree_factory(string_1, 'EXR')
    tree_2 = tree_factory(string_2, 'EXR')

    # Check if either of the trees are storing a `None` value.
    # If yes, then return False for not an exact match
    if not tree_1 or not tree_2:
        return False

    resolved_tree_1 = resolver.resolve_tree_into_TGT(tree_1)

    return resolved_tree_1 and tree_2 and resolved_tree_1.is_unordered_exact_match(tree_2)


def is_semantics_only_unordered_exact_match_post_ER(string_1, string_2, resolver):
    '''
    Function to check if two strings have an unordered EM or not,
    without the non-semantic nodes. Entity resolution step will be performed on
    the semantics only tree representation for string_1. This function is only applicable for
    TOP format string_1. The second string_2 will be loaded as an EXR format string.
    This function returns False if either of the two input strings aren't in valid formats
    using which a tree can be constructed.

    :param string_1: input string 1, TOP format, will undergo ER
    :param string_2: input string 2, EXR format, will NOT undergo ER
    :param resolver: a resolver object from entity_resolution.py

    :return: (bool) A bool value indicating if string 1 and string 2 are
        semantics only unordered EM or not after entity resolution is performed
        the tree obtained from string 1 and semantics only transformation was applied.
    '''

    tree_semantics_only_1 = None

    tree_1 = tree_factory(string_1, 'TOP')
    if tree_1:
        tree_semantics_only_1 = TopSemanticTree.get_semantics_only_tree(tree_1.tree_rep)

    tree_2 = tree_factory(string_2, 'EXPRESS')

    # Check if either of the trees are storing a `None` value.
    # If yes, then return False for not an exact match
    if not tree_semantics_only_1 or not tree_2:
        return False

    resolved_tree_1 = resolver.resolve_tree_into_TGT(tree_semantics_only_1)

    return resolved_tree_1 and tree_2 and \
           resolved_tree_1.is_unordered_exact_match(tree_2)
