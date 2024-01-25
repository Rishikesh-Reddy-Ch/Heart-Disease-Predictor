async function openMaps() {
  // event.preventDefault(); // Prevent the default form submission behavior
  const form = document.querySelector("form");

  if (!form.checkValidity()) {
    alert("Enter valid postal code");
    return false;
  }

  const pinCode = document.getElementById("user-address").value;

  try {
    const response = await fetch("/address_check/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json;charset=UTF-8",
      },
      body: JSON.stringify({ "pin-code": pinCode }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const result = await response.json();
    redirect(result.valid, pinCode);
  } catch (error) {
    console.error("Error:", error);
  }
}

function redirect(response, pin_code) {
  if (response) {
    const location = encodeURIComponent("cardiac hospitals near " + pin_code);

    // Open Google Maps in a new tab
    window.location.href = "https://www.google.com/maps?q=" + location;
  } else {
    alert("Enter valid postal-Code");
  }
}

function Dietary_plans() {
  const followDietPlanCheckbox = document.getElementById("follow-diet-plan");
  const dietaryInput = document.querySelector(".dietary-input");

  if (followDietPlanCheckbox.checked) {
    dietaryInput.style.display = "block";
  } else {
    dietaryInput.style.display = "none";
  }
}
submit = document.getElementById("submit");
if (submit) {
  submit.addEventListener("click", async function (event) {
    event.preventDefault();
    stored = await storeDiet();
    if (stored) {
      setTimeout(function () {
        document.getElementById("h1").style.display = "none";
        document.getElementById("dietary-form").style.display = "none"; // Hide the form
        document.getElementById("confirmation-message").style.display = "block"; // Show confirmation message
      }, 1000);
    } else {
      alert("Cannot access database");
    }
  });
}

async function storeDiet() {
  const input = document.getElementById("dietary-plans");
  response = await fetch("/dietStore/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json;charset=UTF-8",
    },
    //console.log(input.value);
    body: JSON.stringify({ dietStore: input.value }),
  });
  const result = await response.json();
  if (result.stored) return true;
  return false;
}
document.addEventListener("DOMContentLoaded", function () {
  const progressContainer = document.querySelector(".progress-container");
  setPercentage(progressContainer);
  if (progressContainer.getAttribute("prediction") == "High") {
    button = document.querySelector(".DietPlanBut");
    button.onclick = function () {
      document.getElementById("KeyRecommendationsText").hidden = false;
      document.querySelector(".loading-container").hidden = false;
      button.hidden = true;
      dietRequest();
    };
  } else if (progressContainer.getAttribute("prediction") == "Medium") {
    dietRequest();
  }
});
function setPercentage(progressContainer) {
  const percentage = progressContainer.getAttribute("data-percentage") + "%";

  const progressEl = progressContainer.querySelector(".progress");
  const percentageEl = progressContainer.querySelector(".percentage");

  progressEl.style.width = percentage;
  percentageEl.innerText = percentage;
  percentageEl.style.left = percentage;
}
async function dietRequest() {
  request = await fetch("/result/requestDietPlan/");
  dietplandiv = document.getElementById("KeyRecommendations");
  result = await request.json();
  document.querySelector(".loading-container").hidden = true;

  if (result.retrived) {
    dietplandiv.innerHTML = result.dietplan;
  } else {
    dietplandiv.textContent = "Encontered an error";
  }
}
