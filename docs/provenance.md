# Sources, changes and licenses · 来源与改动

## Pinned source / 固定源码

| Component | Fork snapshot | Upstream | License |
|---|---|---|---|
| Cloud training & serving | [openpi_single @ 927584e](https://github.com/innovationasuna/openpi_single/tree/927584e77873200242965f717352596f25085c35) | [Physical Intelligence / openpi](https://github.com/Physical-Intelligence/openpi) | [Apache-2.0](https://github.com/innovationasuna/openpi_single/blob/927584e77873200242965f717352596f25085c35/LICENSE); [Gemma terms](https://github.com/innovationasuna/openpi_single/blob/927584e77873200242965f717352596f25085c35/LICENSE_GEMMA.txt) |
| Collection & robot client | [lerobot_single @ 8eb0a22](https://github.com/innovationasuna/lerobot_single/tree/8eb0a221264759692ddbc40fb9e68b2a78e90062) | [Hugging Face / LeRobot](https://github.com/huggingface/lerobot) | [Apache-2.0](https://github.com/innovationasuna/lerobot_single/blob/8eb0a221264759692ddbc40fb9e68b2a78e90062/LICENSE) |

Git submodule entries pin exact revisions. `git submodule update --init` checks out those revisions; do not use `--remote` when reproducing this snapshot. Both original repositories and their history remain intact. The nested ALOHA/LIBERO simulation submodules are not required for this Episode1 real-robot path.

本仓库原创的运行入口与文档代码采用根目录 [Apache-2.0](../LICENSE)。子模块保留原版权声明和许可证；Gemma/模型权重适用各自条款，Apache-2.0 不授予第三方模型权重的额外权利。`assets/` 中用户拍摄的演示媒体仅用于本项目展示，未随代码授予 Apache-2.0 许可。

## What was adapted / 项目改动

The robot and learning frameworks are upstream work. This project connects them for an Episode1 single arm; it does not claim to implement π0.5 or LeRobot from scratch.

| Area | Project work | Source |
|---|---|---|
| Robot I/O | Feetech leader + Episode1 follower; seven-dimensional ordering, serial retries, socket lock/timeout/reconnect | [leader](https://github.com/innovationasuna/lerobot_single/blob/8eb0a221264759692ddbc40fb9e68b2a78e90062/src/lerobot/teleoperators/enpei_leader/enpei_leader.py), [follower](https://github.com/innovationasuna/lerobot_single/blob/8eb0a221264759692ddbc40fb9e68b2a78e90062/src/lerobot/robots/enpei_follower/enpei_follower.py), [socket](https://github.com/innovationasuna/lerobot_single/blob/8eb0a221264759692ddbc40fb9e68b2a78e90062/src/lerobot/robots/enpei_follower/episode_server.py) |
| Data | Dual-camera recording; local dataset conversion with padding and overwrite protection | [record](https://github.com/innovationasuna/lerobot_single/blob/8eb0a221264759692ddbc40fb9e68b2a78e90062/src/lerobot/record.py), [converter](https://github.com/innovationasuna/openpi_single/blob/927584e77873200242965f717352596f25085c35/examples/libero/lerobot2oppi.py) |
| Training | Local dataset root; π0.5 full-finetune config; checkpoint memory limits and completion checks; W&B resume handling | [config](https://github.com/innovationasuna/openpi_single/blob/927584e77873200242965f717352596f25085c35/src/openpi/training/config.py), [checkpoints](https://github.com/innovationasuna/openpi_single/blob/927584e77873200242965f717352596f25085c35/src/openpi/training/checkpoints.py), [train](https://github.com/innovationasuna/openpi_single/blob/927584e77873200242965f717352596f25085c35/scripts/train.py) |
| Deployment | Cloud WebSocket policy and asynchronous local action consumption; finite/shape checks and action index handling | [server](https://github.com/innovationasuna/openpi_single/blob/927584e77873200242965f717352596f25085c35/scripts/serve_policy.py), [client](https://github.com/innovationasuna/lerobot_single/blob/8eb0a221264759692ddbc40fb9e68b2a78e90062/src/lerobot/test_openpi.py) |
| Integration | Separate dependency environments, one configuration, stage launcher, bilingual presentation and sourced media | [pipeline](../scripts/pipeline.py), [config](../configs/robot.example.json) |

## Experiment record / 实验记录

120 demonstrations and one-H20 full fine-tuning are the author's confirmed experiment facts, also recorded in the pinned repositories. The prior experiment documentation reports checkpoint 20,000 as the real-robot checkpoint. This integration does not rerun that training, re-measure success, or infer checkpoint identity from phone footage.

- [Original experiment log](https://github.com/innovationasuna/openpi_single/blob/927584e77873200242965f717352596f25085c35/docs/enpei_pi05_reproduction_zh.md)
- [W&B experiment](https://wandb.ai/innovationasuna-south-china-university-of-technology/openpi/runs/b9e6ulme)
- [Phone-video provenance](media.md)

The W&B run's recorded `crashed` state and checkpoint-saving issues are retained in the original log. Training loss is not a task success rate. No benchmark success rate is claimed.
