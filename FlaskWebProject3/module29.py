
# test_api.py
from flask import Flask, request

app = Flask(__name__)

@app.route('/api/validate', methods=['POST','GET'])
def validate():
    print("ASDF")
    if request.method=="GET":
        print("ddddddddddddddd")
        return "ERROR", 401
    data = request.get_json()
    userid = data.get("userid")
    password = data.get("password")

    if userid == "testuser" and password == "testpass":
        print("VALID")
        return "VALID", 200
    print("ERROR")
    return ("ERROR", 401)

if __name__ == '__main__':
    print("ASDFs")
    app.run(host="0.0.0.0", debug=True,port=5000)
