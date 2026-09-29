<div align="center">

# π0.5 · Single Arm

**From dual-camera demonstrations to cloud policy and real-world manipulation**

120 demonstrations · Full fine-tuning on one H20 · Cloud inference · Local execution

[中文](README.md) · **English** · [Reproduce](docs/reproduce.md) · [Sources & credits](docs/provenance.md)

<img src="assets/pick-and-place-2x.gif" width="700" alt="Real robot picks up a black block and places it in a white tray, played at 2x speed" />

*Real-robot pick-and-place · 2× playback · [21-second real-time video](assets/pick-and-place-realtime.mp4)*

</div>

## Overview

An end-to-end Episode1 single-arm workflow: **demonstration collection → π0.5 full fine-tuning → cloud policy serving → local robot inference**. A leader–follower setup and fixed/wrist cameras provide 120 demonstrations. π0.5 is fine-tuned on a single H20, then a local client receives cloud-generated action chunks to perform block pick-and-place.

<img src="assets/pipeline.svg" width="100%" alt="Four stages: collect, fine-tune, serve and execute" />

| Collection | Training | Deployment |
| :--- | :--- | :--- |
| 120 demonstrations, two RGB views | π0.5 full fine-tuning, 1 × H20 | Cloud WebSocket policy |
| Six arm joints + gripper | 7-D actions, 50-step chunks | Asynchronous local execution |

## Real-world demonstration

<img src="assets/demo-sequence.jpg" width="100%" alt="Three real frames: approach, lift and transport, release into tray" />

Frames from one continuous clip show approach, lift and placement. This is a qualitative demonstration, not a measured success rate. [Footage provenance](docs/media.md)

## My contributions

- **Collection:** connected a teleoperation leader, Episode1 follower and two cameras; aligned state/action ordering and recorded demonstrations.
- **Training:** adapted LeRobot data, image preprocessing and normalization for π0.5 full fine-tuning; addressed checkpoint memory peaks and training recovery.
- **Deployment:** connected a cloud policy server to the local robot client, including action-chunk execution, state validation and communication recovery.

## Run the pipeline

```bash
git clone https://github.com/innovationasuna/pi05-single-arm.git
cd pi05-single-arm
git submodule update --init
cp configs/robot.example.json configs/robot.json
```

Install the two environments and configure your devices and paths using the [reproduction guide](docs/reproduce.md), then:

```bash
python scripts/pipeline.py record   # Local: record demonstrations
python scripts/pipeline.py convert  # Cloud: convert the dataset
python scripts/pipeline.py norm     # Cloud: compute normalization
python scripts/pipeline.py train    # Cloud: full fine-tuning
python scripts/pipeline.py serve    # Cloud: serve the policy
python scripts/pipeline.py infer    # Local: execute via an SSH tunnel
```

## Organization & credits

`modules/lerobot` handles collection and robot execution; `modules/openpi` handles training and serving. Both are pinned submodules with their original history and licenses. This workspace adds configuration, a stage launcher and documentation.

Built on [Physical Intelligence / OpenPI](https://github.com/Physical-Intelligence/openpi) and [Hugging Face / LeRobot](https://github.com/huggingface/lerobot). The original [openpi_single](https://github.com/innovationasuna/openpi_single) and [lerobot_single](https://github.com/innovationasuna/lerobot_single) repositories remain available. Code is Apache-2.0; see [sources and licensing](docs/provenance.md) for model terms and demo media.
