document.addEventListener("DOMContentLoaded", function () {
  // Transcript form submission
  const transcriptForm = document.getElementById("transcript-form");
  if (transcriptForm) {
    transcriptForm.addEventListener("submit", function (e) {
      e.preventDefault();

      // Get form data
      const companyName = document.getElementById("company-name").value;
      const ticker = document.getElementById("ticker").value.toUpperCase();
      const quarter = document.getElementById("quarter").value;
      const year = document.getElementById("year").value;
      const callDate = document.getElementById("call-date").value;
      const rawText = document.getElementById("transcript-text").value;

      // Show loading state
      const submitButton = this.querySelector('button[type="submit"]');
      const originalButtonText = submitButton.textContent;
      submitButton.textContent = "Processing...";
      submitButton.disabled = true;

      // Submit data to API
      fetch("/api/process-transcript", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          company_name: companyName,
          ticker: ticker,
          quarter: quarter,
          year: parseInt(year),
          call_date: callDate,
          raw_text: rawText,
        }),
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error("Network response was not ok");
          }
          return response.json();
        })
        .then((data) => {
          // Display results
          document.getElementById("summary-text").textContent = data.summary;

          let sentimentText = "";
          if (data.sentiment_score > 0.05) {
            sentimentText = `Positive sentiment (${data.sentiment_score.toFixed(
              2
            )})`;
          } else if (data.sentiment_score < -0.05) {
            sentimentText = `Negative sentiment (${data.sentiment_score.toFixed(
              2
            )})`;
          } else {
            sentimentText = `Neutral sentiment (${data.sentiment_score.toFixed(
              2
            )})`;
          }

          document.getElementById("sentiment-text").textContent = sentimentText;
          document.getElementById(
            "view-full-link"
          ).href = `/transcript/${data.id}`;
          document.getElementById("processing-result").style.display = "block";

          // Reset form
          transcriptForm.reset();
        })
        .catch((error) => {
          console.error("Error:", error);
          alert("Error processing transcript: " + error.message);
        })
        .finally(() => {
          // Restore button state
          submitButton.textContent = originalButtonText;
          submitButton.disabled = false;
        });
    });
  }

  // Company search functionality
  const companySearchForm = document.querySelector('form[action="/company"]');
  if (companySearchForm) {
    companySearchForm.addEventListener("submit", function (e) {
      const tickerInput = this.querySelector('input[name="ticker"]');
      if (!tickerInput.value.trim()) {
        e.preventDefault();
        alert("Please enter a ticker symbol");
      } else {
        tickerInput.value = tickerInput.value.trim().toUpperCase();
      }
    });
  }
});
