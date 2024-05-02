import pytest
import asyncio
from unittest.mock import MagicMock
from src.wiz import (
    WizMessage,
    parse_bulb_response,
    send_message_to_wiz,
    UDP_PORT
)
from typing import Optional, Type

from asyncio import AbstractEventLoop, DatagramProtocol
from typing import Callable, Optional, Type

class DefaultProtocol(DatagramProtocol):
    def datagram_received(self, data, _addr):
        pass


class UDPServer:
    __slots__ = ("_host", "_port", "_loop", "_protocol", "_transport")

    def __init__(
        self,
        *,
        host: str,
        port: int,
        loop: Optional[AbstractEventLoop] = None,
        protocol: Optional[Type[DatagramProtocol]] = None,
    ) -> None:
        self._host = host
        self._port = port

        self._loop = loop or asyncio.get_event_loop()
        self._protocol = protocol or DefaultProtocol
        self._transport = None

    async def __aenter__(self):
        listen = self._loop.create_datagram_endpoint(
            self._protocol, local_addr=(self._host, self._port)
        )
        self._transport, _ = await listen

    async def __aexit__(self, exc_type, exc, tb):
        self._transport.close()
        self._transport = None

# Mocking the response from the UDP server
@pytest.fixture
def mock_udp_server(event_loop):
    # server_transport = MagicMock()
    # server_transport.sendto = MagicMock()
    # server_protocol = MagicMock()

    # async def handle_data(data, addr):
    #     parsed_data = parse_bulb_response(data)
    #     server_protocol.datagram_received(parsed_data, addr)

    # server_protocol.datagram_received = MagicMock(side_effect=handle_data)
    # server_protocol.error_received = MagicMock()
    # server_protocol.connection_lost = MagicMock()

    # transport, protocol = event_loop.run_until_complete(
    #     event_loop.create_datagram_endpoint(
    #         lambda: server_protocol,
    #         local_addr=("localhost", UDP_PORT)
    #     )
    # )
    calls = 0
 
    class ServerProtocol(DatagramProtocol):
        def datagram_received(self, data, addr): 
            nonlocal calls
            calls += 1

    udp_port = UDP_PORT
    udp_server = UDPServer( 
        host="0.0.0.0", port=udp_port, protocol=ServerProtocol
    )

    yield udp_server
    

    udp_server

@pytest.mark.asyncio
async def test_send_message_to_wiz(mock_udp_server):
    ip_address = "127.0.0.1"
    message = WizMessage(method="getPilot")
    response = await send_message_to_wiz(ip_address, message)

    print(mock_udp_server.call_args)

    assert response is not None
    assert isinstance(response, tuple)
    assert len(response) == 2

    error, result = response
    assert error is None
    assert result is not None
    assert isinstance(result, dict)
    assert result.get("state") is not None
    assert result.get("temperature") is not None
