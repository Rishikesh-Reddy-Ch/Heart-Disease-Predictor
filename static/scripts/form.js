function unlock(block_id, input_id, conditionalEle_id, defaoutValue, max) {
  block = document.getElementById(block_id);
  input = document.getElementById(input_id);
  conditionalEle = document.getElementById(conditionalEle_id);
  if (conditionalEle.value === "1") {
    block.hidden = false;
    if (input.value === defaoutValue) input.value = "";
    input.max = max;
    input.required = true;
  } else {
    block.hidden = true;
    input.value = defaoutValue;
    input.max = null;
    input.required = false;
  }
}
ispoorhealth = document.getElementById("poorhealth");
diabetes = document.getElementById("diabetesInput");
ispoorhealth.onclick = function () {
  unlock("poorhealthinputblock", "poorhealthinput", "poorhealth", "88", "30");
};
diabetes.onclick = function () {
  unlock(
    "diabetesAgeInputBlock",
    "diabetesAgeInput",
    "diabetesInput",
    "999",
    "97"
  );
};
//var form1 = document.getElementById("form1");
var progress = document.getElementById("progress");
function Loginredirect() {
  if (document.querySelector(".btn-login").textContent == "Logout") {
    window.location.href = "{{url_for('logout')}}";
  }
}
function vesselqnUnlock() {
  const input = document.getElementById("major-vessels");
  const label = document.getElementById("major-vessels-label");
  if (document.getElementById("coronaryAngiography").value == "1") {
    input.hidden = false;
    label.hidden = false;
    input.required = true;
  } else {
    input.hidden = true;
    label.hidden = true;
    input.required = false;
  }
}
function oldpeak_Unlock() {
  const input1 = document.getElementById("ST-at-stress");
  const input2 = document.getElementById("ST-at-rest");
  const label1 = document.getElementById("ST-at-stress-label");
  const label2 = document.getElementById("ST-at-rest-label");
  if (document.getElementById("oldpeak_unlock").value == "1") {
    input1.hidden = false;
    label1.hidden = false;
    input1.required = true;
    input2.required = true;
    label2.hidden = false;
    input2.hidden = false;
  } else {
    input1.hidden = true;
    label1.hidden = true;
    input1.required = false;
    input2.required = false;
    label2.hidden = true;
    input2.hidden = true;
  }
}
// function bpCal() {
//   ele = document.getElementById("highBloodPressureInput");
//   if(ele.checkValidity()){

//   }
// }
