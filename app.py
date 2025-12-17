from fastapi import FastAPI, Query, Header, HTTPException
from fastapi.responses import PlainTextResponse
import yt_dlp
import os
from typing import Optional

app = FastAPI(title="YouTube Stream API")

CLIENT_KEY = os.getenv("CLIENT_KEY")


# 🔐 Client key verification
def verify_client_key(x_client_key: Optional[str]):
    if CLIENT_KEY is None:
        return
    if not x_client_key or x_client_key != CLIENT_KEY:
        raise HTTPException(status_code=401, detail="Invalid client key")


# 🏠 Health check
@app.get("/")
async def home():
    return "Server running"


# 1️⃣ Get video metadata
@app.get("/getvideo")
async def get_video(
    url: str = Query(..., description="YouTube video URL"),
    x_client_key: Optional[str] = Header(None)
):
    verify_client_key(x_client_key)

    try:
        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "noplaylist": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        formats = []
        for f in info.get("formats", []):
            if f.get("url") and f.get("vcodec") != "none":
                formats.append({
                    "format_id": f.get("format_id"),
                    "ext": f.get("ext"),
                    "resolution": f.get("resolution"),
                    "filesize": f.get("filesize"),
                })

        return {
            "title": info.get("title"),
            "duration": info.get("duration"),
            "thumbnail": info.get("thumbnail"),
            "formats": formats
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 2️⃣ Stream video (returns direct stream URL)
@app.get("/stream", response_class=PlainTextResponse)
async def stream_video(
    url: str = Query(..., description="YouTube video URL"),
    format_id: str = Query("best"),
    x_client_key: Optional[str] = Header(None)
):
    verify_client_key(x_client_key)

    try:
        ydl_opts = {
            "quiet": True,
            "format": format_id,
            "noplaylist": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            stream_url = info["url"]

        return stream_url

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
