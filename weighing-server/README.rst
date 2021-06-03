===============
Weighing-server
===============

Websocket server forwarding weight informations from serial port.
This server is designed to process information from a Mettler Toledo IND42 device. 

run
~~~

..code:: bash

    uvicorn weighing_server.main:app --reload