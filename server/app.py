from flask import Flask, jsonify, request
from flask_socketio import SocketIO
import threading
import pandas as pd
from .preprocess import preprocess_logs
from .model_loader import load_model
from database.db_manager import fetch_logs_by_uuid

# Initialize Flask and SocketIO
app = Flask(__name__)
socketio = SocketIO(app)

# Global variables
model = load_model()
required_logs = 128
queue = []
lock = threading.Lock()

@app.route("/required_logs", methods=["GET"])
def get_required_logs():
    """Provide the required number of logs and WebSocket URL."""
    return jsonify({
        "required_logs": required_logs,
        "socket_url": "http://127.0.0.1:5000"
    })
@app.route("/upload_logs", methods=["POST"])
def upload_logs():
    """
    Receive logs from the client and process them.
    """
    data = request.json
    logs = data.get("logs", [])
    uuid = data.get("uuid")

    print(f"[INFO] Received {len(logs)} logs from client UUID: {uuid}")

    # Process logs (e.g., preprocess and predict)
    predictions = []
    for log in logs:
        parsed_log = preprocess_logs(log)
        predictions.append(model.predict([parsed_log]))

    print(f"[INFO] Predictions: {predictions}")
    return jsonify({"predictions": predictions}), 200


@socketio.on("logs_ready")
def handle_logs_ready(data):
    """Handle logs readiness notification from the client."""
    uuid = data.get("uuid")
    print(f"[INFO] Logs ready from agent {uuid}")
    threading.Thread(target=process_logs, args=(uuid,), daemon=True).start()

def process_logs(uuid):
    """Process logs fetched from the database."""
    raw_logs = fetch_logs_by_uuid(uuid)
    print(f"[INFO] Processing {len(raw_logs)} logs for UUID {uuid}")

    parsed_logs = []
    for raw_log in raw_logs:
        parsed_logs.append(preprocess_logs(raw_log[0]))

    with lock:
        queue.extend(parsed_logs)

    if len(queue) >= required_logs:
        run_predictions()

def run_predictions():
    """Run predictions on the collected logs."""
    with lock:
        if len(queue) < required_logs:
            return

        df = pd.DataFrame(queue[:required_logs])
        del queue[:required_logs]

    print("[INFO] Running predictions...")
    predictions = model.predict(df)

    socketio.emit("prediction_result", {
        "message": "Prediction complete",
        "predictions": predictions.tolist()
    })
    print("[INFO] Predictions sent to clients.")

if __name__ == "__main__":
    print("[INFO] Starting server...")
    socketio.run(app, host="0.0.0.0", port=5000)
