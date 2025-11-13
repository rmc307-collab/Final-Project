from flask import Flask, send_from_directory, abort, jsonify, request
import os, csv
from pathlib import Path
import tempfile

app = Flask(__name__, static_folder='public')

# Data path
DATA_DIR = Path(os.getcwd()) / 'data'
DATA_DIR.mkdir(exist_ok=True)
DATA_FILE = DATA_DIR / 'attendance.csv'

# Try to import Julia executor if available
try:
    from julia_models.JuliaExecutor import SimpleJuliaExecutor
    JULIA_AVAILABLE = True
except Exception:
    SimpleJuliaExecutor = None
    JULIA_AVAILABLE = False


@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def static_proxy(path):
    full_path = os.path.join(app.static_folder, path)
    if os.path.isfile(full_path):
        return send_from_directory(app.static_folder, path)
    abort(404)


@app.route('/api/data', methods=['GET'])
def api_data():
    rows = []
    if DATA_FILE.exists():
        with open(DATA_FILE, newline='') as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append(r)
    return jsonify({'rows': rows})


@app.route('/api/entry', methods=['POST'])
def api_entry():
    payload = request.get_json(force=True)
    # Ensure header
    write_header = not DATA_FILE.exists()
    with open(DATA_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(['Location', 'Time', 'Attendance', 'Cleanliness', 'Date'])
        writer.writerow([payload.get('Location',''), payload.get('Time',''), payload.get('Attendance',''), payload.get('Cleanliness',''), payload.get('Date','')])
    return jsonify({'success': True})


# Lazy Julia executor singleton
_julia_executor = None

def get_julia_executor():
    global _julia_executor
    if _julia_executor is None:
        if not JULIA_AVAILABLE:
            return None
        try:
            _julia_executor = SimpleJuliaExecutor()
        except Exception:
            _julia_executor = None
    return _julia_executor


@app.route('/api/forecast', methods=['GET'])
def api_forecast():
    julia = get_julia_executor()
    if julia is None or not getattr(julia, 'is_running', False):
        return jsonify({'success': False, 'error': 'Julia not available'}), 500

    # Minimal Julia code: return a simple dict
    code = 'result = Dict("success"=>true, "message"=>"Hello from Julia")\nresult'
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jl', mode='w') as tf:
        tf.write(code)
        temp_path = tf.name
    try:
        result = julia.execute_file(temp_path, timeout=20)
    finally:
        try:
            os.unlink(temp_path)
        except:
            pass

    return jsonify(result)


@app.route('/health')
def health():
    return jsonify({'status':'ok'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
