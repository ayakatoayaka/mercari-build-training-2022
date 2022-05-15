import os
import logging
import pathlib
import json
from unicodedata import category
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO
images = pathlib.Path(__file__).parent.resolve() / "image"
origins = [ os.environ.get('FRONT_URL', 'http://localhost:3000') ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET","POST","PUT","DELETE"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Hello, world!"}

@app.post("/items")
def add_item(name: str = Form(...),category: str = Form(...)):
    logger.info(f"Receive item: {name}")
    with open('items.json') as f:
        try: 
            itemData = json.load(f)
        except:
            itemData = {"items":[]}
    itemData["items"].append({"name": f"{name}", "category": f"{category}"})
    with open('items.json', 'w') as f:
        json.dump(itemData, f)
    return {"message": f"item received: {name}"}

@app.get("/items")
async def get_items():
    with open('items.json') as f:
        try: 
            itemData = json.load(f)
        except:
            itemData = {"items":[]}
    return itemData

@app.get("/image/{items_image}")
async def get_image(items_image):
    # Create image path
    image = images / items_image

    if not items_image.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image path does not end with .jpg")

    if not image.exists():
        logger.debug(f"Image not found: {image}")
        image = images / "default.jpg"

    return FileResponse(image)
