from flask import Flask, jsonify, request
from flask_cors import CORS
import convertsegy


app = Flask(__name__) 
CORS(app)

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route("/read-file", methods=["POST"])
def sendData():
  if 'file' not in request.files:
    return jsonify({"message": "No Files Accepted!", "status": 400}), 400
  file = request.files.get('file')
  format = request.form.get('format')

  try:
    if format == "SGY/SEGY" : 
      [result, data] = convertsegy.convertsegy(file)
      return jsonify({"result": result, "data": data, "status": 200, "message": "Data has been imported!"}), 200
    elif format == "LAS":
      return jsonify({"status": 500, "message": "Feature coming soon"}), 500
    else:
      return jsonify({"status": 400, "message": "Your request file has not accepted!"}), 500
  except Exception as e:
    logger.debug(e)
    return jsonify({"error": str(e), "status": 500, "message": "Data failed to imported!"}), 500

if __name__ == "__main__":
  app.run(debug=True)