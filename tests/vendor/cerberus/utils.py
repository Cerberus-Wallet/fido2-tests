import os
import socket
from fido2.ctap import STATUS

from cerberuslib import debuglink
from cerberuslib.debuglink import CerberusClientDebugLink
from cerberuslib.device import wipe as wipe_device
from cerberuslib.transport import enumerate_devices, get_transport


def get_device():
    path = os.environ.get("CERBERUS_PATH")
    interact = os.environ.get("INTERACT") == "1"
    if path:
        try:
            transport = get_transport(path)
            return CerberusClientDebugLink(transport, auto_interact=not interact)
        except Exception as e:
            raise RuntimeError("Failed to open debuglink for {}".format(path)) from e

    else:
        devices = enumerate_devices()
        for device in devices:
            try:
                return CerberusClientDebugLink(device, auto_interact=not interact)
            except Exception:
                pass
        else:
            raise RuntimeError("No debuggable device found")


def load_client():
    try:
        client = get_device()
    except RuntimeError:
        request.session.shouldstop = "No debuggable Cerberus is available"
        pytest.fail("No debuggable Cerberus is available")

    wipe_device(client)
    debuglink.load_device_by_mnemonic(
        client,
        mnemonic=" ".join(["all"] * 12),
        pin=None,
        passphrase_protection=False,
        label="test",
    )
    client.clear_session()

    client.open()
    return client


CERBERUS_CLIENT = load_client()


class DeviceSelectCredential:
    def __init__(self, number=1):
        self.number = number

    def __call__(self, status):
        if status != STATUS.UPNEEDED:
            return

        if self.number == 0:
            CERBERUS_CLIENT.debug.press_no()
        else:
            for _ in range(self.number - 1):
                CERBERUS_CLIENT.debug.swipe_left()
            CERBERUS_CLIENT.debug.press_yes()
