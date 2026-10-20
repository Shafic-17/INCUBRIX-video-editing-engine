"""Run a YAML-like JSON session file against the local API. Input is JSON for zero extra dependencies."""
import argparse, json, urllib.request, urllib.error

def post(url, payload):
    req=urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type":"application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r: return json.loads(r.read())

def main():
    p=argparse.ArgumentParser(); p.add_argument("session_file"); p.add_argument("--base-url",default="http://localhost:8000"); p.add_argument("--output",default="results.json")
    a=p.parse_args(); spec=json.load(open(a.session_file,encoding="utf-8"))
    created=post(a.base_url+"/api/v1/sessions", {"video_id":spec["video_id"],"duration_s":spec["duration_s"]})
    results=[]
    for step in spec["steps"]:
        result=post(a.base_url+f'/api/v1/sessions/{created["session_id"]}/instructions',{"say":step["say"]})
        results.append({"say":step["say"],**result})
    final=urllib.request.urlopen(a.base_url+f'/api/v1/sessions/{created["session_id"]}/timeline').read().decode()
    json.dump({"session_id":created["session_id"],"steps":results,"final_timeline":json.loads(final)},open(a.output,"w",encoding="utf-8"),indent=2)
    print(f"Wrote {a.output}")
if __name__=="__main__": main()
