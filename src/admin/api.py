from fastapi import FastAPI, Request
from starlette.responses import RedirectResponse, Response, JSONResponse
from src.views_service.models import Channel


class CustomFastAPI(FastAPI):
    def setup_manager(self, manager):
        self.manager = manager

    @property
    def accounts_manager(self):
        return self.manager


app = CustomFastAPI()


@app.get("/")
async def index():
    return RedirectResponse(url="/admin")


@app.post("/api/viewPosts")
async def view_posts(request: Request):
    req_json = await request.json()
    try:
        await app.manager.view_posts(
            req_json["name"], req_json["account_id"], req_json["posts"]
        )
        return Response()
    except Exception:
        return Response(status_code=400)


@app.get("/api/getAccounts")
async def get_accounts():
    return JSONResponse({"accounts": app.manager.get_active_account_ids()})


@app.get("/api/getChannels")
async def get_channels():
    channels = await Channel.all().select_related("task")
    ret = []
    for channel in channels:
        ret.append(
            {
                "name": channel.name,
                "last_post_id": channel.last_post_id,
                "task": {"name": channel.task.name, "body": channel.task.body},
            }
        )
    return JSONResponse({"channels": ret})


@app.get("/api/getLastPost")
async def get_last_post(name: str):
    return JSONResponse({"id": await app.manager.get_last_post_id(name)})


@app.get("/api/changeLastPost")
async def change_last_post(post_id: int, name: str):
    channel = await Channel.get(name=name)
    channel.last_post_id = post_id
    await channel.save()
    return JSONResponse({"error": False})
