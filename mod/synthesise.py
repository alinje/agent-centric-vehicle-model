import os
import time
from tulip.synth import synthesize


def synthesiseVehicleController(subject,outputPath='mod\\synthesis\\output\\vehicleController', className='VehicleController'):

    spec = subject
    spec.moore = False
    spec.qinit = r'\A \E'
    spec.plus_one = False
    time1 = time.time()
    ctrl = synthesize(spec)
    time2 = time.time()
    assert ctrl is not None, 'Specification is unrealizable'
    print(f'Synthesised in {time2-time1}.')

    # remove old outputs
    if os.path.isfile(f'{outputPath}.scxml'):
        os.remove(f'{outputPath}.scxml')
    # print new
    if not ctrl.save(filename=f'{outputPath}.scxml'):
        print('could not save as scxml')
    time3 = time.time()

    print(f'Printed in {time3-time2}.')
    print('all done')
