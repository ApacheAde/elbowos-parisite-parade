# Parisite Parade

Full-colour Python 3 neon lane-float arcade for [ElbowOS](https://x.com/ElbowOS).

Three parade lanes rush the camera. Steer a baton into rose, lime, cyan and gold lanterns. Dodge sour drums. Not a ROM, not an emulator, and not a clone of the ring-hop / keep-up / scoop packs.

Featured account: https://x.com/ElbowOS

Drive reel (9:16, 15s): https://drive.google.com/file/d/1p0AB-mOgZaHvL5iDJJfMp7tIQZsRDQkT/view?usp=drivesdk

## Play

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 parisite_parade.py --play
```

A / D or arrow keys change lane. R restarts.

Needs Python 3.10+ and a desktop window (pygame + SDL).

## Record a 9:16 reel

```bash
python3 parisite_parade.py --record
```

Writes `PARISITE_PARADE_ElbowOS.mp4` (1080x1920, 15 seconds, 30 fps, H.264 yuv420p). Headless runs use `SDL_VIDEODRIVER=dummy` and pipe RGB frames to ffmpeg.
