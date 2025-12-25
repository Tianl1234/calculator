from flask import Flask, request, render_template_string
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
        <input type="text" name="url" placeholder="Videolink eingeben" size="60">
        <button type="submit">Abspielen</button>
    </form>

    {% if embed %}
        <h2>Video:</h2>
        {{ embed|safe }}

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

def youtube_embed(url):
    match = re.search(r"(?:v=|youtu\\.be/)([A-Za-z0-9_-]{11})", url)
    if not match:
        return "<p>Konnte YouTube-Video-ID nicht erkennen.</p>"
    video_id = match.group(1)
    return f"""
    <iframe width="640" height="360"
        src="https://www.youtube.com/embed/{video_id}"
        frameborder="0"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen>
    </iframe>
    """

def tiktok_embed(url):
    return f"""
    <blockquote class="tiktok-embed" cite="{url}" data-video-id="">
        <section></section>
    </blockquote>
    <script async src="https://www.tiktok.com/embed.js"></script>
    """

def mp4_embed(url):
    return f"""
    <video controls width="640">
        <source src="{url}" type="video/mp4">
        Dein Browser kann dieses Video nicht abspielen.
    </video>
    """

@app.route("/")
def index():
    url = request.args.get("url")
    embed = None
    mp4 = False

    if url:
        url = url.strip()
        if "youtube.com" in url or "youtu.be" in url:
            embed = youtube_embed(url)
        elif "tiktok.com" in url:
            embed = tiktok_embed(url)
        elif url.lower().endswith(".mp4"):
            embed = mp4_embed(url)
            mp4 = True
        else:
            embed = "<p>Dieser Link wird nicht unterstützt.</p>"

    return render_template_string(HTML, embed=embed, url=url, mp4=mp4)

if __name__ == "__main__":
    app.run(debug=True)
