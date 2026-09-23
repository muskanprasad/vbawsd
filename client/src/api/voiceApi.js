// src/api/voiceApi.js
import axiosClient from "./axiosClient";

/**
 * Sends a multipart/form-data request with key 'audio'
 * Expects backend to accept form-data audio file for both enroll and verify.
 * If your backend expects base64 for verify, we can adapt — but using multipart is most common.
 */

export const enrollVoice = async (audioBlob) => {
  const formData = new FormData();
  formData.append("audio", audioBlob, "sample.wav");
  // you can append other fields like username if backend requires them
  const res = await axiosClient.post("/api/voice/enroll", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
};

export const verifyVoice = async (audioBlob) => {
  const formData = new FormData();
  formData.append("audio", audioBlob, "sample.wav");
  const res = await axiosClient.post("/api/voice/verify", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
};


// // voiceApi.js (DEMO MODE)

// export async function verifyVoiceDemo(mode = "accept") {
//   return new Promise((resolve) => {
//     setTimeout(() => {
//       if (mode === "accept") {
//         resolve({
//           similarity: 0.996,
//           zScore: 1.42,
//           spoofScore: 0.02,
//           decision: "ACCEPT",
//           reason: "Voice matched"
//         });
//       } else {
//         resolve({
//           similarity: 0.91,
//           zScore: -1.8,
//           spoofScore: 0.67,
//           decision: "REJECT",
//           reason: "Spoof detected"
//         });
//       }
//     }, 1200); // realistic delay
//   });
// }
