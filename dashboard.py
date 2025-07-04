from flask import Flask, render_template
import json
import hashlib
import os

app = Flask(__name__)
CHAIN_FILE = '../data/chain.json'

def compute_hash(entry):
    entry_copy = dict(entry)
    entry_copy.pop("curr_hash", None)
    return hashlib.sha256(json.dumps(entry_copy, sort_keys=True).encode()).hexdigest()

def verify_and_load_chain():
    if not os.path.exists(CHAIN_FILE):
        return [], "Chain file not found."

    with open(CHAIN_FILE, 'r') as f:
        chain = json.load(f)

    status = "✅ Chain is valid"
    for i, block in enumerate(chain):
        expected_hash = compute_hash(block)
        block["valid"] = True

        if block["curr_hash"] != expected_hash:
            block["valid"] = False
            status = f"Tampering detected at index {i}"
            break

        if i > 0 and block["prev_hash"] != chain[i-1]["curr_hash"]:
            block["valid"] = False
            status = f"Chain broken at index {i}"
            break

    return chain, status

@app.route('/')
def dashboard():
    logs, status = verify_and_load_chain()
    return render_template("dashboard.html", logs=logs, status=status)

if __name__ == '__main__':
    app.run(debug=True)
