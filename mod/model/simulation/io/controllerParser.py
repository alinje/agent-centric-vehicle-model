    

import hashlib
import json
import re
import time
from typing import Any, Callable

import regex


def scxml2dict(scxmlFileName, inputHash: Callable[[dict[str,Any]],str], outputKeys: list[str], useRegex: bool=False) -> tuple[dict[str,dict[str,dict[str,str]]],str]:
    """ Reads .scxml file representing a controller to a dictionary.

    Args:
        scxmlFileName (str): Path to input file.
        outputKeys (list[str]): List of output variables. Raises KeyError if variable value not provided in every transition. No output can be called `newState`.
        useRegex (bool): Choose to use slower regex search for parsing file in place of parsing with distinct string indices. Use regex search if it appears broken.
    
    Returns:
        tuple[dict[str,dict[str,dict[str,str]]],str]: Tuple of dictionary and string. 
        Dictionary from state to a dictionary from a hash of input values to a dictionary of output variables to their values. Hashed by method inputHash below. The new state is added to the ouput dictionary under the key `newState`.
        String representing initial state.
        
    Raises:
        KeyError: If outputKeys contains variable not given in each transition or if `newState` is listed as an output variable.

    """
    if outputKeys.count('newState') > 0:
        raise KeyError('Output key "newState" is reserved.')
    time1 = time.time()
    file = open(scxmlFileName, "r")
    state2trans = {}
    line = file.readline()
    while '<scxml' not in line:
        line = file.readline()
    initState = re.search(r'initial="(?P<initState>\w+)"', line).group('initState')
    line = file.readline()
    while '</scxml>' not in line:
        # stM = re.search(r'id="(?P<state>\w+)"', line)
        stId = line[12:-3]
        # if stM is None:
        #     print(stM)
        # stId = stM.group('state')
        trans = {}
        file.readline() # transition opening tag
        while '</state>' not in line:
            file.readline() # event prop
            # condsStr = re.search(r'cond=\"(\{\D+\})\"', graph.pop(0))
            line = file.readline()
            condsStr = line[9:-3]
            # if condsStr is None:
                # raise Exception()
            varsSplit = condsStr[1:-1].split(',')
            variables = {varName: _parseValue(varVal) for (varName, varVal) 
                         in regex.findall(r'\w?\'(?P<varName>\w+)\': (?P<varValue>\'?\w+\'?)', condsStr)}
            # fixCondsStr = condsStr.replace("'", '"').replace("False", '"False"').replace("True", '"True"')
            # variables: dict[str,Any] = json.loads(fixCondsStr)
            # value is dictionary of ouput variables
            outputs = _extractOutputs(variables, outputKeys)

            # the new state is added in the dictionary
            line = file.readline() # target prop
            newState = line[11:-3]
            outputs.update({'newState': newState})

            # key is hash of input variables
            key = inputHash(variables)
            trans[key] = outputs

            file.readline() # closing tag
            line = file.readline() # next transition opening tag or state closing tag

        line = file.readline() # next state opening tag or scxml closing tag
        state2trans[stId] = trans
    file.close()
    time2 = time.time()
    print(f'Read dictionary in {time2-time1}.')
    return (state2trans, initState)

def _parseValue(value: str) -> Any:
    if value.isdigit(): return int(value)
    if value == 'True' or value == 'False': return value == 'True'
    return value[1:-1]

def _extractOutputs(varsDict: dict[str,Any], outputKeys: list[str]) -> dict[str,Any]:
    return {key: varsDict.pop(key) for key in outputKeys}
