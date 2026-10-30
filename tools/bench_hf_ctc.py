import sys, os, json, time, glob
sys.path.insert(0,"/data/pylib"); sys.path.insert(0,"/data/pylib2")
import torch, soundfile as sf, numpy as np
from transformers import AutoProcessor, AutoModelForCTC, HubertForCTC
torch.set_num_threads(3)
name=sys.argv[1]; repo="reazon-research/"+name
os.environ["HF_HOME"]="/data/hfcache"
if "hubert" in name: model=HubertForCTC.from_pretrained(repo).eval()
else: model=AutoModelForCTC.from_pretrained(repo,trust_remote_code=True).eval()
proc=AutoProcessor.from_pretrained(repo)
print("loaded",name,sum(p.numel() for p in model.parameters())//10**6,"M",flush=True)
out={}
for cond in os.environ.get("COND","enroll").split(","):
    t0=time.time(); dur=0; h={}
    for p in sorted(glob.glob(f"/data/{cond}/*.wav")):
        x,sr=sf.read(p,dtype="float32"); dur+=len(x)/sr
        x=np.pad(x,int(0.5*16000))
        iv=proc(x,return_tensors="pt",sampling_rate=16000).input_values
        with torch.inference_mode(): lg=model(iv).logits
        ids=torch.argmax(lg,dim=-1)[0]
        h[os.path.basename(p)[:-4]]=proc.decode(ids,skip_special_tokens=True).removeprefix("▁").replace("▁","")
    out[cond]={"hyp":h,"rtf":(time.time()-t0)/dur}
    print(cond,round(out[cond]["rtf"],3),flush=True)
json.dump(out,open(f"/data/res_{name}{os.environ.get("SUF","")}.json","w"),ensure_ascii=False)
