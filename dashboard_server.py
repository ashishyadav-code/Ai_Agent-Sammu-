import os
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BASE_DIR = Path(__file__).parent.absolute()

def get_file_info(filepath):
    """Extract metadata about a file."""
    stat = filepath.stat()
    created = datetime.fromtimestamp(stat.st_ctime).isoformat()
    modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
    size = stat.st_size
    return {
        'name': filepath.name,
        'path': str(filepath.relative_to(BASE_DIR)),
        'size': size,
        'created': created,
        'modified': modified,
        'type': 'file',
        'extension': filepath.suffix.lower()
    }

def detect_model(filepath):
    """Heuristically detect which AI model is used in a Python file."""
    if not filepath.suffix == '.py':
        return None
    try:
        content = filepath.read_text(encoding='utf-8', errors='ignore')
        lines = content.split('\n')
        models = []
        for line in lines:
            line_lower = line.lower()
            if 'whisper' in line_lower:
                if 'whisper.load_model' in line_lower:
                    # extract model size
                    import re
                    match = re.search(r'whisper\.load_model\s*\(\s*["\']([^"\']+)["\']', line)
                    if match:
                        models.append(f'Whisper ({match.group(1)})')
                    else:
                        models.append('Whisper')
                else:
                    models.append('Whisper')
            if 'sentence_transformers' in line_lower:
                models.append('SentenceTransformer')
            if 'ollama' in line_lower or 'chat' in line_lower:
                # detect model names
                if 'qwen2.5:3b' in line:
                    models.append('Qwen2.5-3B')
                elif 'gpt-oss:120b-cloud' in line:
                    models.append('GPT-OSS 120B')
                elif 'model =' in line:
                    # try to extract model name
                    pass
            if 'faster_whisper' in line_lower:
                models.append('Faster-Whisper')
            if 'faiss' in line_lower:
                models.append('FAISS')
        return list(set(models)) if models else None
    except:
        return None

def scan_directory(dir_path):
    """Recursively scan directory and return tree."""
    items = []
    for item in dir_path.iterdir():
        if item.name.startswith('.'):
            continue
        if item.is_dir():
            children = scan_directory(item)
            items.append({
                'name': item.name,
                'path': str(item.relative_to(BASE_DIR)),
                'type': 'directory',
                'children': children
            })
        else:
            info = get_file_info(item)
            models = detect_model(item)
            if models:
                info['models'] = models
            items.append(info)
    return items

@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'dashboard.html')

@app.route('/api/files')
def list_files():
    tree = scan_directory(BASE_DIR)
    return jsonify(tree)

@app.route('/api/run', methods=['POST'])
def run_script():
    data = request.json
    filepath = data.get('file')
    if not filepath:
        return jsonify({'error': 'No file specified'}), 400
    full_path = BASE_DIR / filepath
    if not full_path.exists():
        return jsonify({'error': 'File not found'}), 404
    if full_path.suffix != '.py':
        return jsonify({'error': 'Only Python scripts can be run'}), 400
    
    try:
        # Run the script
        result = subprocess.run(
            [sys.executable, str(full_path)],
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout
        error = result.stderr
        return jsonify({
            'success': result.returncode == 0,
            'output': output,
            'error': error,
            'returncode': result.returncode
        })
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Script timed out after 30 seconds'}), 408
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/file_content')
def file_content():
    filepath = request.args.get('path')
    if not filepath:
        return jsonify({'error': 'No path specified'}), 400
    full_path = BASE_DIR / filepath
    if not full_path.exists() or not full_path.is_file():
        return jsonify({'error': 'File not found'}), 404
    try:
        content = full_path.read_text(encoding='utf-8', errors='ignore')
        return jsonify({'content': content})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002)