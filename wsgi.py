"""A tiny customer-facing Flask web app for learning Git -> OpenShift -> delivery."""
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Hello Customer</title>
  <style>
    body { font-family: system-ui, sans-serif; background: #f4f6fb; margin: 0;
           display: grid; place-items: center; min-height: 100vh; }
    main { background: white; padding: 2rem; border-radius: 14px;
           width: min(420px, 85vw); box-shadow: 0 4px 30px #172d5218; }
    h1 { color: #133c70; margin-top: 0; }
    input, button { padding: .7rem; font-size: 1rem; }
    button { background: #1560ae; color: white; border: 0; border-radius: 5px; }
    p { color: #546477; }
  </style>
</head>
<body><main>
  <h1>Hello, {{ name }}!</h1>
  <p>This app was delivered using GitHub and OpenShift.</p>
  <form method="get">
    <label for="name">Your name</label><br><br>
    <input id="name" name="name" maxlength="60" placeholder="Type a name" required>
    <button type="submit">Greet me</button>
  </form>
  <p><small>Version 1.0 · Try <a href="/health">/health</a></small></p>
</main></body>
</html>"""


@app.get("/")
def index():
    name = (request.args.get("name", "Customer").strip() or "Customer")[:60]
    return render_template_string(PAGE, name=name)


@app.get("/health")
def health():
    return jsonify(status="ok")


if __name__ == "__main__":
    # Local demo only. OpenShift runs wsgi:app using Gunicorn (through S2I).
    app.run(host="127.0.0.1", port=5000)
