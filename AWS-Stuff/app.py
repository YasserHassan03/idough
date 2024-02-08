from flask import Flask,request, jsonify 

app = Flask(__name__)

@app.route('/pause')
def hello():
        return 'Hello World!'

@app.route('/', methods=['POST','GET'])
def json():
        #title = request.json()
        #content = request.json['content']
        data = request.json
        print(data['temp'])
        data= 1
        return jsonify(data)

if __name__ == '__main__':
        app.run(host='0.0.0.0', port=8080, debug=True, ssl_context=('assets/certificate.crt','assets/privateKey.key'))


