from tulip.spec import GRSpec
from tulip.transys import FTS, prepend_with
from tulip.synth import synthesize

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

def agentCentricSpec():
    # fed path information from something that has calculated surroundings for every position
    # ofc that needs to be done live
    # so a top system has positions and overall knowledge
    # hands it down to specification for sensor-area size which calculates move.
    # this only calculates one move? then hands back up


    target = {}
    # we can't sense road length etc, we might be given some expectations
    # as init step we should probably be given road width?
    roadExpectations = {}




    # differences from classic model:
    #   no variable representing agent pos
    #   variables describe surroundings

    env_vars={
        # path forward, left, forward left, etc.
        'pf', 'pl', 'pfl', 'pr', 'pfr', 
    }
    sys_vars={}
    env_init={}
    sys_init={}
    env_safe={}

    # stay in lane if possible
    sys_safe={}
    env_prog={}


    # TODO declared here: everything will shuffle?
    sys_prog={}

    specs = GRSpec(env_vars, sys_vars, env_init, sys_init,
                env_safe, sys_safe, env_prog, sys_prog)

def obstacleAgentCentricSpec():
    # TODO starting pos is not blocked

    env_init = {}

    # TODO an obstacle will not appear in previously declared safe space
    # no obstacles exist outside of sensor range - self made here
    # road is not blocked
    # obstacle does not disappear
    env_safe = {}

    # TODO assuring that next state, the vehicle will have moved
    # does not start in an obstacle
    sys_init = {}

    # TODO no collision
    # stay in lane if possible
    # navigation
    sys_safe = {}

    # being overtaken
    sys_safe |= {}
    # obstacle: overtake 

