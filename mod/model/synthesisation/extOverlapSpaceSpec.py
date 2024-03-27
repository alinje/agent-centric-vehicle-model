from tulip.spec import GRSpec
from model.space.extOverlapSpace import ExtOverlapZone as l

def overlapSpaceSpec() -> GRSpec:
    env_vars = {f'o{l.zoneString[k]}': v for k, v in l.obstaclesDict().items()}

    
    sys_vars = {
        'move': [
            'halt',
            'shift_left_forward',
            'forward',
            'shift_right_forward',
        ],
    }

    env_init = {
        # does not start in an obstacle
        '! oa',
    }

    sys_init = {}

    # obstacles moving in unison
    env_safe = {
        f'(move = "shift_left_forward") -> ({' && '.join(l.leftForwardObstaclesTransitions())})',
        f'(move = "forward") -> ({' && '.join(l.forwardObstaclesTransitions())})',
        f'(move = "shift_right_forward") -> ({' && '.join(l.rightForwardObstaclesTransitions())})',
        f'(move = "halt") -> ({' && '.join(l.haltObstaclesTransitions())})',
    }

    sys_safe = {
        # no collision
        '! oa',
        # moves if possible
        f'{l.pathExistsGuaranteed()} -> ! (move = "halt")',
    }

    env_prog = {
        # inf often a path will exist
        l.pathExistsGuaranteed(),
    }
    sys_prog = {
        # inf often we will progress towards the goal
        l.pathProgression(),
    }

    spec = GRSpec(env_vars, sys_vars, env_init, sys_init,
                  env_safe, sys_safe, env_prog, sys_prog)
    
    return spec


