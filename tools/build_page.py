"""Builds docs/index.html (single file, data embedded) from results/*.csv.  python tools/build_page.py"""
import csv, json, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
def rd(n): return list(csv.DictReader(open(root/"results"/n, encoding="utf-8")))
acc_cv = [(r["model"], r["condition"], float(r["cer_percent"])) for r in rd("accuracy_common_voice.csv")]
acc_own = [(r["model"], r["condition"], float(r["cer_percent"])) for r in rd("accuracy_own_recordings.csv")]
speed = [dict(m=r["model"], t=r["threads"], p=r["preprocessing"], cap=r["container_cpu_cap"], c=r["condition"], cer=float(r["cer_percent"]), rtf=float(r["rtf"])) for r in rd("speed_controlled.csv")]
pre = [dict(e=r["engine"], c=r["condition"], p=r["preprocessing"], cer=float(r["cer_percent"])) for r in rd("preprocessing_gtcrn.csv")]
data = json.dumps(dict(cv=acc_cv, own=acc_own, speed=speed, pre=pre), ensure_ascii=False)
html = (root/"tools"/"page_template.html").read_text(encoding="utf-8").replace("/*DATA*/null", data)
(root/"docs").mkdir(exist_ok=True)
(root/"docs"/"index.html").write_text(html, encoding="utf-8")
print("wrote docs/index.html", len(html), "bytes")
