import asyncio
import json
from glob import glob

from sanic import Request, Sanic
from sanic_ext import render

from config import PAGES, Page
from context import PageContext
from wiz import IP, MESSAGES, PORT, get_transport, parse_bulb_response

app = Sanic(__name__)
app.static("/public", "./public")


def get_js_file(page: Page):
    html_path = page.file_path
    js_glob_path = "public" + "/" + html_path.replace(".html", ".*.js")
    return glob(js_glob_path)[0]


@app.get("/")
@app.ext.template(PAGES.HOME.file_path)
async def home(request: Request):
    error, result = await send_message_to_wiz(MESSAGES["INFO"])
    context = PageContext(current_page=PAGES.HOME).model_dump()
    print(result)

    loop = asyncio.get_event_loop()
    response_future = loop.create_future()
    transport = await get_transport(asyncio.get_event_loop(), response_future, ip=IP)
    transport.sendto(b"hello world")
    response_message, _addr = await asyncio.wait_for(
        asyncio.shield(response_future), timeout=5
    )
    print(response_message)

    return await render(
        headers={"HX-Trigger": json.dumps({"navigating-to-page": PAGES.HOME.name})},
        context={
            "error": error,
            "info_result": [result],
            "js_file": get_js_file(PAGES.HOME),
            **context,
        },
    )


@app.get("/more")
@app.ext.template("pages/more.html")
async def more(request: Request):
    context = PageContext(current_page=PAGES.HOME).model_dump()
    return await render(
        headers={"HX-Trigger": json.dumps({"navigating-to-page": PAGES.MORE.name})},
        context=context,
    )


@app.post("/toggle")
@app.ext.template("components/light-toggle.html")
async def toggle_on_off(request: Request):
    on = request.form.get("on") if request.form.get("on") else False
    # NOTE: request.form.get("off") is always present as a placeholder bc of default checkbox behavior in forms
    # off = True if not on and request.form.get("off") else False
    # if off:
    #     message = MESSAGES["OFF"]
    # if on:
    #     message = MESSAGES["ON"]

    # error, result = await send_message_to_wiz(message)
    # if error:
    #     return

    return {"bulb": {"state": "on" if on else "off"}}


async def send_message_to_wiz(message: str):
    response_future = asyncio.Future()
    transport = await get_transport(
        asyncio.get_event_loop(), response_future, ip=IP, port=PORT
    )

    transport.sendto(message)

    response_message, _addr = await asyncio.wait_for(
        asyncio.shield(response_future), timeout=10
    )
    return parse_bulb_response(response_message)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
