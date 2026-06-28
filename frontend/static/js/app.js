// AgriNova AI - Master Client Engine

const API_BASE = "";

// =====================================================
// JWT & Session Management Helpers
// =====================================================
function getAccessToken() {
    return localStorage.getItem("access_token");
}

function getRefreshToken() {
    return localStorage.getItem("refresh_token");
}

function setTokens(access, refresh) {
    if (access) localStorage.setItem("access_token", access);
    if (refresh) localStorage.setItem("refresh_token", refresh);
}

function clearTokens() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user_info");
}

// Authorized API Fetch Wrapper with Automatic Token Refresh
async function apiFetch(url, options = {}) {
    let token = getAccessToken();
    
    // Set headers
    options.headers = options.headers || {};
    if (token) {
        options.headers["Authorization"] = `Bearer ${token}`;
    }
    
    let response = await fetch(url, options);
    
    // If token expired (401 Unauthorized), attempt to refresh
    if (response.status === 401 && getRefreshToken()) {
        try {
            const refreshRes = await fetch(`${API_BASE}/api/auth/refresh`, {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${getRefreshToken()}`
                }
            });
            
            if (refreshRes.ok) {
                const refreshData = await refreshRes.json();
                setTokens(refreshData.access_token);
                
                // Retry original request with new token
                options.headers["Authorization"] = `Bearer ${refreshData.access_token}`;
                response = await fetch(url, options);
            } else {
                // Refresh token invalid/expired, log out
                clearTokens();
                window.location.href = "/login?msg=Session expired. Please log in again.";
            }
        } catch (err) {
            clearTokens();
            window.location.href = "/login?msg=Session expired. Please log in again.";
        }
    }
    
    return response;
}

// Helper to trigger protected downloads (PDF/CSV/Excel)
async function downloadReport(url, filename) {
    try {
        const res = await apiFetch(url);
        if (!res.ok) throw new Error("Export failed.");
        const blob = await res.blob();
        const blobUrl = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = blobUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(blobUrl);
    } catch (err) {
        alert("Failed to export report: " + err.message);
    }
}

// Page Auth Guard
function guardPage() {
    const publicPages = ["/", "/login", "/register", "/forgot-password", "/reset-password"];
    const path = window.location.pathname;
    
    if (!getAccessToken() && !publicPages.includes(path)) {
        window.location.href = "/login";
    }
}

// Format Dates
function formatDate(isoStr) {
    if (!isoStr) return "N/A";
    const date = new Date(isoStr);
    return date.toLocaleString();
}

// Document Ready Coordinator
document.addEventListener("DOMContentLoaded", () => {
    guardPage();
    setupGlobalNavigation();
    
    const path = window.location.pathname;
    if (path === "/login") initLoginPage();
    else if (path === "/register") initRegisterPage();
    else if (path === "/forgot-password") initForgotPasswordPage();
    else if (path === "/reset-password") initResetPasswordPage();
    else if (path === "/dashboard") initDashboardPage();
    else if (path === "/farms") initFarmsPage();
    else if (path === "/weather") initWeatherPage();
    else if (path === "/prediction") initPredictionPage();
    else if (path === "/reports") initReportsPage();
    else if (path === "/profile") initProfilePage();
});

// =====================================================
// Global Layout: Sidebar & Nav State
// =====================================================
function setupGlobalNavigation() {
    const logoutBtn = document.getElementById("logoutBtn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", async (e) => {
            e.preventDefault();
            try {
                await apiFetch("/api/auth/logout", { method: "POST" });
            } catch (err) {
                console.error("Logout API failed, clearing session locally.", err);
            }
            clearTokens();
            window.location.href = "/login";
        });
    }

    // Toggle Sidebar on mobile
    const toggleSidebar = document.getElementById("toggleSidebar");
    const sidebar = document.querySelector(".sidebar");
    if (toggleSidebar && sidebar) {
        toggleSidebar.addEventListener("click", () => {
            sidebar.classList.toggle("show");
        });
    }

    // Load User info into header
    const userDisplay = document.getElementById("userDisplay");
    if (userDisplay && localStorage.getItem("user_info")) {
        const user = JSON.parse(localStorage.getItem("user_info"));
        userDisplay.textContent = user.full_name;
    }
}

// =====================================================
// 1. Auth Page Logic
// =====================================================
function initLoginPage() {
    const form = document.getElementById("loginForm");
    const alertBox = document.getElementById("alertBox");
    
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;
        
        try {
            const res = await fetch("/api/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password })
            });
            const data = await res.json();
            
            if (data.success) {
                setTokens(data.access_token, data.refresh_token);
                localStorage.setItem("user_info", JSON.stringify(data.user));
                window.location.href = "/dashboard";
            } else {
                alertBox.textContent = data.message || "Invalid credentials.";
                alertBox.classList.remove("d-none");
            }
        } catch (err) {
            alertBox.textContent = "Server connection failed.";
            alertBox.classList.remove("d-none");
        }
    });
}

function initRegisterPage() {
    const form = document.getElementById("registerForm");
    const alertBox = document.getElementById("alertBox");
    
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const full_name = document.getElementById("fullName").value;
        const email = document.getElementById("email").value;
        const phone = document.getElementById("phone").value;
        const password = document.getElementById("password").value;
        const confirm_password = document.getElementById("confirmPassword").value;
        
        if (password !== confirm_password) {
            alertBox.textContent = "Passwords do not match.";
            alertBox.classList.remove("d-none");
            return;
        }
        
        try {
            const res = await fetch("/api/auth/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ full_name, email, phone, password, confirm_password })
            });
            const data = await res.json();
            
            if (data.success) {
                window.location.href = "/login?msg=Registration successful. Please log in.";
            } else {
                alertBox.textContent = data.message || "Registration failed.";
                alertBox.classList.remove("d-none");
            }
        } catch (err) {
            alertBox.textContent = "Server connection failed.";
            alertBox.classList.remove("d-none");
        }
    });
}

function initForgotPasswordPage() {
    const form = document.getElementById("forgotForm");
    const alertBox = document.getElementById("alertBox");
    
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const email = document.getElementById("email").value;
        
        try {
            const res = await fetch("/api/auth/forgot-password", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email })
            });
            const data = await res.json();
            
            if (data.success) {
                alertBox.innerHTML = `Success! Reset token generated:<br><small class="text-break">${data.token || "Check server console."}</small><br><a href="/reset-password?token=${data.token}" class="alert-link mt-2 d-inline-block">Go to Reset Password Form</a>`;
                alertBox.className = "alert alert-success";
            } else {
                alertBox.textContent = data.message || "Failed to process request.";
                alertBox.className = "alert alert-danger";
            }
        } catch (err) {
            alertBox.textContent = "Server connection failed.";
            alertBox.className = "alert alert-danger";
        }
    });
}

function initResetPasswordPage() {
    const form = document.getElementById("resetForm");
    const alertBox = document.getElementById("alertBox");
    
    // Extract token from query parameter
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get("token");
    if (token) {
        document.getElementById("token").value = token;
    }
    
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const inputToken = document.getElementById("token").value;
        const new_password = document.getElementById("password").value;
        
        try {
            const res = await fetch("/api/auth/reset-password", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ token: inputToken, new_password })
            });
            const data = await res.json();
            
            if (data.success) {
                alertBox.textContent = "Password reset successful! Redirecting to login...";
                alertBox.className = "alert alert-success";
                setTimeout(() => { window.location.href = "/login"; }, 2500);
            } else {
                alertBox.textContent = data.message || "Password reset failed.";
                alertBox.className = "alert alert-danger";
            }
        } catch (err) {
            alertBox.textContent = "Server connection failed.";
            alertBox.className = "alert alert-danger";
        }
    });
}

// =====================================================
// 2. Dashboard Logic
// =====================================================
async function initDashboardPage() {
    try {
        const res = await apiFetch("/api/dashboard/stats");
        if (!res.ok) throw new Error("Failed to load dashboard statistics.");
        const data = await res.json();
        
        // Update stats cards
        document.getElementById("farmsCount").textContent = data.stats.farms_count;
        document.getElementById("totalSize").textContent = data.stats.total_size_hectares.toFixed(1) + " Ha";
        document.getElementById("predictionsCount").textContent = data.stats.predictions_count;
        
        // Render Smart Insights
        const insightsContainer = document.getElementById("smartInsightsContainer");
        if (insightsContainer) {
            insightsContainer.innerHTML = "";
            if (data.insights && data.insights.length > 0) {
                data.insights.forEach(insight => {
                    insightsContainer.innerHTML += `
                        <div class="d-flex gap-3 mb-3 pb-3 border-bottom border-light">
                            <div class="feature-icon-wrapper flex-shrink-0 mb-0" style="width:36px;height:36px;">
                                <i class="bi ${insight.icon} ${insight.color} fs-5"></i>
                            </div>
                            <p class="small mb-0 text-dark" style="line-height: 1.5;">${insight.text}</p>
                        </div>
                    `;
                });
            } else {
                insightsContainer.innerHTML = `<p class="text-muted small">No active insights at the moment.</p>`;
            }
        }
        
        // Render Recent Activity table
        const activityBody = document.getElementById("activityBody");
        activityBody.innerHTML = "";
        
        if (data.recent_predictions.length === 0) {
            activityBody.innerHTML = `<tr><td colspan="4" class="text-center text-muted">No recent predictions found.</td></tr>`;
        }
        
        data.recent_predictions.forEach(p => {
            const date = formatDate(p.created_at);
            const type = p.prediction_type.replace("_", " ").title();
            
            let outputSummary = "";
            for (let [k, v] of Object.entries(p.outputs)) {
                outputSummary += `${k.replace("_", " ").title()}: <strong>${v}</strong> `;
            }
            
            activityBody.innerHTML += `
                <tr>
                    <td>${date}</td>
                    <td><span class="badge bg-success">${type}</span></td>
                    <td>${outputSummary}</td>
                    <td><span class="text-primary">${p.confidence ? (p.confidence * 100) + "%" : "N/A"}</span></td>
                </tr>
            `;
        });
    } catch (err) {
        console.error(err);
    }
}

function renderDashboardChart(breakdown) {
    const ctx = document.getElementById("statsChart").getContext("2d");
    new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: ["Crop Rec", "Yield", "Disease", "Fertilizer", "Price"],
            datasets: [{
                data: [
                    breakdown.crop || 0,
                    breakdown.yield || 0,
                    breakdown.disease || 0,
                    breakdown.fertilizer || 0,
                    breakdown.price || 0
                ],
                backgroundColor: ["#16A34A", "#22C55E", "#84CC16", "#10B981", "#3B82F6"],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: "bottom" }
            }
        }
    });
}

// Helper to Capitalize/Title String
String.prototype.title = function() {
    return this.replace(/\b\w/g, l => l.toUpperCase());
};

// =====================================================
// 3. Farm Management Logic
// =====================================================
let currentFarms = [];

async function initFarmsPage() {
    await fetchFarms();
    
    // Setup Cascading Dropdowns for Manual Location
    if (typeof initLocationDropdowns === 'function') {
        initLocationDropdowns("country", "state", "district", "taluk");
    }

    // Handle Location Tabs
    document.getElementById("auto-loc-tab")?.addEventListener("click", () => {
        document.getElementById("locMethod").value = "auto";
    });
    document.getElementById("manual-loc-tab")?.addEventListener("click", () => {
        document.getElementById("locMethod").value = "manual";
    });

    // Geolocate button setup (Nominatim API)
    const geoBtn = document.getElementById("geolocateBtn");
    if (geoBtn) {
        geoBtn.addEventListener("click", () => {
            if (navigator.geolocation) {
                geoBtn.disabled = true;
                const originalHtml = geoBtn.innerHTML;
                geoBtn.innerHTML = `<span class="spinner-border spinner-border-sm"></span> Locating...`;
                document.getElementById("geoStatus").textContent = "Fetching GPS coordinates...";
                
                navigator.geolocation.getCurrentPosition(
                    async (position) => {
                        const lat = position.coords.latitude;
                        const lon = position.coords.longitude;
                        
                        document.getElementById("autoLat").value = lat.toFixed(6);
                        document.getElementById("autoLon").value = lon.toFixed(6);
                        
                        document.getElementById("geoStatus").textContent = "Resolving address...";
                        
                        // Reverse Geocoding via Nominatim
                        try {
                            const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`);
                            const data = await res.json();
                            
                            if (data && data.address) {
                                document.getElementById("autoCountry").value = data.address.country || "India";
                                document.getElementById("autoState").value = data.address.state || "";
                                document.getElementById("autoDistrict").value = data.address.state_district || data.address.county || "";
                                document.getElementById("autoTaluk").value = data.address.county || data.address.city || "";
                                document.getElementById("autoVillage").value = data.address.village || data.address.town || data.address.suburb || "";
                                
                                document.getElementById("autoLocResults").classList.remove("d-none");
                                document.getElementById("geoStatus").textContent = "Location resolved successfully.";
                            }
                        } catch (e) {
                            document.getElementById("geoStatus").textContent = "GPS found, but address resolution failed.";
                            document.getElementById("autoLocResults").classList.remove("d-none");
                        }
                        
                        geoBtn.disabled = false;
                        geoBtn.innerHTML = originalHtml;
                    },
                    (err) => {
                        alert("Geolocation failed: " + err.message);
                        geoBtn.disabled = false;
                        geoBtn.innerHTML = originalHtml;
                        document.getElementById("geoStatus").textContent = "Uses GPS to auto-fill location data.";
                    }
                );
            } else {
                alert("Geolocation not supported by this browser.");
            }
        });
    }

    // Add Farm Form submit
    const addFarmForm = document.getElementById("addFarmForm");
    if (addFarmForm) {
        addFarmForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const farm_name = document.getElementById("farmName").value;
            const farm_size = parseFloat(document.getElementById("farmSize").value);
            const locMethod = document.getElementById("locMethod").value;
            
            let country, state, district, taluk, village, latitude, longitude;
            
            if (locMethod === "auto") {
                country = document.getElementById("autoCountry").value;
                state = document.getElementById("autoState").value;
                district = document.getElementById("autoDistrict").value;
                taluk = document.getElementById("autoTaluk").value;
                village = document.getElementById("autoVillage").value;
                const latInput = document.getElementById("autoLat").value;
                const lonInput = document.getElementById("autoLon").value;
                latitude = latInput ? parseFloat(latInput) : null;
                longitude = lonInput ? parseFloat(lonInput) : null;
            } else {
                country = document.getElementById("country").value;
                state = document.getElementById("state").value;
                district = document.getElementById("district").value;
                taluk = document.getElementById("taluk").value;
                village = document.getElementById("village").value;
                latitude = null;
                longitude = null;
            }
            
            // Soil Type is no longer manually entered. It will be determined by the backend based on coordinates or defaults to a sensible value for the district.
            const soil_type = "Unknown"; // Backend will override this
            
            try {
                const res = await apiFetch("/api/farms/", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ farm_name, country, state, district, taluk, village, soil_type, farm_size, latitude, longitude })
                });
                
                if (res.ok) {
                    // Close Modal and reload
                    const modalEl = document.getElementById("addFarmModal");
                    const modal = bootstrap.Modal.getInstance(modalEl);
                    if (modal) modal.hide();
                    addFarmForm.reset();
                    await fetchFarms();
                } else {
                    const data = await res.json();
                    alert(data.message || "Failed to create farm.");
                }
            } catch (err) {
                alert("Connection failed.");
            }
        });
    }
}

