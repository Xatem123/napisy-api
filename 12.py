from flask import Flask, request, jsonify, send_from_directory
import subprocess

app = Flask(__name__)

def get_languages(url):
    """ Pobiera dostępne języki napisów dla podanego linku """
    try:
        result = subprocess.run(
            ["yt-dlp", "--list-subs", url],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        output = result.stdout
        if "no subtitles" in output.lower():
            return {"error": "Ten film nie posiada napisów."}

        langs = extract_languages(output)
        return {"languages": langs} if langs else {"error": "Nie znaleziono dostępnych języków."}

    except Exception as e:
        return {"error": f"Wystąpił błąd: {e}"}

def extract_languages(output):
    """ Parsuje listę dostępnych języków napisów """
    langs = []
    parsing = False
    for line in output.splitlines():
        if line.strip().startswith("Language"):
            parsing = True
            continue
        if parsing and line.strip():
            lang_code = line.split()[0]
            if lang_code not in langs:
                langs.append(lang_code)
    return langs

@app.route("/get_languages", methods=["POST"])
def get_languages_api():
    """ API do pobierania języków napisów """
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "Brak linku do filmu."}), 400

    response = get_languages(url)
    return jsonify(response)

@app.route("/")
def serve_index():
    """ Zwraca stronę HTML jako stronę główną """
    return send_from_directory(".", "index.html")

if __name__ == "__main__":
    app.run(debug=True)
