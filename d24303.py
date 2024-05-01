import pathlib

from qibolab.channels import Channel, ChannelMap
from qibolab.instruments.qblox.cluster import (
    Cluster,
    Cluster_Settings,
    ReferenceClockSource,
)
from qibolab.instruments.qblox.cluster_qcm_bb import ClusterQCM_BB
from qibolab.instruments.qblox.cluster_qcm_rf import ClusterQCM_RF
from qibolab.instruments.qblox.cluster_qrm_rf import ClusterQRM_RF
from qibolab.instruments.qblox.controller import QbloxController
from qibolab.instruments.rohde_schwarz import SGS100A
from qibolab.platform import Platform
from qibolab.serialize import (
    load_instrument_settings,
    load_qubits,
    load_runcard,
    load_settings,
)

NAME = "d24303"
ADDRESS = "192.168.0.2"
RUNCARD = pathlib.Path(__file__).parent / "d24303.yml"


def create(runcard_path=RUNCARD):
    """2qubit chip with qblox .02.

    Args:
        runcard_path (str): Path to the runcard file.
    """
    runcard = load_runcard(runcard_path)
    cluster = Cluster(
        name="cluster",
        address= ADDRESS,
        settings=Cluster_Settings(reference_clock_source=ReferenceClockSource.EXTERNAL),
    )
    modules = {
        "qrm_rf0": ClusterQRM_RF(
            "qrm_rf0", f"{ADDRESS}:1", cluster
        ),  # qubits q1
        "qcm_rf0": ClusterQCM_RF(
            "qcm_rf0", f"{ADDRESS}:10", cluster
        ),  # qubits q1
        # "qcm_bb0": ClusterQCM_BB(
        #    "qcm_bb0", f"{ADDRESS}:4", cluster
        #),  
    }
    controller = QbloxController("qblox_controller", cluster, modules)
    #twpa_pump0 = SGS100A(name="twpa_pump0", address="192.168.0.37")
    #twpa_pump1 = SGS100A(name="twpa_pump1", address="192.168.0.39")

    instruments = {
        controller.name: controller,
    #    twpa_pump0.name: twpa_pump0,
    #    twpa_pump1.name: twpa_pump1,
    }
    instruments.update(modules)
    instruments = load_instrument_settings(runcard, instruments)

    # # DEBUG: debug folder = report folder ###################################################################
    # import os
    # from datetime import datetime

    # QPU = "tii2qs3f"
    # debug_folder = f"/home/users/bianka.woloncewicz/reports/{datetime.now().strftime('%Y%m%d')}_{QPU}_/debug/"
    # if not os.path.exists(debug_folder):
    #     os.makedirs(debug_folder)
    # for name in modules:
    #     modules[name]._debug_folder = debug_folder
    # #########################################################################################################

    # Create channel objects
    channels = ChannelMap()
    # Readout
    channels |= Channel(name="w5-r", port=modules["qrm_rf0"].ports["o1"])
    # Feedback
    channels |= Channel(name="v-1", port=modules["qrm_rf0"].ports["i1"])
    # Drive
    channels |= Channel(name="w5-d", port=modules["qcm_rf0"].ports["o1"])
    #channels |= Channel(name="L3-4", port=modules["qcm_rf0"].ports["o2"])
    # Flux
    # channels |= Channel(name="L1-5", port=modules["qcm_bb0"].ports["o2"])
    # channels |= Channel(name="dummy", port=modules["qcm_bb0"].ports["o1"])
  


    # create qubit objects
    qubits, couplers, pairs = load_qubits(runcard)

    # assign channels to qubits    
    qubits[1].readout = channels["w5-r"]
    qubits[1].feedback = channels["v-1"]
    qubits[1].drive = channels["w5-d"]
    
    # qubits[2].flux = channels["L1-5"]
    # channels["L1-5"].qubit = qubits[2]
    # qubits[2].flux.max_bias = 2.5

    # qubits[2].readout = channels["L3-26"]
    # qubits[2].feedback = channels["L2-2"]
    # qubits[2].drive = channels["L3-4"]

    # qubits[1].flux = channels["dummy"]
    # channels["dummy"].qubit = qubits[1]
    # qubits[1].flux.max_bias = 2.5

    settings = load_settings(runcard)

    return Platform(
        "d24303", qubits, pairs, instruments, settings, resonator_type="2D")