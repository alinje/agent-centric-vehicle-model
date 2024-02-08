
# NLVL one should decide sensor range on case, e.g. '3l5f'
locations = {'a', 
             'l', 'll',
             'lf', 'llf', 'lff', 'llff',
             'f', 'ff',
             'rf', 'rrf', 'rff', 'rrff',
             'r', 'rr',
             'rb', 'rrb', 'rbb', 'rrbb',
             'b', 'bb',
             'lb', 'llb', 'lbb', 'llbb'}


obstacleLocations = ['o' + loc for loc in locations]
pathLocations     = ['p' + loc for loc in locations] # don't know yet if we refer to passed path as path
altPathLocations  = ['a' + loc for loc in locations] # some locations will get one off path. others are alt paths
roadLocations     = ['r' + loc for loc in locations]
targetLocations   = ['t' + loc for loc in locations]

nonAgentLocations = [loc for loc in locations if loc != 'a']

def forwardMove(loc):
    if loc=='f':
        return 'a'
    if loc=='a':
        return 'b'
    if 'f' in loc:
        return loc[:len(loc)-1]
    return loc + 'b'

def forwardMoveNoAgent(loc):
    return forwardMove(loc).replace('a', '')

def leftForwardMove(loc):
    if loc=='lf':
        return 'a'
    if loc=='a':
        return 'rb'
    if 'l' in loc:
        return forwardMoveNoAgent(loc)[1:]
    return 'r' + forwardMoveNoAgent(loc)

def rightForwardMove(loc):
    if loc=='rf':
        return 'a'
    if loc=='a':
        return 'lb'
    if 'r' in loc:
        return forwardMoveNoAgent(loc)[1:]
    return 'l' + forwardMoveNoAgent(loc)

# TODO rotations

forwardRemaining = [loc for loc in locations if 'bb' not in loc]

leftForwardRemaining = [loc for loc in forwardRemaining if 'rr' not in loc]

rightForwardRemaining = [loc for loc in forwardRemaining if 'll' not in loc]

forwardAppearing = [loc for loc in locations if 'ff' in loc]


############# tests ##############

def test():
    # print(forwardRemaining)
    # print([forwardMove(loc) for loc in forwardRemaining])

    print(leftForwardRemaining)
    print([leftForwardMove(loc) for loc in leftForwardRemaining])

    print(leftForwardMove('f'))

    # print(rightForwardRemaining)
    # print([rightForwardMove(loc) for loc in rightForwardRemaining])

test()