# Japanese ASR on an Intel N150 mini PC: ReazonSpeech family vs. Parakeet-ja, with noise

**日本語要約:** Intel N150(4コア、RAM 7.7 GB、GPUなし)の小型ミニPCで、日本語ASRの精度(CER)と速度(RTF)を、静かな条件・ピンクノイズ・会話ノイズ(他人の話し声)で比べた記録です。
公開サンプル(Common Voice 40件)と、日本語話者2人の読み上げ録音15件(録音自体は非公開)を使いました。
結論: ほとんどの条件で `parakeet-tdt_ctc-0.6b-ja`(speech.cpp、量子化 Q5_K か Q8_0、2スレッド)が最も正確で、2人の録音では全条件で最良(誤りが約1/3〜1/2)でした。速度は RTF 0.2〜0.4 です。F16 は精度が上がらず約3倍遅いので不要です。`reazonspeech-k2-v2`(sherpa-onnx、fp32、**1スレッド**)は最も軽く、公開サンプルの強いノイズ(会話 0 dB)では Parakeet より良い結果でした。
ただし録音は15件と少なく、結果は参考値です。ノイズ抑制(GTCRN)とハイパスは、効果がないか逆効果でした。

Small, honest, reproducible-as-far-as-possible numbers for people who want to run Japanese speech recognition on cheap CPU-only home-server hardware.
Everything here was measured on one machine; treat it as a data point, not a leaderboard.

## Test machine

| | |
|---|---|
| CPU | Intel N150 (4 cores, no hyper-threading), no GPU |
| RAM | 7.7 GB |
| OS | Home Assistant OS (kernel 6.18), tests in throw-away Docker containers |
| CPU limit | set per run with `docker run --cpus N`; **stated in every speed table** |
| Runtimes | sherpa-onnx 2.0.0 (Python 3.12) for k2-v2 · speech.cpp 0.9.2 (`linux-x64-cpu`, SHA-256 verified) for NeMo/Parakeet GGUF · PyTorch CPU + transformers 4.55.4 for the Oct-2025 Zipformer/HuBERT CTC checkpoints |
| Temperature | package temperature reached 86 °C even with a 2-core cap in sustained runs (80+ °C with 4 cores) |

One unexplained reboot of the box happened during a long run without any thermal limit; I cannot say whether heat was the cause.

## Data

