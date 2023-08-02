var counter = 1;
var limit = 3;
function addInput(divName){
     if (counter == limit)  {
          alert("You have ONE reached the limit of adding " + counter + " inputs");
     }
     else {
          var newdiv = document.createElement('tr');
          newdiv.innerHTML = "Entry " + (counter + 1) + " <br><input type='text' name='myInputs[]'>";
          document.getElementById(divName).appendSibling(newdiv);
          counter++;
     }
}
