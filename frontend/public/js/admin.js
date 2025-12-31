// ================================
// ✅ CREATE ELECTION
// ================================
async function createElection() {
    const title = document.getElementById("electionName").value.trim();
    const status = document.getElementById("electionStatus");

    if (!title) {
        status.innerText = "❌ Election name required";
        return;
    }

    try {
        const res = await fetch("/admin/create_election", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title })
        });

        const data = await res.json();
        status.innerText = data.message || "✅ Election created";
    } catch (err) {
        status.innerText = "❌ Server error";
        console.error(err);
    }
}


// ================================
// ✅ DELETE ELECTION
// ================================
async function deleteElection(electionId) {
    const status = document.getElementById("electionStatus");

    try {
        const res = await fetch(`/admin/delete_election/${electionId}`, {
            method: "DELETE"
        });

        const data = await res.json();
        status.innerText = data.message || "✅ Election deleted";
    } catch (err) {
        status.innerText = "❌ Server error";
        console.error(err);
    }
}


// ================================
// ✅ ADD CANDIDATE (FORM-DATA)
// ================================
async function addCandidate() {
    const name = document.getElementById("candidateName").value.trim();
    const party = document.getElementById("partyName").value.trim();
    const photo = document.getElementById("candidatePhoto")?.files[0];
    const status = document.getElementById("candidateStatus");

    if (!name) {
        status.innerText = "❌ Candidate name required";
        return;
    }

    const formData = new FormData();
    formData.append("name", name);
    formData.append("party", party || "");
    if (photo) formData.append("photo", photo);

    try {
        const res = await fetch("/admin/add_candidate", {
            method: "POST",
            body: formData
        });

        const data = await res.json();
        status.innerText = data.message || "✅ Candidate added";
    } catch (err) {
        status.innerText = "❌ Server error";
        console.error(err);
    }
}


// ================================
// ✅ CHECK ADMIN EXISTS → REDIRECT
// 🔥 THIS IS THE MOST IMPORTANT FIX
// ================================
async function checkAdminAndRedirect() {
    try {
        const res = await fetch("/admin/check_admin");

        if (!res.ok) {
            alert("Server error while checking admin");
            return;
        }

        const data = await res.json();

        // ✅ Admin NOT created → go to register
        if (!data.exists) {
            window.location.replace("/admin_register.html");
        }
        // ✅ Admin exists → go to login
        else {
            window.location.replace("/admin_login.html");
        }

    } catch (err) {
        console.error("checkAdmin failed:", err);
        alert("Cannot connect to server");
    }
}


// ================================
// ✅ ADMIN LOGIN (PASSWORD BASED)
// ================================
async function adminLogin() {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();
    const errorBox = document.getElementById("error");

    if (!username || !password) {
        errorBox.innerText = "❌ Username & password required";
        return;
    }

    errorBox.innerText = "⏳ Verifying...";

    try {
        const res = await fetch("/admin/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });

        const data = await res.json();

        if (res.ok && data.success) {
            // ✅ LOGIN SUCCESS
            window.location.replace("/admin.html");
        } else {
            // ❌ LOGIN FAILED
            errorBox.innerText = data.error || "❌ Invalid credentials";
        }

    } catch (err) {
        console.error("Login failed:", err);
        errorBox.innerText = "❌ Server error";
    }
}
