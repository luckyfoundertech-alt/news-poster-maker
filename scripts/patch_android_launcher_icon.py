from pathlib import Path
import base64
from PIL import Image

src=Path("scripts/news-studio-logo.webp.b64")
if not src.exists(): raise SystemExit("NEWS Studio logo source missing")
logo=Image.open(__import__("io").BytesIO(base64.b64decode(src.read_text().strip()))).convert("RGBA")
res=Path("android/app/src/main/res")
for density,size in [("mdpi",48),("hdpi",72),("xhdpi",96),("xxhdpi",144),("xxxhdpi",192)]:
    folder=res/("mipmap-"+density); folder.mkdir(parents=True,exist_ok=True)
    icon=logo.resize((size,size),Image.Resampling.LANCZOS)
    icon.save(folder/"ic_launcher.png",optimize=True)
    icon.save(folder/"ic_launcher_round.png",optimize=True)
drawable=res/"drawable"; drawable.mkdir(parents=True,exist_ok=True)
logo.resize((432,432),Image.Resampling.LANCZOS).save(drawable/"news_studio_foreground.png",optimize=True)
adaptive=res/"mipmap-anydpi-v26"; adaptive.mkdir(parents=True,exist_ok=True)
xml='''<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/news_studio_icon_background"/>
    <foreground android:drawable="@drawable/news_studio_foreground"/>
</adaptive-icon>'''
(adaptive/"ic_launcher.xml").write_text(xml)
(adaptive/"ic_launcher_round.xml").write_text(xml)
colors=res/"values"; colors.mkdir(parents=True,exist_ok=True)
color_file=colors/"news_studio_icon_colors.xml"
color_file.write_text('''<resources><color name="news_studio_icon_background">#07143F</color></resources>''')
print("NEWS Studio launcher icon generated for all Android densities.")
