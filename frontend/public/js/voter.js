// frontend/public/js/voter.js

const video = document.getElementById("video");
const canvas = document.getElementById("circleCanvas");
const registerBtn = document.getElementById("registerBtn");
const showBtn = document.getElementById("showVotersBtn");
const statusBox = document.getElementById("status");

const voterList = document.getElementById("voterList");
const voterTable = document.getElementById("voterTable");

let frames = [];
let stream = null;

/* ================= CAMERA PREVIEW ================= */

function drawCirclePreviewFromVideo() {
  const ctx = canvas.getContext("2d");
  ctx.save();
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  ctx.beginPath();
  ctx.arc(canvas.width / 2, canvas.height / 2, canvas.width / 2, 0, Math.PI * 2);
  ctx.closePath();
  ctx.clip();

  ctx.translate(canvas.width, 0);
  ctx.scale(-1, 1);
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  ctx.restore();
}

async function startCamera() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { width: 640, height: 480 },
      audio: false
    });

    video.srcObject = stream;
    await video.play();

    const interval = setInterval(() => {
      if (!stream) {
        clearInterval(interval);
        return;
      }
      drawCirclePreviewFromVideo();
    }, 1000 / 15);

    return true;
  } catch (err) {
    alert("Camera access denied");
    console.error(err);
    return false;
  }
}

function stopCamera() {
  if (!stream) return;
  stream.getTracks().forEach(t => t.stop());
  stream = null;

  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);
}

/* ================= CAPTURE FRAMES ================= */

async function captureFrames(count = 30, delayMs = 120) {
  frames = [];
  const off = document.createElement("canvas");
  off.width = 260;
  off.height = 260;
  const ctx = off.getContext("2d");

  for (let i = 0; i < count; i++) {
    ctx.drawImage(video, 0, 0, off.width, off.height);
    frames.push(off.toDataURL("image/jpeg", 0.8));
    await new Promise(r => setTimeout(r, delayMs));
  }
}

/* ================= REGISTER VOTER ================= */

registerBtn.onclick = async () => {
  const name = document.getElementById("name").value.trim();
  const enrollment = document.getElementById("enrollment").value.trim();

  if (!name || !enrollment) {
    alert("Name and enrollment required");
    return;
  }

  registerBtn.disabled = true;
  statusBox.innerText = "Starting camera...";

  const ok = await startCamera();
  if (!ok) {
    registerBtn.disabled = false;
    return;
  }

  statusBox.innerText = "Capturing face...";
  await new Promise(r => setTimeout(r, 2000));

  try {
    await captureFrames();

    const res = await fetch("/admin/register_voter_faces", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, enrollment, frames })
    });

    const data = await res.json();

    if (res.ok) {
      statusBox.innerText = "✅ Voter registered successfully";
      document.getElementById("name").value = "";
      document.getElementById("enrollment").value = "";
    } else {
      statusBox.innerText = data.error || "Registration failed";
    }
  } catch (err) {
    console.error(err);
    statusBox.innerText = "❌ Network error";
  } finally {
    stopCamera();
    registerBtn.disabled = false;
  }
};

/* ================= LOAD VOTERS ================= */

async function loadVoters() {
  voterList.style.display = "block";
  voterTable.innerHTML =
    "<tr><td colspan='4'>Loading voters...</td></tr>";

  try {
    const res = await fetch("/admin/get_voters");
    const data = await res.json();

    voterTable.innerHTML = "";

    if (!data.voters || data.voters.length === 0) {
      voterTable.innerHTML =
        "<tr><td colspan='4'>No voters found</td></tr>";
      return;
    }

    data.voters.forEach(v => {
      voterTable.innerHTML += `
        <tr>
          <td>${v.name}</td>
          <td>${v.enrollment}</td>
          <td>${v.has_voted ? "Voted" : "Not Voted"}</td>
          <td>
            ${
              v.has_voted
                ? "—"
                : `<button class="danger" onclick="deleteVoter(${v.id})">
                     Delete
                   </button>`
            }
          </td>
        </tr>
      `;
    });
  } catch (err) {
    console.error(err);
    voterTable.innerHTML =
      "<tr><td colspan='4'>Failed to load voters</td></tr>";
  }
}

if (showBtn) {
  showBtn.onclick = loadVoters;
}

/* ================= DELETE VOTER ================= */

window.deleteVoter = async function (voterId) {
  if (!confirm("Delete this voter?")) return;

  try {
    const res = await fetch(`/admin/delete_voter/${voterId}`, {
      method: "DELETE"
    });

    const data = await res.json();

    if (res.ok) {
      loadVoters(); // clean refresh
    } else {
      alert(data.error || "Delete failed");
    }
  } catch (err) {
    console.error(err);
    alert("Network error");
  }
};
