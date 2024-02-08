from flask import Flask, request 

app = Flask(__name__)

@app.route('/pause')
def hello():
    return 'Hello World!'


@app.route('/', methods=['POST','GET'])
def json():
    data = request.json
    print(data)
    return {"sampling": 2}

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, ssl_context=('certificate.crt', 'privateKey.key'))

