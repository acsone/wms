import asyncio
import logging
import re
import threading
from enum import Enum
from typing import List

import serial
from fastapi import APIRouter, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

_logger = logging.getLogger(__name__)

# pylint: disable=global-statement

html = """
<!DOCTYPE html>
<html>
    <head>
        <title></title>
    </head>
    <body>
        <input id="weight" readonly="1"/>
        <script>
            /*  */
            let ws = null;
            let retry = 0;
            let connect = () => {
                retry ++;
                ws = new WebSocket(`ws://localhost:8000/ws_weight`);
                ws.onmessage = (event) => {
                    let data = JSON.parse(event.data) ;
                    weight_input = document.getElementById('weight');
                    weight_input.value=data.value;
                    if (data.status === 'ACQUIRING') {
                        weight_input.style.backgroundColor='red';
                    } else {
                        weight_input.style.backgroundColor=null;
                    }
                    retry = 0;
                };
                ws.onclose = () => {
                    if (retry > 2) {
                        fallback();
                    } else {
                        connect();
                    }
                };
            };
            connect();
            let fallback = () => {
                setInterval(async function() {
                    let response = await fetch("/weight");
                    let data = await response.json()
                    weight_input = document.getElementById('weight');
                    weight_input.value=data.value;
                    return data
                }, 100);
            };
        </script>
    </body>
</html>
"""


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []  # noqa: E999

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        try:
            _logger.info("Disconnecting Websocket")
            await websocket.close()
            self.active_connections.remove(websocket)
        except ValueError:
            _logger.exception("Websocket not registered")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

    async def broadcast_json(self, json: str):
        for connection in self.active_connections:
            await connection.send_json(json)


stateThread = None
concurrentWeightResult = None
manager = ConnectionManager()
app = FastAPI()
router = APIRouter()


class WeightStatus(str, Enum):
    fixed = "FIXED"
    acquiring = "ACQUIRING"


class WeightResult(BaseModel):
    status: WeightStatus
    value: float


def serrialRead():
    ser = serial.Serial(
        port="/dev/ttyUSB0",
        baudrate=9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=0,
    )
    buffer = ""
    ser.read()
    global concurrentWeightResult
    while True:
        line = ser.readline()
        try:
            buffer += line.decode("utf-8")
        except UnicodeDecodeError:
            buffer = ""
            continue
        try:
            pos = buffer.index("\r\n")
        except ValueError:
            continue
        buffer = buffer[:pos]
        matches = re.match(
            r"^S (?P<stability>[SD])  (?P<weight> +([0-9\.]+)) kg$", buffer[:pos],
        )
        if matches:
            buffer = ""
            groups = matches.groupdict()
            stability = groups["stability"]
            value = float(groups["weight"])
            status = WeightStatus.fixed if stability == "S" else WeightStatus.acquiring
            concurrentWeightResult = WeightResult(value=value, status=status)


@app.on_event("startup")
def start_serial_reader():
    """
        Only 1 connection at a time is allowed on the serial port...
        Start a thread to read the data from serial port and store the result
        into a global variable. The global variable can therefore be safely accesser
        by the different workers running in //
    """
    global stateThread
    _logger.info("Start serial reader")
    stateThread = threading.Thread(target=serrialRead)
    stateThread.daemon = True
    stateThread.start()


@app.get("/")
async def get():
    return HTMLResponse(html)


@router.get("/weight", response_model=WeightResult)
def weight():
    global concurrentWeightResult
    return concurrentWeightResult


app.include_router(router)


@app.websocket("/ws_weight")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(0.2)
            # probe the state of the connection
            # https://github.com/tiangolo/fastapi/issues/3008
            # pylint: disable=except-pass
            try:
                await asyncio.wait_for(websocket.receive_text(), 0.0001)
            except asyncio.TimeoutError:
                pass
            if concurrentWeightResult:
                await manager.broadcast_json(concurrentWeightResult.dict())
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except RuntimeError:
        await manager.disconnect(websocket)
