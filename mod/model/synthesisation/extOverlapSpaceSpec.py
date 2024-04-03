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

    env_safe = {
        # obstacles moving in unison
        f'(move = "shift_left_forward") -> ({' && '.join(l.leftForwardObstaclesTransitions())})',
        f'(move = "forward") -> ({' && '.join(l.forwardObstaclesTransitions())})',
        f'(move = "shift_right_forward") -> ({' && '.join(l.rightForwardObstaclesTransitions())})',
        f'(move = "halt") -> ({' && '.join(l.haltObstaclesTransitions())})',

        # moving obstacles can not merge
        # not meeting and passing at the same time
        '!(olff && olb)',
        '((move = "halt" || move = "forward") && olff) -> X (! olb)',
        '((move = "halt" || move = "forward") && olb) -> X (! olff)',
        # meeting two obstacles
        '((move = "halt") && olff && olf) -> X (olf && (! olb))', 
        # being passed by two obstacles
        '((move = "halt") && olb && olf) -> X (olf && (! olff))',
        '((move = "forward") && olf && olb) -> X (olf && (! olff))',

        # can not get locked in with offroad left and obstacles forward and right forward
        '!(olf && (! olff) && (! olb) && of && orf)', 
        # f'(olf && (! olff) && (! olb) && of && orf) -> (! (X {l.leftForwardPossiblyBlocked()}))', # TODO one might have to wait longer than to next round bf clear
        # '!(olf && olb)',

    }

    sys_safe = {
        # no collision
        '! oa',
        # moves if possible
        f'{l.pathExistsGuaranteed()} -> (! (move = "halt"))',
    }

    env_prog = l.pathWillExist()
    sys_prog = {
        # inf often we will progress towards the goal
        l.pathProgression(),
    }

    spec = GRSpec(env_vars, sys_vars, env_init, sys_init,
                  env_safe, sys_safe, env_prog, sys_prog)
    
    return spec


