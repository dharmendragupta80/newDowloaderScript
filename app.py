from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import PlainTextResponse
from fastapi.concurrency import run_in_threadpool
import yt_dlp
import os

app = FastAPI()

CLIENT_KEY = os.getenv("CLIENT_KEY")


def verify_client_key(x_client_key: str | None = None):
    if CLIENT_KEY is None:
        return True
    if x_client_key != CLIENT_KEY:
        raise HTTPException(status_code=401, detail="Invalid client key")


@app.get("/")
async def home():
    return "Server running"


def extract_video_info(url: str):
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)


@app.get("/getvideo")
async def get_video(url: str, _: bool = Depends(verify_client_key)):
    try:
        info = await run_in_threadpool(extract_video_info, url)

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


@app.get("/stream", response_class=PlainTextResponse)
async def stream_video(
    url: str,
    format_id: str = "best",
    _: bool = Depends(verify_client_key)
):
    def get_stream():
        ydl_opts = {
            "quiet": True,
            "format": format_id,
            "noplaylist": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info["url"]

    try:
        stream_url = await run_in_threadpool(get_stream)
        return stream_url
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
