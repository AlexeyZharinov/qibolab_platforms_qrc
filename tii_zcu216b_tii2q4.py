import pathlib

from qibolab.channels import Channel, ChannelMap
from qibolab.instruments.erasynth import ERA
from qibolab.instruments.rfsoc import RFSoC
from qibolab.instruments.rohde_schwarz import SGS100A
from qibolab.platform import Platform
from qibolab.serialize import load_qubits, load_runcard, load_settings

NAME = "tii_zcu216b_tii2q4"
ADDRESS = "192.168.0.93"
PORT = 6000
RUNCARD = pathlib.Path(__file__).parent / "tii_zcu216b_tii2q4.yml"

TWPA_ADDRESS = "192.168.0.34"
LO_ADDRESS = "192.168.0.33"


def create(runcard_path=RUNCARD):
    """Platform for  board running qibosoq.

    IPs and other instrument related parameters are hardcoded in.
    """
    # Instantiate QICK instruments
    controller = RFSoC(NAME, ADDRESS, PORT)
    controller.cfg.adc_trig_offset = 200
    controller.cfg.repetition_duration = 200
    # Create channel objects
    channels = ChannelMap()

    channels |= Channel("L3-30", port=controller[6])  # Probe readout

    # qubit Q1
    channels |= Channel("L2-04-1", port=controller[0])  # feedback
    channels |= Channel("L1-07", port=controller[1])  # flux
    channels |= Channel("L3-07", port=controller[0])  # drive

    # qubit Q2
    channels |= Channel("L2-04-2", port=controller[1])  # feedback
    channels |= Channel("L1-07", port=controller[3])  # flux
    channels |= Channel("L3-08", port=controller[4])  # drive



    twpa_lo = SGS100A("TWPA", TWPA_ADDRESS)
    twpa_lo.frequency = 5_300_250_000
    twpa_lo.power = -5

    readout_lo = SGS100A("LO", LO_ADDRESS)
    readout_lo.frequency = 7.6e9
    readout_lo.power = 10
    channels["L3-30"].local_oscillator = readout_lo

    local_oscillators = [readout_lo, twpa_lo]
    instruments = [controller] + local_oscillators

    # create qubit objects
    runcard = load_runcard(runcard_path)
    qubits, pairs = load_qubits(runcard)

    # assign channels to qubits
    qubits["Q1"].readout = channels["L3-30"]
    qubits["Q1"].feedback = channels["L2-04-1"]
    qubits["Q1"].drive = channels["L3-07"]
    qubits["Q1"].flux = channels["L1-07"]

    qubits["D2"].readout = channels["L3-30"]
    qubits["D2"].feedback = channels["L2-04-2"]
    qubits["D2"].drive = channels["L3-08"]
    qubits["D2"].flux = channels["L1-07"]


    instruments = {
        controller.name: controller,
        readout_lo.name: readout_lo,
        twpa_lo.name: twpa_lo,
    }
    settings = load_settings(runcard)
    return Platform(NAME, qubits, pairs, instruments, settings, resonator_type="2D")

