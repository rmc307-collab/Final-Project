from flask import Flask, send_from_directory, abort, jsonify
import os
import tempfile

# Import the Julia executor to run small Julia scripts from the API
from julia_models.JuliaExecutor import SimpleJuliaExecutor

app = Flask(__name__, static_folder='public')

# Create placeholder for Julia executor. We will initialize it lazily in the
# /api/forecast handler to avoid issues with Flask's reloader creating multiple
# processes and orphaning the Julia subprocess (which caused broken pipe errors).
app.julia = None


@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def static_proxy(path):
    # Serve static files from public/ if they exist
    full_path = os.path.join(app.static_folder, path)
    if os.path.isfile(full_path):
        return send_from_directory(app.static_folder, path)
    abort(404)


@app.route('/health')
def health():
    return {'status': 'ok'}


@app.route('/api/forecast', methods=['GET'])
def api_forecast():
    """Demo endpoint: execute a tiny Julia script via SimpleJuliaExecutor and return its result as JSON.

    This uses a very small Julia snippet to avoid heavy dependency on MLJ packages.
    """
    # Initialize Julia executor on demand to avoid reloader/subprocess issues
    if app.julia is None:
        try:
            app.julia = SimpleJuliaExecutor()
        except Exception as e:
            return jsonify({'success': False, 'error': f'Failed to start Julia: {e}'}), 500

    if not app.julia.is_running:
        return jsonify({'success': False, 'error': 'Julia executor failed to start'}), 500

    # Minimal Julia code that returns a Dict to be serialized by the Julia wrapper
    code = 'result = Dict("success"=>true, "message"=>"Hello from Julia via API"); result'

    with tempfile.NamedTemporaryFile(delete=False, suffix='.jl', mode='w') as tf:
        tf.write(code)
        temp_path = tf.name

    try:
        result = app.julia.execute_file(temp_path, timeout=20)
    finally:
        try:
            os.unlink(temp_path)
        except:
            pass

    # The executor returns a dict-like object; ensure Flask returns JSON
    if isinstance(result, dict):
        return jsonify(result)
    return jsonify({'success': False, 'error': 'Unexpected executor response'})


# Data CSV helpers
DATA_PATH = os.path.join(os.getcwd(), 'data', 'attendance.csv')
os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)


@app.route('/api/data', methods=['GET'])
def api_data():
    rows = []
    if os.path.exists(DATA_PATH):
        import csv
        with open(DATA_PATH, newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
    return jsonify({'rows': rows})


@app.route('/api/entry', methods=['POST'])
def api_entry():
    from flask import request
    payload = request.get_json() or {}
    # Ensure header exists
    write_header = not os.path.exists(DATA_PATH) or os.path.getsize(DATA_PATH) == 0
    import csv
    with open(DATA_PATH, 'a', newline='') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(['Location', 'Time', 'Attendance', 'Cleanliness', 'Date'])
        writer.writerow([payload.get('Location',''), payload.get('Time',''), payload.get('Attendance',''), payload.get('Cleanliness',''), payload.get('Date','')])
    return jsonify({'success': True})


if __name__ == '__main__':
    # Run on port 3000 for local testing
    app.run(host='0.0.0.0', port=3000, debug=True)
