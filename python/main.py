import os
import logging
import pathlib
import json
import sqlite3
import hashlib
from unicodedata import category
from fastapi import FastAPI, Form, HTTPException, File
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

def transDictList(itemsList):
    itemDictList = []
    for item in itemsList:
        itemDictList.append({"name":item[1],"category":item[2],"image":item[3]})
    return itemDictList

def transDict(item):
    print(item)
    return {"name":item[1],"category":item[2],"image":item[3]} if item != None else {}

@app.get("/")
def root():
    return {"message": "Hello, world!"}

@app.post("/items")
def add_item(name: str = Form(...),category: str = Form(...),image: bytes = File(...)):
    existOrNot()
    conn = sqlite3.connect("../db/mercari.sqlite3")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM items")
    colums_num = c.fetchone()[0]+1
    image_hash = hashlib.sha256(str(image).encode()).hexdigest()
    c.execute("INSERT INTO items VALUES(?, ?, ?, ?)",(colums_num,name,category,image_hash))
    conn.commit()
    conn.close()
    return colums_num,name,category,image_hash

@app.get("/items")
async def get_items():
    existOrNot()
    conn = sqlite3.connect("../db/mercari.sqlite3")
    c = conn.cursor()
    c.execute("SELECT * FROM items")
    items = c.fetchall()
    items_dict = transDictList(items)
    conn.commit()
    conn.close()
    return items_dict

@app.get("/items/{item_id}")
async def get_items(item_id):
    existOrNot()
    conn = sqlite3.connect("../db/mercari.sqlite3")
    c = conn.cursor()
    c.execute("SELECT * FROM items WHERE id = ?",(item_id,))
    item = c.fetchone()
    item_dict = transDict(item)
    conn.commit()
    conn.close()
    return item_dict

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
    items_dict = transDictList(items)
    conn.commit()
    conn.close()
    return {"items":items_dict}