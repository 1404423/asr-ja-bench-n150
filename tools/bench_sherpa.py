"""k2-v2 (ReazonSpeech zipformer transducer) via sherpa-onnx. usage: COND=clean,pink5 python bench_sherpa.py int8|fp32
Reads /data/<condition>/*.wav, writes /data/res_<engine>.json with hypotheses and RTF per condition."""
import sys, json, time, glob, os, soundfile as sf, sherpa_onnx as so
eng = sys.argv[1]
d = "/models/sherpa-onnx-zipformer-ja-reazonspeech-2024-08-01/"
sfx = ".int8.onnx" if eng == "int8" else ".onnx"
rec = so.OfflineRecognizer.from_transducer(d+"encoder-epoch-99-avg-1"+sfx, d+"decoder-epoch-99-avg-1"+sfx,
                                           d+"joiner-epoch-99-avg-1"+sfx, d+"tokens.txt", num_threads=int(os.environ.get("THREADS", "1")))
out = {}
for cond in os.environ["COND"].split(","):
    t0 = time.time(); dur = 0; h = {}
    for p in sorted(glob.glob(f"/data/{cond}/*.wav")):
        x, sr = sf.read(p, dtype="float32"); dur += len(x)/sr
        s = rec.create_stream(); s.accept_waveform(sr, x); rec.decode_stream(s)
        h[os.path.basename(p)[:-4]] = s.result.text
    out[cond] = {"hyp": h, "rtf": (time.time()-t0)/dur}
json.dump(out, open(f"/data/res_{eng}.json", "w"), ensure_ascii=False)
