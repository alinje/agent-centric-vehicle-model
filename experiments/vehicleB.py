from tulip.spec import GRSpec
from tulip.transys import FTS, prepend_with
from tulip.synth import synthesize
from tulip.transys import machines

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
    env_vars = {}

    for loc in l.targetLocations:
        env_vars[loc] = 'boolean'

    for loc in l.obstacleLocations:
        env_vars[loc] = 'boolean'

    # NLVL speed, 
    sys_vars={ 
        'moving': 'boolean',
    } 
    
    env_init={
        'oll',
        # does not start in an obstacle
        '! oa',
        # nor with no way to go
        '!(olf && of && orf)',

        # we don't start in a target, rendering the controller useless
        '! ta'
    }



    sys_init={
        # TODO assuring that next state, the vehicle will have moved
        # QUE does speed need to be explicit then?
        
        # obstacle in the other lane of the starting cut
        # QUE why

        # does not start in an obstacle
        #'! oa',
        # nor with no way to go
        #'(! olf) || (! of) || (! orf)',
        }
    

    
    # TODO an obstacle will not appear in previously declared safe space
    # no obstacles exist outside of sensor range - self made here
    
    # env_safe={
    #     # road is not blocked
    #     '(! olf) || (! of) || (! orf)',
    #     #'X ((! olf) || (! of) || (! orf))'
    # }
    ############
    # all obstacles move in unison and no obstacles randomly appear
    ############
    # TODO road status, targets same treatment?

    # obstacles moving in unison
    mF = []
    for loc in l.forwardRemaining:
        mF.append('(o{0} <-> X o{1})'.format(loc, l.forwardMove(loc)))

    mLF = []
    for loc in l.leftForwardRemaining:
        mLF.append('(o{0} <-> X o{1})'.format(loc, l.leftForwardMove(loc)))
    
    mRF = []
    for loc in l.rightForwardRemaining:
        mRF.append('(o{0} <-> X o{1})'.format(loc, l.rightForwardMove(loc)))

    # targets moving in unison
    for loc in [loc for loc in l.forwardRemaining if 'f' in loc]:
        mF.append('(t{0} <-> (X t{1}))'.format(loc, l.forwardMove(loc)))

    for loc in [loc for loc in l.leftForwardRemaining if 'f' in loc]:
        mLF.append('(t{0} <-> (X t{1}))'.format(loc, l.leftForwardMove(loc)))
    
    for loc in [loc for loc in l.rightForwardRemaining if 'f' in loc]:
        mRF.append('(t{0} <-> (X t{1}))'.format(loc, l.rightForwardMove(loc)))

    # if things have appeared in the leftmost or rightmost places
    # we know there has been a left or right shift respectively
    # QUE very controlled env vars for this? does it matter for computing?
    # BUG can also have slided in from inner court
    # confirmedLeftForward = ' && '.join(mLF)
    # for loc in l.uniqueLeftForwardAppearing:
    #     env_safe |= {'X o{0} -> (({1}) || )'.format(loc, confirmedLeftForward)}
    
    # confirmedRightForward = ' && '.join(mRF)
    # for loc in l.uniqueRightForwardAppearing:
    #     env_safe |= {'X o{0} -> ({1})'.format(loc, confirmedRightForward)}

    # confirmedForward = ' && '.join(mF)
    # things should not appear with no trace in any place but the outermost sensor places
    # for loc in l.alreadySensedSpace:
    #     env_safe |= {
    #         '(X o{0}) -> (({0}) || ({1}) || ({2}))'
    #             .format(loc, confirmedLeftForward, confirmedForward, confirmedRightForward)
    #         # '(X o{0}) -> (o{1} || o{2} || o{3})'
    #         #     .format(loc, l.leftForwardMove(loc), l.forwardMove(loc), l.rightForwardMove(loc))
    #     }


    env_safe = {
        '(moving -> ({0}) || ({1}) || ({2}))'.format(
            ' && '.join(mF),
            ' && '.join(mLF),
            ' && '.join(mRF)), # QUE this is kinda also progression

        # NLVL remove
        # no barriers blocking the entire cut
        '! (ollff && olff && off && orff && orrff)',
        # once a target appears, it never disappears again
        # NLVL there might be a barrier?
        #'({0}) -> (X ({0}))'.format(' || '.join(l.targetLocations)),
        #'(tllff || tlff || tff || trff || trrff) <-> (X (tllf || tlf || tf || trf || trrf))',
        #'(tllf || tlf || tf || trf || trrf) <-> (X (tll || tl || ta || tr || trr))',
        '(tllff && tlff && tff && trff && trrff) || ((! tllff) && (! tlff) && (! tff) && (! trff) && (! trrff))',
        # '!(tllb || tlb || tb || trb || trrb || tllbb || tlbb || tbb || trbb || trrbb)'
        # there will always be some progression, guaranteed by there always being an obstacle
        #' || '.join(l.obstacleLocations),

        # NLVL remove
        # the road will never be fully blocked
        #'!({0})'.format(' && '.join(['o' + loc for loc in l.forwardAppearing]))
    }


    # NOTE cannot ensure progression by moving obstacles
    # because there might not be any obstacles
    
    ############

    # stay in lane if possible
    # navigation
    sys_safe={
        # no collision
        #'! oa',
        # no obstacle front of car 
        '! of',
        # no next state collision
        '(olf || of || orf) -> (X (! oa))', # QUE why this formulation?

        # only move left if nec
        '(off && orf) -> {0}'.format(' && '.join(mLF)),

        # move right if pos
        #'()'

        #'moving',

        # road is not blocked
        #'!(olf && of && orf)',

        # TODO only one move / no appearign

        # NLVL 

    }

    env_prog={
        # NLVL eventually a target will appear in a reachable state
        # eventually a target will appear in the end of the sensor range
        # 'tllff || tlff || tff || trff || trrff'
        'tllff && tlff && tff && trff && trrff'

    }


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
print(specs)

ctrl = synthesize(specs)
assert ctrl is not None, 'specification is unrealizable'
print('realized')



if not ctrl.save(filename='agentCentric', fileformat='svg'):
   print(ctrl)

# print(ctrl)
runs = machines.random_run(ctrl, N=10)
print(runs)