async function fetchFarms() {
    try {
        const res = await apiFetch("/api/farms/");
        if (!res.ok) throw new Error("Failed to load farms.");
        const data = await res.json();
        currentFarms = data.farms;
        
        const farmGrid = document.getElementById("farmGrid");
        if (!farmGrid) return;
        farmGrid.innerHTML = "";
        
        if (currentFarms.length === 0) {
            farmGrid.innerHTML = `
                <div class="col-12 text-center py-5">
                    <p class="text-muted">No farms registered. Click 'Add Farm' to begin.</p>
                </div>
            `;
            return;
        }
        
        currentFarms.forEach(f => {
            farmGrid.innerHTML += `
                <div class="col-md-6 col-lg-4 mb-4">
                    <div class="glass-card animate-fade-in">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h5 class="mb-0 text-success">${f.farm_name}</h5>
                            <span class="badge bg-light text-dark">${f.farm_size} Ha</span>
                        </div>
                        <p class="mb-1 text-muted"><i class="bi bi-geo-alt me-1"></i> ${f.village}, ${f.district}, ${f.state}</p>
                        <p class="mb-1 text-muted"><i class="bi bi-water me-1"></i> Soil: <strong>${f.soil_type}</strong></p>
                        <p class="mb-3 text-muted"><i class="bi bi-compass me-1"></i> Coordinates: ${f.latitude ? f.latitude.toFixed(4) + ", " + f.longitude.toFixed(4) : "None"}</p>
                        <div class="d-flex justify-content-end">
                            <button class="btn btn-sm btn-outline-primary me-2" onclick="editFarm('${f.id}')"><i class="bi bi-pencil"></i></button>
                            <button class="btn btn-sm btn-outline-danger" onclick="deleteFarm('${f.id}')"><i class="bi bi-trash"></i></button>
                        </div>
                    </div>
                </div>
            `;
        });
    } catch (err) {
        console.error(err);
    }
}

