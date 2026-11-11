import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import score  # noqa: E402

D = "2026-11-11"

def mkroot():
    r = Path(tempfile.mkdtemp())
    (r / "docs/evidence/ci/junit").mkdir(parents=True); (r / "docs/evidence/metrics").mkdir(parents=True)
    (r / "docs/evidence/distance").mkdir(parents=True); (r / "ml/runs").mkdir(parents=True)
    return r

def put(r, rel, obj):
    p = r / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(obj))

def junit(r, n=93, fail=0):
    cases = "".join(f'<testcase classname="com.kaleem.blindassist.AlertEngineTest" name="t{i}"/>' for i in range(n - 1))
    cases += '<testcase classname="com.kaleem.blindassist.AlertEngineTest" name="noSpokenStringClaimsClearOrSafe"/>'
    cases += "".join(f'<testcase classname="X" name="f{i}"><failure/></testcase>' for i in range(fail))
    (r / "docs/evidence/ci/junit/a.xml").write_text(f"<testsuite>{cases}</testsuite>")

def metrics(r, secs=7200, fps=20, lat=100, temp=40):
    with open(r / "docs/evidence/metrics/walk.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["t_s", "fps", "latency_ms", "temp_c", "battery_pct", "limited"])
        for t in range(0, secs + 1, 5): w.writerow([t, fps, lat, temp, 90, "false"])

def get(out, name):
    return next(s for n, s, _ in out if n == name)

def full(r):
    junit(r); metrics(r)
    put(r, "docs/evidence/ci/build.json", {"assembleDebug": True, "lint": True, "emulator_smoke": True, "internet_permission_in_merged_manifest": False})
    put(r, "docs/evidence/code_review.json", {"reviewer": "x", "approved": True, "date": D})
    put(r, "ml/runs/eval.json", {"per_class": {c: {"recall": 0.95} for c in score.SAFETY}})
    with open(r / "docs/evidence/distance/d.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["true_distance_m", "estimated_distance_m"])
        for i in range(40): w.writerow([3.0, 3.1])
    put(r, "docs/evidence/field_hazard_eval.json", {"recall": {c: 0.93 for c in score.SAFETY}, "false_alarms_per_5min": 0.5, "minutes": 120, "n_sites": 6, "date": D})
    put(r, "docs/evidence/latency_endtoend.json", {"p95_ms": 120, "date": D})
    put(r, "docs/evidence/user_study.json", {"participants": 12, "om_instructor_review": True, "sus_mean": 82, "languages_tested": ["en", "hi", "te"], "date": D})
    put(r, "docs/evidence/native_review.json", {"hi": {"approved": True, "date": D}, "te": {"approved": True, "date": D}})
    put(r, "docs/evidence/oem_tests.json", {b: {"minutes": 30, "pass": True} for b in ("samsung", "xiaomi", "oppo", "vivo")})
    put(r, "docs/evidence/field_hours.json", {"hours": 25, "crashes": 0, "date": D})

class Score(unittest.TestCase):
    def test_no_evidence_is_low(self):
        out, overall = score.score_all(score.gather(mkroot()))
        self.assertLess(overall, 3.5); self.assertIsNone(get(out, "Innovation"))
        self.assertTrue(all(s <= 4.0 for n, s, _ in out if s is not None))

    def test_ci_evidence_only_lifts_engineering(self):
        r = mkroot(); junit(r)
        put(r, "docs/evidence/ci/build.json", {"assembleDebug": True, "lint": True, "emulator_smoke": True, "internet_permission_in_merged_manifest": False})
        put(r, "docs/evidence/code_review.json", {"approved": True, "date": D})
        out, _ = score.score_all(score.gather(r))
        self.assertEqual(get(out, "Engineering"), 9.0); self.assertEqual(get(out, "Accuracy"), 2.0); self.assertEqual(get(out, "Safety"), 4.0)

    def test_failing_tests_block_points(self):
        r = mkroot(); junit(r, fail=2)
        out, _ = score.score_all(score.gather(r))
        self.assertLessEqual(get(out, "Engineering"), 3.0)

    def test_full_evidence_reaches_nine_not_ten(self):
        r = mkroot(); full(r)
        out, overall = score.score_all(score.gather(r))
        for name in ("Engineering", "Accuracy", "Speed", "Safety", "Reliability", "Languages (hi/te)"):
            self.assertEqual(get(out, name), 9.0, name)
        self.assertGreaterEqual(get(out, "User experience"), 9.0)
        self.assertLessEqual(max(s for _, s, _ in out if s is not None), 9.0)

    def test_bad_distance_and_low_recall_do_not_score(self):
        r = mkroot()
        with open(r / "docs/evidence/distance/d.csv", "w", newline="") as f:
            w = csv.writer(f); w.writerow(["true_distance_m", "estimated_distance_m"])
            for i in range(40): w.writerow([3.0, 3.6])                     # 20 % error
        put(r, "ml/runs/eval.json", {"per_class": {c: {"recall": 0.5} for c in score.SAFETY}})
        out, _ = score.score_all(score.gather(r))
        self.assertEqual(get(out, "Accuracy"), 4.0)

    def test_undated_or_incomplete_evidence_ignored(self):
        r = mkroot()
        put(r, "docs/evidence/user_study.json", {"participants": 20, "om_instructor_review": True, "sus_mean": 90})   # no date
        put(r, "docs/evidence/native_review.json", {"hi": {"approved": True}, "te": {"approved": True}})             # no dates
        out, _ = score.score_all(score.gather(r))
        self.assertEqual(get(out, "User experience"), 3.0); self.assertEqual(get(out, "Languages (hi/te)"), 2.0)

    def test_short_metrics_log_not_credited(self):
        r = mkroot(); metrics(r, secs=120)
        self.assertEqual(get(*[score.score_all(score.gather(r))[0]], "Speed") if False else get(score.score_all(score.gather(r))[0], "Speed"), 3.0)

    def test_ten_requires_independent_replication(self):
        r = mkroot(); put(r, "docs/evidence/expert_review.json", {"reviewers": 3, "scores": {"innovation": 10}, "date": D})
        self.assertEqual(get(score.score_all(score.gather(r))[0], "Innovation"), 9.0)
        put(r, "docs/evidence/independent_replication.json", {"replicated_by": "lab", "date": D})
        self.assertEqual(get(score.score_all(score.gather(r))[0], "Innovation"), 10.0)

    def test_verified_feature_needs_evidence_file(self):
        r = mkroot(); ev = r / "proof.txt"; ev.write_text("x")
        put(r, "docs/evidence/features.json", {"a": {"status": "verified", "evidence": str(ev)}, "b": {"status": "verified"}, "c": {"status": "none"}})
        s, _ = score.assistant(score.gather(r))
        self.assertAlmostEqual(s, round(1 + 8 * 1.4 / 3, 1), places=1)

    def test_internet_permission_lowers_privacy(self):
        r = mkroot(); put(r, "docs/evidence/ci/build.json", {"internet_permission_in_merged_manifest": True})
        self.assertEqual(get(score.score_all(score.gather(r))[0], "Privacy"), 4.0)

    def test_unknown_manifest_check_is_not_credited(self):
        r = mkroot(); put(r, "docs/evidence/ci/build.json", {"internet_permission_in_merged_manifest": None})
        self.assertEqual(get(score.score_all(score.gather(r))[0], "Privacy"), 4.0)

    def test_render_mentions_weakest(self):
        out, overall = score.score_all(score.gather(mkroot()))
        t = score.render(out, overall)
        self.assertIn("Weakest", t); self.assertIn("UNSCORED", t)

if __name__ == "__main__":
    unittest.main()
