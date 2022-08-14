from flask import Flask
import socket
import identification

app = Flask(__name__)
localid = identification.get_local_random_id(32)

AGENT = f'netAutoFS-Server {socket.gethostname()} {localid}'


@app.route('/exists')
def exists():
    return AGENT


app.run(host='0.0.0.0', port=8080, debug=True)
