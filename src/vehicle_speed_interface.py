"""
Common definition of the Vehicle Speed SOME/IP service.
"""

from dataclasses import dataclass

from someipy import (
    Event,
    EventGroup,
    Method,
    ServiceBuilder,
    TransportLayerProtocol,
)

from someipy.serialization import SomeIpPayload, Uint16


# ---------------------------------------------------------------------------
# Service identification
# ---------------------------------------------------------------------------

SERVICE_ID = 0x1234
INSTANCE_ID = 0x5678
MAJOR_VERSION = 1


# ---------------------------------------------------------------------------
# Method identification
# ---------------------------------------------------------------------------

GET_SPEED_METHOD_ID = 0x0001


# ---------------------------------------------------------------------------
# Event identification
# ---------------------------------------------------------------------------

SPEED_CHANGED_EVENT_ID = 0x8001
SPEED_EVENTGROUP_ID = 0x0001


# ---------------------------------------------------------------------------
# Network configuration
# ---------------------------------------------------------------------------

INTERFACE_IP = "127.0.0.1"
PROVIDER_PORT = 3000
CONSUMER_PORT = 3002


# ---------------------------------------------------------------------------
# Payload
# ---------------------------------------------------------------------------

@dataclass
class SpeedPayload(SomeIpPayload):

    speed_kmph: Uint16

    def __init__(self, speed_kmph: int = 0):
        self.speed_kmph = Uint16(speed_kmph)


# ---------------------------------------------------------------------------
# GetSpeed Method
# ---------------------------------------------------------------------------

get_speed_method = Method(
    id=GET_SPEED_METHOD_ID,
    protocol=TransportLayerProtocol.UDP,
)


# ---------------------------------------------------------------------------
# SpeedChanged Event
# ---------------------------------------------------------------------------

speed_changed_event = Event(
    id=SPEED_CHANGED_EVENT_ID,
    protocol=TransportLayerProtocol.UDP,
)


speed_eventgroup = EventGroup(
    id=SPEED_EVENTGROUP_ID,
    events=[speed_changed_event],
)


# ---------------------------------------------------------------------------
# Vehicle Speed Service
# ---------------------------------------------------------------------------

vehicle_speed_service = (
    ServiceBuilder()
    .with_service_id(SERVICE_ID)
    .with_major_version(MAJOR_VERSION)
    .with_method(get_speed_method)
    .with_eventgroup(speed_eventgroup)
    .build()
)
