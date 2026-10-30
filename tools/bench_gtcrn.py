import sys, json, time, glob, os, numpy as np, soundfile as sf, sherpa_onnx as so
d="/models/sherpa-onnx-zipformer-ja-reazonspeech-2024-08-01/"
rec=so.OfflineRecognizer.from_transducer(d+"encoder-epoch-99-avg-1.onnx",d+"decoder-epoch-99-avg-1.onnx",d+"joiner-epoch-99-avg-1.onnx",d+"tokens.txt",num_threads=1)
cfg=so.OfflineSpeechDenoiserConfig(model=so.OfflineSpeechDenoiserModelConfig(gtcrn=so.OfflineSpeechDenoiserGtcrnModelConfig(model="/data/models2/gtcrn_simple.onnx"),num_threads=1))
dn=so.OfflineSpeechDenoiser(cfg)
def run(x,sr,mode):
    if mode=="raw": return x,0
    t=time.time(); r=dn.run(x,sr); y=np.array(r.samples,dtype="float32"); dt=time.time()-t
    if r.sample_rate!=sr: raise SystemExit("sr")
    n=min(len(x),len(y)); y=y[:n]
    if mode=="dn": return y,dt
    if mode=="mix": return 0.5*x[:n]+0.5*y,dt
out={}
for cond in os.environ.get("COND","e_clean_g,e_pink5,e_pink0,e_babble10,e_babble5,noise5,babble5,clean").split(","):
  for mode in ["raw","dn","mix"]:
    h={}; dur=0; t=0; td=0
    for p in sorted(glob.glob(f"/data/{cond}/*.wav")):
        x,sr=sf.read(p,dtype="float32"); dur+=len(x)/sr
        y,dt=run(x,sr,mode); td+=dt; t1=time.time()
        s=rec.create_stream(); s.accept_waveform(sr,y); rec.decode_stream(s); t+=time.time()-t1
        h[os.path.basename(p)[:-4]]=s.result.text
    out[f"{cond}|{mode}"]={"hyp":h,"rtf":t/dur,"dn_rtf":td/dur}
    print(cond,mode,round(t/dur,3),round(td/dur,3),flush=True)
json.dump(out,open("/data/dn_res.json","w"),ensure_ascii=False)
