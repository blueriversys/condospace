/*
   This is invoked by announcs.html to handle announcement related operations.
   Also used by announcs.html to load announcements, loadAnnouncs()
*/

/* invoked by announcs.html */
function onLoadAction() {
    window.loggedin_id_global = document.getElementById('loggedin-id').value;
    window.loggedin_userid_global = document.getElementById('loggedin-userid').value;
    window.loggedin_unit_global = document.getElementById('loggedin-unit').value;
    window.loggedin_name_global = document.getElementById('loggedin-name').value;
    window.loggedin_tenant_global = document.getElementById('loggedin-tenant').value.trim();
    window.loggedin_lang_global = document.getElementById('loggedin-lang').value;
    //loadAnnouncs();
}

function loadAnnouncs() {
    var request = new XMLHttpRequest()
    request.open('GET', '/getannouncs', true)
    
    request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);
      
      if (request.status >= 200 && request.status < 400) {
          var ul = document.getElementById("announc-list");
          for (var i=0; i<json.announcs.length; i++) {
              var li = document.createElement("li");
              li.appendChild(document.createTextNode('example li'));
              ul.appendChild(li);
              li.innerHTML = json.announcs[i];
          }            
      } 
      else {
          alert('Error retrieving announcements list');
      }
        
    }    
  
    request.send();
}