async function deleteFarm(id) {
    if (!confirm("Are you sure you want to delete this farm? This action is irreversible.")) return;
    try {
        const res = await apiFetch(`/api/farms/${id}`, { method: "DELETE" });
        if (res.ok) {
            await fetchFarms();
        } else {
            const data = await res.json();
            alert(data.message || "Failed to delete farm.");
        }
    } catch (err) {
        alert("Delete request failed.");
    }
}

// Open Edit Modal & Populate Fields
window.editFarm = function(id) {
    const farm = currentFarms.find(f => f.id === id);
    if (!farm) return;

    // Create Modal on-the-fly or populate template
    const editModalHtml = `
        <div class="modal fade" id="editFarmModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content glass-card p-0">
                    <div class="modal-header border-0 px-4 pt-4 pb-0">
                        <h5 class="modal-title">Edit Farm Details</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <form id="editFarmForm">
                        <div class="modal-body p-4">
                            <div class="mb-3">
                                <label class="form-label">Farm Name</label>
                                <input type="text" class="form-control" id="editFarmName" value="${farm.farm_name}" required>
                            </div>
                            <div class="row mb-3">
                                <div class="col-md-6">
                                    <label class="form-label">State</label>
                                    <input type="text" class="form-control" id="editState" value="${farm.state}" required>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">District</label>
                                    <input type="text" class="form-control" id="editDistrict" value="${farm.district}" required>
                                </div>
                            </div>
                            <div class="row mb-3">
                                <div class="col-md-6">
                                    <label class="form-label">Village</label>
                                    <input type="text" class="form-control" id="editVillage" value="${farm.village}" required>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">Soil Type</label>
                                    <select class="form-select" id="editSoilType" required>
                                        <option value="Sandy" ${farm.soil_type === "Sandy" ? "selected" : ""}>Sandy</option>
                                        <option value="Loamy" ${farm.soil_type === "Loamy" ? "selected" : ""}>Loamy</option>
                                        <option value="Clayey" ${farm.soil_type === "Clayey" ? "selected" : ""}>Clayey</option>
                                        <option value="Black" ${farm.soil_type === "Black" ? "selected" : ""}>Black</option>
                                        <option value="Red" ${farm.soil_type === "Red" ? "selected" : ""}>Red</option>
                                    </select>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Farm Size (Hectares)</label>
                                <input type="number" step="0.1" class="form-control" id="editFarmSize" value="${farm.farm_size}" required>
                            </div>
                            <div class="row mb-3">
                                <div class="col-md-6">
                                    <label class="form-label">Latitude</label>
                                    <input type="number" step="0.000001" class="form-control" id="editLatitude" value="${farm.latitude || ''}">
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">Longitude</label>
                                    <input type="number" step="0.000001" class="form-control" id="editLongitude" value="${farm.longitude || ''}">
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer border-0 p-4 pt-0">
                            <button type="button" class="btn btn-light" data-bs-dismiss="modal">Cancel</button>
                            <button type="submit" class="btn btn-success">Save Changes</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    `;

    // Append modal, show, and handle submit
    const div = document.createElement("div");
    div.innerHTML = editModalHtml;
    document.body.appendChild(div);

    const editModal = new bootstrap.Modal(document.getElementById("editFarmModal"));
    editModal.show();

    document.getElementById("editFarmForm").addEventListener("submit", async (e) => {
        e.preventDefault();
        const farm_name = document.getElementById("editFarmName").value;
        const state = document.getElementById("editState").value;
        const district = document.getElementById("editDistrict").value;
        const village = document.getElementById("editVillage").value;
        const soil_type = document.getElementById("editSoilType").value;
        const farm_size = parseFloat(document.getElementById("editFarmSize").value);
        const latInput = document.getElementById("editLatitude").value;
        const lonInput = document.getElementById("editLongitude").value;
        const latitude = latInput ? parseFloat(latInput) : null;
        const longitude = lonInput ? parseFloat(lonInput) : null;

        try {
            const res = await apiFetch(`/api/farms/${id}`, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ farm_name, state, district, village, soil_type, farm_size, latitude, longitude })
            });

            if (res.ok) {
                editModal.hide();
                document.getElementById("editFarmModal").remove();
                await fetchFarms();
            } else {
                const data = await res.json();
                alert(data.message || "Failed to update farm.");
            }
        } catch (err) {
            alert("Update request failed.");
        }
    });

    document.getElementById("editFarmModal").addEventListener("hidden.bs.modal", () => {
        document.getElementById("editFarmModal").remove();
    });
};

