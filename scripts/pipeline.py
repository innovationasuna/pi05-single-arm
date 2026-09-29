#!/usr/bin/env python3
"""One entry point for the local robot and cloud OpenPI environments."""
import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OPENPI = ROOT / 'modules/openpi'
LEROBOT = ROOT / 'modules/lerobot'
TRAIN_CONFIG = 'enpei_robot_demo_move_block_pi05_finetune'
CONVERTED = OPENPI / 'enpei_dataset/demo_move_block'


def root_path(value):
    path = Path(value).expanduser()
    return path if path.is_absolute() else ROOT / path


def build_command(stage, cfg, resume=False):
    """Return cwd, argv and env without importing either ML environment."""
    env = os.environ.copy()
    env['PI05_BASE_PARAMS'] = str(root_path(cfg['base_params']))
    env['XLA_PYTHON_CLIENT_PREALLOCATE'] = 'false'
    python = cfg.get('local_python', 'python')
    uv = cfg.get('uv', 'uv')
    task = cfg['task']
    robot = cfg['robot']
    cameras = cfg['cameras']
    if cameras['fixed'] == cameras['handeye']:
        raise ValueError('fixed and handeye must refer to different camera devices')
    if not 0 <= cfg['action_start_index'] < 50:
        raise ValueError('action_start_index must be in [0, 50)')
    if cfg['episodes'] <= 0:
        raise ValueError('episodes must be positive')
    if resume and stage != 'train':
        raise ValueError('--resume is only supported for train')
    size = (320, 240) if stage == 'record' else (640, 480)
    camera_config = {
        name: dict(type='opencv', index_or_path=cameras[name], width=size[0], height=size[1], fps=30)
        for name in ('handeye', 'fixed')
    }
    robot_args = [
        '--robot.type=enpei_follower', '--robot.id=enpei_follower',
        f"--robot.ip_address={robot['host']}", f"--robot.port={robot['port']}",
        f'--robot.cameras={json.dumps(camera_config)}', '--enpei_use_radian=true',
    ]
    if stage == 'record':
        cmd = [python, '-m', 'lerobot.record', *robot_args,
               '--teleop.type=enpei_leader', f"--teleop.port={robot['leader_port']}",
               '--teleop.id=enpei_leader', '--display_data=true',
               '--dataset.repo_id=enpeicv/demo_move_block',
               f"--dataset.root={root_path(cfg['source_dataset'])}",
               '--dataset.push_to_hub=false', f"--dataset.num_episodes={cfg['episodes']}",
               '--dataset.episode_time_s=20', '--dataset.reset_time_s=8',
               f'--dataset.single_task={task}']
        return LEROBOT, cmd, env
    if stage == 'infer':
        cmd = [python, '-m', 'lerobot.test_openpi', *robot_args,
               f"--host={cfg['policy']['host']}", f"--port={cfg['policy']['port']}",
               f'--instruction={task}', '--fps=30',
               f"--action-start-index={cfg['action_start_index']}", '--display-data=true']
        return LEROBOT, cmd, env
    if stage == 'convert':
        cmd = [uv, 'run', 'examples/libero/lerobot2oppi.py',
               '--source-repo-id=enpeicv/demo_move_block',
               '--target-repo-id=enpeicv/demo_move_block_openpi',
               f"--source-dataset-root={root_path(cfg['source_dataset'])}",
               f'--output-path={CONVERTED}', f"--max-episodes={cfg['episodes']}"]
    elif stage == 'norm':
        cmd = [uv, 'run', 'scripts/compute_norm_stats.py', '--config-name', TRAIN_CONFIG]
    elif stage == 'train':
        cmd = [uv, 'run', 'scripts/train.py', TRAIN_CONFIG, f"--exp-name={cfg['experiment']}"]
        if resume:
            cmd.append('--resume')
    elif stage == 'serve':
        checkpoint = OPENPI / 'checkpoints' / TRAIN_CONFIG / cfg['experiment'] / str(cfg['checkpoint'])
        cmd = [uv, 'run', 'scripts/serve_policy.py', 'policy:checkpoint',
               f'--policy.config={TRAIN_CONFIG}', f'--policy.dir={checkpoint}',
               f"--port={cfg['policy']['port']}"]
    else:
        raise ValueError(f'Unknown stage: {stage}')
    return OPENPI, cmd, env


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=['record', 'convert', 'norm', 'train', 'serve', 'infer'])
    parser.add_argument('--config', type=Path, default=ROOT / 'configs/robot.json')
    parser.add_argument('--resume', action='store_true', help='resume the existing training experiment')
    parser.add_argument('--dry-run', action='store_true', help='print command without starting hardware or training')
    args = parser.parse_args()
    if not args.config.is_file():
        parser.error(f'{args.config} not found; copy configs/robot.example.json and configure your devices')
    cfg = json.loads(args.config.read_text())
    cwd, cmd, env = build_command(args.stage, cfg, args.resume)
    print(f'cd {shlex.quote(str(cwd))}', flush=True)
    print(f'PI05_BASE_PARAMS={shlex.quote(env["PI05_BASE_PARAMS"])} XLA_PYTHON_CLIENT_PREALLOCATE=false {shlex.join(cmd)}', flush=True)
    if args.dry_run:
        return
    if not (cwd / 'pyproject.toml').is_file():
        parser.error('Initialize submodules first: git submodule update --init')
    subprocess.run(cmd, cwd=cwd, env=env, check=True)


if __name__ == '__main__':
    main()
