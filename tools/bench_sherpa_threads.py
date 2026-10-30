import sys, json, time, glob, os, numpy as np, soundfile as sf, sherpa_onnx as so
eng, th, hp = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
d="/models/sherpa-onnx-zipformer-ja-reazonspeech-2024-08-01/"
sfx=".int8.onnx" if eng=="int8" else ".onnx"
t0=time.time()
rec=so.OfflineRecognizer.from_transducer(d+"encoder-epoch-99-avg-1"+sfx,d+"decoder-epoch-99-avg-1"+sfx,d+"joiner-epoch-99-avg-1"+sfx,d+"tokens.txt",num_threads=th)
load=time.time()-t0
def highpass(x,sr,fc=80.0):
    X=np.fft.rfft(x); f=np.fft.rfftfreq(len(x),1/sr)
    g=np.clip((f-fc*0.5)/(fc*0.5),0,1); return np.fft.irfft(X*g,len(x)).astype("float32")
out={"load":load}
for cond in os.environ.get("COND","clean,e_clean_g,noise5").split(","):
    h={}; dur=0; t=0
    for p in sorted(glob.glob(f"/data/{cond}/*.wav")):
        x,sr=sf.read(p,dtype="float32")
        if hp: x=highpass(x,sr)
        dur+=len(x)/sr; t1=time.time()
        s=rec.create_stream(); s.accept_waveform(sr,x); rec.decode_stream(s); t+=time.time()-t1
        h[os.path.basename(p)[:-4]]=s.result.text
    out[cond]={"hyp":h,"rtf":t/dur}
json.dump(out,open(f"/data/thr_{eng}_t{th}_hp{hp}.json","w"),ensure_ascii=False)
print(eng,th,hp,"load",round(load,2),{c:round(v["rtf"],3) for c,v in out.items() if c!="load"},flush=True)
