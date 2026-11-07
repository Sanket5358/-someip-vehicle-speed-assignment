"""
Virtual Vehicle ECU.

Provides:
1. GetSpeed method
2. GetVehicleState method
3. SpeedChanged event
4. OverspeedWarning event
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

from vehicle_speed_interface import (
    GET_SPEED_METHOD_ID,
    GET_VEHICLE_STATE_METHOD_ID,
    INSTANCE_ID,
    INTERFACE_IP,
    MAJOR_VERSION,
    MOVING,
    OVERSPEED_EVENTGROUP_ID,
    OVERSPEED_WARNING_EVENT_ID,
    PROVIDER_PORT,
    SERVICE_ID,
    SPEED_CHANGED_EVENT_ID,
    SPEED_EVENTGROUP_ID,
    STOPPED,
    SpeedPayload,
    VehicleStatePayload,
    speed_eventgroup,
    overspeed_eventgroup,
)


current_speed_kmph = 0


# ---------------------------------------------------------------------------
# GetSpeed method handler
# ---------------------------------------------------------------------------

async def get_speed_handler(
    input_data: bytes,
    client_address: Tuple[str, int],
) -> MethodResult:

    print()
    print("GetSpeed request received")
    print(f"Consumer address : {client_address[0]}:{client_address[1]}")
    print(f"Current speed    : {current_speed_kmph} km/h")

    response_payload = SpeedPayload(current_speed_kmph).serialize()

    result = MethodResult()
    result.message_type = MessageType.RESPONSE
    result.return_code = ReturnCode.E_OK
    result.payload = response_payload

    print(f"Response bytes   : {response_payload.hex(' ')}")
    print("GetSpeed response sent")

    return result


# ---------------------------------------------------------------------------
# GetVehicleState method handler
# ---------------------------------------------------------------------------

async def get_vehicle_state_handler(
    input_data: bytes,
    client_address: Tuple[str, int],
) -> MethodResult:

    if current_speed_kmph == 0:
        vehicle_state = STOPPED
        state_name = "STOPPED"
    else:
        vehicle_state = MOVING
        state_name = "MOVING"

    print()
    print("GetVehicleState request received")
    print(f"Consumer address : {client_address[0]}:{client_address[1]}")
    print(f"Current speed    : {current_speed_kmph} km/h")
    print(f"Vehicle state    : {state_name}")

    response_payload = VehicleStatePayload(
        vehicle_state
    ).serialize()

    result = MethodResult()
    result.message_type = MessageType.RESPONSE
    result.return_code = ReturnCode.E_OK
    result.payload = response_payload

    print(f"Response bytes   : {response_payload.hex(' ')}")
    print("GetVehicleState response sent")

    return result


# ---------------------------------------------------------------------------
# Build Vehicle Speed Provider
# ---------------------------------------------------------------------------

def build_provider_service():

    get_speed_method = Method(
        id=GET_SPEED_METHOD_ID,
        protocol=TransportLayerProtocol.UDP,
        method_handler=get_speed_handler,
    )

    get_vehicle_state_method = Method(
        id=GET_VEHICLE_STATE_METHOD_ID,
        protocol=TransportLayerProtocol.UDP,
        method_handler=get_vehicle_state_handler,
    )

    return (
        ServiceBuilder()
        .with_service_id(SERVICE_ID)
        .with_major_version(MAJOR_VERSION)
        .with_method(get_speed_method)
        .with_method(get_vehicle_state_method)
        .with_eventgroup(speed_eventgroup)
        .with_eventgroup(overspeed_eventgroup)
        .build()
    )


# ---------------------------------------------------------------------------
# Vehicle speed simulation and event publishing
# ---------------------------------------------------------------------------

async def simulate_speed(
    service_instance: ServerServiceInstance,
) -> None:

    global current_speed_kmph

    while True:

        current_speed_kmph += 10

        if current_speed_kmph > 100:
            current_speed_kmph = 0

        # Generate SpeedChanged for every speed update
        speed_payload = SpeedPayload(
            current_speed_kmph
        ).serialize()

        print()
        print(
            f"Simulated speed changed to "
            f"{current_speed_kmph} km/h"
        )

        service_instance.send_event(
            SPEED_EVENTGROUP_ID,
            SPEED_CHANGED_EVENT_ID,
            speed_payload,
        )

        print("SpeedChanged event sent")

        # Generate OverspeedWarning only above 80 km/h
        if current_speed_kmph > 80:

            overspeed_payload = SpeedPayload(
                current_speed_kmph
            ).serialize()

            service_instance.send_event(
                OVERSPEED_EVENTGROUP_ID,
                OVERSPEED_WARNING_EVENT_ID,
                overspeed_payload,
            )

            print(
                f"OVERSPEED WARNING! "
                f"Current speed: {current_speed_kmph} km/h"
            )

        await asyncio.sleep(2)


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------

async def main() -> None:

    set_someipy_log_level(logging.INFO)

    print("=" * 60)
    print("Virtual Vehicle ECU")
    print("VehicleSpeedService Provider")
    print("=" * 60)

    print(f"Service ID             : 0x{SERVICE_ID:04X}")
    print(f"Instance ID            : 0x{INSTANCE_ID:04X}")
    print(f"GetSpeed Method ID     : 0x{GET_SPEED_METHOD_ID:04X}")
    print(
        f"GetVehicleState ID     : "
        f"0x{GET_VEHICLE_STATE_METHOD_ID:04X}"
    )
    print(f"SpeedChanged Event ID  : 0x{SPEED_CHANGED_EVENT_ID:04X}")
    print(
        f"Overspeed Event ID     : "
        f"0x{OVERSPEED_WARNING_EVENT_ID:04X}"
    )
    print(f"Speed Event Group      : 0x{SPEED_EVENTGROUP_ID:04X}")
    print(
        f"Overspeed Event Group  : "
        f"0x{OVERSPEED_EVENTGROUP_ID:04X}"
    )
    print(f"Provider endpoint      : {INTERFACE_IP}:{PROVIDER_PORT}")

    print("=" * 60)

    print("Connecting to someipy daemon...")

    daemon = await connect_to_someipy_daemon()

    print("Connected to someipy daemon")

    provider_service = build_provider_service()

    provider_instance = ServerServiceInstance(
        daemon=daemon,
        service=provider_service,
        instance_id=INSTANCE_ID,
        endpoint_ip=INTERFACE_IP,
        endpoint_port=PROVIDER_PORT,
        ttl=5,
        cyclic_offer_delay_ms=2000,
    )

    print("Offering VehicleSpeedService...")

    await provider_instance.start_offer()

    print("VehicleSpeedService is being offered")

    speed_task = asyncio.create_task(
        simulate_speed(provider_instance)
    )

    try:

        await asyncio.Future()

    finally:

        speed_task.cancel()

        try:
            await speed_task
        except asyncio.CancelledError:
            pass

        await provider_instance.stop_offer()

        await daemon.disconnect_from_daemon()


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\nVehicle Speed Service stopped")
