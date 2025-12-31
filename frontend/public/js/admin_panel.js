// =========================================
// 🔐 ADMIN AUTH GUARD (FRONTEND ONLY)
// =========================================
(function () {
    const isLoggedIn = sessionStorage.getItem("admin_logged_in");

    if (!isLoggedIn) {
        // ❌ Not logged in → force back to login
        window.location.replace("/admin_login.html");
    }
})();

// =========================================
// GLOBAL STATE
// =========================================
let currentElection = null;

// MESSAGE BOX
const msgBox = document.getElementById("msg");

// =========================================
// 🗳️ CREATE ELECTION
// =========================================
async function createElection() {
    const name = document.getElementById("electionName").value.trim();
    msgBox.innerHTML = "";

    if (!name) {
        msgBox.style.color = "red";
        msgBox.innerHTML = "Election name required!";
        return;
    }

    try {
        const res = await fetch("/admin/create_election", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title: name })
        });

        const data = await res.json();

        if (data.success) {
            currentElection = data.election_id;

            msgBox.style.color = "#00ff9d";
            msgBox.innerHTML = `✅ Election Created! ID = <b>${data.election_id}</b>`;

            document.getElementById("electionStatus").innerText =
                "Election Active: " + name;

            enableSections();
        } else {
            msgBox.style.color = "yellow";
            msgBox.innerHTML = data.message || "Election already exists";
        }

    } catch (err) {
        console.error(err);
        msgBox.style.color = "red";
        msgBox.innerHTML = "Server error while creating election";
    }
}

// =========================================
// ENABLE SECTIONS AFTER ELECTION
// =========================================
function enableSections() {
    document.querySelectorAll(".box")[1].style.opacity = "1";
    document.querySelectorAll(".box")[2].style.opacity = "1";
    document.querySelectorAll(".box")[1].style.pointerEvents = "auto";
    document.querySelectorAll(".box")[2].style.pointerEvents = "auto";
}

// =========================================
// 👤 ADD CANDIDATE
// =========================================
async function addCandidate() {
    if (!currentElection) {
        msgBox.style.color = "red";
        msgBox.innerHTML = "Create election first!";
        return;
    }

    const name = document.getElementById("candidateName").value.trim();
    const party = document.getElementById("candidateParty").value.trim();

    if (!name || !party) {
        msgBox.style.color = "red";
        msgBox.innerHTML = "Candidate name and party required!";
        return;
    }

    const formData = new FormData();
    formData.append("name", name);
    formData.append("party", party);

    try {
        const res = await fetch("/admin/add_candidate", {
            method: "POST",
            body: formData
        });

        const data = await res.json();

        if (res.ok) {
            document.getElementById("candidateList").innerHTML += `
                <p>✅ ${name} (${party})</p>
            `;
            msgBox.style.color = "#00e1ff";
            msgBox.innerHTML = "Candidate added successfully!";
        } else {
            msgBox.style.color = "red";
            msgBox.innerHTML = data.error || "Error adding candidate";
        }

    } catch (err) {
        console.error(err);
        msgBox.style.color = "red";
        msgBox.innerHTML = "Server error while adding candidate";
    }
}

// =========================================
// 📷 VOTER CAMERA
// =========================================
const video = document.getElementById("camera");
let capturedFrames = [];

if (video) {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => video.srcObject = stream)
        .catch(err => console.error("Camera error:", err));
}

function captureFace() {
    const canvas = document.getElementById("captureCanvas");
    const ctx = canvas.getContext("2d");

    capturedFrames = [];

    for (let i = 0; i < 50; i++) {
        ctx.drawImage(video, 0, 0, 320, 240);
        capturedFrames.push(canvas.toDataURL("image/jpeg"));
    }

    msgBox.style.color = "#00ff9d";
    msgBox.innerHTML = "✅ 50 frames captured";
}

// =========================================
// 🧑‍🦱 REGISTER VOTER
// =========================================
async function registerVoter() {
    if (!currentElection) {
        msgBox.style.color = "red";
        msgBox.innerHTML = "Create election first!";
        return;
    }

    const name = document.getElementById("voterName").value.trim();
    const enrollment = document.getElementById("enrollment").value.trim();

    if (!name || !enrollment) {
        msgBox.style.color = "red";
        msgBox.innerHTML = "All fields required!";
        return;
    }

    try {
        const blob = await fetch(capturedFrames[0]).then(r => r.blob());

        const formData = new FormData();
        formData.append("name", name);
        formData.append("enrollment", enrollment);
        formData.append("image", blob, "face.jpg");

        const res = await fetch("/admin/register_voter", {
            method: "POST",
            body: formData
        });

        const data = await res.json();

        if (data.voter_id) {
            msgBox.style.color = "#00ff9d";
            msgBox.innerHTML = "Voter registered successfully!";
        } else {
            msgBox.style.color = "red";
            msgBox.innerHTML = data.error || "Voter registration failed";
        }

    } catch (err) {
        console.error(err);
        msgBox.style.color = "red";
        msgBox.innerHTML = "Server error while registering voter";
    }
}

// =========================================
// 🚪 LOGOUT ADMIN
// =========================================
function logoutAdmin() {
    sessionStorage.removeItem("admin_logged_in");
    window.location.replace("/admin_login.html");
}
