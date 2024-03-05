import re

locations = {'a', 
             'l', 'll',
             'lf', 'llf', 'lff', 'llff',
             'f', 'ff',
             'rf', 'rrf', 'rff', 'rrff',
             'r', 'rr',
             'rb', 'rrb', 'rbb', 'rrbb',
             'b', 'bb',
             'lb', 'llb', 'lbb', 'llbb'}

slimLocations = {'p0l0', 
                 'p_1l0', 
                 'p_1l1', 'p_1l2', 'p_2l2',
                 'p0l1', 'p0l2',
                 'p1l1', 'p1l2', 'p2l2',
                 'p1l0'}


obstacleLocations = ['o' + loc for loc in locations]
pathLocations     = ['p' + loc for loc in locations] # don't know yet if we refer to passed path as path
altPathLocations  = ['a' + loc for loc in locations] # some locations will get one off path. others are alt paths
roadLocations     = ['r' + loc for loc in locations]



nonAgentLocations = [loc for loc in locations if loc != 'a']

def forwardMove(loc):
    loc = loc.replace("_", "-")
    parts = list(filter(None, re.split('[pl]', loc)))
    return f'p{str(int(parts[0])).replace("-", "_")}l{str(int(parts[1])-1).replace("-", "_")}'

def leftForwardMove(loc):
    loc = loc.replace("_", "-")
    parts = list(filter(None, re.split('[pl]', loc)))
    return f'p{str(int(parts[0])+1).replace("-", "_")}l{str(int(parts[1])-1).replace("-", "_")}'

def rightForwardMove(loc):
    loc = loc.replace("_", "-")
    parts = list(filter(None, re.split('[pl]', loc)))
    return f'p{str(int(parts[0])-1).replace("-", "_")}l{str(int(parts[1])-1).replace("-", "_")}'

# NLVL rotations

forwardRemaining = [loc for loc in locations if 'bb' not in loc]

leftForwardRemaining = [loc for loc in forwardRemaining if 'rr' not in loc]

rightForwardRemaining = [loc for loc in forwardRemaining if 'll' not in loc]

slimForwardRemaining = ['p0l2', 'p_1l2', 'p1l2', 'p_1l1', 'p0l1', 'p1l1']

slimLeftForwardRemaining = ['p0l2', 'p_1l2', 'p_1l1', 'p0l1', 'p_2l2']

slimRightForwardRemaining = ['p0l2', 'p1l2', 'p1l1', 'p0l1', 'p2l2']

forwardAppearing = [loc for loc in locations if 'ff' in loc]

leftForwardAppearing = [loc for loc in locations if ('ll' in loc or 'ff' in loc)]

rightForwardAppearing = [loc for loc in locations if ('rr' in loc or 'ff' in loc)]

uniqueLeftForwardAppearing = [loc for loc in leftForwardAppearing if 'll' in loc]

uniqueRightForwardAppearing = [loc for loc in rightForwardAppearing if 'rr' in loc]

alreadySensedSpace = [loc for loc in locations if ('ll' not in loc and 'ff' not in loc and 'rr' not in loc)]

##################################
pathExists = '(! op0l1) && ((! op0l2) || ((! op_1l1) && (!op_1l2)) || ((! op1l1) && (! op1l2)))'


##################################

# maybe targets can be in only one cut
targetLocations   = ['t' + loc for loc in forwardAppearing]

############# tests ##############

def test():
    pass
    # print(forwardRemaining)
    # print([forwardMove(loc) for loc in forwardRemaining])

    # print(leftForwardRemaining)
    # print([leftForwardMove(loc) for loc in leftForwardRemaining])

    # print(leftForwardMove('f'))

    # print(rightForwardRemaining)
    # print([rightForwardMove(loc) for loc in rightForwardRemaining])

test()