from tulip.spec import GRSpec
from space import ExtOverlapZone as l
from space import ExtOverlapZoneType as zt

def overlapSpaceSpec() -> GRSpec:
    env_vars = {l.overlapZoneString(k): v for k, v in l.obstaclesDict().items()}

    
    sys_vars = {
        'move': [
            'halt',
            'shift_left_forward',
            'forward',
            'shift_right_forward',
        ],
        # 'mh': 'boolean', # brake
        # 'mlf': 'boolean', 
        # 'mf': 'boolean',
        # 'mrf': 'boolean',
    }

    env_init = {
        # does not start in an obstacle
        'a != "present"',
        # nor with no possible opening
        l.pathCanExist(),
    }

    sys_init = {}

    # obstacles moving in unison
    env_safe = {
        f'move = "shift_left_forward" -> ({' && '.join(l.leftForwardObstaclesTransitions())})',
        f'move = "forward" -> ({' && '.join(l.forwardObstaclesTransitions())})',
        f'move = "shift_right_forward" -> ({' && '.join(l.rightForwardObstaclesTransitions())})',
        f'move = "halt" -> ({' && '.join(l.haltObstaclesTransitions())})',

        l.pathCanExist(),

        # TODO dif env obs should not melt together
    }

    sys_safe = {
        # no collision
        'a != "present"',

        # only move left if nec
        f'({l.rightForwardBlocked()} && {l.forwardBlocked()} && ! {l.leftForwardBlocked()}) -> move = "shift_left_forward"',

        # move right if pos
        f'(! {l.rightForwardBlocked()}) -> move = "shift_right_forward"',

        # otherwise move left
        f'({l.rightForwardBlocked()} && (! {l.forwardBlocked()})) -> move = "forward"',
    }

    env_prog = {
        # inf often a path will exist
        l.pathExists(),
    }
    sys_prog = {
        # inf often we will progress towards the goal
        l.pathProgression(),
    }

    spec = GRSpec(env_vars, sys_vars, env_init, sys_init,
                  env_safe, sys_safe, env_prog, sys_prog)
    
    return spec


