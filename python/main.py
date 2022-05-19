import os
import logging
import pathlib
import json
import sqlite3
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

def existOrNot():
    conn = sqlite3.connect("../db/mercari.sqlite3")
    c = conn.cursor()
    with open("../db/items.db",'r') as f:
        schema = f.read()

    if not c.fetchone():
        c.execute(f"""{schema}""")

    conn.commit()
    conn.close()


@app.get("/")
def root():
    return {"message": "Hello, world!"}

@app.post("/items")
def add_item(name: str = Form(...),category: str = Form(...)):
    existOrNot()
    conn = sqlite3.connect("../db/mercari.sqlite3")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM items")
    colums_num = c.fetchone()[0]+1
    c.execute("INSERT INTO items VALUES(?, ?, ?)",(colums_num,name,category))
    conn.commit()
    conn.close()
    return colums_num,name,category

@app.get("/items")
async def get_items():
    existOrNot()
    conn = sqlite3.connect("../db/mercari.sqlite3")
    c = conn.cursor()
    c.execute("SELECT * FROM items")
    items = c.fetchall()
    conn.commit()
    conn.close()
    return items

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

@app.get("/search")
async def search_item(keyword: str):
    existOrNot()
    conn = sqlite3.connect("../db/mercari.sqlite3")
    c = conn.cursor()
    #https://www.ravness.com/posts/pythonsqlite
    c.execute("SELECT * FROM items WHERE name LIKE ? ", ('%'+keyword+'%',))
    items = c.fetchall()
    conn.commit()
    conn.close()
    return items