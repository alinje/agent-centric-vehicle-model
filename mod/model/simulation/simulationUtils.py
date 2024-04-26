

import hashlib
import json


def inputHash(inp: dict[str,str]) -> str:
    """ Hash function for dictionary, implemented from solution by Nuric: 
    https://www.doc.ic.ac.uk/~nuric/posts/coding/how-to-hash-a-dictionary-in-python/"""
    dictHash = hashlib.md5()
    encoded = json.dumps(inp, sort_keys=True).encode()
    dictHash.update(encoded)
    return dictHash.hexdigest()