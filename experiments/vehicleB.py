from tulip.spec import GRSpec
from tulip.transys import FTS, prepend_with
from tulip.synth import synthesize

import locUtils as l

def agentCentricStraightFTS():
    ts = FTS()
    ts.atomic_propositions.add_from(['agent', 'path', 'possPath']) # QUE !possPath enough to mark obstacle? might help w moving obstacles
    # TODO navigation aim another prop?

    # NOTE zoning might not have to be fixed size tiles, can be domain dependent?
    ts.states.add_from({'a', 
                        'l', 'll',
                        'lf', 'llf', 'lff', 'llff',
                        'f', 'ff',
                        'rf', 'rrf', 'rff', 'rrff',
                        'r', 'rr',
                        'rb', 'rrb', 'rbb', 'rrbb',
                        'b', 'bb',
                        'lb', 'llb', 'lbb', 'llbb'})
    
    ts.transitions.add('a', 'f', 'forward') # NOTE wait no this is dumb?
    # QUE what are the states here?
    # like what properties that are true in that position
    
    # i guess an action should just change all

def navigationTop():
    roadNet = {}
    path = {} # subset of roadnet

    pathInfo = {}

    for pos in roadNet:
        surroundings = {}
        surroundingsPath = {} # path U surroundings
        pathInfo |= {pos: surroundingsPath}


    currentPos = {}
    while True:
        currentPos = agentCentricSpec(pathInfo[currentPos])


def agentCentricSpec(pathSurroundings):
    # QUE will generic parts of specification be passed down?
    # fed path information from something that has calculated path surroundings for every possible location
    # so a top system has positions and 'global' knowledge
    # such as which lane leeds to the correct
    # hands it down to specification for sensor-area size which calculates move.
    # this only calculates one move? then hands back up

    # what can be given
    # path forward, left, forward left, etc.
    # 'pf', 'pl', 'pfl', 'pr', 'pfr',




    # differences from classic model:
    #   no variable representing agent pos
    #   variables describe surroundings

    # NLVL obstacle value of moving eq speed, faster, slower, static or non-existing
    # NLVL other environmental context as temparuture, grip etc
    env_vars = l.obstacleLocations + l.targetLocations

    # NLVL speed, 
    sys_vars={ 
        #'moving': 'boolean',
    } 
    
    # TODO starting pos is not blocked
    env_init={
        # does not start in an obstacle
        '! oa',

    }



    sys_init={
        # TODO assuring that next state, the vehicle will have moved
        # does speed need to be explicit then?
        }
    

    
    # TODO an obstacle will not appear in previously declared safe space
    # no obstacles exist outside of sensor range - self made here
    
    env_safe={
        # road is not blocked
        '(! olf) || (! of) || (! orf)'
    }
    ############
    # all obstacles move in unison and no obstacles randomly appear
    # TODO road status, targets same treatment?

    mF = []
    for loc in l.forwardRemaining:
        mF.append('(o{0} <-> X o{1})'.format(loc, l.forwardMove(loc)))
        mF.append('(t{0} <-> X t{1})'.format(loc, l.forwardMove(loc)))

    mLF = []
    for loc in l.leftForwardRemaining:
        mLF.append('(o{0} <-> X o{1})'.format(loc, l.leftForwardMove(loc)))
        mLF.append('(t{0} <-> X t{1})'.format(loc, l.leftForwardMove(loc)))
    
    mRF = []
    for loc in l.rightForwardRemaining:
        mRF.append('(o{0} <-> X o{1})'.format(loc, l.rightForwardMove(loc)))
        mRF.append('(t{0} <-> X t{1})'.format(loc, l.rightForwardMove(loc)))

    env_safe = {
        '<->'.join(mF),
        '<->'.join(mLF),
        '<->'.join(mRF),
    }
    
    ############

    # stay in lane if possible
    # navigation
    sys_safe={
        # no collision
        '! oa',

        # no next state collision
        
    }

    env_prog={}


    # TODO declared here: everything will shuffle?
    sys_prog={
        # eventually the agent will be in a target
        'ta'
    }

    specs = GRSpec(env_vars, sys_vars, env_init, sys_init,
                env_safe, sys_safe, env_prog, sys_prog)
    
    return specs

specs = agentCentricSpec('')
specs.moore = True
specs.qinit = r'\E \A'
ctrl = synthesize(specs)
assert ctrl is not None, 'specification is unrealizable'

if not ctrl.save('agentCentric'):
    print(ctrl)

