import os
import tempfile
from pathlib import Path

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 100MB upload limit


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/scrape", methods=["POST"])
def scrape():
    data = request.get_json()
    if not data or not data.get("url"):
        return jsonify({"error": "URL is required"}), 400

    url = data["url"].strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        from converters import get_converter

        converter = get_converter(url=True)
        if converter is None:
            return jsonify({"error": "Web scraping is not available. Missing dependencies."}), 500

        result = converter.convert(url)
        return jsonify({
            "markdown": result.content,
            "title": result.title or url,
            "source": url,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/convert", methods=["POST"])
def convert():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    original_name = file.filename
    ext = Path(original_name).suffix.lower()

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            file.save(tmp)
            tmp_path = tmp.name

        from converters import get_converter

        converter = get_converter(extension=ext, filepath=tmp_path)
        if converter is None:
            supported = _get_supported_formats()
            return jsonify({
                "error": f"Unsupported file type: '{ext}'. Supported formats: {', '.join(supported)}"
            }), 400

        result = converter.convert(tmp_path)
        return jsonify({
            "markdown": result.content,
            "title": result.title or original_name,
            "filename": Path(original_name).stem + ".md",
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


@app.route("/api/formats", methods=["GET"])
def formats():
    from converters import get_supported_formats

    return jsonify(get_supported_formats())


def _get_supported_formats():
    from converters import get_supported_formats

    info = get_supported_formats()
    return [ext for ext, available in info.items() if available]


if __name__ == "__main__":
    app.run(debug=True, port=5000)
