import sys
# sys.dont_write_bytecode = True
import os
import time
from tulip.synth import synthesize
from tulip.dumpsmach import write_python_case

from synthesisation.targetOrientationSpec import overlapSpaceSpec


def synthesiseVehicleController(outputPath='mod\\model\\synthesisation\\output\\targetOrientationControl', className='TargetOrientationControl'):

    spec = overlapSpaceSpec()
    spec.moore = False
    spec.qinit = r'\A \E'
    spec.plus_one = False
    time1 = time.time()
    ctrl = synthesize(spec)
    time2 = time.time()
    assert ctrl is not None, 'specification is unrealizable'
    print(f'Synthesized in {time2-time1}.')
    # remove old outputs
    if os.path.isfile(f'{outputPath}.scxml'):
        os.remove(f'{outputPath}.scxml')
    if os.path.isfile(f'{outputPath}.py'):
        os.remove(f'{outputPath}.py')

    write_python_case(f'{outputPath}.py', ctrl, classname=className)
    time3 = time.time()
    print(f'Printed in {time3-time2}.')
    print('all done')

# if __name__ == '__main__':
synthesiseVehicleController()
