from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": {"name": "Szymson"}}


# path parameters
@app.get("/blog/{id}")
def show(id: int):
    #fetch blog with id = id
    return {"data": id}
