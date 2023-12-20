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
