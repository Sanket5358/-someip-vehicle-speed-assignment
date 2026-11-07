"""
Virtual Climate ECU.

Provides:
1. GetCabinTemperature method
2. SetTargetTemperature method
3. CabinTemperatureChanged event
"""

import asyncio
import logging
from typing import Tuple

from someipy import (
    MessageType,
    Method,
    MethodResult,
    ReturnCode,
    ServerServiceInstance,
    ServiceBuilder,
    TransportLayerProtocol,
    connect_to_someipy_daemon,
)

from someipy.someipy_logging import set_someipy_log_level

from climate_interface import (
    CLIMATE_SERVICE_ID,
    CLIMATE_INSTANCE_ID,
    CLIMATE_MAJOR_VERSION,
    INTERFACE_IP,
    CLIMATE_PROVIDER_PORT,
    GET_CABIN_TEMPERATURE_METHOD_ID,
    SET_TARGET_TEMPERATURE_METHOD_ID,
    CABIN_TEMPERATURE_CHANGED_EVENT_ID,
    CLIMATE_EVENTGROUP_ID,
    MIN_TARGET_TEMPERATURE,
    MAX_TARGET_TEMPERATURE,
    ACCEPTED,
    INVALID_TEMPERATURE,
    CabinTemperaturePayload,
    TargetTemperaturePayload,
    TemperatureStatusPayload,
    climate_eventgroup,
)


# ---------------------------------------------------------------------------
# Climate ECU State
# ---------------------------------------------------------------------------

# Temperature values are stored in tenths of a degree Celsius.
# 240 means 24.0 degrees Celsius.
current_cabin_temperature = 240
target_temperature = 220


# ---------------------------------------------------------------------------
# GetCabinTemperature Method Handler
# ---------------------------------------------------------------------------

async def get_cabin_temperature_handler(
    input_data: bytes,
    client_address: Tuple[str, int],
) -> MethodResult:

    print()
    print("GetCabinTemperature request received")
    print(f"Consumer address          : {client_address[0]}:{client_address[1]}")
    print(
        f"Current Cabin Temperature : "
        f"{current_cabin_temperature / 10:.1f} degree Celsius"
    )

    response_payload = CabinTemperaturePayload(
        current_cabin_temperature
    ).serialize()

    result = MethodResult()
    result.message_type = MessageType.RESPONSE
    result.return_code = ReturnCode.E_OK
    result.payload = response_payload

    print(f"Response bytes            : {response_payload.hex(' ')}")
    print("GetCabinTemperature response sent")

    return result


# ---------------------------------------------------------------------------
# SetTargetTemperature Method Handler
# ---------------------------------------------------------------------------

async def set_target_temperature_handler(
    input_data: bytes,
    client_address: Tuple[str, int],
) -> MethodResult:

    global target_temperature

    # Decode the incoming signed 16-bit temperature.
    request = TargetTemperaturePayload().deserialize(input_data)

    requested_temperature = request.target_temperature.value

    print()
    print("SetTargetTemperature request received")
    print(f"Consumer address             : {client_address[0]}:{client_address[1]}")
    print(
        f"Requested Target Temperature : "
        f"{requested_temperature / 10:.1f} degree Celsius"
    )

    # Validate target temperature: 16.0 to 30.0 degrees Celsius.
    if MIN_TARGET_TEMPERATURE <= requested_temperature <= MAX_TARGET_TEMPERATURE:

        target_temperature = requested_temperature
        status = ACCEPTED

        print(
            f"New Target Temperature      : "
            f"{target_temperature / 10:.1f} degree Celsius"
        )
        print("Status                       : ACCEPTED")

    else:

        status = INVALID_TEMPERATURE

        print("Status                       : INVALID_TEMPERATURE")
        print(
            f"Existing Target Temperature  : "
            f"{target_temperature / 10:.1f} degree Celsius"
        )
        print("Target temperature was NOT updated")

    response_payload = TemperatureStatusPayload(status).serialize()

    result = MethodResult()
    result.message_type = MessageType.RESPONSE
    result.return_code = ReturnCode.E_OK
    result.payload = response_payload

    print(f"Response bytes               : {response_payload.hex(' ')}")
    print("SetTargetTemperature response sent")

    return result


# ---------------------------------------------------------------------------
# Build Climate Service
# ---------------------------------------------------------------------------

