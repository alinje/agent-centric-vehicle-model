
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

slimLocations = {'a', 
                 'l', 
                 'lf', 'lff', 'llff',
                 'f', 'ff',
                 'rf', 'rff', 'rrff',
                 'r'}


obstacleLocations = ['o' + loc for loc in locations]
pathLocations     = ['p' + loc for loc in locations] # don't know yet if we refer to passed path as path
altPathLocations  = ['a' + loc for loc in locations] # some locations will get one off path. others are alt paths
roadLocations     = ['r' + loc for loc in locations]

# maybe targets can be in only one cut
targetLocations   = ['t' + loc for loc in locations if 'b' not in loc]

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

# NLVL rotations

forwardRemaining = [loc for loc in locations if 'bb' not in loc]

leftForwardRemaining = [loc for loc in forwardRemaining if 'rr' not in loc]

rightForwardRemaining = [loc for loc in forwardRemaining if 'll' not in loc]

slimForwardRemaining = ['ff', 'lff', 'rff', 'lf', 'f', 'rf']

slimLeftForwardRemaining = [loc for loc in slimForwardRemaining if 'r' not in loc]

slimRightForwardRemaining = [loc for loc in slimForwardRemaining if 'l' not in loc]

forwardAppearing = [loc for loc in locations if 'ff' in loc]

leftForwardAppearing = [loc for loc in locations if ('ll' in loc or 'ff' in loc)]

rightForwardAppearing = [loc for loc in locations if ('rr' in loc or 'ff' in loc)]

uniqueLeftForwardAppearing = [loc for loc in leftForwardAppearing if 'll' in loc]

uniqueRightForwardAppearing = [loc for loc in rightForwardAppearing if 'rr' in loc]

alreadySensedSpace = [loc for loc in locations if ('ll' not in loc and 'ff' not in loc and 'rr' not in loc)]

##################################
pathExists = '(! of) && ((! off) || ((! olf) && (! olff)) || ((! orf) && (! orff)))'


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