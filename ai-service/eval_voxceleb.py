import os
import requests
import numpy as np
import json

API = "http://localhost:8000/ai"
VOX_PATH = "data/eval_dataset/voxceleb"

ENROLLED_SPEAKER = "speaker_61"
N_ENROLL = 3
Z_THRESHOLD = 0.70

def enroll_single(wav):
    with open(wav, "rb") as f:
        r = requests.post(f"{API}/enroll", files={"file": f})
    r.raise_for_status()
    return np.array(r.json()["embedding"], dtype=np.float32)

def verify_single(wav, centroid, z):
    payload = {
        "stored_embedding": json.dumps(centroid.tolist()),
        "z_score": str(z)
    }
    with open(wav, "rb") as f:
        r = requests.post(f"{API}/verify", files={"file": f}, data=payload)
    r.raise_for_status()
    return r.json()

def l2(v):
    return v / (np.linalg.norm(v) + 1e-6)

# ============ ENROLL ============
print(f"\n[ENROLL] {ENROLLED_SPEAKER}")
ref_path = os.path.join(VOX_PATH, ENROLLED_SPEAKER)
files = sorted(f for f in os.listdir(ref_path) if f.endswith(".wav"))

embs = [enroll_single(os.path.join(ref_path, f)) for f in files[:N_ENROLL]]
centroid = l2(np.mean(embs, axis=0))
genuine_test = os.path.join(ref_path, files[N_ENROLL])

# ============ IMPOSTOR COHORT ============
print("\n[BUILD IMPOSTOR COHORT]")
scores = []

for spk in os.listdir(VOX_PATH):
    if spk == ENROLLED_SPEAKER:
        continue
    spk_path = os.path.join(VOX_PATH, spk)
    wavs = [f for f in os.listdir(spk_path) if f.endswith(".wav")]
    if not wavs:
        continue
    try:
        res = verify_single(os.path.join(spk_path, wavs[0]), centroid, 0.0)
        scores.append(res["similarity"])
    except Exception as e:
        print(f"[WARN] {spk}: {e}")

scores = np.array(scores)
mu, sigma = scores.mean(), scores.std() + 1e-6
print(f"Impostor mean: {mu:.4f}")
print(f"Impostor std : {sigma:.4f}")

# ============ VERIFY ============
print("\n[VERIFY - GENUINE]")
g_res = verify_single(
    genuine_test,
    centroid,
    (verify_single(genuine_test, centroid, 0)["similarity"] - mu) / sigma
)
print(g_res)

imp_spk = [s for s in os.listdir(VOX_PATH) if s != ENROLLED_SPEAKER][0]
imp_path = os.path.join(VOX_PATH, imp_spk)
imp_wav = os.path.join(imp_path, os.listdir(imp_path)[0])

print("\n[VERIFY - IMPOSTOR]")
i_res = verify_single(
    imp_wav,
    centroid,
    (verify_single(imp_wav, centroid, 0)["similarity"] - mu) / sigma
)
print(i_res)
