import sherpa_onnx, soundfile as sf, sys
d="sherpa-onnx-whisper-medium/"
rec=sherpa_onnx.OfflineRecognizer.from_whisper(encoder=d+"medium-encoder.int8.onnx",decoder=d+"medium-decoder.int8.onnx",tokens=d+"medium-tokens.txt",language="fr",task="transcribe",num_threads=4)
a,sr=sf.read("rush16.wav",dtype="float32")
for w in sys.argv[1:]:
    s,e=map(float,w.split("-"))
    st=rec.create_stream(); st.accept_waveform(sr,a[int(s*sr):int(e*sr)]); rec.decode_stream(st)
    print(w, st.result.text.strip(),flush=True)
