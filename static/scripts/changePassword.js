flash = document.querySelector(".error-flash");
otpBut = document.getElementById("Send-Otp");
submit = document.getElementById("submit");
otp = document.getElementById("OTP");
otpinput = document.getElementById("OTP-input");
newPass = document.getElementById("New-Password");
confirPass = document.getElementById("Comfirm-Password");
user = document.getElementById("Username");
eye = document.getElementById("password");
const form = document.getElementById("Form_");
const msg = document.querySelector(".error-flash");
var typingTimer;
var doneTypingInterval = 1000;
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
eye.onclick = function () {
  showpassword("password");
};
otpBut.onclick = function () {
  send_otp();
};
async function send_otp() {
  if (form.checkValidity()) {
    if (confirPass.value !== newPass.value) {
      var errorMessage = "Passwords don't match";
      flash.innerText = errorMessage;
      return false;
    }
    // flash.innerText='{% if messages%} {{messages[-1]}} {% endif %}'
    // prettier-ignore
    User = { 'username': user.value ,'password':newPass.value};
    const response = await fetch("/changePassword/generateotp/", {
      method: "POST",
      headers: { "Content-Type": "application/json;charset=UTF-8" },
      body: JSON.stringify(User),
    });
    result = await response.json();
    if (result.generated) {
      processing();
    } else {
      flash.innerText = result.error;
    }
  } else {
    form.reportValidity();
  }
}
function processing() {
  //   flash.innerText = "{% if messages%} {{messages[-1]}} {% endif %}";
  otpBut.hidden = true;
  otp.style.display = "flex";
  submit.hidden = false;
  otpinput.required = true;
}
async function otpVerification() {
  if (!form.checkValidity()) {
    form.reportValidity();
    return False;
  }

  const response = await fetch("/changePassword/otpvalidation/", {
    method: "POST",
    headers: { "Content-Type": "application/json;charset=UTF-8" },
    //prettier-ignore
    body: JSON.stringify({'password':newPass.value,'OTP':otpinput.value,'username':user.value}),
  });
  result = await response.json();
  if (result.changed) {
    window.close();
  } else {
    flash.innerText = result.error;
    return false;
  }
}
newPass.onblur = function () {
  if (newPass.value !== "") {
    invalid_password(newPass.value);
  }
};
newPass.addEventListener("input", function () {
  if (newPass.value != "") {
    clearTimeout(typingTimer);
    typingTimer = setTimeout(function () {
      invalid_password(newPass.value);
    }, doneTypingInterval);
  }
});
function invalid_password(password) {
  var result = passwordCheck(password);

  if (!result.valid) {
    otpBut.disabled = true;
    if (result.message === "") {
      msg.textContent = "Password must be at least 8 characters long.";
    } else {
      msg.textContent =
        "Password is Missing " +
        result.message.slice(0, result.message.length - 2);
    }
    otpBut.disabled = true;
    return false;
  } else {
    msg.textContent = "";
    otpBut.disabled = false;
    return true;
  }
}
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
function matchCheck() {
  if (newPass.value !== confirPass.value) {
    msg.textContent = "Passwords do not match";
    otpBut.disabled = true;
  } else {
    msg.textContent = "";
    invalid_password(newPass.value);
    otpBut.disabled = false;
  }
}
confirPass.onblur = function () {
  if (confirPass.value !== "") {
    matchCheck();
  }
};
confirPass.addEventListener("input", function () {
  if (confirPass.value != "") {
    clearTimeout(typingTimer);
    typingTimer = setTimeout(matchCheck, doneTypingInterval);
  }
});
