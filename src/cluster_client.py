"""
Virtual Instrument Cluster ECU.

Consumes VehicleSpeedService.

Methods:
1. GetSpeed
2. GetVehicleState

Events:
1. SpeedChanged
2. OverspeedWarning
"""

import asyncio
import logging

from someipy import (
    ClientServiceInstance,
    MessageType,
    ReturnCode,
    connect_to_someipy_daemon,
)

from someipy.someipy_logging import set_someipy_log_level

from vehicle_speed_interface import (
    CONSUMER_PORT,
    GET_SPEED_METHOD_ID,
    GET_VEHICLE_STATE_METHOD_ID,
    INSTANCE_ID,
    INTERFACE_IP,
    MOVING,
    OVERSPEED_EVENTGROUP_ID,
    OVERSPEED_WARNING_EVENT_ID,
    SERVICE_ID,
    SPEED_CHANGED_EVENT_ID,
    STOPPED,
    SpeedPayload,
    VehicleStatePayload,
    speed_eventgroup,
    overspeed_eventgroup,
    vehicle_speed_service,
)


# ---------------------------------------------------------
# Event Callback
# ---------------------------------------------------------

def speed_event_callback(
    event_id: int,
    event_payload: bytes,
) -> None:

    try:

        if event_id == SPEED_CHANGED_EVENT_ID:

            speed_message = SpeedPayload().deserialize(
                event_payload
            )

            print()
            print("SpeedChanged notification received")
            print(
                f"Vehicle Speed : "
                f"{speed_message.speed_kmph.value} km/h"
            )

        elif event_id == OVERSPEED_WARNING_EVENT_ID:

            speed_message = SpeedPayload().deserialize(
                event_payload
            )

            print()
            print("=" * 45)
            print("!!! OVERSPEED WARNING !!!")
            print(
                f"Vehicle Speed : "
                f"{speed_message.speed_kmph.value} km/h"
            )
            print("=" * 45)

    except Exception as error:

        print(f"Could not decode event payload: {error}")


# ---------------------------------------------------------
# GetSpeed Method Call
# ---------------------------------------------------------

async def call_get_speed(
    client_instance: ClientServiceInstance,
) -> None:

    try:

        result = await client_instance.call_method(
            GET_SPEED_METHOD_ID,
            b"",
        )

        if result.message_type == MessageType.RESPONSE:

            if result.return_code == ReturnCode.E_OK:

                speed_message = SpeedPayload().deserialize(
                    result.payload
                )

                print()
                print("GetSpeed response received")
                print(
                    f"Vehicle Speed : "
                    f"{speed_message.speed_kmph.value} km/h"
                )

        elif result.message_type == MessageType.ERROR:

            print("GetSpeed returned SOME/IP error")

    except Exception as error:

        print(f"GetSpeed call failed: {error}")


# ---------------------------------------------------------
# GetVehicleState Method Call
# ---------------------------------------------------------

async def call_get_vehicle_state(
    client_instance: ClientServiceInstance,
) -> None:

    try:

        result = await client_instance.call_method(
            GET_VEHICLE_STATE_METHOD_ID,
            b"",
        )

        if result.message_type == MessageType.RESPONSE:

            if result.return_code == ReturnCode.E_OK:

                state_message = VehicleStatePayload().deserialize(
                    result.payload
                )

                state_value = state_message.state.value

                if state_value == STOPPED:
                    state_name = "STOPPED"

                elif state_value == MOVING:
                    state_name = "MOVING"

                else:
                    state_name = "UNKNOWN"

                print()
                print("GetVehicleState response received")
                print(f"Vehicle State : {state_name}")

        elif result.message_type == MessageType.ERROR:

            print("GetVehicleState returned SOME/IP error")

    except Exception as error:

        print(f"GetVehicleState call failed: {error}")


# ---------------------------------------------------------
# Periodic Vehicle Data Requests
# ---------------------------------------------------------

async def request_vehicle_data(
    client_instance: ClientServiceInstance,
) -> None:

    while True:

        await call_get_speed(client_instance)

        await call_get_vehicle_state(client_instance)

        await asyncio.sleep(5)


# ---------------------------------------------------------
# Main Consumer Application
# ---------------------------------------------------------

async def main() -> None:

    set_someipy_log_level(logging.INFO)

    print("=" * 60)
    print("Virtual Instrument Cluster ECU")
    print("VehicleSpeedService Consumer")
    print("=" * 60)

    print(f"Service ID       : 0x{SERVICE_ID:04X}")
    print(f"Instance ID      : 0x{INSTANCE_ID:04X}")
    print(f"Consumer endpoint: {INTERFACE_IP}:{CONSUMER_PORT}")

    print("=" * 60)

    print("Connecting to someipy daemon...")

    daemon = await connect_to_someipy_daemon()

    print("Connected to someipy daemon")

    client_instance = ClientServiceInstance(
        daemon=daemon,
        service=vehicle_speed_service,
        instance_id=INSTANCE_ID,
        endpoint_ip=INTERFACE_IP,
        endpoint_port=CONSUMER_PORT,
    )

    # Register event callback
    client_instance.register_callback(
        speed_event_callback
    )

    # Search for VehicleSpeedService
    print("Searching for VehicleSpeedService...")

    while not await client_instance.is_available():

        print("VehicleSpeedService is NOT AVAILABLE")

        await asyncio.sleep(1)

    print()
    print("VehicleSpeedService AVAILABLE")

    # Subscribe to SpeedChanged event group
    print("Subscribing to SpeedChanged...")

    client_instance.subscribe_eventgroup(
        speed_eventgroup,
        5,
    )

    # Subscribe to OverspeedWarning event group
    print("Subscribing to OverspeedWarning...")

    client_instance.subscribe_eventgroup(
        overspeed_eventgroup,
        5,
    )

    print("Both event-group subscription requests sent")

    # Start periodic method requests
    method_task = asyncio.create_task(
        request_vehicle_data(client_instance)
    )

    try:

        await asyncio.Future()

    finally:

        method_task.cancel()

        try:
            await method_task

        except asyncio.CancelledError:
            pass

        await daemon.disconnect_from_daemon()


# ---------------------------------------------------------
# Application Entry Point
# ---------------------------------------------------------

if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:

        print("\nInstrument Cluster stopped")
