"""
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.  

// SPDX-License-Identifier: CC-BY-NC-4.0
"""
import os
from abc import ABC, abstractmethod
from trees import ExpressSemanticTree
from express_utils import load_catalog_file, to_prefix_notation


class EntityResolver(ABC):
    """
    This class is a parent class for domain/skill-specific entity resolvers, which take as input
    a TopSemanticTree instance and return an ExpressSemanticTree where some leaf nodes have been
    resolved to grammar-defined entities, e.g. '(SIZE extra large size )' --> (SIZE EXTRA_LARGE ). Those resolvers are
    based on the content of catalog files defined for each grammar.
    """
    # If an entity is not in a catalog, the leaf for that entity value in tree will be UNK_ENTITY_SYMBOL
    UNK_ENTITY_SYMBOL = '<UNKNOWN_ENTITY>'


    @abstractmethod
    def _init_entities_files(self):
        """
        Each resolver relies on grammar-defined terminal nodes, and catalog file paths.
        Hence this method has to be implemented by each task-specific resolver.
        This method requires initialization of member variable catalog_files which is a dictionary
        mapping strings to catalog file names. The mapping key string must match the label of the node to be resolved.
        """

    def _load_catalogs(self):
        """
        Simple utils that populates the entities dictionary attribute of a resolver.
        """
        self.entities = {}
        for entity in self.catalog_files:
            self.entities[entity] = load_catalog_file(self.catalog_files[entity])


    def resolve_entities(self, tree):
        '''
        This method resolves groups of tokens into entities based on the parent node of those leaves, which determines
        which catalog file will be used. If a catalog file exists for the entity
        but the value is not matched in the file, then UNK_ENTITY_SYMBOL will be inserted in place of the resolved
        entity, for eg. (SIZE biggest size ) --> (SIZE <UNKNOWN_ENTITY> ).

        Catalog file can be mapping a group of tokens to an arbitrary tree, for eg. 'two liters' --> VOLUME(2,LITER)
        hence this method converts the notation VOLUME(2,LITER) to the flat string representation
        (VOLUME 2 LITER ) before loading the string as an ExpressSemanticTree and inputting that as resolved entity.

        Note that this method assumes that when constructing a tree from a string the group of tokens will be inserted
        left to right as children of an entity node. For eg. given an input string  '(TOPPING green peppers )' the tree
        constructed from it and passed to the resolver must preserve the order of 'green' and 'peppers' when constructing
        the children of TOPPING, otherwise this method could potentially try to look for 'peppers green' in the catalog
        and return that no such entity value is known.
        :param: (SemanticTree) Input SemanticTree object.
        :return: (SemanticTree) SemanticTree object where entities are resolved.
        '''

        tree_class = type(tree)
        # We only resolve entities if all the children are terminal.
        if all(c.is_leaf() for c in tree.children()):
            children_tokens = [c.root_symbol() for c in tree.children()]
            if tree.root_symbol() in self.entities:
                entity_value = ' '.join(children_tokens)
                if entity_value in self.entities[tree.root_symbol()]:
                    string_subtree = to_prefix_notation(self.entities[tree.root_symbol()][entity_value])
                    resolved_subtree = tree_class(flat_string=string_subtree).children()[0]
                    return resolved_subtree
                # If the node is supposed to be a resolvable entity (a catalog file exits) but the value is unknown, then
                # we input the unknown entity symbol.
                else:
                    return tree_class(flat_string=f"({tree.root_symbol()} {EntityResolver.UNK_ENTITY_SYMBOL} )").children()[0]
            # If the node itself is not an entity for which we want to perform ER (for eg. a NAME node for which
            # we want to capture the exact string as is in the tree, and not resolve it) then the children tokens
            # are inserted as is.
            return tree_class(tree_rep=tree.tree_rep)

        # We then recursively apply the method to children. Leaves of a node which has other
        # non-terminals as children are untouched. Other non-terminals are sent through entity resolution themselves.
        new_children = [c if c.is_leaf() else self.resolve_entities(c) for c in tree.children()]

        return tree_class(root_symbol=tree.root_symbol(), children=new_children)

    @abstractmethod
    def _add_defaults(self, tree):
        """
        Some resolvers can also add default subtrees in the resolved tree. This is resolver specific.
        """

    @abstractmethod
    def resolve_tree_into_TGT(self, tree):
        """
        Some resolver might only resolve entities, other might also add default nodes and values in the
        resolved tree. Hence this method is resolver specific and must be implemented by children classes.
        """


class PizzaSkillEntityResolver(EntityResolver):

    def __init__(self):
        super(EntityResolver, self).__init__()
        self._init_entities_files()
        self._load_catalogs()


    def _init_entities_files(self):
        """
        Each resolver will be loading a specific set of catalog files, and map the loaded values to
        pre-defined non-terminal entity nodes as chosen in EXR format.
        """
        script_dir = os.path.dirname(__file__)
        catalogs_dir_name = 'catalogs'
        catalogs_full_path = os.path.join(script_dir, catalogs_dir_name)

        self.catalog_files = {
                                  'TOPPING': f'{catalogs_full_path}/topping.txt',
                                  'NUMBER': f'{catalogs_full_path}/number.txt',
                                  'SIZE': f'{catalogs_full_path}/size.txt',
                                  'STYLE': f'{catalogs_full_path}/style.txt',
                                  'DRINKTYPE': f'{catalogs_full_path}/drinks.txt',
                                  'VOLUME': f'{catalogs_full_path}/drink_volume.txt',
                                  'CONTAINERTYPE': f'{catalogs_full_path}/container.txt',
                                  'QUANTITY': f'{catalogs_full_path}/quant_qualifier.txt'
                                }

    def _add_defaults(self, tree):
        """
        This method adds the default (NUMBER 1 ) subtree to every tree rooted in
        PIZZAORDER or DRINKORDER which does not already contain an occurrence of this node.
        This is a convention in EXR that all orders have a default (NUMBER 1), but the
        TOP format could be 'get me pie with X' which will have no NUMBER to resolve into the
        default (NUMBER 1). Hence we need to add it before comparing to EXR.
        :param: (ExpressSemanticTree) Input ExpressSemanticTree object.
        :return: (ExpressSemanticTree) ExpressSemanticTree object with added defaults
        """

        # Stopping criterion for our recursion
        if tree.is_leaf():
            return tree

        # If the root node is either of the following two, we consider adding the defaults
        if tree.root_symbol() in ['PIZZAORDER', 'DRINKORDER']:
            # We only add the default if not already present
            if all(c.root_symbol() != 'NUMBER' for c in tree.children()):
                children = tree.children()
                children.append(ExpressSemanticTree(flat_string=f"(NUMBER 1 )").children()[0])
                return ExpressSemanticTree(root_symbol=tree.root_symbol(), children=children)

        return ExpressSemanticTree(root_symbol=tree.root_symbol(), children=[self._add_defaults(c) for c in tree.children()])

    def resolve_tree_into_TGT(self, tree):
        """
        This simple method wraps up the two steps of resolution for the pizza skill resolver:
        1) resolving entities according to catalog file mapping
        2) setting default NUMBER if absent
        :param tree: (SemanticTree) Input SemanticTree object.
        :return: (ExpressSemanticTree) ExpressSemanticTree which is the input tree resolved and comparable to EXR
        """
        resolved_tree = ExpressSemanticTree(tree_rep=self.resolve_entities(tree).tree_rep)
        return self._add_defaults(resolved_tree)





