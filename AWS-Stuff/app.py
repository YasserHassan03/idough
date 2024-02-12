from flask import Flask, request 
import prediction as pred
import sys

app = Flask(__name__)
predictor = pred.breadPredictor()


@app.route('/pause')
def hello():
    return 'Hello World!'


@app.route('/sensors', methods=['POST','GET'])
def getSensors():
    data = request.json
    
    distance = data['tof']
    temp = data['temp']
    humid = data['humid']
    sampling = data['sampling']
    
    predictor.insertData(distance=distance, temp=temp, humid=humid) 
    print(f'dist: {distance}, temp: {temp}, humid: {humid}, sampling:{sampling}')
    # timeRemaining = predictor.predictTime()
    # print(f'Time Remaining: {timeRemaining}')
    #
    return {"sampling": sampling}


@app.route('/predict')
def predict():
    timeRemaining = predictor.predictTime()

    print(f'Time Remaining: {timeRemaining}')
    
    return {"eta" : timeRemaining}


if __name__ == '__main__':
    print(sys.argv)
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    app.run(host='0.0.0.0', port=port, debug=True, ssl_context=('certificate.crt', 'privateKey.key'))

