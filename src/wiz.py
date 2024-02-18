import asyncio
import json
import logging
from typing import ByteString, Callable, Literal, Optional, Tuple, Union

from pydantic import BaseModel, Field
from tenacity import (
    retry_if_exception_type,
    stop_after_delay,
    wait_fixed,
    RetryError,
    AsyncRetrying,
)

_LOGGER = logging.getLogger(__name__)

UDP_PORT = 38899
TIMEOUT = 2


class WizProtocol(asyncio.DatagramProtocol):
    def __init__(
            self,
            on_response: Optional[Callable[[bytes, Tuple[str, int]], None]] = None,
            on_error: Optional[Callable[[Optional[Exception]], None]] = None,
    ) -> None:
        """Init the protocol."""
        self.on_response = on_response
        self.on_error = on_error

    def datagram_received(self, data: bytes, addr: Tuple[str, int]) -> None:
        """Trigger on_response."""
        _LOGGER.info("Received data: %s", data)
        if self.on_response is not None:
            self.on_response(data, addr)

    def error_received(self, exc: Optional[Exception]) -> None:
        """Handle error."""
        _LOGGER.debug("WizProtocol error: %s", exc)
        if self.on_error is not None:
            self.on_error(exc)

    def connection_lost(self, exc: Optional[Exception]) -> None:
        """The connection is lost."""
        _LOGGER.debug("WizProtocol connection lost: %s", exc)


class BulbParameters(BaseModel):
    r: Optional[int] = Field(
        default=None, alias="red", ge=0, le=255, description="Red track value"
    )
    g: Optional[int] = Field(
        default=None, alias="green", ge=0, le=255, description="Green track value"
    )
    b: Optional[int] = Field(
        default=None, alias="blue", ge=0, le=255, description="Blue track value"
    )
    c: Optional[int] = Field(
        default=None,
        alias="cold_white",
        ge=0,
        le=255,
        description="Cold white track value",
    )
    w: Optional[int] = Field(
        default=None,
        alias="warm_white",
        ge=0,
        le=255,
        description="Warm white track value",
    )
    dimming: Optional[int] = Field(
        default=None, alias="brightness", ge=10, le=100, description="Brightness value"
    )
    sceneId: Optional[int] = Field(
        default=None, ge=1, le=32, description="Predefined light mode ID"
    )
    speed: Optional[int] = Field(
        default=None, ge=10, le=200, description="Speed of dynamic light modes"
    )
    ratio: Optional[int] = Field(
        default=None, ge=0, le=100, description="Ratio for dual-zone devices"
    )
    state: bool = Field(..., description="State of the device")
    temp: Optional[int] = Field(
        default=None,
        alias="temperature",
        ge=2200,
        le=6500,
        description="CCT value, measured in Kelvins",
    )


class WizMessage(BaseModel):
    method: Literal["setPilot", "getPilot"] = Field(
        default="setPilot", description="Method name"
    )
    params: Optional[BulbParameters] = Field(
        default={}, description="Parameters for the bulb method"
    )


class WizGetResult(BaseModel):
    mac: Optional[str] = Field(default=None, description="MAC address of the bulb")
    rssi: Optional[int] = Field(default=None, description="Signal strength of the bulb")
    src: Optional[str] = Field(default=None, description="Source of the message")
    r: Optional[int] = Field(default=None, ge=0, le=255, description="Red track value")
    g: Optional[int] = Field(
        default=None, ge=0, le=255, description="Green track value"
    )
    b: Optional[int] = Field(default=None, ge=0, le=255, description="Blue track value")
    c: Optional[int] = Field(
        default=None,
        alias="cold_white",
        ge=0,
        le=255,
        description="Cold white track value",
    )
    w: Optional[int] = Field(
        default=None,
        alias="warm_white",
        ge=0,
        le=255,
        description="Warm white track value",
    )
    state: Optional[bool] = Field(description="State of the bulb (on/off)")
    sceneId: Optional[int] = Field(
        default=None, ge=0, le=32, description="Predefined scene ID"
    )
    speed: Optional[int] = Field(
        default=None, ge=20, le=200, description="Speed of dynamic light modes"
    )
    temp: Optional[int] = Field(
        default=None, description="Color temperature in kelvins"
    )
    dimming: Optional[int] = Field(
        default=None, ge=10, le=100, description="Brightness value"
    )
    schdPsetId: Optional[int] = Field(default=None, description="Rhythm ID of the room")


