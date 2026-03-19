"""
CyberClip Graph UI – Flask backend
Run from inside the cyberclip package directory:
    python flask_server.py
"""
import sys, os, asyncio, json, re, traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from flask import Flask, request, jsonify, render_template
except ImportError:
    print("❌ CyberClip Web Interface requires Flask.")
    print("\nTo install web dependencies, run:")
    print("   pip install cyberclip[web]")
    print("\nOr install all optional dependencies:")
    print("   pip install cyberclip[all]")
    sys.exit(1)

try:
    from cyberclip.clipParser import clipParser
    from cyberclip.utilities import clean_tsv
except ImportError:
    from clipParser import clipParser
    from utilities import clean_tsv

app = Flask(__name__, static_folder="static", template_folder="templates")

# ── Global parser (loaded once) ──────────────────────────────────────────────
_parser: clipParser | None = None

def get_parser() -> clipParser:
    global _parser
    if _parser is None:
        _parser = clipParser()
        _parser.load_all()
    return _parser


def _serialize_action(name: str, action) -> dict:
    return {
        "name":          name,
        "description":   action.description if hasattr(action, "description") else name,
        "supportedType": sorted(list(action.supportedType)) if action.supportedType else [],
        "indicators":    getattr(action, "indicators", ""),
        "complex_param": action.complex_param if action.complex_param else {},
    }

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/actions", methods=["GET"])
def api_actions():
    """Return all available actions sorted alphabetically."""
    p = get_parser()
    actions = sorted(
        [_serialize_action(n, a) for n, a in p.actions.items()],
        key=lambda x: x["description"].lower()
    )
    return jsonify(actions)


@app.route("/api/parse", methods=["POST"])
def api_parse():
    """Parse text and return detected entities as graph nodes/edges."""
    data = request.get_json(force=True)
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text provided"}), 400

    p = get_parser()
    results = p.parseData(text)
    nodes, edges = [], []
    seen: dict[str, str] = {}
    nid = [0]

    def new_id():
        i = nid[0]; nid[0] += 1
        return f"n{i}"

    for ptype, values in results["matches"].items():
        if not values:
            continue
        for val in values:
            val_str = str(val).strip()
            if not val_str:
                continue
            key = f"{ptype}::{val_str}"
            if key not in seen:
                nid_ = new_id()
                seen[key] = nid_
                nodes.append({
                    "id":       nid_,
                    "label":    val_str[:45] + ("…" if len(val_str) > 45 else ""),
                    "value":    val_str,
                    "type":     ptype,
                    "metadata": {},
                })

    return jsonify({
        "nodes":   nodes,
        "edges":   edges,
        "types":   list(results["detectedType"]),
    })


@app.route("/api/parse_bulk", methods=["POST"])
def api_parse_bulk():
    """
    Parse multiple text values in bulk and return results for each.
    Request: { "values": ["text1", "text2", ...] }
    Response: { "results": [{ "nodes": [...], "types": [...] }, ...] }
    """
    data = request.get_json(force=True)
    values = data.get("values", [])

    if not values:
        return jsonify({"error": "No values provided"}), 400

    p = get_parser()
    results = []

    for text in values:
        text_str = str(text).strip()
        if not text_str:
            results.append({"nodes": [], "types": []})
            continue

        parsed = p.parseData(text_str)
        nodes = []
        seen: dict[str, str] = {}
        nid = [0]

        def new_id():
            i = nid[0]; nid[0] += 1
            return f"n{i}"

        for ptype, pvalues in parsed["matches"].items():
            if not pvalues:
                continue
            for val in pvalues:
                val_str = str(val).strip()
                if not val_str:
                    continue
                key = f"{ptype}::{val_str}"
                if key not in seen:
                    nid_ = new_id()
                    seen[key] = nid_
                    nodes.append({
                        "id":       nid_,
                        "label":    val_str[:45] + ("…" if len(val_str) > 45 else ""),
                        "value":    val_str,
                        "type":     ptype,
                        "metadata": {},
                    })

        results.append({
            "nodes": nodes,
            "types": list(parsed["detectedType"])
        })

    return jsonify({"results": results})


@app.route("/api/execute", methods=["POST"])
def api_execute():
    """Execute a single action on text."""
    data        = request.get_json(force=True)
    text        = data.get("text", "")
    action_name = data.get("action", "")
    complex_param = data.get("complex_param", {})

    if not text or not action_name:
        return jsonify({"error": "text and action are required"}), 400

    p = get_parser()
    action = p.actions.get(action_name)
    if action is None:
        return jsonify({"error": f"Action '{action_name}' not found"}), 404

    if complex_param:
        action.complex_param = complex_param

    try:
        result = asyncio.run(p.apply_actionable(action, text))
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e), "detail": traceback.format_exc()}), 500


@app.route("/api/execute_bulk", methods=["POST"])
def api_execute_bulk():
    """
    Execute action on a list of values (table column).
    Mirrors App.py logic: apply clean_tsv then split tabs into sub-columns.
    If column_name provided, merges duplicate columns.
    """
    data          = request.get_json(force=True)
    values        = data.get("values", [])
    action_name   = data.get("action", "")
    complex_param = data.get("complex_param", {})

    if not values or not action_name:
        return jsonify({"error": "values and action are required"}), 400

    p = get_parser()
    action = p.actions.get(action_name)
    if action is None:
        return jsonify({"error": f"Action '{action_name}' not found"}), 404

    if complex_param:
        action.complex_param = complex_param

    try:
        # Run sequentially to avoid race conditions with shared parser/action state
        raw_results = []
        for v in values:
            result = asyncio.run(p.apply_actionable(action, str(v)))
            raw_results.append(result)

        # Mirror App.py: clean TSV prefix, split into sub-columns
        cleaned = [clean_tsv(str(r), str(orig)) for r, orig in zip(raw_results, values)]
        split   = [r.split("\t") for r in cleaned]
        max_cols = max((len(r) for r in split), default=1)
        padded   = [r + [""] * (max_cols - len(r)) for r in split]

        return jsonify({
            "results":     padded,
            "num_columns": max_cols,
            "action_name": action_name,
        })
    except Exception as e:
        return jsonify({"error": str(e), "detail": traceback.format_exc()}), 500


@app.route("/api/actions_for", methods=["POST"])
def api_actions_for():
    """Return applicable actions for given text (for command palette context)."""
    data = request.get_json(force=True)
    text = data.get("text", "")
    if not text:
        return jsonify({"actions": []})

    p = get_parser()
    p.parseData(text)
    applicable = sorted(
        [_serialize_action(n, a) for n, a in p.actions.items() if a.parsers],
        key=lambda x: x["description"].lower()
    )
    return jsonify({"actions": applicable})


def main(host="127.0.0.1", port=5001, debug=False):
    """Main entry point for CyberClip web interface.

    Args:
        host (str): Host address to bind to. Default: 127.0.0.1
        port (int): Port number to listen on. Default: 5001
        debug (bool): Enable Flask debug mode. Default: False

    Returns:
        int: Exit code (always 0)
    """
    print(f"🌐 CyberClip Web Interface")
    print(f"📡 Loading parsers and actions...")
    get_parser()  # preload
    print(f"✓ Ready")
    print(f"🔗 Serving at http://{host}:{port}")
    print(f"   Press Ctrl+C to stop")

    try:
        app.run(host=host, port=port, debug=debug, use_reloader=False)
        return 0
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        return 0


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="CyberClip Web Interface")
    parser.add_argument("--host", default="127.0.0.1", help="Host address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5001, help="Port number (default: 5001)")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    main(host=args.host, port=args.port, debug=args.debug)
