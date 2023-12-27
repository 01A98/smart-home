import asyncio

from sanic import Request, Sanic

from .context import HOME_PAGE, MORE_PAGE, PageContext
from .wiz import IP, MESSAGES, PORT, get_transport, parse_bulb_response

app = Sanic("smart-home")
app.static("/public", "./public")


@app.get("/")
@app.ext.template(HOME_PAGE.template_path)
async def home(request: Request):
    error, result = await send_message_to_wiz(MESSAGES["INFO"])
    context = PageContext(current_page=HOME_PAGE)
    return {
        "error": error,
        "info_result": [result],
        **context.model_dump(),
    }


@app.get("/more")
@app.ext.template(MORE_PAGE.template_path)
async def more(request: Request):
    context = PageContext(current_page=MORE_PAGE)
    return context.model_dump()


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


async def send_message_to_wiz(message: bytes):
    response_future = asyncio.Future()
    transport = await get_transport(
        asyncio.get_event_loop(), response_future, ip=IP, port=PORT
    )

    transport.sendto(message)

    response_message, _addr = await response_future
    return parse_bulb_response(response_message)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
