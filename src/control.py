import asyncio

from src.wiz import send_message_to_wiz, MESSAGES, WizMessage, BulbParameters
from src.models.bulb import Bulb

# async def assign_room_state(self) -> None:
#     await asyncio.gather(*[bulb.assign_wiz_info() for bulb in self.bulbs])

#     if not any(bulb.wiz_info for bulb in self.bulbs):
#         self.bulbs_state = None
#     else:
#         self.bulbs_state = any(
#             bulb.wiz_info and bulb.wiz_info.get("state") for bulb in self.bulbs
#         )

# async def assign_room_brightness(self) -> None:
#     # TODO: should probably be average of all bulbs
#     bulb = self.bulbs[0]
#     await bulb.assign_wiz_info()
#     await asyncio.gather(*[bulb.assign_wiz_info() for bulb in self.bulbs])

#     if not any(bulb.wiz_info for bulb in self.bulbs):
#         self.bulbs_brightness = None
#     if bulb.wiz_info:
#         avg = sum(
#             int(bulb.wiz_info["dimming"] if bulb.wiz_info["state"] else 0)
#             for bulb in self.bulbs
#         ) / len(self.bulbs)
#         self.bulbs_brightness = int(avg)


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
