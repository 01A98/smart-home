import asyncio
from src.wiz import send_message_to_wiz, MESSAGES, WizMessage, BulbParameters
from src.models.bulb import Bulb
from typing import Literal


async def toggle_state(bulb_ids: list[int], state: bool) -> bool:
    if not bulb_ids:
        return False

    bulbs = await Bulb.filter(id__in=bulb_ids)
    tasks = [bulb.toggle_state(state) for bulb in bulbs]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    return not any(isinstance(result, Exception) for result in results)


async def change_brightness(bulb_ids: list[int], brightness: int) -> bool:
    if not bulb_ids:
        return False

    bulbs = await Bulb.filter(id__in=bulb_ids)
    tasks = [bulb.set_brightness(brightness) for bulb in bulbs]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    return not any(isinstance(result, Exception) for result in results)


async def set_scene_id(bulb_ids: list[int], scene_id: int) -> bool:
    if not bulb_ids:
        return False

    bulbs = await Bulb.filter(id__in=bulb_ids)
    tasks = [
        bulb.send_message(
            WizMessage(params=BulbParameters(state=True, sceneId=scene_id))
        )
        for bulb in bulbs
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    return not any(isinstance(result, Exception) for result in results)


async def set_temperature_by_name(
    bulb_ids: list[int],
    temperature: Literal["warmest", "warmer", "warm", "cold", "colder", "coldest"],
) -> bool:
    if not bulb_ids:
        return False

    bulbs = await Bulb.filter(id__in=bulb_ids)
    tasks = [bulb.send_message(MESSAGES[temperature.upper()]) for bulb in bulbs]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    return not any(isinstance(result, Exception) for result in results)
