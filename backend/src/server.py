from fastapi import FastAPI
import uvicorn

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello, World!"}


@app.get("/hello/{name}")
async def hello(name: str):
    return {"message": f"Hello, {name}!"}


#if you want to run fastapi from python interpreter with "python server.py" please uncomment the following codes
## or you can run with the following command
##       "uvicorn server:app --port 8000 --reload"
## if __name__ == "__main__":
##
##    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
##
##