window.deleteFarm = deleteFarm;

// =====================================================
// 4. Weather Dashboard Logic
// =====================================================
async function initWeatherPage() {
    const farmSelect = document.getElementById("weatherFarmSelect");
    if (!farmSelect) return;
    
    // Fetch and populate farms dropdown
    try {
        const res = await apiFetch("/api/farms/");
        const data = await res.json();
        
        farmSelect.innerHTML = `<option value="">Select a farm...</option>`;
        data.farms.forEach(f => {
            farmSelect.innerHTML += `<option value="${f.id}">${f.farm_name} (${f.village})</option>`;
        });
        
        farmSelect.addEventListener("change", async () => {
            const fid = farmSelect.value;
            if (!fid) {
                document.getElementById("weatherDetailsArea").classList.add("d-none");
                return;
            }
            await loadWeatherForFarm(fid);
        });
    } catch (err) {
        console.error(err);
    }
}

async function loadWeatherForFarm(farmId) {
    const spinner = document.getElementById("weatherSpinner");
    const detailsArea = document.getElementById("weatherDetailsArea");
    
    spinner.classList.remove("d-none");
    detailsArea.classList.add("d-none");
    
    try {
        const res = await apiFetch(`/api/weather/?farm_id=${farmId}`);
        const data = await res.json();
        
        spinner.classList.add("d-none");
        
        if (!data.success) {
            alert(data.message || "Failed to fetch weather.");
            return;
        }
        
        detailsArea.classList.remove("d-none");
        
        // Populate Current Weather
        const w = data.weather.current;
        document.getElementById("sourceBadge").textContent = data.source;
        document.getElementById("currTemp").textContent = w.temp.toFixed(1) + "°C";
        document.getElementById("currDesc").textContent = w.description;
        document.getElementById("currHumidity").textContent = w.humidity + "%";
        document.getElementById("currWind").textContent = w.wind_speed.toFixed(1) + " m/s";
        document.getElementById("currRain").textContent = w.rain_probability + "%";
        document.getElementById("currUV").textContent = w.uv_index;
        
        // Populate Alerts
        const alertBox = document.getElementById("weatherAlertsBox");
        alertBox.innerHTML = "";
        if (data.weather.alerts.length === 0) {
            alertBox.innerHTML = `<div class="text-success"><i class="bi bi-shield-check me-2"></i> No active weather alerts for this farm.</div>`;
        } else {
            data.weather.alerts.forEach(a => {
                alertBox.innerHTML += `
                    <div class="alert alert-warning mb-2 py-2">
                        <i class="bi bi-exclamation-triangle-fill me-2"></i><strong>${a.type.replace("_", " ").toUpperCase()}:</strong> ${a.message}
                    </div>
                `;
            });
        }
        
        // Populate 7-Day Forecast
        const forecastCards = document.getElementById("forecastCards");
        forecastCards.innerHTML = "";
        
        data.weather.forecast.forEach(f => {
            const dateObj = new Date(f.date);
            const dayName = dateObj.toLocaleDateString("en-US", { weekday: "short" });
            const dayNum = dateObj.toLocaleDateString("en-US", { day: "numeric", month: "short" });
            
            // Choose weather icon class based on description
            let iconClass = "bi-cloud-sun";
            const desc = f.description.toLowerCase();
            if (desc.includes("rain") || desc.includes("shower")) iconClass = "bi-cloud-rain";
            else if (desc.includes("thunder")) iconClass = "bi-cloud-lightning-rain";
            else if (desc.includes("sunny") || desc.includes("clear")) iconClass = "bi-sun";
            else if (desc.includes("overcast") || desc.includes("cloudy")) iconClass = "bi-cloudy";

            forecastCards.innerHTML += `
                <div class="col-6 col-md-4 col-lg-2 mb-3">
                    <div class="forecast-card">
                        <small class="d-block text-muted">${dayName}</small>
                        <strong class="d-block mb-2">${dayNum}</strong>
                        <i class="bi ${iconClass} text-success" style="font-size: 2rem;"></i>
                        <span class="d-block text-muted small mt-1 text-truncate" title="${f.description}">${f.description}</span>
                        <div class="mt-2 small">
                            <span class="text-danger fw-bold">${f.temp_day.toFixed(0)}°</span>
                            <span class="text-primary ms-1">${f.temp_night.toFixed(0)}°</span>
                        </div>
                    </div>
                </div>
            `;
        });
        
    } catch (err) {
        spinner.classList.add("d-none");
        alert("Failed to connect to weather service.");
    }
}

