def kalaha():
    from tulip.spec import GRSpec
    from itertools import chain



    neutralPits = range(1, 7).chain(range(8,14))
    oppPit = 7
    myPit = 0

    env_vars={
        'oSel': neutralPits
    }

    sys_vars={
        'mSel': neutralPits
    }

    # me and opponent start with 0 pearls
    # all of the other pits have tree pearls
    env_init = {'s7 == 0'}

    sys_init= {'s0 == 0'}
    for i in range(neutralPits):
        sys_init |= {'s{0}==3'.format(i)}

    env_safe={
        '(X s7) >= s7',
    }
    sys_safe={
        '(X s0) >= s0'
    }

    prog = []
    for i in neutralPits:
        sys_safe={
            # a selected pit will be empty next turn
            '(mSel == {0} && (s{0} < 13)) -> (X (s{0} == 0))'.format(i),
            # unless we move multiple loops
            '(mSel == {0} && (s{0} > 12) && (s{0} < 25)) -> (X (s{0} == 1))'.format(i),
            '(mSel == {0} && (s{0} > 26)) -> (X (s{0} == 2))'.format(i),
        }

        # where the pearls will be in the next state
        for j in range(0,36):
            for k in range(0, j):
                if (i+k) == oppPit:
                    continue # TODO the range must be one further if we are hitting the pit
                sys_safe={
                    '(mSel == {0} && s{0} == {1}) -> (X (s{2} == s{2} + {3}))'.format(i, j, k%14, (k//14)+1) # TODO test
                }

        prog.append('s{0} == 0'.format(i))

    # eventually all neutral pits will be empty
    pitsEmpty = ' && '.join(prog)
    sys_prog = pitsEmpty
    
    #if they are, I have more pearls
    sys_safe |= {'({0}) -> s0 > s7'.format(pitsEmpty)}

    # TODO skip opp turn if we score in target


    # QUE do the pits need to be duplicated since they are changed by both me and opponent?
    # check stick picking, same situation
    #for i in range (0,6):
    #    env_safe={}


    # this should be way too many states to synthesize
    specs = GRSpec(env_vars, sys_vars, env_init, sys_init,
                env_safe, sys_safe, env_prog, sys_prog)