* **Common Voice (CV):** 40 clips from [`japanese-asr/ja_asr.common_voice_8_0`](https://huggingface.co/datasets/japanese-asr/ja_asr.common_voice_8_0) (test split), 230 s of audio. Hypotheses are in `raw_cv/`.
* **Own recordings:** 15 scored clips (two adult Japanese speakers, A and B, reading 10 sentences aloud; recorded through the voice assistant's microphone, not a studio setup); audio and per-clip outputs are **not published**, only aggregate CER. The sentences (reconstructed from the recordings):
  1. 今日は朝から忙しくて、まだお昼ご飯を食べていません。 2. 公園まで散歩に行く予定です。 3. 冷蔵庫に牛乳が残っているか、後で確認しておいてください。 4. 新しい本を買ったので、夜にゆっくり読もうと思っています。 5. 駅までは歩いて十分くらいかかります。 6. すみません、もう一度ゆっくり説明してもらえますか。 7. 明日の会議の資料はもう準備できましたか。 8. この前行ったお店はとても美味しかったです。 9. 洗濯物を取り込んでから買い物に行きます。 10. ありがとう、また後でお願いします。
* **Noise:** synthetic, see `tools/make_sets.py`. `pinkN` = pink (1/f) noise at N dB SNR; `babbleN` = three other speech clips summed at N dB SNR. `+gain` means the same per-segment auto-gain that the real-time pipeline applies (target RMS 3000, max 30x) was applied first; the recordings are quiet, and the sherpa-onnx models are sensitive to level (the Hugging Face CTC models appear to normalise input themselves).

**Metric.** CER after converting both sides to hiragana with pykakasi and removing punctuation/whitespace (`tools/score.py`). RTF = processing time / audio length (smaller is faster); for speech.cpp ~6 s process start-up is subtracted.

## Results: accuracy (CER %, lower is better)

### Common Voice (40 clips)

| model | clean | pink10 | pink5 | pink0 | babble10 | babble5 | babble0 |
|---|---|---|---|---|---|---|---|
| reazonspeech-k2-v2 int8 (sherpa-onnx) | 4.9 | 5.3 | 7.1 | 11.9 | 6.0 | 18.4 | 39.0 |
| reazonspeech-k2-v2 fp32 (sherpa-onnx) | 4.8 | 5.3 | 6.6 | 10.5 | 7.2 | 16.7 | 36.5 |
| japanese-zipformer-base-k2-rs35kh | 7.7 | 12.1 | 15.0 | 21.6 | 14.6 | 25.3 | 49.6 |
| japanese-zipformer-base-k2-rs35kh-bpe | 8.3 | 13.2 | 17.0 | 24.5 | 15.2 | 28.5 | 50.0 |
| japanese-hubert-base-k2-rs35kh | 6.8 | 7.9 | 10.8 | 16.0 | 10.9 | 20.4 | 46.1 |
| japanese-hubert-base-k2-rs35kh-bpe | 7.0 | 9.1 | 13.6 | 20.5 | 13.6 | 22.3 | 48.6 |
| reazonspeech-nemo-v2 Q8_0 (speech.cpp) | 3.8 | – | 8.4 | – | – | 25.8 | – |
| parakeet-tdt_ctc-0.6b-ja Q8_0 (speech.cpp) | 3.1 | 3.6 | 6.9 | 8.9 | 7.2 | 17.1 | 40.7 |
| parakeet-tdt_ctc-0.6b-ja F16 (speech.cpp) | – | – | 6.7 | – | – | – | – |
| parakeet-tdt_ctc-0.6b-ja Q5_K (speech.cpp) | – | – | 6.4 | – | – | – | – |

### Own recordings (15 clips, two speakers)

| model | as_recorded | clean+gain | pink10 | pink5 | pink0 | babble10 | babble5 | babble0 |
|---|---|---|---|---|---|---|---|---|
| reazonspeech-k2-v2 int8 (sherpa-onnx) | 6.2 | 5.1 | 8.2 | 10.8 | 19.7 | 20.8 | 43.1 | 91.0 |
| reazonspeech-k2-v2 fp32 (sherpa-onnx) | 3.6 | 5.1 | 6.9 | 9.5 | 19.5 | 15.6 | 37.9 | 89.7 |
| japanese-zipformer-base-k2-rs35kh | 6.7 | 7.2 | 13.3 | 19.2 | 30.8 | 24.6 | 49.7 | 73.3 |
| japanese-zipformer-base-k2-rs35kh-bpe | 4.9 | 4.9 | 11.5 | 17.2 | 38.5 | 23.6 | 50.0 | 75.4 |
| japanese-hubert-base-k2-rs35kh | 6.7 | 6.7 | 10.3 | 14.4 | 22.3 | 15.4 | 37.9 | 70.3 |
| japanese-hubert-base-k2-rs35kh-bpe | 7.9 | 7.9 | 11.5 | 13.3 | 27.2 | 21.3 | 36.9 | 70.8 |
| reazonspeech-nemo-v2 Q8_0 (speech.cpp) | – | 11.3 | – | 16.9 | – | 18.7 | 42.3 | – |
| parakeet-tdt_ctc-0.6b-ja Q8_0 (speech.cpp) | 2.3 | 2.3 | 4.4 | 5.4 | 9.0 | 4.6 | 16.4 | 72.3 |
| parakeet-tdt_ctc-0.6b-ja F16 (speech.cpp) | – | 2.3 | – | 4.4 | – | – | 17.2 | – |
| parakeet-tdt_ctc-0.6b-ja Q5_K (speech.cpp) | – | 2.3 | – | 4.4 | – | – | 15.6 | – |

`as_recorded` is the raw level; the Hugging Face CTC models give identical numbers there and with gain (presumably because their processor normalises the waveform). Dashes were not measured. The Parakeet F16 and Q5_K builds were only run on four conditions (CV pink 5 dB; own clean+gain, pink 5 dB, babble 5 dB).

## Results: speed (RTF, controlled runs only)

`results/speed_controlled.csv` holds every controlled run (incl. the CPU cap of each). RTF in the first big accuracy sweep is **not** published: core limits changed during that sweep (3 cores, later 1 core to limit heat), so those values are not comparable. The runs below used `--cpus 2`.

| model | threads | CER / RTF (CV pink 5 dB) | CER / RTF (own clean+gain) |
|---|---|---|---|
| k2-v2 fp32 (sherpa-onnx) | 1 | 6.6 / 0.27 | 5.1 / 0.28 |
| k2-v2 fp32 (sherpa-onnx) | 2 | 6.6 / 0.47 | 5.1 / 0.49 |
| k2-v2 fp32 (sherpa-onnx) | 3 | 6.6 / 0.96 | 5.1 / 0.97 |
| k2-v2 fp32 (sherpa-onnx) | 4 | 6.6 / 1.34 | 5.1 / 1.64 |
| k2-v2 int8 (sherpa-onnx) | 3 | 7.1 / 0.58 | 5.1 / 0.46 |
| NeMo v2 Q8_0 (speech.cpp) | 1 | 8.4 / 0.82 | 11.3 / 0.76 |
| NeMo v2 Q8_0 (speech.cpp) | 2 | 8.4 / 0.48 | 11.3 / 0.4 |
| Parakeet-ja Q8_0 (speech.cpp) | 1 | 6.9 / 0.71 | 2.3 / 0.67 |
| Parakeet-ja Q8_0 (speech.cpp) | 2 | 6.9 / 0.36 | 2.3 / 0.3 |
| Parakeet-ja Q5_K (speech.cpp) | 2 | 6.4 / 0.26 | 2.3 / 0.21 |
| Parakeet-ja F16 (speech.cpp) | 2 | 6.7 / 1.0 | 2.3 / 0.97 |

Container peak memory (cgroup, includes page cache): Parakeet F16 ≈ 2.5 GB. The model authors report 0.77 GB (Q8_0) / 1.35 GB (F16) peak on Apple silicon; the numbers are not directly comparable.

## Findings

1. **More threads made k2-v2 slower** on this CPU (fp32: RTF 0.27 at 1 thread vs 1.34 at 4; accuracy identical). The speech.cpp GGUF models behave the opposite way (1 → 2 threads ≈ 2× faster).
2. **fp32 vs int8 k2-v2:** same or better CER in nearly every condition, the gap grows with noise; and at 1 thread it is also faster than int8 at 3 threads.
3. **Parakeet-tdt_ctc-0.6b-ja (speech.cpp) was the most accurate model in most conditions.** On the two-speaker recordings it is best in every condition measured (e.g. babble 10 dB: 4.6 % vs 15.6 % for k2-v2 fp32; clean+gain 2.3 % vs 5.1 %). On Common Voice it wins clean (3.1 vs 4.8 %) and pink noise (pink 5 dB 6.9 vs 6.6 is a tie; 10 dB 3.6 vs 5.3; 0 dB 8.9 vs 10.5), ties at babble 10/5 dB, and loses at babble 0 dB (40.7 vs 36.5 %).
4. **Quantisation barely matters for Parakeet, but speed does:** F16 is not more accurate than Q8_0 (differences ±1 point on 15 clips) and ~3× slower (RTF ≈ 1.0 with 2 threads). **Q5_K matched or beat Q8_0 and was the fastest** (RTF 0.21–0.26 with 2 threads).
5. **ReazonSpeech NeMo v2** is good on clean CV (3.8 %) but clearly worse with noise and on the recordings.
6. The Oct-2025 `reazon-research/japanese-{zipformer,hubert}-base-k2-rs35kh*` CTC checkpoints did not beat k2-v2 here, especially with noise.
7. **Preprocessing does not help** (`results/preprocessing_gtcrn.csv`): the GTCRN denoiser made most noisy conditions worse (e.g. own pink 5 dB 9.5 → 17.2 %), mixing 50 % of the original back reduced the damage but did not give a reliable gain; an 80 Hz high-pass gave no gain on CV and a worse number on the recordings (5.1 → 7.2 %).

## Caveats (please read)

* **Small samples.** 15 recordings: one wrong sentence moves CER by several points. The Parakeet advantage is consistent across all conditions on the recordings and on most Common Voice conditions but still needs a larger, independent check.
* The reference sentences of the own recordings were reconstructed, not taken from a saved script.
* Noise is synthetic; real far-field/reverberant speech was not tested.
* Mixed runtimes (sherpa-onnx vs speech.cpp vs PyTorch) and quantisations (int8, fp32, Q8_0) — these are model *and* runtime comparisons.
* Container core limits differ between some runs (listed in the CSV).
* GGUF conversions are community builds: [`sakasegawa/reazonspeech-nemo-v2-GGUF`](https://huggingface.co/sakasegawa/reazonspeech-nemo-v2-GGUF), [`sakasegawa/parakeet-tdt_ctc-0.6b-ja-GGUF`](https://huggingface.co/sakasegawa/parakeet-tdt_ctc-0.6b-ja-GGUF).

## Interactive view

`docs/index.html` is a single static page (Chart.js from a CDN, data embedded): pick models and conditions, compare accuracy vs noise, speed vs accuracy, and preprocessing. Open it locally (`python3 -m http.server -d docs`) or serve `docs/` with GitHub Pages. Rebuild with `python3 tools/build_page.py` after editing the CSVs.

## Layout

* `results/*.csv` – all numbers · `raw_cv/` – CV references and hypotheses · `docs/index.html` – interactive charts · `tools/` – scripts as used (paths are those of the test container).

## License

MIT for code and numbers. Models and datasets keep their own licenses (Common Voice: CC0; check each model card).
