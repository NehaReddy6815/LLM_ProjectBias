async function analyzePrompt() {
    const prompt = document.getElementById("prompt").value.trim();
    if (!prompt) {
      alert("Please enter a prompt!");
      return;
    }
  
    document.getElementById("loading").style.display = "block";
    document.getElementById("results").style.display = "none";
  
    try {
      const response = await fetch("http://127.0.0.1:5001/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });
  
      const data = await response.json();
      document.getElementById("loading").style.display = "none";
  
      if (response.ok) {
        showResults(data);
      } else {
        alert("Error: " + (data.error || "Unexpected backend issue."));
      }
    } catch (err) {
      document.getElementById("loading").style.display = "none";
      alert("❌ Failed to connect to backend: " + err);
    }
  }
  
  function showResults(data) {
    document.getElementById("results").style.display = "block";
    document.getElementById("bias_category").innerText = data.bias_category.join(", ");
    document.getElementById("bias_score").innerText = data.bias_score;
    document.getElementById("original").innerText = data.original;
    document.getElementById("corrected").innerText = data.corrected;
  
    const correctionsList = document.getElementById("corrections");
    correctionsList.innerHTML = "";
    (data.corrections || []).forEach(corr => {
      const li = document.createElement("li");
      li.textContent = corr;
      correctionsList.appendChild(li);
    });
  
    const ctx = document.getElementById("biasChart").getContext("2d");
    if (window.biasChartInstance) window.biasChartInstance.destroy();
    window.biasChartInstance = new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: ["Bias Score", "Remaining"],
        datasets: [{
          data: [data.bias_score * 100, 100 - data.bias_score * 100],
          backgroundColor: ["#f87171", "#d1d5db"]
        }]
      },
      options: { responsive: true, plugins: { legend: { position: "bottom" } } }
    });
  }
  