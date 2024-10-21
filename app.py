from flask import Flask, jsonify, request
from flask_cors import CORS
import convertsegy
import convertlas


app = Flask(__name__) 
CORS(app)

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
      [result, data] = convertlas.convertlas(file)
      print(jsonify({"result": result, "data": data, "status": 200, "message": "Data has been imported"}))
      return jsonify({"result": result, "data": data, "status": 200, "message": "Data has been imported"}), 200
    else:
      return jsonify({"status": 400, "message": "Your request file has not accepted!"}), 400
  except Exception as e:
    return jsonify({"error": str(e), "status": 500, "message": "Data failed to imported!"}), 500

if __name__ == "__main__":
  app.run(debug=True, host="0.0.0.0", port=5000)