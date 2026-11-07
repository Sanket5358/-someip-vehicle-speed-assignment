"""
Common definition of the Climate SOME/IP service.
"""

from dataclasses import dataclass

from someipy import (
    Event,
    EventGroup,
    Method,
    ServiceBuilder,
    TransportLayerProtocol,
)

from someipy.serialization import (
    SomeIpPayload,
    Sint16,
    Uint8,
)


# ---------------------------------------------------------
# Service Identification
# ---------------------------------------------------------

CLIMATE_SERVICE_ID = 0x2234
CLIMATE_INSTANCE_ID = 0x0001
CLIMATE_MAJOR_VERSION = 1


# ---------------------------------------------------------
# Method Identification
# ---------------------------------------------------------

GET_CABIN_TEMPERATURE_METHOD_ID = 0x0001
SET_TARGET_TEMPERATURE_METHOD_ID = 0x0002


# ---------------------------------------------------------
# Event Identification
# ---------------------------------------------------------

CABIN_TEMPERATURE_CHANGED_EVENT_ID = 0x8001
CLIMATE_EVENTGROUP_ID = 0x0001


# ---------------------------------------------------------
# Network Configuration
# ---------------------------------------------------------

INTERFACE_IP = "127.0.0.1"

CLIMATE_PROVIDER_PORT = 3004
CLIMATE_CONSUMER_PORT = 3006


# ---------------------------------------------------------
# Temperature Limits
# ---------------------------------------------------------

MIN_TARGET_TEMPERATURE = 160
MAX_TARGET_TEMPERATURE = 300

ACCEPTED = 0
INVALID_TEMPERATURE = 1


# ---------------------------------------------------------
# Cabin Temperature Payload (int16)
# ---------------------------------------------------------

@dataclass
class CabinTemperaturePayload(SomeIpPayload):

    temperature: Sint16

    def __init__(self, temperature: int = 240):
        self.temperature = Sint16(temperature)


# ---------------------------------------------------------
# Target Temperature Request Payload (int16)
# ---------------------------------------------------------

@dataclass
class TargetTemperaturePayload(SomeIpPayload):

    target_temperature: Sint16

    def __init__(self, target_temperature: int = 220):
        self.target_temperature = Sint16(target_temperature)


# ---------------------------------------------------------
# Set Target Temperature Response (uint8)
# ---------------------------------------------------------

@dataclass
class TemperatureStatusPayload(SomeIpPayload):

    status: Uint8

    def __init__(self, status: int = ACCEPTED):
        self.status = Uint8(status)


# ---------------------------------------------------------
# Method Definitions
# ---------------------------------------------------------

get_cabin_temperature_method = Method(
    id=GET_CABIN_TEMPERATURE_METHOD_ID,
    protocol=TransportLayerProtocol.UDP,
)

set_target_temperature_method = Method(
    id=SET_TARGET_TEMPERATURE_METHOD_ID,
    protocol=TransportLayerProtocol.UDP,
)


# ---------------------------------------------------------
# Event Definition
# ---------------------------------------------------------

cabin_temperature_changed_event = Event(
    id=CABIN_TEMPERATURE_CHANGED_EVENT_ID,
    protocol=TransportLayerProtocol.UDP,
)


# ---------------------------------------------------------
# Event Group
# ---------------------------------------------------------

climate_eventgroup = EventGroup(
    id=CLIMATE_EVENTGROUP_ID,
    events=[cabin_temperature_changed_event],
)


# ---------------------------------------------------------
# Climate Service Definition
# ---------------------------------------------------------

climate_service = (
    ServiceBuilder()
    .with_service_id(CLIMATE_SERVICE_ID)
    .with_major_version(CLIMATE_MAJOR_VERSION)
    .with_method(get_cabin_temperature_method)
    .with_method(set_target_temperature_method)
    .with_eventgroup(climate_eventgroup)
    .build()
)
