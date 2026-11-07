"""
Virtual Central Display ECU.

Consumes:
1. VehicleSpeedService
2. ClimateService

Vehicle functions:
- GetSpeed
- GetVehicleState
- SpeedChanged
- OverspeedWarning

Climate functions:
- GetCabinTemperature
- SetTargetTemperature
- CabinTemperatureChanged
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

# Vehicle interface
from vehicle_speed_interface import (
    SERVICE_ID,
    INSTANCE_ID,
    INTERFACE_IP,
    GET_SPEED_METHOD_ID,
    GET_VEHICLE_STATE_METHOD_ID,
    SPEED_CHANGED_EVENT_ID,
    OVERSPEED_WARNING_EVENT_ID,
    SpeedPayload,
    VehicleStatePayload,
    STOPPED,
    MOVING,
    speed_eventgroup,
    overspeed_eventgroup,
    vehicle_speed_service,
)

# Climate interface
from climate_interface import (
    CLIMATE_SERVICE_ID,
    CLIMATE_INSTANCE_ID,
    CLIMATE_MAJOR_VERSION,
    CLIMATE_CONSUMER_PORT,
    GET_CABIN_TEMPERATURE_METHOD_ID,
    SET_TARGET_TEMPERATURE_METHOD_ID,
    CABIN_TEMPERATURE_CHANGED_EVENT_ID,
    CLIMATE_EVENTGROUP_ID,
    ACCEPTED,
    INVALID_TEMPERATURE,
    CabinTemperaturePayload,
    TargetTemperaturePayload,
    TemperatureStatusPayload,
    climate_eventgroup,
    climate_service as climate_service_definition,
)


# ---------------------------------------------------------
# Central Display Network Configuration
# ---------------------------------------------------------

VEHICLE_CONSUMER_PORT = 3008
CLIMATE_DISPLAY_PORT = CLIMATE_CONSUMER_PORT

# Temperature is sent in tenths of a degree Celsius.
# Example: 23.0 C = 230.
# The user can enter a different target at runtime.


# ---------------------------------------------------------
# Vehicle Event Callback
# ---------------------------------------------------------

def vehicle_event_callback(
    event_id: int,
    event_payload: bytes,
) -> None:

    try:

        if event_id == SPEED_CHANGED_EVENT_ID:

            message = SpeedPayload().deserialize(event_payload)

            print()
            print("[CENTRAL DISPLAY] SpeedChanged received")
            print(
                f"Vehicle Speed: "
                f"{message.speed_kmph.value} km/h"
            )

        elif event_id == OVERSPEED_WARNING_EVENT_ID:

            message = SpeedPayload().deserialize(event_payload)

            print()
            print("=" * 50)
            print("[CENTRAL DISPLAY] !!! OVERSPEED WARNING !!!")
            print(f"Vehicle Speed: {message.speed_kmph.value} km/h")
            print("=" * 50)

    except Exception as error:

        print(f"Vehicle event decoding error: {error}")


# ---------------------------------------------------------
# Climate Event Callback
# ---------------------------------------------------------

def climate_event_callback(
    event_id: int,
    event_payload: bytes,
) -> None:

    try:

        if event_id == CABIN_TEMPERATURE_CHANGED_EVENT_ID:

            message = CabinTemperaturePayload().deserialize(
                event_payload
            )

            temperature = message.temperature.value / 10

            print()
            print(
                "[CENTRAL DISPLAY] CabinTemperatureChanged received"
            )
            print(f"Cabin Temperature: {temperature:.1f} degree Celsius")

    except Exception as error:

        print(f"Climate event decoding error: {error}")


# ---------------------------------------------------------
# Vehicle GetSpeed Method
# ---------------------------------------------------------

async def call_get_speed(client_instance):

    try:

        result = await client_instance.call_method(
            GET_SPEED_METHOD_ID,
            b"",
        )

        if (
            result.message_type == MessageType.RESPONSE
            and result.return_code == ReturnCode.E_OK
        ):

            message = SpeedPayload().deserialize(result.payload)

            print()
            print("[CENTRAL DISPLAY] GetSpeed response")
            print(f"Vehicle Speed: {message.speed_kmph.value} km/h")

        elif result.message_type == MessageType.ERROR:

            print("GetSpeed returned SOME/IP error")

    except Exception as error:

        print(f"GetSpeed call failed: {error}")


# ---------------------------------------------------------
# Vehicle GetVehicleState Method
# ---------------------------------------------------------

async def call_get_vehicle_state(client_instance):

    try:

        result = await client_instance.call_method(
            GET_VEHICLE_STATE_METHOD_ID,
            b"",
        )

        if (
            result.message_type == MessageType.RESPONSE
            and result.return_code == ReturnCode.E_OK
        ):

            message = VehicleStatePayload().deserialize(
                result.payload
            )

            state_value = message.state.value

            if state_value == STOPPED:
                state_name = "STOPPED"

            elif state_value == MOVING:
                state_name = "MOVING"

            else:
                state_name = "UNKNOWN"

            print("[CENTRAL DISPLAY] Vehicle State:", state_name)

        elif result.message_type == MessageType.ERROR:

            print("GetVehicleState returned SOME/IP error")

    except Exception as error:

        print(f"GetVehicleState call failed: {error}")


# ---------------------------------------------------------
# Climate GetCabinTemperature Method
# ---------------------------------------------------------

async def call_get_cabin_temperature(client_instance):

    try:

        result = await client_instance.call_method(
            GET_CABIN_TEMPERATURE_METHOD_ID,
            b"",
        )

        if (
            result.message_type == MessageType.RESPONSE
            and result.return_code == ReturnCode.E_OK
        ):

            message = CabinTemperaturePayload().deserialize(
                result.payload
            )

            temperature = message.temperature.value / 10

            print()
            print("[CENTRAL DISPLAY] GetCabinTemperature response")
            print(f"Cabin Temperature: {temperature:.1f} degree Celsius")

        elif result.message_type == MessageType.ERROR:

            print("GetCabinTemperature returned SOME/IP error")

    except Exception as error:

        print(f"GetCabinTemperature call failed: {error}")


# ---------------------------------------------------------
# Climate SetTargetTemperature Method
# ---------------------------------------------------------

async def call_set_target_temperature(
    client_instance,
    requested_temperature: int,
):

    try:

        request_payload = TargetTemperaturePayload(
            requested_temperature
        ).serialize()

        print()
        print(
            "[CENTRAL DISPLAY] Sending target temperature: "
            f"{requested_temperature / 10:.1f} C"
        )

        result = await client_instance.call_method(
            SET_TARGET_TEMPERATURE_METHOD_ID,
            request_payload,
        )

        if (
            result.message_type == MessageType.RESPONSE
            and result.return_code == ReturnCode.E_OK
        ):

            response = TemperatureStatusPayload().deserialize(
                result.payload
            )

            if response.status.value == ACCEPTED:

                print("[CENTRAL DISPLAY] Target temperature ACCEPTED")

            elif response.status.value == INVALID_TEMPERATURE:

                print(
                    "[CENTRAL DISPLAY] "
                    "INVALID_TEMPERATURE received"
                )

            else:

                print(
                    "[CENTRAL DISPLAY] Unknown temperature status:",
                    response.status.value,
                )

        elif result.message_type == MessageType.ERROR:

            print("SetTargetTemperature returned SOME/IP error")

    except Exception as error:

        print(f"SetTargetTemperature call failed: {error}")


# ---------------------------------------------------------
# Independent Service Availability Monitoring
# ---------------------------------------------------------

async def monitor_services(
    vehicle_client,
    climate_client,
):

    vehicle_was_available = False
    climate_was_available = False

    while True:

        # Check VehicleSpeedService
        vehicle_available = await vehicle_client.is_available()

        if vehicle_available and not vehicle_was_available:

            print()
            print("[CENTRAL DISPLAY] VehicleSpeedService AVAILABLE")

            vehicle_client.subscribe_eventgroup(
                speed_eventgroup,
                5,
            )

            vehicle_client.subscribe_eventgroup(
                overspeed_eventgroup,
                5,
            )

            print("[CENTRAL DISPLAY] Vehicle event subscriptions requested")

        elif not vehicle_available and vehicle_was_available:

            print()
            print("[CENTRAL DISPLAY] VehicleSpeedService NOT AVAILABLE")

        vehicle_was_available = vehicle_available

        # Check ClimateService independently
        climate_available = await climate_client.is_available()

        if climate_available and not climate_was_available:

            print()
            print("[CENTRAL DISPLAY] ClimateService AVAILABLE")

            climate_client.subscribe_eventgroup(
                climate_eventgroup,
                5,
            )

            print("[CENTRAL DISPLAY] Climate event subscription requested")

        elif not climate_available and climate_was_available:

            print()
            print("[CENTRAL DISPLAY] ClimateService NOT AVAILABLE")

        climate_was_available = climate_available

        await asyncio.sleep(1)


# ---------------------------------------------------------
# Periodic Requests to Both Services
# ---------------------------------------------------------

async def request_vehicle_and_climate_data(
    vehicle_client,
    climate_client,
):

    while True:

        if await vehicle_client.is_available():

            await call_get_speed(vehicle_client)

            await call_get_vehicle_state(vehicle_client)

        if await climate_client.is_available():

            await call_get_cabin_temperature(climate_client)

        await asyncio.sleep(5)


# ---------------------------------------------------------
# Interactive Target Temperature Input
# ---------------------------------------------------------

async def target_temperature_input(climate_client):

    print()
    print("Central Display target temperature control")
    print("Enter a temperature between 16.0 and 30.0 C.")
    print("Enter q to stop entering target temperatures.")

    while True:

        if not await climate_client.is_available():

            await asyncio.sleep(1)
            continue

        user_input = await asyncio.to_thread(
            input,
            "\nEnter target temperature in C: ",
        )

        if user_input.strip().lower() == "q":

            print("Target temperature input stopped")
            return

        try:

            temperature_celsius = float(user_input)

            requested_temperature = round(
                temperature_celsius * 10
            )

            if not -32768 <= requested_temperature <= 32767:

                print("Temperature value is outside the supported range")
                continue

            await call_set_target_temperature(
                climate_client,
                requested_temperature,
            )

        except ValueError:

            print("Invalid input. Example: 23.0")


# ---------------------------------------------------------
# Main Central Display Application
# ---------------------------------------------------------

async def main():

    set_someipy_log_level(logging.INFO)

    print("=" * 60)
    print("Virtual Central Display ECU")
    print("Multi-Service SOME/IP Consumer")
    print("=" * 60)

    print(
        f"VehicleSpeedService ID : 0x{SERVICE_ID:04X}"
    )

    print(
        f"Vehicle consumer port  : {VEHICLE_CONSUMER_PORT}"
    )

    print(
        f"ClimateService ID      : 0x{CLIMATE_SERVICE_ID:04X}"
    )

    print(
        f"Climate consumer port  : {CLIMATE_DISPLAY_PORT}"
    )

    print("=" * 60)

    print("Connecting to someipy daemon...")

    daemon = await connect_to_someipy_daemon()

    print("Connected to someipy daemon")

    # VehicleSpeedService client
    vehicle_client = ClientServiceInstance(
        daemon=daemon,
        service=vehicle_speed_service,
        instance_id=INSTANCE_ID,
        endpoint_ip=INTERFACE_IP,
        endpoint_port=VEHICLE_CONSUMER_PORT,
    )

    # ClimateService client
    climate_client = ClientServiceInstance(
        daemon=daemon,
        service=climate_service_definition,
        instance_id=CLIMATE_INSTANCE_ID,
        endpoint_ip=INTERFACE_IP,
        endpoint_port=CLIMATE_DISPLAY_PORT,
    )

    # Register independent event callbacks
    vehicle_client.register_callback(
        vehicle_event_callback
    )

    climate_client.register_callback(
        climate_event_callback
    )

    print("Vehicle and Climate clients created")

    # Start monitoring and method requests
    tasks = [
        asyncio.create_task(
            monitor_services(vehicle_client, climate_client)
        ),
        asyncio.create_task(
            request_vehicle_and_climate_data(
                vehicle_client,
                climate_client,
            )
        ),
        asyncio.create_task(
            target_temperature_input(climate_client)
        ),
    ]

    try:

        await asyncio.Future()

    finally:

        for task in tasks:
            task.cancel()

        await asyncio.gather(
            *tasks,
            return_exceptions=True,
        )

        await daemon.disconnect_from_daemon()


# ---------------------------------------------------------
# Application Entry Point
# ---------------------------------------------------------

if __name__ == "__main__":

    try:

        asyncio.run(main())

    except KeyboardInterrupt:

        print("\nCentral Display ECU stopped")
