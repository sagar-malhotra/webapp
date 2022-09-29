from flask import Flask, jsonify
application = Flask(__name__)

@application.route("/")
def health():
    return jsonify({"about":"Application is healthy"})

if __name__== '__main__':
    application.run(debug=True)
