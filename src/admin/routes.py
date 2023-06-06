from fastapi import Depends, UploadFile, File
from starlette.requests import Request
from starlette.responses import RedirectResponse
from fastapi_admin.app import app
from fastapi_admin.depends import get_resources
from fastapi_admin.template import templates
from typing import Annotated
from src.views_service.models import Proxy
from fastapi import Form, status
import shutil
import os
from src.views_service.models import Account
import pyunpack
from src.admin.start import app as root_app

@app.get("/")
async def home(
    request: Request,
    resources=Depends(get_resources),
):
    return templates.TemplateResponse(
        "dashboard.html",
        context={
            "request": request,
            "resources": resources,
            "resource_label": "Просмотреть канал",
            "page_title": "Просмотреть канал",
        },
    )

@app.get("/proxy/import")
async def import_proxy_page(
    request: Request,
    resources=Depends(get_resources),
):
    return templates.TemplateResponse(
        "proxy.html",
        context={
            "request": request,
            "resources": resources,
            "resource_label": "Импортировать прокси",
            "page_title": "Импортировать прокси",
        },
    )

@app.post("/proxy/import")
async def import_proxy(
    request: Request,
    text: Annotated[str, Form()],
    resources=Depends(get_resources),
):
    raw_proxies = text.split("\r\n")
    proxies = []
    for raw_proxy in raw_proxies:
        data = raw_proxy.split(":")
        if len(data) == 3:
            username = data[0]
            password, ip = data[1].split("@")
            port = data[2]
            proxies.append(Proxy(ip=ip, port=port, username=username, password=password))
        else:
            ip = data[0]
            port = data[1]
            proxies.append(Proxy(ip=ip, port=port))
    await Proxy.bulk_create(proxies, ignore_conflicts=True)
    return RedirectResponse("/admin/proxy/list",status_code=status.HTTP_303_SEE_OTHER)


@app.get("/account/import")
async def import_account(
    request: Request,
    resources=Depends(get_resources),
):
    return templates.TemplateResponse(
        "upload_accounts.html",
        context={
            "request": request,
            "resources": resources,
            "page_title": "Загрузите архив с tdata аккаунтов",
        },
    )

@app.post("/account/import")
async def import_acc(
    file: UploadFile = File(...),
):
    filepath = f"static/{file.filename}"
    ex_filename = filepath.replace(".rar","").replace(".zip","")
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    try:
        os.mkdir(ex_filename)
    except FileExistsError:
        shutil.rmtree(ex_filename, ignore_errors=True)
        os.mkdir(ex_filename)
    pyunpack.Archive(filepath).extractall(ex_filename)
    subdirs = next(os.walk(ex_filename))[1]
    accounts = []
    for dir in subdirs:
        accounts.append(Account(tdata_path=os.path.abspath(f"{ex_filename}/{dir}/tdata")))
    await Account.bulk_create(accounts, ignore_conflicts=True)
    await root_app.manager.add_accounts()
    return RedirectResponse("/admin/account/list",status_code=status.HTTP_303_SEE_OTHER)
