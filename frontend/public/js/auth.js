// frontend/public/js/auth.js
import { API_BASE } from "./api.js";

/* =========================================================
   VOTER FACE AUTH — LIVE CAMERA INSIDE CIRCLE
   ========================================================= */

const authBtn = document.getElementById("authBtn");
const enrollmentInput = document.getElementById("enrollment");
const usernameInput = document.getElementById("username");
const msg = document.getElementById("msg");

const video = document.getElementById("video");
const circle = document.getElementById("circle");

let stream = null;

/* ---------- START CAMERA ---------- */
async function startCamera() {
    circle.style.display = "block";

    stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 320, height: 320 }
    });

    video.srcObject = stream;

    await new Promise(resolve => {
        video.onloadedmetadata = () => resolve();
    });
}

/* ---------- STOP CAMERA ---------- */
function stopCamera() {
    if (stream) {
        stream.getTracks().forEach(t => t.stop());
        stream = null;
    }
}

/* ---------- CAPTURE FRAME ---------- */
function captureFrame() {
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0);

    return canvas.toDataURL("image/jpeg", 0.9);
}

/* ---------- AUTH BUTTON ---------- */
authBtn.addEventListener("click", async () => {

    const enrollment = enrollmentInput.value.trim();
    const username = usernameInput.value.trim();

    if (!username || !enrollment) {
        msg.style.color = "red";
        msg.innerText = "Username and Enrollment are required!";
        return;
    }

    msg.style.color = "#00cfff";
    msg.innerText = "📷 Starting camera...";

    try {
        await startCamera();

        // warm-up camera
        await new Promise(r => setTimeout(r, 1500));

        msg.innerText = "🔍 Capturing face...";

        const frames = [];
        for (let i = 0; i < 5; i++) {
            frames.push(captureFrame());
            await new Promise(r => setTimeout(r, 300));
        }

        stopCamera();

        msg.innerText = "🔐 Verifying face...";

        const res = await fetch(`${API_BASE}/voter/authenticate`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                username,
                enrollment,
                frames
            })
        });

        const data = await res.json();

        if (res.ok && data.success) {
            msg.style.color = "#00ff9d";
            msg.innerText = "✅ Face verified! Redirecting...";

            // 🔥🔥🔥 MOST IMPORTANT FIX
            sessionStorage.setItem("username", username);
            sessionStorage.setItem("enrollment", enrollment);
            sessionStorage.setItem("voter_id", data.voter_id);
            sessionStorage.setItem("voter_name", data.voter_name);

            setTimeout(() => {
                window.location.href = "vote.html";
            }, 1000);


        } else {
            msg.style.color = "red";
            msg.innerText = data.error || "Face verification failed";
        }

    } catch (err) {
        console.error(err);
        stopCamera();
        msg.style.color = "red";
        msg.innerText = "Camera or server error";
    }
});
