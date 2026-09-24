from fastapi import FastAPI, Form, HTTPException, Request
import numpy as np
import librosa
import joblib
import os
import json
import io
import soundfile as sf

app = FastAPI()

# ================= PATHS =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SPOOF_MODEL_PATH = os.path.join(BASE_DIR, "models", "spoof_model.joblib")
SPOOF_SCALER_PATH = os.path.join(BASE_DIR, "models", "spoof_scaler.joblib")

spoof_model = joblib.load(SPOOF_MODEL_PATH)
spoof_scaler = joblib.load(SPOOF_SCALER_PATH)

Z_THRESHOLD = 1.20
SPOOF_THRESHOLD = 0.30

def load_audio(file_bytes, target_sr=16000):
    audio, sr = sf.read(io.BytesIO(file_bytes), dtype="float32")
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)
    if sr != target_sr:
        audio = librosa.resample(audio, orig_sr=sr, target_sr=target_sr)
    return audio

def extract_embedding(audio):
    mfcc = librosa.feature.mfcc(y=audio, sr=16000, n_mfcc=40)
    emb = np.mean(mfcc, axis=1)
    emb /= (np.linalg.norm(emb) + 1e-6)
    return emb

def compute_spoof_score(audio):
    mfcc = librosa.feature.mfcc(y=audio, sr=16000, n_mfcc=40)
    feat = np.mean(mfcc, axis=1)
    feat = spoof_scaler.transform([feat])
    return float(spoof_model.predict_proba(feat)[0][1])

# ================= ENROLL =================
@app.post("/ai/enroll")
async def enroll(request: Request):
    try:
        # Accept raw audio/wav bytes from Node
        audio_bytes = await request.body()
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="No audio received")
        
        audio = load_audio(audio_bytes)
        emb = extract_embedding(audio)
        spoof_score = compute_spoof_score(audio)
        
        return {
            "embedding": emb.tolist(),
            "spoofScore": float(spoof_score)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================= VERIFY =================
@app.post("/ai/verify")
async def verify(request: Request):
    try:
        # Parse JSON body from Node
        body = await request.json()
        audio_base64 = body.get("audio")
        stored_embedding = body.get("storedEmbedding")
        
        if not audio_base64 or not stored_embedding:
            raise HTTPException(status_code=400, detail="Missing audio or embedding")
        
        # Decode base64 audio
        import base64
        audio_bytes = base64.b64decode(audio_base64)
        
        centroid = np.array(stored_embedding, dtype=np.float32)
        audio = load_audio(audio_bytes)
        emb = extract_embedding(audio)
        
        similarity = float(np.dot(emb, centroid))
        spoof_score = compute_spoof_score(audio)
        
        # Compute z-score (distance from centroid)
        z_score = similarity
        
        if spoof_score >= SPOOF_THRESHOLD:
            decision = "REJECT"
            reason = "Spoof detected"
        elif z_score < Z_THRESHOLD:
            decision = "REJECT"
            reason = "Low similarity"
        else:
            decision = "ACCEPT"
            reason = "Voice matched"
        
        return {
            "similarity": round(similarity, 6),
            "spoofScore": round(spoof_score, 6),
            "decision": decision,
            "reason": reason
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/health")
@app.head("/health")
async def health():
    return {"status": "ok"}