"""Smoke tests for OPTOUT. No network. Run with: python -m pytest or unittest."""
import io
import json
import os
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from optout import TOOL_NAME, TOOL_VERSION, BROKERS, OptOutEngine, render_letter
from optout.core import get_broker, load_profile
from optout.cli import main

DEMO = Path(__file__).resolve().parents[1] / "demos" / "01-basic" / "profile.json"


class TestCore(unittest.TestCase):
    def setUp(self):
        self.profile = load_profile(DEMO)

    def test_registry_nonempty_and_unique(self):
        self.assertTrue(len(BROKERS) >= 15)
        slugs = [b.slug for b in BROKERS]
        self.assertEqual(len(slugs), len(set(slugs)))

    def test_load_profile_validates_missing_name(self):
        import tempfile
        fd, p = tempfile.mkstemp(suffix=".json")
        os.write(fd, b'{"email": "x@y.com"}')
        os.close(fd)
        try:
            with self.assertRaises(ValueError):
                load_profile(p)
        finally:
            os.unlink(p)

    def test_build_requests_deterministic_ids(self):
        eng = OptOutEngine()
        r1 = eng.build_requests(self.profile, "CCPA")
        r2 = eng.build_requests(self.profile, "CCPA")
        self.assertEqual([r.request_id for r in r1], [r.request_id for r in r2])
        self.assertTrue(all(r.request_id.startswith("OPT-") for r in r1))
        self.assertTrue(all(r.status == "pending" for r in r1))

    def test_build_requests_only_unknown_raises(self):
        eng = OptOutEngine()
        with self.assertRaises(ValueError):
            eng.build_requests(self.profile, "CCPA", only=["nope-broker"])

    def test_build_requests_only_subset(self):
        eng = OptOutEngine()
        reqs = eng.build_requests(self.profile, "CCPA", only=["spokeo", "radaris"])
        self.assertEqual({r.broker_slug for r in reqs}, {"spokeo", "radaris"})

    def test_render_letter_contains_identity_and_law(self):
        broker = get_broker("spokeo")
        ccpa = render_letter(self.profile, broker, "CCPA")
        self.assertIn("CCPA", ccpa)
        self.assertIn(self.profile["full_name"], ccpa)
        self.assertIn(broker.privacy_email, ccpa)
        gdpr = render_letter(self.profile, broker, "GDPR")
        self.assertIn("Article 17", gdpr)

    def test_render_bad_regime_raises(self):
        broker = get_broker("spokeo")
        with self.assertRaises(ValueError):
            render_letter(self.profile, broker, "PIPEDA")

    def test_summary(self):
        eng = OptOutEngine()
        reqs = eng.build_requests(self.profile, "CCPA")
        summ = eng.summarize(reqs)
        self.assertEqual(summ["total"], len(reqs))
        self.assertEqual(summ["by_status"]["pending"], len(reqs))


class TestCLI(unittest.TestCase):
    def _run(self, argv):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(argv)
        return rc, buf.getvalue()

    def test_brokers_json(self):
        rc, out = self._run(["--format", "json", "brokers"])
        self.assertEqual(rc, 0)
        data = json.loads(out)
        self.assertTrue(any(b["slug"] == "spokeo" for b in data))

    def test_plan_json(self):
        rc, out = self._run(["--format", "json", "plan", str(DEMO), "--regime", "CCPA"])
        self.assertEqual(rc, 0)
        data = json.loads(out)
        self.assertEqual(data["regime"], "CCPA")
        self.assertEqual(data["summary"]["total"], len(data["requests"]))

    def test_letter_table(self):
        rc, out = self._run(["letter", "spokeo", str(DEMO)])
        self.assertEqual(rc, 0)
        self.assertIn("Data Deletion", out)

    def test_unknown_broker_letter_exit_code(self):
        rc, _ = self._run(["letter", "does-not-exist", str(DEMO)])
        self.assertEqual(rc, 2)

    def test_missing_profile_nonzero(self):
        rc, _ = self._run(["plan", "no-such-file.json"])
        self.assertEqual(rc, 1)

    def test_version_string(self):
        self.assertEqual(TOOL_NAME, "optout")
        self.assertTrue(TOOL_VERSION)


if __name__ == "__main__":
    unittest.main()
