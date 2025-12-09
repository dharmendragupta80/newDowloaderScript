from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

@app.route('/')
def home():
    return 'YouTube Downloader API is running!'

@app.route('/getvideo', methods=['GET'])
def get_video():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL parameter missing'}), 400

    ydl_opts = {
        'quiet': True,
        'format': 'best[ext=mp4]/best',
        'noplaylist': True,
        'socket_timeout': 10,
        'retries': 3,
        'geo_bypass': True,
        'nocheckcertificate': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'entries' in info:
                info = info['entries'][0]

            direct_url = info.get('url')

            if not direct_url:
                return jsonify({'error': 'Could not extract direct video URL'}), 500

            return jsonify({'url': direct_url})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