// =====================================================
// 5. AI Predictions Forms & Results Logic
// =====================================================
async function initPredictionPage() {
    const farmSelects = document.querySelectorAll(".farm-select");
    
    // Load farms into all farm selectors in prediction tabs
    try {
        const res = await apiFetch("/api/farms/");
        const data = await res.json();
        
        farmSelects.forEach(sel => {
            sel.innerHTML = `<option value="">Select Farm (Optional)...</option>`;
            data.farms.forEach(f => {
                sel.innerHTML += `<option value="${f.id}" data-soil="${f.soil_type}" data-state="${f.state}" data-district="${f.district}" data-village="${f.village}">${f.farm_name}</option>`;
            });
        });
    } catch (err) {
        console.error("Failed to load farms for selectors", err);
    }

    // Auto fill properties if farm is selected (e.g. soil type, location)
    const fertFarmSel = document.getElementById("fertFarm");
    if (fertFarmSel) {
        fertFarmSel.addEventListener("change", () => {
            const opt = fertFarmSel.options[fertFarmSel.selectedIndex];
            const soil = opt.getAttribute("data-soil");
            if (soil) {
                document.getElementById("fertSoil").value = soil;
            }
        });
    }

    const yieldFarmSel = document.getElementById("yieldFarm");
    if (yieldFarmSel) {
        yieldFarmSel.addEventListener("change", () => {
            const opt = yieldFarmSel.options[yieldFarmSel.selectedIndex];
            const state = opt.getAttribute("data-state");
            if (state) {
                document.getElementById("yieldState").value = state;
            }
        });
    }

    const priceFarmSel = document.getElementById("priceFarm");
    if (priceFarmSel) {
        priceFarmSel.addEventListener("change", () => {
            const opt = priceFarmSel.options[priceFarmSel.selectedIndex];
            const state = opt.getAttribute("data-state");
            const district = opt.getAttribute("data-district");
            if (state) document.getElementById("priceState").value = state;
            if (district) document.getElementById("priceDistrict").value = district;
        });
    }

    // Bind Forms
    setupCropForm();
    setupYieldForm();
    setupFertilizerForm();
    setupPriceForm();
    setupDiseaseForm();
}

