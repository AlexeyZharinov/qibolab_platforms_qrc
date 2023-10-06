# Platform build on a ZCU216 controlling the qw5q_gold chip

import pathlib

from qibolab.channels import Channel, ChannelMap
from qibolab.instruments.erasynth import ERA
from qibolab.instruments.rfsoc import RFSoC
from qibolab.instruments.rohde_schwarz import SGS100A
from qibolab.platform import Platform
from qibolab.serialize import load_qubits, load_runcard, load_settings

NAME = "tii_zcu216_qw5q"
ADDRESS = "192.168.0.85"
PORT = 6000
RUNCARD = pathlib.Path(__file__).parent / "tii_zcu216_qw5q.yml"

TWPA_ADDRESS = "192.168.0.37"
LO_ADDRESS = "192.168.0.35"


def create(runcard_path=RUNCARD):
    """Platform for RFSoC4x2 board running qibosoq.

    IPs and other instrument related parameters are hardcoded in.
    """
    # Instantiate QICK instruments
    controller = RFSoC(NAME, ADDRESS, PORT)
    controller.cfg.adc_trig_offset = 200
    controller.cfg.repetition_duration = 200
    # Create channel objects
    channels = ChannelMap()

    channels |= Channel("L3-25", port=controller[6])  # readout

    # qubit 0
    channels |= Channel("L2-5-0", port=controller[0])  # feedback
    channels |= Channel("L4-5", port=controller[1])  # flux
    channels |= Channel("L3-15", port=controller[0])  # drive

    # qubit 1
    channels |= Channel("L2-5-1", port=controller[1])  # feedback
    channels |= Channel("L4-1", port=controller[3])  # flux
    channels |= Channel("L3-11", port=controller[4])  # drive

    # qubit 2
    channels |= Channel("L2-5-2", port=controller[2])  # feedback
    channels |= Channel("L4-2", port=controller[5])  # flux
    channels |= Channel("L3-12", port=controller[2])  # drive

    twpa_lo = SGS100A("TWPA", TWPA_ADDRESS)
    twpa_lo.frequency = 6_535_900_000
    twpa_lo.power = 4

    readout_lo = SGS100A("LO", LO_ADDRESS)
    readout_lo.frequency = 7.7e9
    readout_lo.power = 10
    channels["L3-25"].local_oscillator = readout_lo

    local_oscillators = [readout_lo, twpa_lo]
    instruments = [controller] + local_oscillators

    # create qubit objects
    runcard = load_runcard(runcard_path)
    qubits, pairs = load_qubits(runcard)

    # assign channels to qubits
    qubits[0].readout = channels["L3-25"]
    qubits[0].feedback = channels["L2-5-0"]
    qubits[0].drive = channels["L3-15"]
    qubits[0].flux = channels["L4-5"]

    qubits[1].readout = channels["L3-25"]
    qubits[1].feedback = channels["L2-5-1"]
    qubits[1].drive = channels["L3-11"]
    qubits[1].flux = channels["L4-1"]

    qubits[2].readout = channels["L3-25"]
    qubits[2].feedback = channels["L2-5-2"]
    qubits[2].drive = channels["L3-12"]
    qubits[2].flux = channels["L4-2"]

    instruments = {
        controller.name: controller,
        readout_lo.name: readout_lo,
        twpa_lo.name: twpa_lo,
    }
    settings = load_settings(runcard)
    return Platform(NAME, qubits, pairs, instruments, settings, resonator_type="2D")

