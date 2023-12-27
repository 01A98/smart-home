import asyncio
import logging
import json
from typing import ByteString, Callable, Literal, Optional, Tuple, Union

from pydantic import BaseModel, Field, validator
import argparse

_LOGGER = logging.getLogger(__name__)

IP = "192.168.1.28"
PORT = 38899


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
    state: bool = Field(..., alias="on", description="State of the device")
    temp: Optional[int] = Field(
        default=None,
        alias="temperature",
        ge=2000,
        le=7000,
        description="CCT value, measured in Kelvins",
    )

    @validator("state", pre=False)
    def bool_to_on_or_off(cls, val):
        if val is None:
            return val
        return "on" if val else "off"


class WizMessage(BaseModel):
    method: Literal["setPilot", "getPilot"] = Field(
        default="setPilot", description="Method name"
    )
    params: Optional[BulbParameters] = Field(
        default={}, description="Parameters for the bulb method"
    )


class WizGetResult(BaseModel):
    mac: Optional[str] = Field(description="MAC address of the bulb")
    rssi: Optional[int] = Field(description="Signal strength of the bulb")
    src: Optional[str] = Field(description="Source of the message")
    state: Optional[bool] = Field(description="State of the bulb (on/off)")
    sceneId: Optional[int] = Field(ge=0, le=32, description="Predefined scene ID")
    speed: Optional[int] = Field(
        None, ge=20, le=200, description="Speed of dynamic light modes"
    )
    temp: Optional[int] = Field(description="Color temperature in kelvins")
    dimming: Optional[int] = Field(ge=10, le=100, description="Brightness value")
    schdPsetId: Optional[int] = Field(description="Rhythm ID of the room")

    @validator("state", pre=False)
    def bool_to_on_or_off(cls, val):
        if val is None:
            return val
        return "on" if val else "off"


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
    result: Optional[Union[WizGetResult, WizSetResult]] = Field(
        default=None, description="Result message from the bulb"
    )
    error: Optional[WizError] = Field(
        default=None, description="Error message from the bulb"
    )


MESSAGES = {
    "ON": WizMessage(params=BulbParameters(on=True))
    .model_dump_json(
        exclude_none=True,
    )
    .encode("utf-8"),
    "OFF": WizMessage(params=BulbParameters(on=False))
    .model_dump_json(
        exclude_none=True,
    )
    .encode("utf-8"),
    "INFO": WizMessage(method="getPilot")
    .model_dump_json(
        exclude_none=True,
    )
    .encode("utf-8"),
    "WARM": WizMessage(params=BulbParameters(on=True, temperature=2000))
    .model_dump_json(
        exclude_none=True,
    )
    .encode("utf-8"),
    "COLD": WizMessage(params=BulbParameters(on=True, temperature=6500))
    .model_dump_json(
        exclude_none=True,
    )
    .encode("utf-8"),
}


def parse_args():
    parser = argparse.ArgumentParser(description="Wiz Light Control Script")
    parser.add_argument(
        "message",
        choices=list(map(str.lower, MESSAGES.keys())),
        help="Select the message to send",
    )
    return parser.parse_args()


def parse_bulb_response(
    response_message: ByteString
) -> Tuple[Optional[WizError], Optional[Union[WizSetResult, WizGetResult]]]:
    response_data = json.loads(response_message)
    error = response_data.get("error")
    result = response_data.get("result")
    return error, result


async def get_transport(
    event_loop: asyncio.AbstractEventLoop,
    response_future: asyncio.Future,
    ip: str = "255.255.255.255",
    port: int = 38899,
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


async def main():
    args = parse_args()
    event_loop = asyncio.get_event_loop()
    response_future = asyncio.Future()
    transport = await get_transport(IP, event_loop, response_future)

    transport.sendto(MESSAGES[args.message.upper()])

    response_message, _addr = await asyncio.wait_for(
        asyncio.shield(response_future), timeout=10
    )
    error, result = parse_bulb_response(response_message)
    if error:
        print(error)
    if result:
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