function showResultCard(cardId, contentHtml) {
    const card = document.getElementById(cardId);
    card.innerHTML = contentHtml;
    card.classList.remove("d-none");
    card.scrollIntoView({ behavior: "smooth" });
}

function setupCropForm() {
    const form = document.getElementById("cropForm");
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        const formData = new FormData();
        const farmId = document.getElementById("cropFarm").value;
        if (farmId) formData.append("farm_id", farmId);
        
        formData.append("season", document.getElementById("cropSeason").value);
        formData.append("farming_goal", document.getElementById("cropGoal").value);
        
        const fileInput = document.getElementById("cropSoilReport");
        if (fileInput.files.length > 0) {
            formData.append("soil_report", fileInput.files[0]);
        }
        
        try {
            const res = await apiFetch("/api/crop/recommend", {
                method: "POST",
                // Do not set Content-Type for FormData, fetch will set it with boundary
                body: formData
            });
            const data = await res.json();
            
            if (data.success) {
                showResultCard("cropResult", `
                    <div class="alert alert-success border-0 mb-0 d-flex align-items-center">
                        <i class="bi bi-journal-check me-3" style="font-size: 2.5rem;"></i>
                        <div>
                            <h4 class="alert-heading fw-bold mb-1">Recommended Crop: ${data.recommended_crop}</h4>
                            <p class="mb-0 small">Based on our advanced AI analysis of your farm's location and derived parameters, we recommend cultivating <strong>${data.recommended_crop}</strong>.</p>
                        </div>
                    </div>
                `);
            } else {
                alert(data.message || "Failed to calculate.");
            }
        } catch (err) {
            alert("Connection error.");
        }
    });
}

