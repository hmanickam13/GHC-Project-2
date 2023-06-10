from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['GET'])
def test_endpoint():
    client_ip = request.remote_addr
    print(f"Received request from IP address: {client_ip}")
    return "Test Endpoint"

if __name__ == '__main__':
    app.run(debug=True)
