from flask import Flask
import socket
import config

app = Flask(__name__)
localid = config.get_local_random_id(32)
DEFAULT_PROTOCOL_PORT = 7007


AGENT = f'netAutoFS-Server {socket.gethostname()} {localid}'


@app.route('/exists')
def exists():
    return AGENT


app.run(host='0.0.0.0', port=DEFAULT_PROTOCOL_PORT, debug=True)
