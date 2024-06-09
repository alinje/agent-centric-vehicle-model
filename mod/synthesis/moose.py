from tulip.spec import GRSpec

def avoidMoose():

    env_vars = {
        'moose_front': 'boolean',
        'moose_collision': 'boolean',
    }

    sys_vars = {
        'go': 'boolean',
    }

    env_init = {
        '! moose_collision',
    }

    sys_init = {}

    env_safe = {
        'moose_front && go <-> next moose_collision',
    }

    sys_safe = {
        '! moose_collision',
    }

    env_prog = {
        '! moose_front',
    }

    sys_prog = {
        'go',
    }

    spec = GRSpec(env_vars, sys_vars, env_init, sys_init,
                  env_safe, sys_safe, env_prog, sys_prog)
    
    return spec