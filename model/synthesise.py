from tulip.synth import synthesize
from tulip.dumpsmach import write_python_case

from synthesisation.overlapSpaceSpec import overlapSpaceSpec


def synthesiseVehicleController(outputPath='model\\synthesisation\\output\\overlapControl', className='OverlapControl'):

    spec = overlapSpaceSpec()
    spec.moore = False
    spec.qinit = r'\A \E'
    spec.plus_one = False
    ctrl = synthesize(spec)
    assert ctrl is not None, 'specification is unrealizable'
    
    if not ctrl.save(filename=f'{outputPath}.png'):
        print('could not save as dot')

    write_python_case(f'{outputPath}.py', ctrl, classname=className)

    print('all done')

# if __name__ == '__main__':
synthesiseVehicleController()
