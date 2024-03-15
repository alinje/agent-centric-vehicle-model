from tulip.synth import synthesize
from tulip.dumpsmach import write_python_case

from synthesisation.extOverlapSpaceSpec import overlapSpaceSpec


def synthesiseVehicleController(outputPath='mod\\model\\synthesisation\\output\\extOverlapControl', className='OverlapControl'):

    spec = overlapSpaceSpec()
    spec.moore = False
    spec.qinit = r'\A \E'
    spec.plus_one = False
    ctrl = synthesize(spec)
    assert ctrl is not None, 'specification is unrealizable'
    
    if not ctrl.save(filename=f'{outputPath}.scxml'):
        print('could not save as scxml')

    write_python_case(f'{outputPath}.py', ctrl, classname=className)

    print('all done')

# if __name__ == '__main__':
synthesiseVehicleController()
