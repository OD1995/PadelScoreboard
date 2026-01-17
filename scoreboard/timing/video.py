import subprocess
from datetime import datetime
import json

class VideoTiming:

    def __init__(self, video_file_path):
        self.video_file_path = video_file_path


    def get_video_start(self) -> datetime|None:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-print_format", "json",
            "-show_entries",
            "format_tags=creation_time:stream_tags=creation_time",
            self.video_file_path
        ]

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        data = json.loads(result.stdout)

        # Try format-level tag first
        creation_time = (
            data.get("format", {}).get("tags", {}).get("creation_time")
        )

        # Fallback: check video stream tags
        if not creation_time:
            for stream in data.get("streams", []):
                if stream.get("codec_type") == "video":
                    creation_time = stream.get("tags", {}).get("creation_time")
                    if creation_time:
                        break

        return datetime.fromisoformat(creation_time.replace("Z", "+00:00"))