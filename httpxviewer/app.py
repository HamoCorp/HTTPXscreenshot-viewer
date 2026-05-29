from flask import Flask, render_template, request, send_from_directory
import os
import re

app = Flask(__name__)


def normalize_site(site):
    site = site.lower().replace("http://", "").replace("https://", "")
    if site.startswith("www."):
        site = site[4:]
    return site.rstrip("/")


def parse_httpx(httpx_path, output_dir):
    screenshot_dir = os.path.join(output_dir, "screenshot")
    response_dir = os.path.join(output_dir, "response")
    data = {}

    with open(httpx_path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            m = re.match(r"(https?://[^\s]+)", line)
            if not m:
                continue
            url = m.group(1)
            site = normalize_site(url)
            brackets = re.findall(r"\[.*?\]", line)
            data[site] = {"url": url, "brackets": brackets, "screenshots": [], "responses": []}

            # Screenshots
            ss_path = os.path.join(screenshot_dir, site)
            if os.path.exists(ss_path):
                data[site]["screenshots"] = [os.path.join(ss_path, f) for f in os.listdir(ss_path) if f.endswith(".png")]

            # Responses
            resp_path = os.path.join(response_dir, site)
            if os.path.exists(resp_path):
                data[site]["responses"] = [os.path.join(resp_path, f) for f in os.listdir(resp_path) if f.endswith(".txt")]

    return data


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        httpx_file = request.files.get("httpx_file")
        output_folder = request.form.get("output_folder")

        if not httpx_file or not output_folder:
            return "<h3>Please provide both HTTPX file and output folder path.</h3>"

        # Save HTTPX file temporarily
        tmp_path = os.path.join(os.getcwd(), "httpx_temp.txt")
        httpx_file.save(tmp_path)

        # Parse sites using provided output folder
        sites = parse_httpx(tmp_path, output_folder)
        return render_template("index.html", sites=sites)

    return render_template("upload.html")


@app.route("/file/<path:filepath>")
def serve_file(filepath):
    if os.path.exists(filepath):
        folder, name = os.path.split(filepath)
        return send_from_directory(folder, name)
    return "File not found", 404


if __name__ == "__main__":
    app.run(debug=True)
