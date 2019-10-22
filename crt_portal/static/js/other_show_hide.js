var otherbox = document.getElementById("other-class-option");
otherbox.setAttribute("hidden","");

var otherCheck = document.querySelectorAll('.' + 'usa-checkbox').item(11);
var otherCheckID = document.querySelectorAll('.' + 'usa-checkbox__input').item(11).id;

function checkOther(elem){
  var checkBox = document.querySelectorAll('.' + 'usa-checkbox__input').item(11);
  var otherArea = document.getElementById("other-class-option");
  if (checkBox.checked == true){
    otherArea.removeAttribute('hidden');
  } else {
    otherArea.setAttribute('hidden', '');
  }
}

otherCheck.setAttribute("onclick","checkOther(otherCheckID);");

window.selectionchange = checkOther(document.querySelectorAll('.' + 'usa-checkbox__input').item(11).id);