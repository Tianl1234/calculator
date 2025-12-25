from flask import Flask, request, render_template_string
from markupsafe import Markup, escape
from urllib.parse import urlparse
import re

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Universal Videoplayer</title>
</head>
<body>
    <h1>Universal Videoplayer</h1>

    <form method="GET">
        <input type="text" name="url" placeholder="Videolink eingeben" size="60" value="{{ url|e }}">
        <button type="submit">Abspielen</button>
    </form>

    {% if embed %}
        <h2>Video:</h2>
        {{ embed }}

        {% if mp4 %}
            <br><br>
            <a href="{{ url }}" download>
                <button>Video herunterladen</button>
            </a>
        {% endif %}
    {% endif %}
</body>
</html>
"""

def is_safe_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
    except Exception:
        return False
    return parsed.scheme in ("http", "https") and parsed.netloc != ""

def youtube_embed(url: str) -> Markup:
    # supports watch?v=..., youtu.be/... and embed/... URLs
    match = re.search(r"(?:v=|youtu\.be/|embed/)([A-Za-z0-9_-]{11})", url)
    if not match:
        return Markup("<p>Konnte YouTube-Video-ID nicht erkennen.</p>")
    video_id = match.group(1)
    html = f"""
    <iframe width="640" height="360"
        src="https://www.youtube.com/embed/{escape(video_id)}"
        frameborder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen>
    </iframe>
    """
    return Markup(html)

def tiktok_embed(url: str) -> Markup:
    # versuche Video-ID aus /video/<id> zu extrahieren
    m = re.search(r"/video/(\d+)", url)
    if m:
        vid = m.group(1)
        html = f'''
        <blockquote class="tiktok-embed" cite="{escape(url)}" data-video-id="{escape(vid)}">
            <section></section>
        </blockquote>
        <script async src="https://www.tiktok.com/embed.js"></script>
        '''
        return Markup(html)
    # Fallback: nutze blockquote mit cite (manchmal reicht das)
    return Markup(f'''
        <blockquote class="tiktok-embed" cite="{escape(url)}">
            <section></section>
        </blockquote>
        <script async src="https://www.tiktok.com/embed.js"></script>
    ''')

def mp4_embed(url: str) -> Markup:
    # url wurde bereits validiert; escape für Attribute
    return Markup(f"""
    <video controls width="640">
        <source src="{escape(url)}" type="video/mp4">
        Dein Browser kann dieses Video nicht abspielen.
    </video>
    """)

@app.route("/")
def index():
    url = request.args.get("url", "").strip()
    embed = None
    mp4 = False

    if url:
        if not is_safe_url(url):
            embed = Markup("<p>Ungültige oder unsichere URL. Bitte http/https verwenden.</p>")
        else:
            lower = url.lower()
            if "youtube.com" in lower or "youtu.be" in lower:
                embed = youtube_embed(url)
            elif "tiktok.com" in lower:
                embed = tiktok_embed(url)
            elif lower.endswith(".mp4"):
                embed = mp4_embed(url)
                mp4 = True
            else:
                embed = Markup("<p>Dieser Link wird nicht unterstützt.</p>")

    # render_template_string auto-escapt Jinja-Ausgaben; embed ist Markup (sicher markiert)
    return render_template_string(HTML, embed=embed, url=url, mp4=mp4)

if __name__ == "__main__":
    app.run(debug=True)
