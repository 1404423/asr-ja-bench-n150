"""CER on hiragana-normalised text (pykakasi), punctuation and whitespace removed. RTF = processing time / audio duration."""
import re, unicodedata, pykakasi, editdistance
_kk = pykakasi.kakasi()
def norm(s):
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"[\s、。,.!?！？「」『』〜~・…]+", "", s)
    return "".join(x["hira"] for x in _kk.convert(s))
def cer(hyp: dict, ref: dict) -> float:
    e = sum(editdistance.eval(norm(hyp.get(k, "")), norm(ref[k])) for k in ref)
    n = sum(len(norm(v)) for v in ref.values())
    return 100 * e / n
