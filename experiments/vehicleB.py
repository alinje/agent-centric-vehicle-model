from tulip.spec import GRSpec
from tulip.transys import FTS, prepend_with
from tulip.synth import synthesize
from tulip.transys import machines
from tulip.dumpsmach import write_python_case

import locUtils as l


def navigationTop(arena):
    """
    @type arena: str
    @param arena: name of map file mapping according to rules:
        - driveable road marked '-'
        - blocked road marked 'X'
        - vehicle start location marked 'S'
        - vehicle target location marked 'T'
    """
    roadNet = {} # arena split in multiple smaller maps which internally has same driving rules
    path = {} # subset of roadnet which vehicle passes through in the initial strategic plan

    pathInfo = {} # conditions to send 

    for pos in roadNet:
        surroundings = {}
        surroundingsPath = {} # path U surroundings
        pathInfo |= {pos: surroundingsPath}

    targetPos = findTargetPos()

    currentPos = initPos
    currentTacticalPlan = initTacticalPlan
    while currentPos != targetPos:
        currentTacticalPlan = agentCentricSpec(pathInfo[currentPos]) # make new tactical planner
        currentPos = runPlan(currentPos, currentTacticalPlan) # run new tactical planner until we are in partial target

def runPlan(startPos, tacticalPlan, finalTarget):
    """
    @return: new position
    """
    currentPos = startPos
    currentTarget = extractCurrentTarget(tacticalPlan)

    while currentPos != currentTarget and currentPos != finalTarget:
        env = collectCurrentEnv()
        move = getMove(tacticalPlan, env)
        execMove(move)

def slimAgentCentricSpec():
    specs = GRSpec()
    return specs

def agentCentricSpec(pathSurroundings):
    # QUE will generic parts of specification be passed down?
    # fed path information from something that has calculated path surroundings for every possible location
    # so a top system has positions and 'global' knowledge
    # such as which lane leeds to the correct
    # hands it down to specification for sensor-area size which calculates move.
    # this only calculates one move? then hands back up




    # differences from classic model:
    #   no variable representing agent pos
    #   variables describe surroundings

    # NLVL obstacle value of moving eq speed, faster, slower, static or non-existing
    # NLVL other environmental context as temparuture, grip etc
    env_vars = {}

    # for loc in l.targetLocations:
    #     env_vars[loc] = 'boolean'

    for loc in l.slimLocations:
        env_vars['o' + loc] = 'boolean' # TODO o+loc results in var 'or' which doesn't work with python gen

    
    sys_vars={ 
        'mlf': 'boolean', 
        'mf': 'boolean',
        'mrf': 'boolean',
    } 


    env_init={
        # does not start in an obstacle
        '! op0l0',
        # nor with no way to go
        l.pathExists,
    }


    sys_init={
        # TODO assuring that next state, the vehicle will have moved
        # QUE does speed need to be explicit then?
        

        }
    

    
    # TODO an obstacle will not appear in previously declared safe space
    # no obstacles exist outside of sensor range - self made here
    

    ############
    # all obstacles move in unison and no obstacles randomly appear
    ############
    # TODO road status, targets same treatment?

    # obstacles moving in unison
    mF = []
    for loc in l.slimForwardRemaining:
        mF.append('(o{0} <-> (X o{1}))'.format(loc, l.forwardMove(loc)))

    mLF = []
    for loc in l.slimLeftForwardRemaining:
        mLF.append('(o{0} <-> (X o{1}))'.format(loc, l.leftForwardMove(loc)))
    
    mRF = []
    for loc in l.slimRightForwardRemaining:
        mRF.append('(o{0} <-> (X o{1}))'.format(loc, l.rightForwardMove(loc)))

    # targets moving in unison
    # for loc in [loc for loc in l.slimForwardRemaining]:
    #     mF.append('(t{0} <-> (X t{1}))'.format(loc, l.forwardMove(loc)))

    # for loc in [loc for loc in l.slimLeftForwardRemaining]:
    #     mLF.append('(t{0} <-> (X t{1}))'.format(loc, l.leftForwardMove(loc)))
    
    # for loc in [loc for loc in l.slimRightForwardRemaining]:
    #     mRF.append('(t{0} <-> (X t{1}))'.format(loc, l.rightForwardMove(loc)))



    env_safe = {

        'mlf <-> ({0})'.format(" && ".join(mLF)),
        'mf <-> ({0})'.format(" && ".join(mF)),
        'mrf <-> ({0})'.format(" && ".join(mRF)),


        # NLVL car is not surrounded (except by moving vehicles (or not?))
        # no barriers blocking the entire cut
        # there is always a path
        # NOTE this is very hard coded
        '(op_1l1 && op1l1) -> ! op0l2',
        '(op_1l1 && (! op1l1)) -> ((! op0l2) || (! op1l1))',
        '((! op_1l1) && op1l1) -> ((! op0l2) || (! op_1l1))',


        # '(tllff || tlff || tff || trff || trrff) -> ! (tlf || tf || trf || ta)',
        # '(tlf || tf || trf) -> ! (tllff || tlff || tff || trff || trrff || ta)',
        # 'ta -> ! (tllff || tlff || tff || trff || trrff || ta || tlf || tf || trf)',
        # 'tff'

    }

    # target only in one cut, then transformed into obstacles
    # for loc in l.forwardAppearing:
    #         env_safe |= {'((! t{0}) && ({1})) -> o{0}'
    #             .format(loc, ' || '.join([locWo for locWo in l.targetLocations if locWo != loc]))}


    # NOTE cannot ensure progression by moving obstacles
    # because there might not be any obstacles
    
    ############

    # stay in lane if possible
    # navigation
    sys_safe={
        # vehicle is always moving
        # but only in one way
        '(mlf && (! mf) && (! mrf)) || ((! mlf) && mf && (! mrf)) || ((! mlf) && (! mf) && mrf)',

        # no collision
        '! op0l0',
        'X (! op0l0)',
        # no moving into dead ends
        'X {0}'.format(l.pathExists),

        # NOTE probably bad form
        # only move left if nec
        '((op1l1 || op1l2) && (! op0l2)) -> mf',

        # move right if pos
        '(! (op1l1 || op1l2)) -> mrf',

        #NLVL attempt to come as close as possible to path obstacle before deciding?

    }

    env_prog={
        # NLVL eventually a target will appear in a reachable state
        # eventually a target will appear in the end of the sensor range
        #'tllff || tlff || tff || trff || trrff',

    }


    sys_prog={
        # eventually the agent will be in a target
        #'ta',
    }

    specs = GRSpec(env_vars, sys_vars, env_init, sys_init,
                env_safe, sys_safe, env_prog, sys_prog)
    
    return specs

specs = agentCentricSpec('')
specs.moore = False
specs.qinit = r'\\A \\E'
specs.plus_one = False

print(specs)

ctrl = synthesize(specs, solver='omega')
assert ctrl is not None, 'specification is unrealizable'
print('realized:')
# print(ctrl)

# if not ctrl.plot():
#     print('can not open in dot')
name = 'agentCentric'

# if not ctrl.save(filename='agentCentric.html'):
#     print('could not save as dot')

# if not ctrl.save(filename='agentCentric.scxml'):
#     print('could not save as scxml')


write_python_case('{0}.py'.format(name), ctrl, classname="VehicleB")

runs = machines.random_run(ctrl, N=1)
print('all done')


