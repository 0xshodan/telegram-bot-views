from fastapi_admin.app import app
from fastapi_admin.resources import Link
from fastapi_admin.file_upload import FileUpload
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
upload = FileUpload(uploads_dir=os.path.join(BASE_DIR, "static", "uploads"))


@app.register
class Home(Link):
    label = "Home"
    icon = "fas fa-home"
    url = "/admin"
