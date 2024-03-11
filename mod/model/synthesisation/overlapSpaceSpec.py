from tulip.spec import GRSpec
from space import OverlapZone as l
from space import OverlapZoneType as zt

def overlapSpaceSpec():
    env_vars = { 
        ('o' + l.overlapZoneString(k)): 'boolean' for k in zt
        }
    
    sys_vars = {
        'mlf': 'boolean', 
        'mf': 'boolean',
        'mrf': 'boolean',
    }

    env_init = {
        # does not start in an obstacle
        '! oa',
        # nor with no way to go
        l.pathExists,
    }

    sys_init = {}

    # obstacles moving in unison
    mLF = []
    for loc in l.leftForwardRemaining:
        mLF.append(f'(o{loc} <-> (X o{l.leftForwardMove(loc)}))')
    
    mF = []
    for loc in l.forwardRemaining:
        mF.append(f'(o{loc} <-> (X o{l.forwardMove(loc)}))')

    mRF = []
    for loc in l.rightForwardRemaining:
        mRF.append(f'(o{loc} <-> (X o{l.rightForwardMove(loc)}))')

    env_safe = {
        f'mlf -> ({' && '.join(mLF)})',
        f'mf -> ({' && '.join(mF)})',
        f'mrf -> ({' && '.join(mRF)})',

        l.pathExists,
    }

    sys_safe = {
        # vehicle is always moving
        # but only in one way
        'mlf <-> (! (mf || mrf))',
        'mf <-> (! (mlf || mrf))',
        'mrf <-> (! (mlf || mf))',

        # no collision
        '! oa',
        'X (! oa)',

        # only move left if nec
        '(orf && (! of)) <-> mf',

        # move right if pos
        '(! orf) <-> mrf',

        # otherwise move left
        '(orf && of) <-> mlf',
    }

    # NLVL moving obstacles: if appeared, will eventually ...
    env_prog = {}
    sys_prog = {}

    spec = GRSpec(env_vars, sys_vars, env_init, sys_init,
                  env_safe, sys_safe, env_prog, sys_prog)
    
    return spec



