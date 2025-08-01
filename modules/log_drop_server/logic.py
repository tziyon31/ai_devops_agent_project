from flask import Flask, request, jsonify

def create_logdrop_app():
    app = Flask(__name__)
    logs = []

    @app.route("/analyze", methods=["POST"])
    def analyze():
        try:
            data = request.get_json()
            log = data.get("log", "")
            if not log:
                return jsonify({"error": "Missing log data"}), 400
            logs.append(log)
            return jsonify({
                "message": "Log received and stored",
                "total_logs": len(logs)
            }), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/logs", methods=["GET"])
    def get_logs():
        return jsonify({
            "total": len(logs),
            "logs": logs
        })

    return app, logs
'''
Use Instructions
In order to use the logs add code to insert them into DB for furthure use.
from logdrop_server import create_logdrop_app

app, logs = create_logdrop_app()
app.run(debug=True, port=5000)

'''
