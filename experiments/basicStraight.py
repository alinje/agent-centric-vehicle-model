from tulip.spec import GRSpec
from tulip.transys import FTS, prepend_with
from tulip.synth import synthesize

from scipy import sparse

roadLength = 5
stateAmount = roadLength*3


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

# print the finite transition model
print(sys_sws)

# now, environment variables

# direction of legal travel, should be same as one is heading
env_vars={'w','e'}
# oi - boolean indicating obstacle in position i
#env_vars={"o1", "o2", ..., "om"},
env_vars=set()
env_init=set()
env_prog=set() # QUE stuff that happens inf often?
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

# TODO format output files
# work on specification
# transition model prob ok
# brum
# functional decomposition