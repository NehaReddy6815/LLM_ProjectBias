let categoryChartInstance = null;
let biasChartInstance = null;


// Tab switching
function showTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName + '-tab').classList.add('active');
    event.target.classList.add('active');
    
    // Load data when switching tabs
    if (tabName === 'history') {
        loadHistory();
    } else if (tabName === 'stats') {
        loadStats();
    }
}

// Original analyze function
async function analyzePrompt() {
    const prompt = document.getElementById("prompt").value.trim();
    if (!prompt) {
        alert("Please enter a prompt.");
        return;
    }

    document.getElementById("loading").style.display = "block";
    document.getElementById("results").style.display = "none";

    try {
        const response = await fetch("http://localhost:5001/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt }),
        });

        const data = await response.json();

        if (data.error) {
            alert("Error: " + data.error);
            return;
        }

        document.getElementById("original").innerText = data.original;
        document.getElementById("corrected").innerText = data.corrected;
        document.getElementById("bias_category").innerText = Array.isArray(data.bias_category) 
            ? data.bias_category.join(", ") 
            : data.bias_category;
        document.getElementById("bias_score").innerText = data.bias_score;
        document.getElementById("tx_hash").innerText = data.tx_hash || "N/A";

        const correctionsList = document.getElementById("corrections");
        correctionsList.innerHTML = "";
        if (data.corrections && data.corrections.length > 0) {
            data.corrections.forEach((c) => {
                const li = document.createElement("li");
                li.innerText = c;
                correctionsList.appendChild(li);
            });
        } else {
            correctionsList.innerHTML = "<li>No corrections needed</li>";
        }

        drawBiasChart(data.bias_score);

        document.getElementById("results").style.display = "block";
    } catch (err) {
        alert("Error connecting to server: " + err.message);
    } finally {
        document.getElementById("loading").style.display = "none";
    }
}
function drawBiasChart(biasScore) {
    const ctx = document.getElementById("biasChart").getContext("2d");

    // ✅ If a chart already exists, destroy it first
    if (biasChartInstance) {
        biasChartInstance.destroy();
    }

    biasChartInstance = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: ["Bias Detected", "Unbiased"],
            datasets: [{
                data: [biasScore, 1 - biasScore],
                backgroundColor: ["#ff6384", "#36a2eb"],
            }],
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: "bottom" },
                title: { display: true, text: "Bias Distribution" },
            },
        },
    });
}

   

// Load history
async function loadHistory() {
    document.getElementById("history-loading").style.display = "block";
    document.getElementById("history-list").innerHTML = "";
    
    try {
        const response = await fetch("http://localhost:5001/history");
        const data = await response.json();
        
        if (data.success && data.history.length > 0) {
            let html = "";
            data.history.forEach((record, index) => {
                html += `
                    <div class="history-item">
                        <div class="history-header">
                            <strong>#${index + 1}</strong>
                            <span class="badge ${record.on_chain ? 'badge-success' : 'badge-warning'}">
                                ${record.on_chain ? '⛓️ On-Chain' : '⏳ Pending'}
                            </span>
                        </div>
                        <div class="history-body">
                            <p><strong>Prompt:</strong> ${record.prompt}</p>
                            <p><strong>Output:</strong> ${record.output.substring(0, 150)}...</p>
                            <p><strong>Bias Category:</strong> ${record.bias_category}</p>
                            <p><strong>Bias Score:</strong> ${record.bias_score_before}</p>
                            <p style="font-size: 11px; color: #666;"><strong>Hash:</strong> ${record.full_hash}</p>
                        </div>
                    </div>
                `;
            });
            document.getElementById("history-list").innerHTML = html;
        } else {
            document.getElementById("history-list").innerHTML = "<p>No records found.</p>";
        }
    } catch (err) {
        document.getElementById("history-list").innerHTML = `<p style="color: red;">Error loading history: ${err.message}</p>`;
    } finally {
        document.getElementById("history-loading").style.display = "none";
    }
}

// Load statistics
async function loadStats() {
    document.getElementById("stats-loading").style.display = "block";
    
    try {
        const response = await fetch("http://localhost:5001/stats");
        const data = await response.json();
        
        if (data.success) {
            const stats = data.stats;
            
            document.getElementById("total-records").innerText = stats.total_records;
            document.getElementById("biased-records").innerText = stats.biased_records;
            document.getElementById("avg-bias").innerText = stats.average_bias_score.toFixed(2);
            
            // Draw category chart
            if (stats.top_bias_categories.length > 0) {
                drawCategoryChart(stats.top_bias_categories);
            }
        }
    } catch (err) {
        alert("Error loading statistics: " + err.message);
    } finally {
        document.getElementById("stats-loading").style.display = "none";
    }
}

function drawCategoryChart(categories) {
    const ctx = document.getElementById("categoryChart").getContext("2d");
    
    // Destroy previous chart if exists
    if (categoryChartInstance) {
        categoryChartInstance.destroy();
    }
    
    categoryChartInstance = new Chart(ctx, {
        type: "bar",
        data: {
            labels: categories.map(c => c.category),
            datasets: [{
                label: "Occurrences",
                data: categories.map(c => c.count),
                backgroundColor: "#ff6384",
            }],
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                title: { display: true, text: "Most Common Bias Types" },
            },
            scales: {
                y: { beginAtZero: true }
            }
        },
    });
}

// Load history on page load
window.addEventListener('load', () => {
    // Optional: load history by default
    // loadHistory();
});