def build_climate_service():

    get_temperature_method = Method(
        id=GET_CABIN_TEMPERATURE_METHOD_ID,
        protocol=TransportLayerProtocol.UDP,
        method_handler=get_cabin_temperature_handler,
    )

    set_temperature_method = Method(
        id=SET_TARGET_TEMPERATURE_METHOD_ID,
        protocol=TransportLayerProtocol.UDP,
        method_handler=set_target_temperature_handler,
    )

    return (
        ServiceBuilder()
        .with_service_id(CLIMATE_SERVICE_ID)
        .with_major_version(CLIMATE_MAJOR_VERSION)
        .with_method(get_temperature_method)
        .with_method(set_temperature_method)
        .with_eventgroup(climate_eventgroup)
        .build()
    )


# ---------------------------------------------------------------------------
# Cabin Temperature Simulation and Event Publishing
# ---------------------------------------------------------------------------

async def simulate_cabin_temperature(
    service_instance: ServerServiceInstance,
) -> None:

    global current_cabin_temperature

    # Initial temperature is 24.0 degrees Celsius.
    # Subsequent values simulate a changing cabin temperature.
    temperature_sequence = [245, 250, 255, 260, 240]

    sequence_index = 0

    while True:

        await asyncio.sleep(2)

        new_temperature = temperature_sequence[sequence_index]

        sequence_index = (
            sequence_index + 1
        ) % len(temperature_sequence)

        # Publish only when the temperature changes.
        if new_temperature != current_cabin_temperature:

            current_cabin_temperature = new_temperature

            event_payload = CabinTemperaturePayload(
                current_cabin_temperature
            ).serialize()

            print()
            print(
                f"Cabin temperature changed to "
                f"{current_cabin_temperature / 10:.1f} degree Celsius"
            )

            service_instance.send_event(
                CLIMATE_EVENTGROUP_ID,
                CABIN_TEMPERATURE_CHANGED_EVENT_ID,
                event_payload,
            )

            print("CabinTemperatureChanged event sent")


# ---------------------------------------------------------------------------
# Main Climate ECU Application
# ---------------------------------------------------------------------------

async def main() -> None:

    set_someipy_log_level(logging.INFO)

    print("=" * 60)
    print("Virtual Climate ECU")
    print("ClimateService Provider")
    print("=" * 60)

    print(f"Service ID                 : 0x{CLIMATE_SERVICE_ID:04X}")
    print(f"Instance ID                : 0x{CLIMATE_INSTANCE_ID:04X}")
    print(
        f"GetCabinTemperature ID     : "
        f"0x{GET_CABIN_TEMPERATURE_METHOD_ID:04X}"
    )
    print(
        f"SetTargetTemperature ID    : "
        f"0x{SET_TARGET_TEMPERATURE_METHOD_ID:04X}"
    )
    print(
        f"CabinTemperatureChanged ID : "
        f"0x{CABIN_TEMPERATURE_CHANGED_EVENT_ID:04X}"
    )
    print(f"Climate Event Group        : 0x{CLIMATE_EVENTGROUP_ID:04X}")
    print(f"Provider endpoint          : {INTERFACE_IP}:{CLIMATE_PROVIDER_PORT}")

    print(
        f"Initial Cabin Temperature  : "
        f"{current_cabin_temperature / 10:.1f} degree Celsius"
    )
    print(
        f"Initial Target Temperature : "
        f"{target_temperature / 10:.1f} degree Celsius"
    )

    print("=" * 60)

    print("Connecting to someipy daemon...")

    daemon = await connect_to_someipy_daemon()

    print("Connected to someipy daemon")

    climate_service = build_climate_service()

    climate_instance = ServerServiceInstance(
        daemon=daemon,
        service=climate_service,
        instance_id=CLIMATE_INSTANCE_ID,
        endpoint_ip=INTERFACE_IP,
        endpoint_port=CLIMATE_PROVIDER_PORT,
        ttl=5,
        cyclic_offer_delay_ms=2000,
    )

    print("Offering ClimateService...")

    await climate_instance.start_offer()

    print("ClimateService is being offered")

    temperature_task = asyncio.create_task(
        simulate_cabin_temperature(climate_instance)
    )

    try:

        await asyncio.Future()

    finally:

        temperature_task.cancel()

        try:
            await temperature_task
        except asyncio.CancelledError:
            pass

        await climate_instance.stop_offer()

        await daemon.disconnect_from_daemon()


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\nClimate ECU stopped")
