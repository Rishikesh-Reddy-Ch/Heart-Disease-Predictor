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
const submit=document.getElementById("submitbtn");
const form=document.getElementById("form");
user = document.getElementById("Username");
var typingTimer;
var doneTypingInterval = 1000;
user.onblur = function () {
  Id_available();
};
 async function Id_available() {
  if (user.value != "") {
    const response = await fetch("/register/usercheck/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json;charset=UTF-8",
      },
      body: JSON.stringify({ "UserID": user.value }),
    });
    const result = await response.json();
    Id_msg=document.getElementById("Id_msg");
    if (!result.valid && !result.msg) {
      Id_msg=document.getElementById("Id_msg");
      msg=document.querySelector(".error-flash");
      submit.disabled=true;
      // submit.style.filter="blur(1px)";
      // if (result.msg!==""){
      //   msg.textContent=result.msg;
      //   // console.log(textContent)
      //   return false;
      Id_msg.hidden=false;
      return false;
      }
        // msg.textContent='{% if messages%} {{messages[-1]}} {% endif %}'
    else{
      Id_msg.hidden=true;
      submit.disabled=false;
      return true;    
    }
  }
};
user.addEventListener('input', function() {
  // Clear the previous timer
  clearTimeout(typingTimer);

  // Set a new timer to check availability after the user stops typing
  typingTimer = setTimeout(Id_available, doneTypingInterval);
});

submit.onclick=async function(){
  if(!form.checkValidity()){
    form.reportValidity();
    return false;
  }
  if (await Id_available()){
    
    form.submit();
  }
  else{
    return false;

  }
}
