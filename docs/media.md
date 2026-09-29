# Real robot footage review

All eight originals were inspected through twelve evenly spaced frames per file; the selected clip was additionally inspected at grasp / lift / release frames. This is visual review, not a frame-by-frame video audit. Originals remain unchanged in `/Users/geyinuo/Downloads`.

## Selected demonstration

- Source: `IMG_5403.MOV`, 22.100 seconds, 1920×1080, 30 fps, HLG/Dolby Vision metadata.
- Selected interval: **00:01.000–00:22.000**, one continuous 21-second clip, no internal cuts.
- Observed: white arm approaches the black rectangular block, closes its pink gripper, lifts and transfers it into the white tray, releases it, and withdraws. The block remains in the tray at the end. No human hand is visible in this selected interval.
- `pick-and-place-realtime.mp4`: 960×540 H.264, original speed, silent, HDR converted to SDR, faststart. Approx 1.6 MB.
- `pick-and-place-2x.gif`: 560×341 (including caption strip), 8 fps, 2× playback explicitly burned into the caption, about 10.5 seconds and 6.1 MB. Same continuous source interval.
- `demo-sequence.jpg`: three aligned frames with source timestamps 00:06, 00:14, 00:21 (approach / lift / placed), 1500×352.
- `approach.jpg`, `lift.jpg`, `placed.jpg`: individual selected frames at source 6, 14, 21 seconds, 960×540.

Footage alone cannot establish whether commands came from teleoperation or an autonomous policy, identify the checkpoint, prove training hardware/method/data count, or support a numerical success rate. The visual material should be captioned as a real-robot block pick-and-place demonstration; project/training statements should cite the user's confirmed experience separately.

## Original inventory and screening notes

| File | Duration (s) | Sampled visual observation |
|---|---:|---|
| IMG_5402.MOV | 62.705 | Several grasp/place motions; a human hand resets the block around 34 s. |
| IMG_5403.MOV | 22.100 | Clean continuous complete grasp/place sequence; chosen for concise presentation. |
| IMG_5404.MOV | 6.802 | Mostly stationary arm and block; not a useful action demonstration. |
| IMG_5405.MOV | 19.643 | Arm approaches and lowers toward block; sampled ending does not show a complete deposit. |
| IMG_5406.MOV | 157.852 | Multiple cycles, changing camera angle, visible manual reset around 129 s. |
| IMG_5407.MOV | 125.902 | Multiple pick/place motions, block/tray states change between cycles; less concise than chosen clip. |
| IMG_5408.MOV | 231.927 | Multiple cycles, close camera views and visible manual reset around 147 s. |
| IMG_5409.MOV | 184.068 | Multiple cycles, strong camera movement and manual resets around 50/134 s. |

All eight contact sheets (`IMG_54xx-sheet.jpg`) are retained for review only and need not be published.

## Reproduce selected MP4

```bash
ffmpeg -ss 1 -i IMG_5403.MOV -t 21 -an \
  -vf 'zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,scale=960:-2' \
  -c:v libx264 -preset medium -crf 24 -movflags +faststart pick-and-place-realtime.mp4
```

No synthesis, object edits, interpolation or claimed outcome enhancement was applied. Still/GIF typography was added only outside the footage. The GIF is explicitly accelerated; the MP4 is real time. Source audio was omitted.
