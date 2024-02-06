from tulip.spec import GRSpec
from tulip.transys import FTS, prepend_with
from tulip.synth import synthesize

from scipy import sparse

roadLength = 5
stateAmount = roadLength*3

# transition model of a straight road with no obstacles
def straightRoad(roadLength):
    sys_sws = FTS()
    sys_sws.atomic_propositions.add_from(['start','end'])


    states = prepend_with(list(range(stateAmount)), 's')
    sys_sws.states.add_from(set(states))
    # label the beginning and end of each lane
    sys_sws.states.add('s0',ap={'start'})
    sys_sws.states.add('s'+str(len(states)-3),ap={'end'})
    sys_sws.states.add('s'+str(len(states)-1),ap={'start'})
    sys_sws.states.add('s2', ap={'end'})

    sys_sws.states.initial.add_from({'s0','s'+str(len(states)-1)})


    # env actions, atm none
    #sys_sws.env?

    # transitions between adjacent road pieces
    # only in the correct direction of travel
    # should adjust for speed
    sys_sws.sys_actions.add_from({'plus','minus','halt'})
    #transitions = set()
    for i in range(len(states)):
        if i%3 == 0 and i < len(states)-3:
            sys_sws.transitions.add('s'+str(i), 's'+str(i+3), sys_actions='plus')
        elif i%3 == 2 and i > 2:
            sys_sws.transitions.add('s'+str(i),'s'+str(i-3), sys_actions='minus')

        # one can halt everywhere but on the line dividing the lanes
        if i%3 != 1:
            sys_sws.transitions.add('s'+str(i),'s'+str(i), sys_actions='halt')
    return sys_sws

# trajectory planner
def shortHorizon(horizonLength, roadLength, roadWidth):
    # W here is a promise of continoued forward progression
    shProb = []

    w = []
    for i in range(0, roadLength):
        env_vars={'obs': range(0,roadLength)}

        # is in a target state
        for ts in range(i*roadWidth, i*roadWidth +3):
            w.append('s' + str(ts))

        # invariant Phi
            

        sys_vars = {}

        

        shs = GRSpec(env_vars, sys_vars, env_init, sys_init,
                     env_safe, sys_safe, env_prog, sys_prog)
        w.append(shs)

    # set F(W)
    for i in range(0, roadLength):
        w[i].setFW(w[min([roadLength-1, i+horizonLength-1])]) # function does not exist
    return w
        

# goal generator
def longHorizon(roadLength, roadWidth):


    dynamics = straightRoad(roadLength)

    env_vars={'obs': range(0,roadLength)} # one obstacle at a time
    sys_vars={}
    env_init={}

    sys_init={}
    env_safe={}

    # obstacle not in starting pos
    stms = []
    for vpos in range(0, roadLength*roadWidth):
        #for opos in range(max([0,vpos-1]), min([roadLength, vpos+2])):
        stms.append('(( s{0} ) -> !(obs != {0} ))'.format(vpos))



    sys_safe={}
    env_prog={}

    # eventually reach end
    sys_prog={}

    specs = GRSpec(env_vars, sys_vars, env_init, sys_init,
                   env_safe, sys_safe, env_prog, sys_prog)
    return specs

# attempt to imitate
def rhc():
    ts = basicStraight(5)

    #environment assumption φe encapsulates the following statements which are assumed to hold in any execution: 
    #(A1) obstacles may not block a road; 
    #(A2) an obstacle is detected before the vehicle gets too close to it, i.e., an obstacle may not instantly pop up right in front of the vehicle; 
    #(A3) sensing range is limited, i.e., the vehicle cannot detect an obstacle that is away from it farther than certain distance.
    #(A4) to make sure that the stay-in-lane property is achievable, we assume that an obstacle does not disappear while the vehicle is in its vicinity; 
    #(A5) obstacles may not span more than a certain number of consecutive cells in the middle of the road; 
    #(A6) each of the intersections is clear infinitely often; and 
    #(A7) each of the cells marked by star and its adjacent cells are not occupied by an obstacle infinitely often.
    roadLength = 25
    roadWidth = 3
    specs = longHorizon(roadLength, roadLength)
    shs = shortHorizon(5, roadLength, roadWidth)

    planner = synthesize(specs)

    
    # TODO the vehicle starts from an obstacle-free cell on R1 with at least one obstacle-free cell adjacent to it
    sys_init = {} 

# synthesis of a straight road with no obstacles
def basicStraight():
    sys_sws = straightRoad(5)

    # print the finite transition model
    print(sys_sws)

    # now, environment variables

    # direction of legal travel, should be same as one is heading
    env_vars={'w','e'}
    # oi - boolean indicating obstacle in position i
    #env_vars={"o1", "o2", ..., "om"},
    env_vars=set()
    env_init=set()
    env_prog=set()
    env_safe=set() # specifies the assumption about the evolution of the environment state


    # specification
    # first step: start in one of the starts, get to one of the ends
    # sys_prog = {''}

    # s -position, p - which direction on the road one is heading, 
    sys_vars = {"l", "r"}
    sys_init = {'start'} # this could be either starting point
    sys_safe = {'((end -> (X end)))'} # specifies safety requirement
    sys_prog = {'end'}



    specs = GRSpec(env_vars, sys_vars, env_init, sys_init,
                env_safe, sys_safe, env_prog, sys_prog)

    specs.moore = True
    specs.qinit = r'\E \A'

    # synthesis
    ctrl = synthesize(specs, sys=sys_sws) # NOTE undeterministically creates a machine for travel either west or east 
    assert ctrl is not None, 'specification is unrealizable'

    if not ctrl.save('basicStraight'):
        print(ctrl)

    # TODO
    # work on specification
    # transition model prob ok
    # brum
    # functional decomposition
        
basicStraight()