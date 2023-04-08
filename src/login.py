from flask import Flask, request

app = Flask(__name__)

@app.route('/login', methods=['GET'])
def login():
    # TODO: implement
    pass    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
