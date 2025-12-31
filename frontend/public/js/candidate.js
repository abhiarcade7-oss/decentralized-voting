// ===============================
// CHECK IF ELECTION EXISTS
// ===============================
window.addEventListener("load", async () => {
    try {
        const res = await fetch("/admin/current_election");
        const data = await res.json();

        if (!data.exists) {
            alert("❗ No election exists! Please create one first.");
            window.location.href = "/create_election.html";
            return;
        }
    } catch (err) {
        alert("❌ Failed to check election!");
        console.error(err);
    }

    loadCandidates();
});


// ===============================
// ADD CANDIDATE  (UPDATED)
// ===============================
async function addCandidate() {
    const name = document.getElementById("candidateName").value.trim();
    const party = document.getElementById("partyName").value.trim();
    const age = document.getElementById("candidateAge").value;

    if (!name) {
        alert("❌ Candidate name is required!");
        return;
    }

    const form = new FormData();
    form.append("name", name);
    form.append("party", party);
    form.append("age", age);

    let q = document.getElementById("qualification").value;
    if (q === "Other") {
        q = document.getElementById("qualificationOther").value.trim();
    }
    form.append("qualification", q);

    const photo = document.getElementById("candidatePhoto").files[0];
    if (photo) form.append("photo", photo);

    const res = await fetch("/admin/add_candidate", {
        method: "POST",
        body: form
    });

    const data = await res.json();

    if (data.error) {
        alert("❌ " + data.error);
        return;
    }

    alert(`✅ Candidate "${data.name || name}" added successfully!`);

    // If server returns the new candidate info, prepend instantly
    if (data && data.candidate_id) {
        prependCandidateToList({
            id: data.candidate_id,
            name: data.name || name,
            party: data.party || party,
            age: age || "",
            qualification: q || "",
            photo: data.photo_url || "/static/default_candidate.png"
        });

        clearForm();
        return;
    }

    // fallback reload
    clearForm();
    loadCandidates();
}


// ===============================
// PREPEND NEW CANDIDATE TO LIST (NEW FUNCTION)
// ===============================
function prependCandidateToList(c) {
    const list = document.getElementById("candidateList");

    // Fix photo path by adding domain
    const photoURL = c.photo
        ? (window.location.origin + c.photo)
        : "/static/default_candidate.png";

    const html = `
      <div class="candidate-card">
         <div class="candidate-left">
            <img src="${photoURL}" class="candidate-photo">
            <div class="info">
               <h3>${c.name}</h3>
               <p>${c.party || ''}</p>
               <p>Age: ${c.age || 'N/A'}</p>
               <p>Qualification: ${c.qualification || 'N/A'}</p>
            </div>
         </div>
         <button class="delete-btn" onclick="deleteCandidate(${c.id})">❌ Delete</button>
      </div>
    `;
    list.insertAdjacentHTML('afterbegin', html);
}



// ===============================
// CLEAR FORM AFTER SUCCESS
// ===============================
function clearForm() {
    document.getElementById("candidateName").value = "";
    document.getElementById("partyName").value = "";
    document.getElementById("candidateAge").value = "";
    document.getElementById("qualification").value = "";
    document.getElementById("candidatePhoto").value = "";
    document.getElementById("qualificationOther").style.display = "none";
}



// ===============================
// LOAD CANDIDATES ON PAGE
// ===============================
async function loadCandidates() {
    const res = await fetch("/admin/get_candidates");
    const data = await res.json();

    const list = document.getElementById("candidateList");
    list.innerHTML = "";

    if (!data.candidates || data.candidates.length === 0) {
        list.innerHTML = "<p style='color:#aaa;'>No candidates added yet.</p>";
        return;
    }

    data.candidates.forEach(c => {

        // Fix photo serving — add absolute origin
        const photoURL = c.photo
            ? (window.location.origin + c.photo)
            : "/static/default_candidate.png";

        list.innerHTML += `
        <div class="candidate-card">

            <div class="candidate-left">
                <img src="${photoURL}" class="candidate-photo">

                <div class="info">
                    <h3>${c.name}</h3>
                    <p>${c.party || ''}</p>
                    <p>Age: ${c.age || 'N/A'}</p>
                    <p>Qualification: ${c.qualification || 'N/A'}</p>
                </div>
            </div>

            <button class="delete-btn" onclick="deleteCandidate(${c.id})">
                ❌ Delete
            </button>

        </div>
        `;
    });
}



// ===============================
// DELETE CANDIDATE
// ===============================
async function deleteCandidate(id) {
    if (!confirm("Do you really want to delete this candidate?")) return;

    const res = await fetch(`/admin/delete_candidate/${id}`, {
        method: "DELETE"
    });

    const data = await res.json();

    if (data.error) {
        alert("❌ " + data.error);
        return;
    }

    alert("🗑 Candidate deleted successfully!");
    loadCandidates();
}