function setupYieldForm() {
    const form = document.getElementById("yieldForm");
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const body = {
            farm_id: document.getElementById("yieldFarm").value || null,
            crop: document.getElementById("yieldCrop").value,
            season: document.getElementById("yieldSeason").value
        };

        try {
            const res = await apiFetch("/api/prediction/yield", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(body)
            });
            const data = await res.json();

            if (data.success) {
                showResultCard("yieldResult", `
                    <div class="alert alert-primary border-0 mb-0 d-flex align-items-center">
                        <i class="bi bi-graph-up-arrow me-3" style="font-size: 2.5rem;"></i>
                        <div>
                            <h4 class="alert-heading fw-bold mb-1">Predicted Yield: ${data.predicted_yield} Tonnes</h4>
                            <p class="mb-0 small">Forecasted productivity: <strong>${data.yield_per_hectare} tonnes per hectare</strong> for ${body.crop.title()} in ${body.season} season based on auto-fetched weather data.</p>
                        </div>
                    </div>
                `);
            } else {
                alert(data.message || "Prediction failed.");
            }
        } catch (err) {
            alert("Connection error.");
        }
    });
}

function setupFertilizerForm() {
    const form = document.getElementById("fertForm");
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        const formData = new FormData();
        const farmId = document.getElementById("fertFarm").value;
        if (farmId) formData.append("farm_id", farmId);
        
        formData.append("crop_type", document.getElementById("fertCrop").value);
        formData.append("farming_goal", document.getElementById("fertGoal").value);
        
        const fileInput = document.getElementById("fertSoilReport");
        if (fileInput.files.length > 0) {
            formData.append("soil_report", fileInput.files[0]);
        }

        try {
            const res = await apiFetch("/api/ai/fertilizer", {
                method: "POST",
                body: formData
            });
            const data = await res.json();

            if (data.success) {
                showResultCard("fertResult", `
                    <div class="alert alert-info border-0 mb-0 d-flex align-items-center">
                        <i class="bi bi-droplet-half me-3" style="font-size: 2.5rem;"></i>
                        <div>
                            <h4 class="alert-heading fw-bold mb-1">Recommended Fertilizer: ${data.recommended_fertilizer}</h4>
                            <p class="mb-0 small">Suggested application: <strong>${data.recommended_fertilizer}</strong>. Adjust dosage proportional to nitrogen margins to preserve local groundwater health.</p>
                        </div>
                    </div>
                `);
            } else {
                alert(data.message || "Failed to calculate.");
            }
        } catch (err) {
            alert("Connection error.");
        }
    });
}

function setupPriceForm() {
    const form = document.getElementById("priceForm");
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const body = {
            state: document.getElementById("priceState").value,
            district: document.getElementById("priceDistrict").value,
            commodity: document.getElementById("priceCommodity").value,
            month: parseInt(document.getElementById("priceMonth").value)
        };

        try {
            const res = await apiFetch("/api/prediction/price", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(body)
            });
            const data = await res.json();

            if (data.success) {
                showResultCard("priceResult", `
                    <div class="alert alert-warning border-0 mb-0 d-flex align-items-center">
                        <i class="bi bi-currency-rupee me-3" style="font-size: 2.5rem;"></i>
                        <div>
                            <h4 class="alert-heading fw-bold mb-1">Predicted Modal Price: ₹${data.predicted_price} / Quintal</h4>
                            <p class="mb-0 small">Estimated market rate for <strong>${body.commodity}</strong> at district mandis. Highly recommended to store yield if pricing curves lean upwards in coming months.</p>
                        </div>
                    </div>
                `);
            } else {
                alert(data.message || "Prediction failed.");
            }
        } catch (err) {
            alert("Connection error.");
        }
    });
}

function setupDiseaseForm() {
    const form = document.getElementById("diseaseForm");
    const uploadInput = document.getElementById("diseaseFile");
    
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        if (uploadInput.files.length === 0) {
            alert("Please select a leaf image file first.");
            return;
        }
        
        const formData = new FormData();
        formData.append("file", uploadInput.files[0]);
        const farmId = document.getElementById("diseaseFarm").value;
        if (farmId) formData.append("farm_id", farmId);
        
        const loader = document.getElementById("diseaseLoader");
        loader.classList.remove("d-none");
        
        try {
            // Cannot use apiFetch directly because body is FormData (must let browser set multipart/form-data boundary)
            const token = getAccessToken();
            const res = await fetch("/api/disease/detect", {
                method: "POST",
                headers: {
                    "Authorization": `Bearer ${token}`
                },
                body: formData
            });
            const data = await res.json();
            
            loader.classList.add("d-none");
            
            if (data.success) {
                const statusColor = data.healthy ? "success" : "danger";
                const statusIcon = data.healthy ? "bi-check-circle-fill" : "bi-exclamation-octagon-fill";
                
                showResultCard("diseaseResult", `
                    <div class="glass-card animate-fade-in p-4 border-${statusColor}">
                        <div class="d-flex align-items-center mb-3">
                            <i class="bi ${statusIcon} text-${statusColor} me-3" style="font-size: 2.5rem;"></i>
                            <div>
                                <h4 class="mb-0 fw-bold">Classification: ${data.crop} - ${data.disease}</h4>
                                <span class="badge bg-${statusColor}">Confidence: ${(data.confidence * 100).toFixed(0)}%</span>
                            </div>
                        </div>
                        <div class="bg-light p-3 rounded-3 mt-2">
                            <h6><i class="bi bi-life-preserver me-2 text-primary"></i>Action Plan & Treatment:</h6>
                            <p class="mb-0 text-muted small">${data.recommendation}</p>
                        </div>
                    </div>
                `);
            } else {
                alert(data.message || "Detection failed.");
            }
        } catch (err) {
            loader.classList.add("d-none");
            alert("File upload failed.");
        }
    });
}

