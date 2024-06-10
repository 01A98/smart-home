import random
from dataclasses import dataclass

from sanic import Request, Sanic, html, json
from sanic.views import HTTPMethodView
from tortoise.transactions import atomic

from src.models.bulb import Bulb
from src.wiz import BulbParameters, WizMessage


@dataclass
class Routes:
    bulb_with_state: str = "bulb_with_state"


def create_view(app: Sanic) -> None:
    class BulbView(HTTPMethodView):
        decorators = [atomic()]

        @staticmethod
        async def get(request: Request, id: str):
            return html("Unimplemented", 404)

        @staticmethod
        async def post(request: Request, id: str):
            return html("Unimplemented", 404)

        @staticmethod
        async def patch(request: Request, id: str):
            return html("Unimplemented", 404)

        @staticmethod
        async def delete(request: Request, id: str):
            return html("Unimplemented", 404)

    # TODO: add option for room view alongside other inputs
    async def pick_random_color(request: Request, id: int):
        bulb = await Bulb.get(id=id)
        await bulb.send_message(
            WizMessage(
                params=BulbParameters(
                    state=True,
                    red=random.randint(0, 255),
                    green=random.randint(0, 255),
                    blue=random.randint(0, 255),
                )
            )
        )
        return json(
            bulb.wiz_info,
            headers={"HX-Trigger": f"reload-bulb-{bulb.id}-control-form"},
        )

    app.add_route(BulbView.as_view(), "/bulbs/<id:strorempty>")

    app.add_route(
        pick_random_color,
        "bulbs/<id:int>/pick-random-color",
        name="pick_random_color",
        methods=["POST"],
    )