class WizSetResult(BaseModel):
    success: bool = Field(..., description="Success status of the setPilot method")


class WizError(BaseModel):
    code: Optional[int] = Field(None, description="Error code")
    message: Optional[str] = Field(None, description="Error message")


class WizResponse(BaseModel):
    method: Literal["setPilot", "getPilot"] = Field(
        default="setPilot", description="Method name"
    )
    env: Literal["pro"] = "pro"
    result: Optional[Union[BulbParameters, WizSetResult]] = Field(
        default=None, description="Result message from the bulb"
    )
    error: Optional[WizError] = Field(
        default=None, description="Error message from the bulb"
    )


MESSAGES = {
    "ON": WizMessage(params=BulbParameters(state=True)),
    "OFF": WizMessage(params=BulbParameters(state=False)),
    "INFO": WizMessage(method="getPilot"),
    "WARMEST": WizMessage(
        params=BulbParameters(state=True, temperature=2200, brightness=20)
    ),
    "WARMER": WizMessage(
        params=BulbParameters(state=True, temperature=2700, brightness=20)
    ),
    "WARM": WizMessage(
        params=BulbParameters(state=True, temperature=3200, brightness=20)
    ),
    "COLDEST": WizMessage(
        params=BulbParameters(state=True, temperature=6500, brightness=20)
    ),
    "COLDER": WizMessage(
        params=BulbParameters(state=True, temperature=5700, brightness=20)
    ),
    "COLD": WizMessage(
        params=BulbParameters(state=True, temperature=5000, brightness=20)
    ),
}

ParsedBulbResponse = Tuple[
    Optional[WizError], Optional[Union[WizSetResult, WizGetResult]]
]


def parse_bulb_response(
        response_message: ByteString,
        wiz_message_method: Literal["setPilot", "getPilot"] = "setPilot",
):
    response_data = json.loads(response_message)
    error = response_data.get("error")
    result = response_data.get("result")

    parsed_error = WizError(**error) if error else None
    parsed_result = (
        WizSetResult(**result)
        if wiz_message_method == "setPilot"
        else WizGetResult(**result)
    )

    return parsed_error, parsed_result


async def get_transport(
        event_loop: asyncio.AbstractEventLoop,
        response_future: asyncio.Future,
        ip: str = "192.168.1.255",
        port: int = UDP_PORT,
):
    transport, _protocol = await event_loop.create_datagram_endpoint(
        lambda: WizProtocol(
            on_response=lambda data, addr: response_future.set_result((data, addr)),
            on_error=lambda exc: response_future.set_exception(
                exc if exc else Exception("Unknown error")
            ),
        ),
        remote_addr=(ip, port),
    )
    return transport


async def send_message_to_wiz(
        ip: str, message: WizMessage = MESSAGES["INFO"]
) -> Union[
    tuple[Union[None, WizSetResult, WizGetResult]], tuple[Union[str, WizError], None]
]:
    no_response_error_message = "Bulb offline"
    message_bytes = message.model_dump_json(
        exclude_none=True,
    ).encode("utf-8")

    response_future = asyncio.Future()
    transport = await get_transport(asyncio.get_event_loop(), response_future, ip)

    try:
        transport.sendto(message_bytes, (ip, UDP_PORT))
        async for attempt in AsyncRetrying(
                retry=retry_if_exception_type(asyncio.exceptions.InvalidStateError),
                wait=wait_fixed(0.05),  # 50ms
                stop=stop_after_delay(TIMEOUT),
        ):
            with attempt:
                response_message, _addr = response_future.result()
                parsed_response = parse_bulb_response(
                    response_message, wiz_message_method=message.method
                )
                return parsed_response
    except RetryError:
        return no_response_error_message, None
