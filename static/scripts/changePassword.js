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
flash = document.querySelector(".error-flash");
otpBut = document.getElementById("Send-Otp");
submit = document.getElementById("submit");
otp = document.getElementById("OTP");
otpinput = document.getElementById("OTP-input");
newPass = document.getElementById("New-Password");
confirPass = document.getElementById("Comfirm-Password");

const form = document.getElementById("Form_");
console.log(form);
async function send_otp() {
  console.log(form);
  if (form.checkValidity()) {
    if (confirPass.value !== newPass.value) {
      var errorMessage = "Passwords don't match";
      flash.innerText = errorMessage;
      return false;
    }
    // flash.innerText='{% if messages%} {{messages[-1]}} {% endif %}'
    const request = new XMLHttpRequest();

    request.open("POST", "/changePassword/generateotp/");
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    user = document.getElementById("Username");
    // prettier-ignore
    user = { 'username': user.value ,'password':newPass.value};
    request.send(JSON.stringify(user));
    request.onload = function () {
      response = JSON.parse(request.responseText);
      if (response.generated) {
        processing();
      } else {
        flash.innerText = response.error;
      }
    };
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
function otpVerification() {
  if (!form.checkValidity()) {
    form.reportValidity();
    return False;
  }
  if (confirPass.value !== newPass.value) {
    var errorMessage = "Passwords don't match";
    flash.innerText = errorMessage;
    return false;
  }
  const request = new XMLHttpRequest();
  request.open("POST", "/changePassword/otpvalidation/");
  request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  user = document.getElementById("Username");
  // prettier-ignore
  request.send(JSON.stringify({'password':newPass.value,'OTP':otpinput.value,'username':user.value}))
  request.onload = function () {
    var response = JSON.parse(request.responseText);
    if (response.changed) {
      window.close();
    } else {
      flash.innerText = response.error;
      return false;
    }
  };
}
