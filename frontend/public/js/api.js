// frontend/public/js/api.js
// export const API_BASE = "http://localhost:5000";
export const API_BASE = "https://voting-backend.onrender.com";


export async function apiFetch(path, options = {}) {
    const res = await fetch(API_BASE + path, options);
    const json = await res.json().catch(() => ({}));
    if (!res.ok) throw json;
    return json;
}
