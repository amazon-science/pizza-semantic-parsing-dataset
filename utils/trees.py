"""
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.  

// SPDX-License-Identifier: CC-BY-NC-4.0
"""
import re
from abc import ABC, abstractmethod
from anytree import AnyNode, RenderTree
from sexp_reader import build_parent_group_mapping, parse_sexp


class SemanticTree(ABC):
    ROOT_SYMBOL = 'DUMMY-ROOT'

    def __init__(self, *, flat_string=None, tree_rep=None, root_symbol=None, children=None):
        '''
        This construtor is used to instantiate an object of derived classes
        using either a flat string `flat_string`, a tree representation
        `tree_rep`, or the combination of a root symbol and a list of tree_rep children.

        :param flat_string: (str) input flat string to construct a tree, if possible.
        :param tree_rep: (AnyNode) a tree.
        :param root_symbol: (str) a string that will be used as id of root node.
        :param children: (list) a list of SemanticTree objects to be defined as children of root_symbol.
        '''
        try:
            # we pass `flat_string` when we instantiate an object of "Tree" class
            # when no underlying Tree representation is currently existing, i.e we
            # create an object from ground up. 
            if flat_string:
                self.tree_rep = self._linearized_rep_to_tree_rep(flat_string)
            # we pass `tree_rep` when we instantiate an object of a derived class
            # when an underlying Tree representation already exists but we want to
            # have a new tree representation from an existing one.
            elif tree_rep:
                self.tree_rep = tree_rep
            # we pass root_symbol and children when we want to construct a new tree
            # object from a list of valid tree children and a symbol for the parent root node.
            elif root_symbol and children:
                self.tree_rep = AnyNode(id=root_symbol, children=[c.tree_rep for c in children])

        except Exception as e:
            raise ValueError() from e

    def pretty_string(self):
        '''
        Return a string for the rendered tree. 

        :return: (str) Returns a rendered tree string
        '''
        tree_string = ""
        for tree_string_prelude, _, node in RenderTree(self.tree_rep):
            tree_string += f"{tree_string_prelude}{node.id}\n"
        return tree_string

    # Since we don't want to expose the internal implementation details of 
    # the how we construct a tree, i.e using AnyNode class we pass a dict 
    # with different attributes. In this case, its just `id`.  
    def root_symbol(self):
        '''
        Returns the name of the root for this tree.

        :return: (str) Name of the root of the tree 
        '''
        return self.tree_rep.id

    def is_leaf(self):
        '''
        Check if a tree is a leaf or not

        :return: (bool) Return True if tree is a leaf else False
        '''
        return not self.children()

    def is_unordered_exact_match(self, otree):
        '''
        This method is used to check if `otree`, a tree object, is an exact match 
        with the tree object calling this method.

        :param otree: (TopSemanticTree/ExpressSemanticTree) Tree object to compare with.
        :return: (bool) If the two trees have an unordered exact match or not.  
        '''
        if not isinstance(otree, type(self)):
            raise TypeError(f"Expected both trees to be of type {type(self)} "
                f"but one of them is of type {type(otree)}")
        # check if the roots of trees are same. 
        # If not, its not an exact match.
        if self.root_symbol() != otree.root_symbol():
            return False
        # Check if the number of children of both trees are same.
        # If not, its not an exact match.
        if len(self.children()) != len(otree.children()):
            return False
        # Count the number of equal sub-trees, i.e. children
        matched_subtrees_idx_1, matched_subtrees_idx_2 = set(), set()
        for i,child_1 in enumerate(self.children()):
            for j,child_2 in enumerate(otree.children()):
                if (i not in matched_subtrees_idx_1) and \
                    (j not in matched_subtrees_idx_2):
                    if child_1.is_unordered_exact_match(child_2):
                        matched_subtrees_idx_1.add(i)
                        matched_subtrees_idx_2.add(j)
        # If the no. of matched sub-trees are equal to the 
        # number of children itself, that means all childdren are a match
        # and hence its an exact match, otherwise not. 
        return len(matched_subtrees_idx_1) == len(self.children())

    @abstractmethod
    def children(self):
        '''Get the children of the root calling this method'''

    @abstractmethod
    def _linearized_rep_to_tree_rep(self, flat_string):
        '''Get the tree representation for flat input string `flat_string`'''

