"""Host-side torque excitation, acquisition and servo identification for the AQTUATOR test rig.

Entry points:
    aqtuator-sequential  -> sequential_run.main     Workflow A: torque playback + acquisition
    aqtuator-servo-id    -> servo_identification.main  Workflow B: ODrive high-rate frequency sweep
    aqtuator-multisine   -> multisine.main          Generate a crest-factor-optimised waveform
"""

__version__ = "0.1.0"
