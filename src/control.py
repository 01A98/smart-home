import asyncio

from src.wiz import send_message_to_wiz, MESSAGES, WizMessage, BulbParameters
from src.models.bulb import Bulb
from typing import Literal


async def toggle_state(bulb_ids: list[int], state: bool) -> bool:
    bulbs = await Bulb.filter(id__in=bulb_ids)

    if len(bulb_ids) == 0:
        return False

    async with asyncio.TaskGroup() as group:
        tasks = [group.create_task(bulb.toggle_state(state)) for bulb in bulbs]

    # TODO: this doesn't make sense if it throws
    return False if any([task.exception() for task in tasks]) else True


async def change_brightness(bulb_ids: list[int], brightness: int) -> bool:
    bulbs = await Bulb.filter(id__in=bulb_ids)

    if len(bulb_ids) == 0:
        return False

    async with asyncio.TaskGroup() as group:
        tasks = [group.create_task(bulb.set_brightness(brightness)) for bulb in bulbs]

    # TODO: this doesn't make sense if it throws
    return False if any([task.exception() for task in tasks]) else True


async def set_scene_id(bulb_ids: list[int], scene_id: int) -> bool:
    bulbs = await Bulb.filter(id__in=bulb_ids)

    if len(bulb_ids) == 0:
        return False

    async with asyncio.TaskGroup() as group:
        tasks = [
            group.create_task(
                bulb.send_message(
                    WizMessage(params=BulbParameters(state=True, sceneId=scene_id))
                )
            )
            for bulb in bulbs
        ]

    # TODO: this doesn't make sense if it throws
    return False if any([task.exception() for task in tasks]) else True


async def set_temperature_by_name(
    bulb_ids: list[int],
    temperature: Literal["warmest", "warmer", "warm", "cold", "colder", "coldest"],
) -> bool:
    bulbs = await Bulb.filter(id__in=bulb_ids)

    if len(bulb_ids) == 0:
        return False

    async with asyncio.TaskGroup() as group:
        tasks = [
            group.create_task(
                bulb.send_message(
                    MESSAGES[temperature.upper()],
                )
            )
            for bulb in bulbs
        ]

    # TODO: this doesn't make sense if it throws
    return False if any([task.exception() for task in tasks]) else True
