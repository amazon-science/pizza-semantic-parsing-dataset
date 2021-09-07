"""
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.  

// SPDX-License-Identifier: CC-BY-NC-4.0
"""
def to_prefix_notation(str_):
    """
    A simple utils method that converts the input string A(B,C(D),E) into the more
    familiar EXR format: (A B (C D ) E ). One extra processing is the upper-casing of
    of non-terminal nodes to match the EXR format convention.
    :param str_: input string to be converted
    :return: str after conversion
    """
    res = []
    str_ = str_.replace(')',' )').replace('(','( ').replace(',', ' ')
    for word in str_.split():
        if word.endswith('('):
            word = '(' + word.strip('(').upper()
        res.append(word)
    return ' '.join(res)


def load_catalog_file(file_path):
    """
    This method loads the content of a catalog file into a dict object.
    :param file_path: (str) the path to a catalog file, for eg. PATH/TO/topping.txt
    :return: (dict) a dict object which keys are the entity values (left column in tries file) and values are the
                    corresponding entity (right column in catalog file).
                    e.g. { 'personal sized' : 'PERSONAL_SIZE',
                           'extra large size' : 'EXTRA_LARGE',
                           'small': 'SMALL',
                              .
                              .
                            }
    """
    mapping = {}
    for line in open(file_path, 'r').readlines():
        line = line.strip()
        if len(line) > 0:
            entity_value, entity_name = line.split('\t')
            mapping[entity_value] = entity_name
    return mapping
