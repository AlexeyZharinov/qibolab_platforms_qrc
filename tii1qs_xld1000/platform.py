import pathlib

from qibolab.channels import Channel, ChannelMap
from qibolab.instruments.qblox.cluster_qcm_bb import QcmBb
from qibolab.instruments.qblox.cluster_qcm_rf import QcmRf
from qibolab.instruments.qblox.cluster_qrm_rf import QrmRf
from qibolab.instruments.qblox.controller import QbloxController
from qibolab.instruments.rohde_schwarz import SGS100A
from qibolab.platform import Platform
from qibolab.serialize import (
    load_instrument_settings,
    load_qubits,
    load_runcard,
    load_settings,
)

FOLDER = pathlib.Path(__file__).parent


def create():
    """QuantWare 5q-chip controlled using qblox cluster.

    Args:
        runcard_path (str): Path to the runcard file.
    """
    opx = OPXplus("con1")
    octave = Octave("octave1", port=100, connectivity=opx)
    controller = QMController(
        "qm",
        "192.168.0.101:80",
        opxs=[opx],
        octaves=[octave1],
        time_of_flight=280,
    )
    # twpa_pump0 = SGS100A(name="twpa_pump0", address="192.168.0.37")

    channels = ChannelMap()
    # Readout
    channels |= Channel(name="L3-31r", port=octave.ports("o1"))
    # Feedback
    channels |= Channel(name="L2-1", port=octave.ports("i1", out=False))
    # Drive
    channels |= Channel(name="L3-31d", port=octave.ports("o5"))

    channels |= Channel(name="L99", port=modules["qcm_rf0"].ports("i1", out=False))

    # create qubit objects
    runcard = load_runcard(FOLDER)
    qubits, couplers, pairs = load_qubits(runcard)

    qubits[0].readout = channels["L3-31r"]
    qubits[0].feedback = channels["L2-1"]
    qubits[0].drive = channels["L3-31d"]

    instruments = {controller.name: controller}  # , twpa.name: twpa}
    instruments.update(controller.opxs)
    instruments.update(controller.octaves)
    instruments = load_instrument_settings(runcard, instruments)
    return Platform(
        str(FOLDER), qubits, pairs, instruments, settings, resonator_type="3D"
    )
