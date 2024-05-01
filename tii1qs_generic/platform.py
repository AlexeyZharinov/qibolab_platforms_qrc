import pathlib

from qibolab.channels import Channel, ChannelMap
from qibolab.instruments.qblox.cluster_qcm_bb import QcmBb
from qibolab.instruments.qblox.cluster_qcm_rf import QcmRf
from qibolab.instruments.qblox.cluster_qrm_rf import QrmRf
from qibolab.instruments.qblox.controller import QbloxController
from qibolab.instruments.qblox.port import QbloxOutputPort
from qibolab.instruments.rohde_schwarz import SGS100A
from qibolab.platform import Platform
from qibolab.serialize import (
    load_instrument_settings,
    load_qubits,
    load_runcard,
    load_settings,
)

NAME = "qblox"
ADDRESS = "192.168.0.2"
FOLDER = pathlib.Path(__file__).parent

def create():
    """Transmon on 3d cavity using qblox cluster.

    Args:
        runcard_path (str): Path to the runcard file.
    """
    runcard = load_runcard(FOLDER)
    modules = {
        "qrm_rf0": QrmRf("qrm_rf0", f"{ADDRESS}:1"),
        "qcm_rf0": QcmRf("qcm_rf0", f"{ADDRESS}:10"),
    }
    controller = QbloxController("qblox_controller", ADDRESS, modules)

    instruments = {
        controller.name: controller,
    }
    instruments.update(modules)
    instruments = load_instrument_settings(runcard, instruments)
    
    # Create channel objects
    channels = ChannelMap()
    # Readout
    channels |= Channel(name="W5-R", port=modules["qrm_rf0"].ports("o1"))

    # Feedback
    channels |= Channel(name="V1-R", port=modules["qrm_rf0"].ports("i1", out=False))

    # Drive
    channels |= Channel(name="W5-D", port=modules["qcm_rf0"].ports("o1"))
    

    # create qubit objects
    qubits, couplers, pairs = load_qubits(runcard)

    qubits[0].readout = channels["W5-R"]
    qubits[0].feedback = channels["V1-R"]
    qubits[0].drive = channels["W5-D"]


    settings = load_settings(runcard)
    #instruments = load_instrument_settings(runcard, instruments)

    return Platform(
        str(FOLDER), qubits, pairs, instruments, settings, resonator_type="3D"
    )