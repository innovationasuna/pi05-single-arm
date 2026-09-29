# Reproduce the pipeline · 复现指南

This workspace connects two pinned forks; the robot and GPU server use **separate environments**. Commands below start from the repository root unless noted. / 两端分别安装，以下命令默认从本仓库根目录执行。

## 1. Get the code / 获取源码

```bash
git clone https://github.com/innovationasuna/pi05-single-arm.git
cd pi05-single-arm
git submodule update --init
cp configs/robot.example.json configs/robot.json
```

Edit `configs/robot.json` on each machine. `source_dataset` and `base_params` may be absolute paths or paths relative to this workspace. Camera IDs `4` and `2` are historical examples: detect and inspect both views before recording. `local_python` must be the Python executable of your activated robot environment. The policy host defaults to the local SSH tunnel. Keep the experiment name and checkpoint aligned across machines.

分别修改配置中的数据目录、模型目录、串口与相机编号。`configs/robot.json` 不进入 Git。原始示范数据、基础权重、微调 checkpoint、Episode1 GUI server 二进制需自行准备；本仓库不包含这些文件。可从 [OpenPI 的模型说明](https://github.com/Physical-Intelligence/openpi#available-models) 获取 π0.5 基础权重，遵循对应模型条款。

## 2. Local robot / 本地环境

Reference setup: Ubuntu, Python 3.10, Feetech leader, Episode1 follower, two OpenCV cameras, Episode1 GUI server at `localhost:12345`.

```bash
conda create -n pi05-robot python=3.10 -y
conda activate pi05-robot
python -m pip install -e './modules/lerobot[feetech]'
python -m pip install -e modules/lerobot/packages/openpi-client
python -m lerobot.find_cameras opencv
# In a separate terminal, start your Episode1 GUI server:
modules/lerobot/scripts/run_enpei_gui.sh /path/to/3.gui_server_uni
# Follow the hardware calibration procedure, then:
python -m lerobot.set_middle --port=/dev/ttyACM0
python -m lerobot.episode_default_position
python scripts/pipeline.py record
```

Recording uses 30 FPS, 20-second episodes, 8-second resets and 120 requested episodes. Inspect both camera streams and the resulting dataset before transfer. The original recorded dataset contained 120 episodes / 71,760 frames; requesting 120 episodes alone does not establish data quality or an identical frame count. Keep an operator and physical power cutoff available during robot movement.

采集后将整个原始数据目录（`meta/`、`data/`、`videos/`）复制到云端，并让云端配置的 `source_dataset` 指向它。不要只传 Parquet。重复采集/续录请参照 [原采集记录](https://github.com/innovationasuna/lerobot_single/blob/8eb0a221264759692ddbc40fb9e68b2a78e90062/README.md#方块数据录制记录)，入口默认不会续录或覆盖数据。

## 3. GPU environment / 云端环境

Reference training hardware: one NVIDIA H20 96 GB. OpenPI uses Python 3.11, CUDA 12 JAX and its committed `uv.lock`. Its dataset reader is a pinned upstream LeRobot revision; **do not install `modules/lerobot` into this environment**.

```bash
cd modules/openpi
GIT_LFS_SKIP_SMUDGE=1 uv sync --frozen
GIT_LFS_SKIP_SMUDGE=1 uv pip install -e .
cd ../..
python3 scripts/pipeline.py convert
python3 scripts/pipeline.py norm
python3 scripts/pipeline.py train
# To resume the same experiment after interruption:
# python3 scripts/pipeline.py train --resume
```

`convert` writes to `modules/openpi/enpei_dataset/demo_move_block`, matching the existing training configuration. It pads RGB images to 224×224 and embeds them in Parquet; `total_videos=0` in converted metadata is expected. It does not alter state/action units. Existing output is rejected rather than overwritten.

默认入口选用 `enpei_robot_demo_move_block_pi05_finetune`：π0.5 全量微调，batch 32、horizon 50、单设备、EMA 0.999。代码保留另一个 LoRA 配置，但本项目经历和默认入口均为全量微调。训练配置上限为 30,000 steps；展示记录使用 20,000 checkpoint。训练恢复、checkpoint 主机内存峰值和可选监控脚本见 [原实验记录](https://github.com/innovationasuna/openpi_single/blob/927584e77873200242965f717352596f25085c35/docs/enpei_pi05_reproduction_zh.md)。完整训练 checkpoint 约 42 GB，需为临时保存与保留版本预留空间。

## 4. Cloud policy → local robot / 云端服务与真机推理

On the GPU server:

```bash
python3 scripts/pipeline.py serve
```

On the local machine, keep a separate terminal open for the SSH tunnel (replace `USER`, `GPU_HOST` and `SSH_PORT`):

```bash
ssh -N -L 6006:127.0.0.1:6006 -p SSH_PORT USER@GPU_HOST
```

In the activated robot environment:

```bash
python -m lerobot.episode_default_position
python scripts/pipeline.py infer
```

The server binds `0.0.0.0:6006` and has no application authentication; keep that port behind the host firewall and use SSH forwarding. The local control loop targets 30 Hz; this is **not** a claim of 30 network inference requests per second. A request sends two images, state and instruction; the policy returns an action chunk, and the client begins at index 2.

## Interface / 数据契约

| Layer | Contract |
|---|---|
| Recorded cameras | `observation.images.fixed`, `observation.images.handeye` |
| Converted cameras | `image`, `wrist_image` → 224×224 RGB, aspect-ratio-preserving padding |
| Online request | `observation/image`, `observation/wrist_image`, `observation/state`, `prompt` |
| State / action order | `joint1…joint6, gripper` |
| Units | First six joints: radians. Historical follower gripper observation: radians; gripper command: normalized actuator value. Preserve this asymmetry. |
| Model adaptation | First six actions use delta transforms internally; policy output is restored for robot execution |
| Response | `actions`: finite `(N, 7)` array; trained horizon is 50 |
| Execution | Start index 2; validate shape and finite values, queue asynchronous chunks |

不要把夹爪观测和命令当成同一单位，或仅修改其中一端；若改变数据契约，需要重新转换、统计和训练。详细实现见 [源码导航](provenance.md)。

## Local checks / 本次可运行检查

```bash
python3 -m unittest discover -s tests -v
python3 scripts/pipeline.py infer --config configs/robot.example.json --dry-run
```

These check command wiring without moving hardware. GPU training and real-robot execution require the external assets and hardware above. See [validation](validation.md) for what was actually run during integration.