// =====================================================
// 6. Reports & Export Page Logic
// =====================================================
async function initReportsPage() {
    // Populate reports summary logs
    try {
        const res = await apiFetch("/api/dashboard/stats");
        const data = await res.json();
        
        const logBody = document.getElementById("reportLogBody");
        if (!logBody) return;
        logBody.innerHTML = "";
        
        if (data.recent_predictions.length === 0) {
            logBody.innerHTML = `<tr><td colspan="5" class="text-center text-muted">No logs recorded yet. Run predictions or register farms to generate data.</td></tr>`;
        }
        
        data.recent_predictions.forEach(p => {
            const date = formatDate(p.created_at);
            const type = p.prediction_type.replace("_", " ").title();
            
            let summary = "";
            for (let [k, v] of Object.entries(p.outputs)) {
                summary += `${k.replace("_", " ").title()}: ${v} | `;
            }
            summary = summary.slice(0, -3); // trim trailing divider
            
            logBody.innerHTML += `
                <tr>
                    <td>${date}</td>
                    <td><span class="badge bg-success">${type}</span></td>
                    <td>${summary}</td>
                    <td>${p.confidence ? (p.confidence * 100) + "%" : "N/A"}</td>
                    <td><span class="text-muted text-break small">${JSON.stringify(p.inputs)}</span></td>
                </tr>
            `;
        });
    } catch (err) {
        console.error("Failed to load prediction history", err);
    }
    
    // Bind buttons for download exports
    const exportBtns = document.querySelectorAll(".export-btn");
    exportBtns.forEach(btn => {
        btn.addEventListener("click", async (e) => {
            e.preventDefault();
            const format = btn.getAttribute("data-format");
            const type = btn.getAttribute("data-type");
            
            const url = `/api/reports/export?format=${format}&report_type=${type}`;
            const ext = format === "excel" ? "xlsx" : format;
            const filename = `agrinova_${type}_report.${ext}`;
            
            await downloadReport(url, filename);
        });
    });
}

// =====================================================
// 7. User Profile Logic
// =====================================================
async function initProfilePage() {
    try {
        const res = await apiFetch("/api/auth/profile");
        const data = await res.json();
        
        if (data.success) {
            const u = data.user;
            document.getElementById("profileName").textContent = u.full_name;
            document.getElementById("profileEmail").textContent = u.email;
            document.getElementById("profilePhone").textContent = u.phone || "Not Configured";
            document.getElementById("profileRegistered").textContent = formatDate(u.created_at);
            document.getElementById("profileVerified").innerHTML = u.is_verified 
                ? `<span class="badge bg-success"><i class="bi bi-patch-check-fill me-1"></i> Verified Account</span>` 
                : `<span class="badge bg-warning text-dark"><i class="bi bi-exclamation-circle me-1"></i> Unverified Account</span>`;
        }
    } catch (err) {
        console.error(err);
    }

    // Change Password Form submit
    const pwForm = document.getElementById("changePasswordForm");
    if (pwForm) {
        pwForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            
            // Generate a reset link via forgot-password using current email
            const user = JSON.parse(localStorage.getItem("user_info"));
            const alertBox = document.getElementById("profileAlert");
            
            try {
                // Generate token
                const tokenRes = await fetch("/api/auth/forgot-password", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email: user.email })
                });
                const tokenData = await tokenRes.json();
                
                if (tokenData.success && tokenData.token) {
                    // Apply new password
                    const newPassword = document.getElementById("newPassword").value;
                    const applyRes = await fetch("/api/auth/reset-password", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ token: tokenData.token, new_password: newPassword })
                    });
                    const applyData = await applyRes.json();
                    
                    if (applyData.success) {
                        alertBox.textContent = "Password updated successfully.";
                        alertBox.className = "alert alert-success";
                        alertBox.classList.remove("d-none");
                        pwForm.reset();
                    } else {
                        alertBox.textContent = applyData.message;
                        alertBox.className = "alert alert-danger";
                        alertBox.classList.remove("d-none");
                    }
                } else {
                    alertBox.textContent = "Failed to initiate password change.";
                    alertBox.className = "alert alert-danger";
                    alertBox.classList.remove("d-none");
                }
            } catch (err) {
                alertBox.textContent = "Network connection failed.";
                alertBox.className = "alert alert-danger";
                alertBox.classList.remove("d-none");
            }
        });
    }
}
