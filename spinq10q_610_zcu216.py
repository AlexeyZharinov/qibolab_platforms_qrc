import pathlib

from qibolab.channels import Channel, ChannelMap
from qibolab.instruments.erasynth import ERA
from qibolab.instruments.rfsoc import RFSoC
from qibolab.instruments.rohde_schwarz import SGS100A
from qibolab.platform import Platform
from qibolab.serialize import (
    load_instrument_settings,
    load_qubits,
    load_runcard,
    load_settings,
)

NAME = "spinq10q_610_zcu216"
ADDRESS = "192.168.0.93"
PORT = 6000
RUNCARD = pathlib.Path(__file__).parent / "spinq10q_610_zcu216.yml"

TWPA_ADDRESS = "192.168.0.39"
LO_ADDRESS = "192.168.0.35"


def create(runcard_path=RUNCARD):
    """Platform for ZCU216 board running qibosoq.

    IPs and other instrument related parameters are hardcoded in.
    """
    # Instantiate QICK instruments
    controller = RFSoC(NAME, ADDRESS, PORT)
    controller.cfg.adc_trig_offset = 200
    controller.cfg.repetition_duration = 200
    # Create channel objects
    channels = ChannelMap()

    channels |= Channel("L3-21", port=controller.ports(8))  # readout probe

    # qubit 1
    channels |= Channel("L2-17-0", port=controller.ports(0))  # feedback
    channels |= Channel("L6-44", port=controller.ports(1))  # flux
    channels |= Channel("L6-6", port=controller.ports(0))  # drive

    # qubit 2
    channels |= Channel("L2-17-1", port=controller.ports(1))  # feedback
    channels |= Channel("L6-45", port=controller.ports(3))  # flux
    channels |= Channel("L6-7", port=controller.ports(4))  # drive

    # qubit 3
    channels |= Channel("L2-17-2", port=controller.ports(2))  # feedback
    channels |= Channel("L6-46", port=controller.ports(5))  # flux
    channels |= Channel("L6-8", port=controller.ports(2))  # drive

    # qubit 4 BAD PORTS
    channels |= Channel("L2-17-3", port=controller.ports(0))  # feedback
    channels |= Channel("L6-47", port=controller.ports(0))  # flux
    channels |= Channel("L6-9", port=controller.ports(0))  # drive

    # qubit 5 BAD PORTS
    channels |= Channel("L2-17-4", port=controller.ports(0))  # feedback
    channels |= Channel("L6-48", port=controller.ports(0))  # flux
    channels |= Channel("L6-10", port=controller.ports(0))  # drive    

    twpa_lo = SGS100A("TWPA", TWPA_ADDRESS)
    readout_lo = SGS100A("readout_lo", LO_ADDRESS)
    channels["L3-21"].local_oscillator = readout_lo

    # create qubit objects
    runcard = load_runcard(runcard_path)
    qubits, couplers, pairs = load_qubits(runcard)

    # assign channels to qubits
    qubits[6].readout = channels["L3-21"]
    qubits[6].feedback = channels["L2-17-0"]
    qubits[6].drive = channels["L6-6"]
    qubits[6].flux = channels["L6-44"]

    qubits[7].readout = channels["L3-21"]
    qubits[7].feedback = channels["L2-17-1"]
    qubits[7].drive = channels["L6-7"]
    qubits[7].flux = channels["L6-45"]

    qubits[8].readout = channels["L3-21"]
    qubits[8].feedback = channels["L2-17-2"]
    qubits[8].drive = channels["L6-8"]
    qubits[8].flux = channels["L6-46"]

    qubits[9].readout = channels["L3-21"]
    qubits[9].feedback = channels["L2-17-3"]
    qubits[9].drive = channels["L6-9"]
    qubits[9].flux = channels["L6-47"]

    qubits[10].readout = channels["L3-21"]
    qubits[10].feedback = channels["L2-17-4"]
    qubits[10].drive = channels["L6-10"]
    qubits[10].flux = channels["L6-48"]

    instruments = {
        controller.name: controller,
        readout_lo.name: readout_lo,
        twpa_lo.name: twpa_lo,
    }

    settings = load_settings(runcard)
    instruments = load_instrument_settings(runcard, instruments)
    return Platform(NAME, qubits, pairs, instruments, settings, resonator_type="2D")

