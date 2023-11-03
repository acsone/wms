# create a simpel REST service with fastapi
# with a method GET /hw_proxy/weight that returns a json with a value field with a
# random weight between 0 and 1000 and a status field with a value of 'SUCCESS'
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


@app.get("/hw_proxy/weight")
async def get_weight():
    return {
        "value": 999,
        "status": "FIXED",
    }


# disable CORS
# https://fastapi.tiangolo.com/tutorial/cors/
# https://fastapi.tiangolo.com/advanced/cors/


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
