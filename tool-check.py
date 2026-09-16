import json,shutil
TOOLS={'ffmpeg':['ffmpeg'],'imagemagick':['magick','convert'],'exiftool':['exiftool'],'yt-dlp':['yt-dlp'],'pandoc':['pandoc']}
print(json.dumps({k:next((shutil.which(n) for n in v if shutil.which(n)),None) for k,v in TOOLS.items()},indent=2))
