#!/usr/bin/env python3
"""Reproducible audit of military-exposure findability in public NCI metadata.
1) NCI Genomic Data Commons (GDC) public API: counts of cases with exposure fields populated.
2) Index of NCI Studies (INS) public data files (CBIIT/INS-Data release 2.4.1): keyword search.
Uses only open-access, public metadata (no controlled-access data)."""
import json, urllib.request, urllib.parse, datetime, csv, re, glob, os, sys
API = "https://api.gdc.cancer.gov/"
def get(path, params=None):
    url = API + path + ("?" + urllib.parse.urlencode(params) if params else "")
    return json.load(urllib.request.urlopen(url, timeout=60))
def count(filt=None):
    p = {"size": 0}
    if filt: p["filters"] = json.dumps(filt)
    return get("cases", p)["data"]["pagination"]["total"]
def notmissing(field): return {"op": "not", "content": {"field": field, "value": ["MISSING"]}}
def isin(field, vals): return {"op": "in", "content": {"field": field, "value": vals}}
out = {"run_at_local": datetime.datetime.now().isoformat(timespec="seconds")}
out["gdc_status"] = get("status")["data_release"]
out["gdc_projects"] = get("projects", {"size": 0})["data"]["pagination"]["total"]
out["gdc_cases_total"] = count()
out["cases_any_occupation_type"] = count(notmissing("exposures.occupation_type"))
out["cases_armed_forces_occupation"] = count(isin("exposures.occupation_type", ["Armed Forces Occupations, Other Ranks", "Commissioned Armed Forces Officers", "Non-commissioned Armed Forces Officers"]))
out["cases_any_chemical_exposure_type"] = count(notmissing("exposures.chemical_exposure_type"))
out["cases_agent_orange"] = count(isin("exposures.chemical_exposure_type", ["Agent Orange"]))
d = get("v0/submission/_dictionary/exposure", {"format": "json"})
out["exposure_type_enum"] = d["properties"]["exposure_type"]["enum"]
p = d["properties"]["chemical_exposure_type"]; out["chemical_exposure_type_enum"] = p.get("enum") or p.get("items", {}).get("enum")
out["exposure_entity_fields"] = sorted(k for k in d["properties"] if k not in ("cases","batch_id","created_datetime","updated_datetime","id","project_id","state","submitter_id","type"))
ap = {}
for pid in ["APOLLO-LUAD", "APOLLO-OV", "APOLLO-BRCA-1", "VAREPOP-APOLLO"]:
    f = isin("project.project_id", [pid])
    ap[pid] = {"cases": count(f),
               "with_occupation_type": count({"op": "and", "content": [f, notmissing("exposures.occupation_type")]}),
               "with_chemical_exposure_type": count({"op": "and", "content": [f, notmissing("exposures.chemical_exposure_type")]}),
               "with_exposure_type": count({"op": "and", "content": [f, notmissing("exposures.exposure_type")]})}
out["apollo_projects"] = ap
# INS keyword audit (download https://github.com/CBIIT/INS-Data/releases/download/2.4.1/ins_data_files_2.4.1.0.zip and unzip to ./ins)
insdir = sys.argv[1] if len(sys.argv) > 1 else None
if insdir and os.path.isdir(insdir):
    csv.field_size_limit(10**9)
    terms = {"agent orange": r"agent orange", "burn pit": r"burn[- ]?pit", "camp lejeune": r"lejeune",
             "airborne hazard": r"airborne hazard", "military": r"\bmilitary\b", "veteran": r"\bveteran"}
    res = {}; total = 0
    for f in sorted(glob.glob(os.path.join(insdir, "*datasets*.tsv"))):
        if "subset_clones" in f: continue
        rows = list(csv.DictReader(open(f, encoding="utf-8", errors="ignore"), delimiter="\t"))
        total += len(rows)
        for t, p in terms.items():
            hits = [r.get("dataset_title", "") for r in rows if re.search(p, " ".join(map(str, r.values())), re.I)]
            res.setdefault(t, []).extend(hits)
    out["ins_dataset_records_searched"] = total
    out["ins_hits"] = {t: {"n": len(h), "titles": sorted(set(h))} for t, h in res.items()}
print(json.dumps(out, indent=1))
