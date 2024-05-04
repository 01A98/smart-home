import asyncio
import contextlib
import json
import socket
from asyncio import DatagramProtocol
from typing import Type, Any

import pytest

from src.wiz import WizMessage, send_message_to_wiz


class UDPServer:
    def __init__(self, host: str, port: int, protocol: Type[DatagramProtocol]) -> None:
        self._host = host
        self._port = port
        self._loop = asyncio.get_event_loop()
        self._protocol = protocol
        self._transport = None

    async def __aenter__(self) -> None:
        listen = self._loop.create_datagram_endpoint(
            self._protocol, local_addr=(self._host, self._port)
        )
        self._transport, _ = await listen

    async def __aexit__(self, exc_type, exc, tb) -> None:
        self._transport.close()


def get_unused_udp_port() -> int:
    with contextlib.closing(socket.socket(type=socket.SOCK_DGRAM)) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


# TODO: use data from here to mock responses https://docs.pro.wizconnected.com/#graphql-schema


@pytest.mark.parametrize("server_res_data", [{"test": 12345}])
@pytest.mark.asyncio
async def test_send_message_to_wiz(
    server_res_data: dict[str, Any],
):
    class ServerProtocol(DatagramProtocol):
        def connection_made(self, transport):
            self.transport = transport

        def datagram_received(self, data, addr):
            self.transport.sendto(json.dumps(server_res_data).encode(), addr)

    host = "0.0.0.0"
    port = get_unused_udp_port()
    udp_server = UDPServer(host=host, port=port, protocol=ServerProtocol)

    async with udp_server:
        message = WizMessage(method="getPilot")
        res = await send_message_to_wiz(host, message, port)
        assert res is None
