"""Integration wiring tests: no ML dependencies and no hardware required."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('pipeline', ROOT / 'scripts/pipeline.py')
pipeline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pipeline)


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.cfg = json.loads((ROOT / 'configs/robot.example.json').read_text())

    def test_camera_roles_and_units_survive_local_commands(self):
        for stage in ('record', 'infer'):
            cwd, cmd, _ = pipeline.build_command(stage, self.cfg)
            self.assertEqual(cwd, ROOT / 'modules/lerobot')
            self.assertIn('--enpei_use_radian=true', cmd)
            cameras = json.loads(next(x.split('=', 1)[1] for x in cmd if x.startswith('--robot.cameras=')))
            self.assertEqual(cameras['fixed']['index_or_path'], 2)
            self.assertEqual(cameras['handeye']['index_or_path'], 4)
        self.assertIn('--action-start-index=2', cmd)

    def test_converter_matches_training_root_and_preserves_source(self):
        self.cfg['source_dataset'] = '/tmp/raw data'
        cwd, cmd, _ = pipeline.build_command('convert', self.cfg)
        self.assertEqual(cwd, ROOT / 'modules/openpi')
        self.assertIn('--source-dataset-root=/tmp/raw data', cmd)
        self.assertIn(f'--output-path={cwd}/enpei_dataset/demo_move_block', cmd)
        self.assertFalse(any('overwrite' in x for x in cmd))

    def test_full_finetune_checkpoint_and_resume(self):
        cwd, train, _ = pipeline.build_command('train', self.cfg, resume=True)
        _, serve, _ = pipeline.build_command('serve', self.cfg)
        self.assertIn(pipeline.TRAIN_CONFIG, train)
        self.assertIn('--resume', train)
        self.assertIn('policy:checkpoint', serve)
        self.assertIn(f'--policy.dir={cwd}/checkpoints/{pipeline.TRAIN_CONFIG}/demo_move_block_full_v1/20000', serve)
        self.assertIn('--port=6006', serve)
        self.assertFalse(any('low_mem' in x for x in train + serve))

    def test_base_params_resolved_from_workspace(self):
        _, _, env = pipeline.build_command('norm', self.cfg)
        self.assertEqual(env['PI05_BASE_PARAMS'], str(ROOT / 'weights/pi05_base/params'))

    def test_rejects_invalid_hardware_contract(self):
        for key, value in [('action_start_index', 50), ('action_start_index', -1), ('episodes', 0)]:
            cfg = {**self.cfg, key: value}
            with self.assertRaises(ValueError):
                pipeline.build_command('infer', cfg)
        self.cfg['cameras']['fixed'] = self.cfg['cameras']['handeye']
        with self.assertRaises(ValueError):
            pipeline.build_command('record', self.cfg)

    def test_dispatch_uses_selected_environment_and_cwd(self):
        with tempfile.TemporaryDirectory(prefix='pi05 config ') as tmp:
            config = Path(tmp) / 'robot.json'
            config.write_text(json.dumps(self.cfg))
            for stage in ('record', 'convert', 'norm', 'train', 'serve', 'infer'):
                with self.subTest(stage=stage), patch.object(sys, 'argv', ['pipeline.py', stage, '--config', str(config)]), patch.object(pipeline.subprocess, 'run') as run:
                    pipeline.main()
                    args, kwargs = run.call_args
                    expected = pipeline.build_command(stage, self.cfg)
                    self.assertEqual(args[0], expected[1])
                    self.assertEqual(kwargs['cwd'], expected[0])
                    self.assertTrue(kwargs['check'])
                    self.assertNotIn('shell', kwargs)

    def test_cli_dry_run_is_dependency_free(self):
        for stage in ('record', 'convert', 'norm', 'train', 'serve', 'infer'):
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/pipeline.py'), stage,
                                     '--config', str(ROOT / 'configs/robot.example.json'), '--dry-run'],
                                    cwd='/tmp', capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('cd ', result.stdout)

    def test_missing_config_fails_without_execution(self):
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/pipeline.py'), 'record',
                                 '--config', '/nonexistent/pi05.json'], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('copy configs/robot.example.json', result.stderr)


if __name__ == '__main__':
    unittest.main()