class TopSemanticTree(SemanticTree):
    def __init__(self, *, flat_string=None, tree_rep=None, root_symbol=None, children=None):
        super(TopSemanticTree, self).__init__(flat_string=flat_string, tree_rep=tree_rep, root_symbol=root_symbol,
                                              children=children)

    def children(self):
        '''
        :return: (List) Return a list of TopSemanticTree objects that are children of `self` 
        '''
        return [TopSemanticTree(tree_rep=c) for c in self.tree_rep.children]

    @classmethod
    def get_semantics_only_tree(cls, tree_rep):
        '''
        Returns a class object by removing the non-semantic nodes from its tree 
        representation. 
        
        :param tree_rep: (AnyNode) A tree representation

        :return: (TopSemanticTree) A tree class object with the non-semantic nodes removed.
        '''
        tree_rep_ = cls.remove_non_semantic_nodes(tree_rep)
        return cls(tree_rep=tree_rep_)

    @staticmethod
    def remove_non_semantic_nodes(tree_rep):
        '''
        Method functionally removes the non-semantic nodes from a tree representation.

        :param: (AnyNode) Pointer to the input tree.
        :return: (AnyNode) Pointer to a new tree carrying only semantic nodes.
        '''
        # Check if all the children are terminal.
        if all(c.is_leaf for c in tree_rep.children):
            return AnyNode(id=tree_rep.id, children=[AnyNode(id=c.id) for c in tree_rep.children])

        # If the above check fails, filter the terminal children
        # and get the non-terminal child nodes.
        non_terminal_children = filter(lambda c: not c.is_leaf, tree_rep.children)
        new_children = [TopSemanticTree.remove_non_semantic_nodes(c) for c in non_terminal_children]
        
        return AnyNode(id=tree_rep.id, children=new_children)

    def _linearized_rep_to_tree_rep(self, flat_string):
        '''
        Get the tree representation for flat input string `flat_string`
        Example input string:
        "(ORDER can i have (PIZZAORDER (NUMBER a ) (SIZE large ) (TOPPING bbq pulled pork ) ) please )"

        Invalid flat strings include those with misplaced brackets, mismatched brackets,
        or semantic nodes with no children

        :param flat_string: (str) input flat string to construct a tree, if possible.
        :raises ValueError: when s is not a valid flat string
        :raises IndexError: when s is not a valid flat string
        
        :return: (AnyNode) returns a pointer to a tree node.
        '''
        # Keep track of all the semantics in the input string.
        semantic_stack = [AnyNode(id=TopSemanticTree.ROOT_SYMBOL)]

        for token in flat_string.split():
            if '(' in token:
                node = AnyNode(id=token.strip('('), parent=semantic_stack[-1])
                semantic_stack.append(node)
            elif token == ')':
                # If the string is not valid an error will be thrown here.
                # E.g. (PIZZAORDER (SIZE LARGE ) ) ) ) ) ) )
                try:
                    # If there are no children within this semantic node, throw an error
                    # E.g. (PIZZAORDER (SIZE LARGE ) (NOT ) )
                    if not semantic_stack[-1].children:
                        raise Exception("Semantic node with no children")
                    semantic_stack.pop()
                except Exception as e:
                    raise IndexError(e) from e
            else:
                AnyNode(id=token, parent=semantic_stack[-1])
        # If there are more than one elements in semantic stack, that means
        # the input string is malformed, i.e. it cant be used to construct a tree
        if len(semantic_stack) > 1:
            raise ValueError()
        return semantic_stack[-1]


class ExpressSemanticTree(SemanticTree):
    def __init__(self, *, flat_string=None, tree_rep=None, root_symbol=None, children=None):
        super(ExpressSemanticTree, self).__init__(flat_string=flat_string, tree_rep=tree_rep, root_symbol=root_symbol,
                                                  children=children)

    def children(self):
        '''
        Get the children for the root calling this method

        :return: (List) Return a list of ExpressSemanticTree objects that are children of `self` 
        '''
        return [ExpressSemanticTree(tree_rep=c) for c in self.tree_rep.children]

    @staticmethod
    def tokenize(flat_string):
        '''
        Tokenize EXR string
        Example input string:
        "(ORDER (PIZZAORDER (NUMBER 1) (TOPPING HAM) (COMPLEX_TOPPING (TOPPING ONIONS) (QUANTITY EXTRA))))"

        :param flat_string: (str) EXR-format input flat string to construct a tree

        :return: (list) A list of tokens obtained after tokenizing `flat_string`.
        '''
        special_characters = [',', '\n']
        return [t for t in re.split('([^a-zA-Z0-9._-])',flat_string) \
            if t and not(t.isspace()) and t not in special_characters]

    def _linearized_rep_to_tree_rep(self, flat_string):
        '''
        Get the tree representation for flat input string `flat_string`
        Example input string:
        "(ORDER (PIZZAORDER (NUMBER 1) (TOPPING HAM) (COMPLEX_TOPPING (TOPPING ONIONS) (QUANTITY EXTRA))))"

        :param flat_string: (str) EXR-format input flat string to construct a tree, if possible.
        :return: (AnyNode) returns a pointer to a tree.
        '''
        flat_string = f'({ExpressSemanticTree.ROOT_SYMBOL} {flat_string})'
        # Split the flat string using a regular expression and filter the special characters.
        toks = ExpressSemanticTree.tokenize(flat_string)
        parent_group_mapping = build_parent_group_mapping(toks)
        return parse_sexp(toks, 0, len(toks), parent_group_mapping)
