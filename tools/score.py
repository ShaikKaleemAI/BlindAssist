"""Evidence-driven rating. Scores come ONLY from evidence files (see docs/evidence/README.md); nothing is self-assigned.
Caps are conservative: no 9 without field evidence, no 10 without independent replication, innovation is never self-scored."""
import csv
import glob
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import analyze_metrics  # noqa: E402

SAFETY = ["stairs", "step", "pothole", "open_drain", "manhole", "curb", "pole", "glass_door", "speed_bump"]
GUARD_TEST = "noSpokenStringClaimsClearOrSafe"

def jload(p):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def dated(d):
    return isinstance(d, dict) and bool(d.get("date"))

def read_junit(root):
    files = glob.glob(f"{root}/app/build/test-results/testDebugUnitTest/*.xml") + glob.glob(f"{root}/docs/evidence/ci/junit/*.xml")
    res = {}
    for f in files:
        try:
            for tc in ET.parse(f).getroot().iter("testcase"):
                key = tc.get("classname", "") + "." + tc.get("name", "")
                bad = tc.find("failure") is not None or tc.find("error") is not None
                res[key] = "fail" if bad else ("skip" if tc.find("skipped") is not None else "pass")
        except ET.ParseError:
            pass
    return res

def read_distance(root):
    errs = []
    for f in glob.glob(f"{root}/docs/evidence/distance/*.csv"):
        with open(f, newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                try:
                    t = float(r["true_distance_m"]); e = float(r["estimated_distance_m"])
                except (KeyError, ValueError):
                    continue
                if 1.0 <= t <= 5.0:
                    errs.append(abs(e - t) / t)
    return errs

def best_metrics(root):
    best = None
    for f in glob.glob(f"{root}/docs/evidence/metrics/*.csv"):
        try:
            s = analyze_metrics.summarize(f)
        except Exception:
            continue
        if s.get("rows") and (best is None or s["duration_s"] > best["duration_s"]):
            best = s
    return best

def gather(root):
    root = str(root)
    ev = {"tests": read_junit(root), "build": jload(f"{root}/docs/evidence/ci/build.json") or {},
          "eval": jload(f"{root}/ml/runs/eval.json"), "dist": read_distance(root), "metrics": best_metrics(root)}
    for n in ("latency_endtoend", "field_hazard_eval", "user_study", "native_review", "oem_tests", "field_hours",
              "expert_review", "independent_replication", "code_review", "features"):
        ev[n] = jload(f"{root}/docs/evidence/{n}.json")
    return ev

def engineering(ev):
    s, why = 1.0, []
    t = ev["tests"]
    if len(t) >= 50: s += 2; why.append(f"{len(t)} tests found")
    else: why.append("fewer than 50 test results found (run evidence workflow)")
    if t and not any(v == "fail" for v in t.values()): s += 2; why.append("no failing tests")
    b = ev["build"]
    for k, label in (("assembleDebug", "debug build ok"), ("lint", "lint ok"), ("emulator_smoke", "emulator smoke test ok")):
        if b.get(k) is True: s += 1; why.append(label)
        else: why.append(f"{label}: no evidence")
    cr = ev["code_review"]
    if dated(cr) and cr.get("approved") is True: s += 1; why.append("independent code review approved")
    else: why.append("no independent code review")
    return s, why

def accuracy(ev):
    why = []
    e, d, f = ev["eval"], ev["dist"], ev["field_hazard_eval"]
    eval_pass = False
    if e and e.get("per_class"):
        rec = [v["recall"] for c, v in e["per_class"].items() if c in SAFETY]
        eval_pass = len(rec) >= 5 and sum(rec) / len(rec) >= 0.90
        why.append(f"open-data eval present, {len(rec)} safety classes, mean recall {sum(rec)/len(rec):.2f}" if rec else "open-data eval has no safety classes")
    dist_pass = len(d) >= 30 and sum(d) / len(d) < 0.10
    if d: why.append(f"distance trials in 1-5 m: n={len(d)}, mean error {100*sum(d)/len(d):.1f}%")
    field_pass = False
    if dated(f):
        rec = [v for c, v in (f.get("recall") or {}).items() if c in SAFETY]
        field_pass = (len(rec) >= 5 and sum(rec) / len(rec) >= 0.90 and f.get("false_alarms_per_5min", 99) <= 1.0
                      and f.get("minutes", 0) >= 60 and f.get("n_sites", 0) >= 5)
        why.append("field hazard evaluation " + ("meets" if field_pass else "does NOT meet") + " recall/false-alarm/size requirements")
    if field_pass and dist_pass: return 9.0, why
    if field_pass: return 8.0, why
    if dist_pass: return 7.0, why
    if eval_pass: return 5.0, why
    if e: return 4.0, why
    return 2.0, why + ["no evaluation evidence"]

def speed(ev):
    m, l = ev["metrics"], ev["latency_endtoend"]
    why = []
    if not m: return 2.0, ["no metrics.csv from a real walk"]
    ok = m["fps_mean"] >= 15 and m["latency_p95_ms"] < 150
    why.append(f"{m['duration_s']:.0f} s log: fps {m['fps_mean']:.1f}, analyzer p95 {m['latency_p95_ms']:.0f} ms (not end-to-end)")
    if m["duration_s"] < 600: return 3.0, why + ["log shorter than 10 minutes"]
    s = 6.0 if ok else 4.0
    if ok and m["duration_s"] >= 7200 and (m.get("temp_max_c") or 99) < 43: s = 7.0; why.append("2 h log, temperature under 43 C")
    if ok and dated(l) and l.get("p95_ms", 999) < 150: s += 2; why.append("external end-to-end latency p95 under 150 ms")
    return min(s, 9.0), why

def safety(ev):
    s, why = 3.0, []
    if ev["tests"].get(f"com.kaleem.blindassist.AlertEngineTest.{GUARD_TEST}") == "pass": s = 4.0; why.append("never-says-clear guard test passes")
    else: why.append("guard test result not found/passing")
    u, f = ev["user_study"], ev["field_hazard_eval"]
    if dated(u) and u.get("om_instructor_review") is True: s = max(s, 7.0); why.append("O&M instructor review recorded")
    if dated(u) and u.get("participants", 0) >= 5 and u.get("om_instructor_review") is True: s = 8.0; why.append(">= 5 participants")
    if s >= 8.0 and dated(f) and f.get("false_alarms_per_5min", 99) <= 1.0: s = 9.0; why.append("field false-alarm rate within target")
    return s, why

def ux(ev):
    u = ev["user_study"]
    if not dated(u) or "sus_mean" not in u: return 3.0, ["no user study (SUS) evidence"]
    n, sus = u.get("participants", 0), u["sus_mean"]
    why = [f"SUS {sus} with n={n}"]
    if n >= 10 and sus >= 80: return 9.0, why
    if n >= 5 and sus >= 68: return 8.0, why
    return 5.0, why + ["below SUS 68 or n < 5"]

def reliability(ev):
    m, o, h = ev["metrics"], ev["oem_tests"], ev["field_hours"]
    why, s = [], 2.0
    if m and m["duration_s"] >= 7200 and (m.get("temp_max_c") or 99) < 43: s = 5.0; why.append("2 h log under 43 C")
    brands = [k for k, v in (o or {}).items() if isinstance(v, dict) and v.get("pass") is True and v.get("minutes", 0) >= 30]
    if len(brands) >= 4: s = max(s, 8.0); why.append("OEM screen-off passes: " + ", ".join(sorted(brands)))
    else: why.append(f"OEM screen-off tests passed on {len(brands)}/4 brands")
    if s >= 8.0 and dated(h) and h.get("hours", 0) >= 20 and h.get("crashes", 1) == 0: s = 9.0; why.append("20+ crash-free hours")
    return s, why

def languages(ev):
    n, u = ev["native_review"], ev["user_study"]
    ok = [k for k in ("hi", "te") if isinstance((n or {}).get(k), dict) and n[k].get("approved") is True and n[k].get("date")]
    why = [f"native review approved: {ok or 'none'}"]
    s = 2.0 + (3.0 if len(ok) >= 1 else 0) + (2.0 if len(ok) == 2 else 0)
    if len(ok) == 2 and dated(u) and {"hi", "te"} <= set(u.get("languages_tested", [])): s = 9.0; why.append("hi/te tested with users")
    return s, why

def assistant(ev):
    f = ev["features"]
    if not f: return 1.0, ["no features.json"]
    items = {k: v for k, v in f.items() if not k.startswith("_")}
    pts = 0.0
    for k, v in items.items():
        st = v.get("status")
        if st == "verified" and v.get("evidence") and Path(v["evidence"]).exists(): pts += 1
        elif st == "verified": pts += 0.4
        elif st == "built": pts += 0.4
    return round(1 + 8 * pts / len(items), 1), [f"{len(items)} features, {pts:.1f} credit (built=0.4, verified+evidence=1)"]

def privacy(ev):
    b = ev["build"]
    if b.get("internet_permission_in_merged_manifest") is None: return 4.0, ["merged-manifest check not run"]
    return (7.0, ["no INTERNET permission in merged manifest (CI)"]) if b["internet_permission_in_merged_manifest"] is False else (4.0, ["merged manifest DECLARES INTERNET"])

def innovation(ev):
    r = ev["expert_review"]
    if dated(r) and r.get("reviewers", 0) >= 2 and "innovation" in (r.get("scores") or {}): return float(r["scores"]["innovation"]), [f"{r['reviewers']} independent reviewers"]
    return None, ["UNSCORED: needs 2+ independent expert reviews (never self-scored)"]

CRITERIA = [("Engineering", engineering), ("Accuracy", accuracy), ("Speed", speed), ("Safety", safety), ("User experience", ux),
            ("Reliability", reliability), ("Languages (hi/te)", languages), ("Assistant features", assistant), ("Privacy", privacy),
            ("Innovation", innovation)]

def score_all(ev):
    rep = ev["independent_replication"]
    can10 = dated(rep) and bool(rep.get("replicated_by"))
    out = []
    for name, fn in CRITERIA:
        s, why = fn(ev)
        if s is not None and s > 9 and not can10: s = 9.0; why.append("capped at 9: no independent replication")
        out.append((name, s, why))
    scored = [s for _, s, _ in out if s is not None]
    overall = round(sum(scored) / len(scored), 1) if scored else None
    return out, overall

def render(out, overall):
    L = ["# Evidence-driven score (generated by tools/score.py — do not hand-edit)", "",
         f"**Overall: {overall}/10** (mean of scored criteria; weakest criterion matters more than the mean)", "",
         "| Criterion | Score | Evidence / why |", "|---|---|---|"]
    for n, s, why in out:
        L.append(f"| {n} | {'-' if s is None else s} | {'; '.join(why)} |")
    low = min((s, n) for n, s, _ in out if s is not None)
    L += ["", f"Weakest: **{low[1]} ({low[0]})**. Add the evidence files listed in docs/evidence/README.md to raise it."]
    return "\n".join(L) + "\n"

def main(root="."):
    out, overall = score_all(gather(root))
    text = render(out, overall)
    p = Path(root) / "docs" / "generated"; p.mkdir(parents=True, exist_ok=True)
    (p / "SCORE.md").write_text(text, encoding="utf-8")
    print(text)

if __name__ == "__main__":
    main(*sys.argv[1:])
