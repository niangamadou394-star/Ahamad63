import sherpa_onnx, soundfile as sf, sys
d="sherpa-onnx-whisper-medium/"
rec=sherpa_onnx.OfflineRecognizer.from_whisper(encoder=d+"medium-encoder.int8.onnx",decoder=d+"medium-decoder.int8.onnx",tokens=d+"medium-tokens.txt",language="fr",task="transcribe",num_threads=4)
a,sr=sf.read(sys.argv[1],dtype="float32")
isl=[tuple(map(float,l.split()[:2])) for l in open("rush.txt") if l.strip()]
ch=[list(isl[0])]
for s,e in isl[1:]:
    if s-ch[-1][1]<1.6 and e-ch[-1][0]<22: ch[-1][1]=e
    else: ch.append([s,e])
for s,e in ch:
    st=rec.create_stream(); st.accept_waveform(sr,a[int((s-0.1)*sr):int((e+0.15)*sr)]); rec.decode_stream(st)
    print(f"{s:7.2f} {e:7.2f} {st.result.text.strip()}",flush=True)
