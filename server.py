from flask import Flask
import socket
import identification

app = Flask(__name__)

AGENT = f'netAutoFS-Server {socket.gethostname()} {identification.get_local_random_id()}'


@app.route('/exists')
def exists():
    return AGENT
