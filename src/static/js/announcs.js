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

/*
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
*/


function saveAnnounc(type) {
    user_id = loggedin_userid_global;
    if (type == '1') {
        announc_text = document.getElementById("ad_text").value.trim();
        attach_file = document.getElementById('ad_file').files[0];
    }
    else
    if (type == '0') {
        announc_text = document.getElementById("announc_text").value.trim();
        attach_file = document.getElementById('announc_file').files[0];
    }
    else {
        showMsgBox( gettext('Announcement type is unrecognized') );
        return;
    }

    if ( announc_text.length == 0) {
        showMsgBox( gettext('Text is a required field') );
        return;
    }

    if (attach_file != undefined) {
        file_name = attach_file.name;
    }
    else {
        file_name = '';
    }

    var request = new XMLHttpRequest();
    request.open('POST', `/${window.loggedin_tenant_global}/save_announc`, true);

    showSpinner();

    request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);

      if (request.status >= 200 && request.status < 400) {
          if (json.response.status == 'success') {
              //showMsgBoxSuccess( gettext('Record saved to database') );
          }
          else {
              showMsgBox( gettext('Error saving record to database') );
          }
      }
      else {
          showMsgBox( gettext('Error saving record to database') );
      }

      location.reload();
    }

    // create form data to send via XHR request
    var formData = new FormData();
    formData.append('tenant', loggedin_tenant_global);
    formData.append('created_by', user_id);
    formData.append('text', announc_text);
    formData.append("attach_file_name", file_name); // will be empty if no file was chosen
    formData.append("attach_file", attach_file);
    formData.append("announc_type", type);

    // send request to the server
    request.send(formData);
}

function displayImageFile(file_name, img_control) {
    var reader = new FileReader();
    reader.readAsDataURL(file_name);
    reader.onload = function (e) {
        var image = new Image();
        image.src = e.target.result;
        image.onload = function () {
            document.getElementById(img_control).src = image.src;
            document.getElementById(img_control).style.display = 'block';
        };
    }
}

function get_file_extension(file_name) {
    ind = file_name.indexOf('.');
    if (ind < 0) {
        return '';
    }

    file_ext = file_name.substring(ind);
    return file_ext;
}

function pictureSelectAction(img_file_control, img_control) {
    file = document.getElementById(img_file_control).files[0];
    file_name = file.name;
    console.log('file name: '+file_name);
    file_ext = get_file_extension(file_name);

    if (file_ext == '.jpg' || file_ext == '.png') {
        displayImageFile(file, img_control);
        // show the file name
        document.getElementById("announc_file_name").textContent = file_name;
    }
    else {
        if ( file_ext == '.pdf' ) {
            file_name = '/common/img/file_format_sm_pdf_red.png';
        }
        else
        if ( file_ext == '.txt' ) {
            file_name = '/common/img/file_format_sm_txt_black.png';
        }
        else
        if ( file_ext == '.doc' ) {
            file_name = '/common/img/file_format_sm_doc_blue.png';
        }

        document.getElementById(img_control).src = file_name;
        document.getElementById(img_control).style.display = 'block';
        document.getElementById("announc_file_name").textContent = '';
    }
}

function deleteAnnounc(announc_id) {
    // here we make a request to "delete_announc"
    var request = new XMLHttpRequest();
    request.open('POST', `/${window.loggedin_tenant_global}/delete_announc`, true);

    showSpinner();

    request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);

      if (request.status >= 200 && request.status < 400) {
          if (json.response.status == 'success') {
              location.reload();
              return;
          }
      }

      showMsgBox( gettext('Error executing this action') );
      return;
    }

    var requestObj = new Object();
    requestObj.tenant = window.loggedin_tenant_global;
    requestObj.user_id = window.loggedin_userid_global;
    requestObj.announc_id = announc_id;
    jsonStr = '{ "announc": ' + JSON.stringify(requestObj) + '}';
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(jsonStr);
}

function sendEmailToResidents(announc_id) {
    // here we make a request to "delete_announc"
    var request = new XMLHttpRequest();
    request.open('POST', `/${window.loggedin_tenant_global}/email_announc`, true);

    showSpinner();

    request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);

      if (request.status >= 200 && request.status < 400) {
          if (json.response.status == 'success') {
              location.reload();
              return;
          }
      }

      showMsgBox( gettext('Error executing this action') );
      return;
    }

    var requestObj = new Object();
    requestObj.tenant = window.loggedin_tenant_global;
    requestObj.user_id = window.loggedin_userid_global;
    requestObj.announc_id = announc_id;
    jsonStr = '{ "announc": ' + JSON.stringify(requestObj) + '}';
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(jsonStr);
}

