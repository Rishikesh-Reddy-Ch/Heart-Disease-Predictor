const inputs = document.querySelectorAll(".input");

// function addcl() {
//   let parent = this.parentNode.parentNode;
//   parent.classList.add("focus");
// }

// function remcl() {
//   let parent = this.parentNode.parentNode;
//   if (this.value == "") {
//     parent.classList.remove("focus");
//   }
// }

// inputs.forEach((input) => {
//   input.addEventListener("focus", addcl);
//   input.addEventListener("blur", remcl);
// });

function showpassword(name) {
  const passInput = document.querySelector('input[name="' + name + '"]');
  // console.log(passInput);
  const icon = document.getElementById(name);
  if (passInput.type == "password") {
    passInput.type = "text";
    icon.classList.remove("fa-eye-slash");
    icon.classList.add("fa-eye");

    icon.style.marginLeft = "2px";
  } else {
    passInput.type = "password";
    icon.classList.remove("fa-eye");
    icon.classList.add("fa-eye-slash");
    icon.style.marginLeft = "0px";
  }
}
const submit = document.getElementById("submitbtn");
const form = document.getElementById("form");
user = document.getElementById("Username");
var typingTimer;
var doneTypingInterval = 1000;
user.onblur = function () {
  Id_available();
};
async function Id_available() {
  if (user.value != "") {
    let response = await fetch("/register/usercheck/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json;charset=UTF-8",
      },
      // prettier-ignore
      body: JSON.stringify({ 'UserID': user.value }),
    });
    const result = await response.json();
    Id_msg = document.getElementById("Id_msg");
    if (!result.valid && !result.msg) {
      Id_msg = document.getElementById("Id_msg");
      submit.disabled = true;
      Id_msg.hidden = false;
      return false;
    } else {
      Id_msg.hidden = true;
      submit.disabled = false;
      return true;
    }
  }
}
user.addEventListener("input", function () {
  clearTimeout(typingTimer);
  typingTimer = setTimeout(Id_available, doneTypingInterval);
});
const pass = document.getElementById("password-input");
pass.addEventListener("input", function () {
  clearTimeout(typingTimer);
  typingTimer = setTimeout(function () {
    invalid_password(pass.value);
  }, doneTypingInterval);
});
pass.onblur = function () {
  invalid_password(pass.value);
};
function passwordCheck(password) {
  let message = "";
  let valid = true;

  if (password.length < 8) {
    valid = false;
    return { valid, message };
  }

  if (!/[A-Z]/.test(password)) {
    valid = false;
    message += "Uppercase, ";
  }

  if (!/[a-z]/.test(password)) {
    valid = false;
    message += "Lowercase, ";
  }

  if (!/\d/.test(password)) {
    valid = false;
    message += "Digit, ";
  }

  if (!/\W/.test(password)) {
    valid = false;
    message += "Special-Char, ";
  }
  // console.log(valid);
  return { valid, message };
}
const msg = document.querySelector(".error-flash");
function invalid_password(password) {
  var result = passwordCheck(password);
  // console.log(passwordCheck(password));
  // console.log(result);
  if (!result.valid) {
    submit.disabled = true;
    if (result.message === "") {
      msg.textContent = "Password must be at least 8 characters long.";
    } else {
      msg.textContent =
        "Password is Missing " +
        result.message.slice(0, result.message.length - 2);
    }
    return false;
  } else {
    msg.textContent = "";
    submit.disabled = false;
    return true;
  }
}
function isValidDateAndPast(dateString) {
  const currentDate = new Date();
  const inputDate = new Date(dateString);
  return currentDate > inputDate;
}
function dobCheck() {
  if (!dob.checkValidity()) dob.reportValidity();
  else {
    if (!isValidDateAndPast(dob.value)) {
      msg.textContent = " Please provide the correct date of birth.";
      submit.disabled = true;
      return false;
    } else {
      msg.textContent = "";
      submit.disabled = false;
      return true;
    }
  }
}
const dob = document.getElementById("DOB");
dob.onblur = function () {
  dobCheck();
};
form.addEventListener("submit", async function (event) {
  event.preventDefault();

  const isUsernameValid = await Id_available();
  const isPasswordValid = passwordCheck(pass.value);
  const isDOBValid = dobCheck();

  if (!isUsernameValid || !isPasswordValid || !isDOBValid) {
    return;
  }

  form.submit();
});
