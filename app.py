from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

VOICES_URL = "https://airvoz.com/api/tts/voices?type=voices&language="
HEADERS = {"accept": "application/json"}

# ─────────────────────────────────────────────────────────
# Language / Locale list (dropdown data)
# ─────────────────────────────────────────────────────────
languages_locales = [
    {"language": "African", "locale": "af-ZA"},
    {"language": "Albanian", "locale": "sq-AL"},
    {"language": "Amharic", "locale": "am-ET"},
    {"language": "Arabic", "locale": "ar-SA"},
    {"language": "Armenian", "locale": "hy-AM"},
    {"language": "Assamese", "locale": "as-IN"},
    {"language": "Azerbaijani", "locale": "az-AZ"},
    {"language": "Basque", "locale": "eu-ES"},
    {"language": "Bengali", "locale": "bn-IN"},
    {"language": "Bosnian", "locale": "bs-BA"},
    {"language": "Bulgarian", "locale": "bg-BG"},
    {"language": "Burmese", "locale": "my-MM"},
    {"language": "Catalan", "locale": "ca-ES"},
    {"language": "Chinese", "locale": "zh-CN"},
    {"language": "Croatian", "locale": "hr-HR"},
    {"language": "Czech", "locale": "cs-CZ"},
    {"language": "Danish", "locale": "da-DK"},
    {"language": "Dutch", "locale": "nl-NL"},
    {"language": "English", "locale": "en-US"},
    {"language": "Estonian", "locale": "et-EE"},
    {"language": "Finnish", "locale": "fi-FI"},
    {"language": "French", "locale": "fr-FR"},
    {"language": "Galician", "locale": "gl-ES"},
    {"language": "German", "locale": "de-DE"},
    {"language": "Greek", "locale": "el-GR"},
    {"language": "Gujarati", "locale": "gu-IN"},
    {"language": "Hebrew", "locale": "he-IL"},
    {"language": "Hindi", "locale": "hi-IN"},
    {"language": "Hungarian", "locale": "hu-HU"},
    {"language": "Icelandic", "locale": "is-IS"},
    {"language": "Indonesian", "locale": "id-ID"},
    {"language": "Inuktitut", "locale": "iu-Latn-CA"},
    {"language": "Irish", "locale": "ga-IE"},
    {"language": "Italian", "locale": "it-IT"},
    {"language": "Japanese", "locale": "ja-JP"},
    {"language": "Javanese", "locale": "jv-ID"},
    {"language": "Kannada", "locale": "kn-IN"},
    {"language": "Kazakh", "locale": "kk-KZ"},
    {"language": "Khmer", "locale": "km-KH"},
    {"language": "Korean", "locale": "ko-KR"},
    {"language": "Lao", "locale": "lo-LA"},
    {"language": "Latvian", "locale": "lv-LV"},
    {"language": "Lithuanian", "locale": "lt-LT"},
    {"language": "Macedonian", "locale": "mk-MK"},
    {"language": "Malayalam", "locale": "ml-IN"},
    {"language": "Maltese", "locale": "mt-MT"},
    {"language": "Marathi", "locale": "mr-IN"},
    {"language": "Mongolian", "locale": "mn-MN"},
    {"language": "Nepali", "locale": "ne-NP"},
    {"language": "Norwegian", "locale": "nb-NO"},
    {"language": "Odia", "locale": "or-IN"},
    {"language": "Pashto", "locale": "ps-AF"},
    {"language": "Persian", "locale": "fa-IR"},
    {"language": "Polish", "locale": "pl-PL"},
    {"language": "Portuguese", "locale": "pt-BR"},
    {"language": "Punjabi", "locale": "pa-IN"},
    {"language": "Romanian", "locale": "ro-RO"},
    {"language": "Russian", "locale": "ru-RU"},
    {"language": "Serbian", "locale": "sr-RS"},
    {"language": "Sinhala", "locale": "si-LK"},
    {"language": "Slovak", "locale": "sk-SK"},
    {"language": "Slovenian", "locale": "sl-SI"},
    {"language": "Somali", "locale": "so-SO"},
    {"language": "Spanish", "locale": "es-ES"},
    {"language": "Sundanese", "locale": "su-ID"},
    {"language": "Swahili", "locale": "sw-KE"},
    {"language": "Swedish", "locale": "sv-SE"},
    {"language": "Tamil", "locale": "ta-IN"},
    {"language": "Telugu", "locale": "te-IN"},
    {"language": "Thai", "locale": "th-TH"},
    {"language": "Turkish", "locale": "tr-TR"},
    {"language": "Ukrainian", "locale": "uk-UA"},
    {"language": "Urdu", "locale": "ur-PK"},
    {"language": "Uzbek", "locale": "uz-UZ"},
    {"language": "Vietnamese", "locale": "vi-VN"},
    {"language": "Welsh", "locale": "cy-GB"},
    {"language": "Zulu", "locale": "zu-ZA"},
]

# ─────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────
def normalize_voice(v):
    """Normalize possibly different API field names from AirVoz."""
    def pick(*keys, default=None):
        for k in keys:
            if isinstance(v, dict) and k in v and v[k] not in (None, ""):
                return v[k]
        return default

    return {
        "name":       pick("name", "VoiceName", "voice_name", default="Unknown"),
        "gender":     pick("gender", "Gender", default="N/A"),
        "voice_id":   pick("voice_id", "id", "VoiceId", "voiceID", default=""),
        "style":      pick("style", "Style", default=""),
        "avatar_url": pick("avatar_url", "AvatarUrl", "avatarURL", "image_url", default=""),
        "sample_url": pick("sample_url", "SampleUrl", "audio_sample_url", "preview_url", default=""),
        "locale":     pick("locale", "Locale", default=None),
    }

# ─────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────
@app.get("/")
def index():
    return render_template("index.html", languages=languages_locales)

@app.get("/api/voices")
def api_voices():
    locale = request.args.get("locale", "").strip()
    if not locale:
        return jsonify({"ok": False, "error": "Missing 'locale' query param"}), 400

    try:
        r = requests.get(VOICES_URL + locale, headers=HEADERS, timeout=20)
        if r.status_code != 200:
            return jsonify({"ok": False, "error": f"Upstream error {r.status_code}"}), 502

        data = r.json()
        if not isinstance(data, list):
            return jsonify({"ok": False, "error": "Unexpected API response format"}), 502

        voices = [normalize_voice(v) for v in data]
        return jsonify({"ok": True, "count": len(voices), "voices": voices})
    except requests.exceptions.RequestException as e:
        return jsonify({"ok": False, "error": f"Network error: {e}"}), 502
    except Exception as e:
        return jsonify({"ok": False, "error": f"Unexpected error: {e}"}), 500

if __name__ == "__main__":
    # Run the server
    app.run(host="0.0.0.0", port=5000, debug=True)
