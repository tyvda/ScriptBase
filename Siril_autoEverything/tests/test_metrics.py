import tempfile
from types import SimpleNamespace
from pathlib import Path
import unittest

from Siril_autoEverything import siril_auto_everything as sae


class MetricsParsingTests(unittest.TestCase):
    def test_parse_value_extracts_first_float(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "stat.log"
            log_path.write_text("Mean=0.123 Median: 0.456", encoding="utf-8")
            value = sae.parse_value(log_path, "Median")
            self.assertEqual(value, 0.456)

    def test_derive_blackpoint_uses_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            metrics_dir = Path(tmpdir)
            sae.write_json(metrics_dir / "stat_denoised.json", {"median": 0.1, "stddev": 0.02})
            blackpoint = sae.derive_blackpoint(metrics_dir)
            self.assertLessEqual(blackpoint, 0.1)
            self.assertGreaterEqual(blackpoint, 0.0)

    def test_assess_clip_fraction_handles_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fraction = sae.assess_clip_fraction(Path(tmpdir))
            self.assertEqual(fraction, 0.0)


class ExportNameTests(unittest.TestCase):
    def test_render_export_name_with_tokens(self) -> None:
        header = {"object": "M42", "exptime": "120", "filter": "Ha"}
        name = sae.render_export_name("{object}_{filter}_{session}", "night1", header)
        self.assertTrue(name.startswith("M42_Ha_night1"))

    def test_slugify_protects_empty(self) -> None:
        self.assertEqual(sae.slugify(""), "export")


class PresetBlueprintTests(unittest.TestCase):
    def test_load_effective_preset_uses_blueprint_defaults(self) -> None:
        args = SimpleNamespace(preset=None)
        preset = sae.load_effective_preset(args)
        self.assertGreater(len(preset), 0)
        self.assertAlmostEqual(preset.get("asinh_strength"), 0.22)
        self.assertEqual(preset.get("export_name_template"), "{object}_{session}_{date}")


if __name__ == "__main__":
    unittest.main()
