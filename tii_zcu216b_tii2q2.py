import pathlib

from qibolab.channels import Channel, ChannelMap
from qibolab.instruments.erasynth import ERA
from qibolab.instruments.rfsoc import RFSoC
from qibolab.instruments.rohde_schwarz import SGS100A
from qibolab.platform import Platform
from qibolab.serialize import load_qubits, load_runcard, load_settings

NAME = "tii_zcu216b_tii2q3"
ADDRESS = "192.168.0.93"
PORT = 6000
RUNCARD = pathlib.Path(__file__).parent / "tii_zcu216b_tii2q2.yml"

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

    channels |= Channel("L3-26", port=controller[6])  # Probe readout

    # qubit Q1
    channels |= Channel("L2-02-1", port=controller[0])  # feedback
    channels |= Channel("L1-05", port=controller[1])  # flux
    channels |= Channel("L3-03", port=controller[0])  # drive

    # qubit Q2
    channels |= Channel("L2-02-2", port=controller[1])  # feedback
    channels |= Channel("L1-06", port=controller[3])  # flux
    channels |= Channel("L3-04", port=controller[4])  # drive



    # twpa_lo = SGS100A("TWPA", TWPA_ADDRESS)
    # twpa_lo.frequency = 7_000_000_000
    # twpa_lo.power = -5

    readout_lo = SGS100A("LO", LO_ADDRESS)
    readout_lo.frequency = 7.5e9
    readout_lo.power = 10
    channels["L3-26"].local_oscillator = readout_lo

    local_oscillators = [readout_lo] #, twpa_lo]
    instruments = [controller] + local_oscillators

    # create qubit objects
    runcard = load_runcard(runcard_path)
    qubits, pairs = load_qubits(runcard)

    # assign channels to qubits
    qubits["Q1"].readout = channels["L3-26"]
    qubits["Q1"].feedback = channels["L2-02-1"]
    qubits["Q1"].drive = channels["L3-03"]
    qubits["Q1"].flux = channels["L1-06"]

    qubits["Q2"].readout = channels["L3-26"]
    qubits["Q2"].feedback = channels["L2-02-2"]
    qubits["Q2"].drive = channels["L3-04"]
    qubits["Q2"].flux = channels["L1-06"]


    instruments = {
        controller.name: controller,
        readout_lo.name: readout_lo,
#        twpa_lo.name: twpa_lo,
    }
    settings = load_settings(runcard)
    return Platform(NAME, qubits, pairs, instruments, settings, resonator_type="2D")

