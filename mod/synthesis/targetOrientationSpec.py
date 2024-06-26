from tulip.spec import GRSpec

def leftTurnBlockedSpec() -> GRSpec:
    env_vars = {
        'olf':   'boolean', # static, oncoming and overtaking obstacles to the left and slightly forward of the agent
        'olff':  'boolean', # oncoming obstacles to the left and further forward of the agent
        'olb':   'boolean', # overtaking obstacles to the left and besides and slightly behind the agent

    }

def targetOrientationSpec() -> GRSpec:
    env_vars = {
        # obstacle occupancies
        'olf':   'boolean', # static, oncoming and overtaking obstacles to the left and slightly forward of the agent
        'olff':  'boolean', # oncoming obstacles to the left and further forward of the agent
        'olb':   'boolean', # overtaking obstacles to the left and besides and slightly behind the agent
        'of':    'boolean', # static obstacles in front of the agent
        'oa':    'boolean', # obstacles colliding or risking collision with the agent
        'orf':   'boolean', # static obstacles to the right and slightly forward of the agent
       
        'ofc':   'boolean', # obstacles with paths risking to perpendicularily cross forward or left movement of the agent
        # 'olc':   'boolean', # obstacles with paths risking to cross left turn movement of the target

        'olt':   'boolean', # obstacles that prevents a left turn of the agent
        'ort':   'boolean', # obstacles that prevents a right turn of the agent

        # orientation of the target location: left, forward or right
        'target': [
            't_l',
            't_f',
            't_r',
            't', # BUG in tulip, should not exist: https://github.com/tulip-control/tulip-control/issues/238
        ],
    }
    
    sys_vars = {
        'move': [
            'm_slf',
            'm_f',
            'm_srf',
            'm_h',
            'm_tl',
            'm_tr',
        ],
    }

    env_init = {
        # does not start in an obstacle
        '! oa',
    }

    sys_init = {}

    leftForwardObstaclesTransitions = [
        '((X oa) <-> (olf || olb || olff || ofc))',
        '(of <-> X orf)',
        '(((! olf) && olt) -> (X (! olb)))',

    ]
    forwardObstaclesTransitions = [
        '((of || ofc) <-> X oa)',
    ]
    rightForwardObstaclesTransitions = [
        '((orf || ofc) <-> X oa)',
        '(of -> X olf)',
    ]
    haltObstaclesTransitions = [
        '(olff -> X olf)',
        '(olb -> X olf)',
        '((X olf) -> (olff || olf || olb))',
        '(oa <-> (X oa))',
        '(of <-> X of)',
        '(orf <-> X orf)',
        
    ]

    leftTurnObstaclesTransitions = [
        '((olff || ofc || olt) <-> X oa)',
    ]
    rightTurnObstaclesTransitions = [
        '(ort <-> X oa)',
        '((orf && (! ort)) -> X olb)',
    ]

    env_safe = {
        # obstacles moving in unison
        f'(move = "m_slf") -> ({' && '.join(leftForwardObstaclesTransitions)})',
        f'(move = "m_f") -> ({' && '.join(forwardObstaclesTransitions)})',
        f'(move = "m_srf") -> ({' && '.join(rightForwardObstaclesTransitions)})',
        f'(move = "m_h") -> ({' && '.join(haltObstaclesTransitions)})',
        f'(move = "m_tl") -> ({' && '.join(leftTurnObstaclesTransitions)})',
        f'(move = "m_tr") -> ({' && '.join(rightTurnObstaclesTransitions)})',


        # moving obstacles can not merge
        # not meeting and passing at the same time
        '! (olff && olb)',
        '((move = "m_h" || move = "m_f") && olff) -> X (! olb)',
        '((move = "m_h" || move = "m_f") && olb) -> X (! olff)',
        # meeting two obstacles
        '((move = "m_h") && olff && olf) -> X (olf && (! olb))', 
        # being passed by two obstacles
        '((move = "m_h") && olb && olf) -> X (olf && (! olff))',
        '((move = "m_f") && olf && olb) -> X (olf && (! olff))',


        # some aspects of the target transitions are known even in this simple discretization
        # target is static when halting
        '(move = "m_h") -> (target = (X target))',

        # moving away from target will result in not facing the target
        '((move = "m_f") && (target = "t_l" || target = "t_r")) -> (target = X target)',
        '((move = "m_tl" && target = "t_r") || (move = "m_tr" && target = "t_l")) -> ((X target) != "t_f")',

        # turning when facing target will result in target changing
        '((move = "m_tr") && (target = "t_f")) -> ((X target) = "t_l")',
        '((move = "m_tl") && (target = "t_f")) -> ((X target) = "t_r")',

        # turning towards the target will not move it to other side of you
        '((move = "m_tr") && (target = "t_r")) -> ((X target) != "t_l")',
        '((move = "m_tl") && (target = "t_l")) -> ((X target) != "t_r")',

        # shifting when target is in front will not result in target being on side you shifted towards
        '((move = "m_slf") && (target = "t_f")) -> ((X target) != "t_l")',
        '((move = "m_srf") && (target = "t_f")) -> ((X target) != "t_r")',

        # shifting along target front line will not move you to face target
        '(((move = "m_slf") && (target = "t_l")) || ((move = "m_srf") && (target = "t_r"))) -> (X (target != "t_f"))',

        # shifting away from target will keep target in same area
        '((move = "m_slf" && target = "t_r") || (move = "m_srf" && target = "t_l")) -> (target = (X target))',
    }

    leftForwardShiftBlocked = '(olf || olff || olb || ofc)'
    forwardBlocked = '(of || ofc)'
    rightForwardShiftBlocked = '(orf || ofc)'
    leftTurnBlocked = '(olt || olff || olb || ofc)'
    rightTurnBlocked = 'ort'

    pathExistsGuaranteed = f'(! ({leftForwardShiftBlocked} && {forwardBlocked} && {rightForwardShiftBlocked} && {leftTurnBlocked} && {rightTurnBlocked}))'

    # if multiple paths are available, agent attempts to approach target
    movePrefsTargetForward = [
        f'((! {forwardBlocked}) -> (move = "m_f"))',
        # if it is a temporary block, we wait for a path to open up
        f'(({forwardBlocked} && (! of)) -> (move = "m_h"))',
        # if target is forward, one should keep right
        f'((of && (! {rightForwardShiftBlocked})) -> (move = "m_srf"))',
        f'((of && {rightForwardShiftBlocked} && (! orf)) -> (move = "m_h"))',
        f'((of && orf && (! {leftForwardShiftBlocked})) -> (move = "m_slf"))',
        f'((of && orf && {leftForwardShiftBlocked} && (! olf)) -> (move = "m_h"))',
        # or turn left
        f'((of && olf && orf && (! {leftTurnBlocked})) -> (move = "m_tl"))',
        f'((of && olf && orf && {leftTurnBlocked} && (! olt)) -> (move = "m_h"))',
    ]
    movePrefsTargetLeft = [
        f'((! {leftTurnBlocked}) -> move = "m_tl")',
        f'(({leftTurnBlocked} && (! olt)) -> move = "m_h")',
        f'((olt && (! {leftForwardShiftBlocked})) -> move = "m_slf")',
        f'((olt && {leftForwardShiftBlocked} && (! olf)) -> move = "m_h")',
        f'((olt && olf && (! {forwardBlocked})) -> move = "m_f")',
        f'((olt && olf && {forwardBlocked} && (! of)) -> move = "m_h")',
    ]
    movePrefsTargetRight = [
        f'((! {rightTurnBlocked}) -> move = "m_tr")',
        f'(({rightTurnBlocked} && (! ort)) -> move = "m_h")',
        f'((ort && (! {rightForwardShiftBlocked})) -> move = "m_srf")',
        f'((ort && {rightForwardShiftBlocked} && (! orf)) -> move = "m_h")',
        f'((ort && orf && (! {forwardBlocked})) -> move = "m_f")',
        f'((ort && orf && {forwardBlocked} && (! of)) -> move = "m_h")',
    ]


    sys_safe = {
        # no collision
        '! oa',

        # towards the target
        f'((target = "t_f") -> ({' && '.join(movePrefsTargetForward)}))',
        f'((target = "t_l") -> ({' && '.join(movePrefsTargetLeft)}))',
        f'((target = "t_r") -> ({' && '.join(movePrefsTargetRight)}))',

    }

    pathWillExist = [
        pathExistsGuaranteed,
        # space can not be permanently occupied by moving objects
        '(! olff)',
        '(! olb)',
        '(! ofc)',
    ]

    env_prog = pathWillExist
    sys_prog = {}

    spec = GRSpec(env_vars, sys_vars, env_init, sys_init,
                  env_safe, sys_safe, env_prog, sys_prog)
    
    return spec


