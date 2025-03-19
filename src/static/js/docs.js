
function onLoadAction() {
    window.loggedin_id_global = document.getElementById('loggedin-id').value;
    window.loggedin_userid_global = document.getElementById('loggedin-userid').value;
    window.loggedin_unit_global = document.getElementById('loggedin-unit').value;
    window.loggedin_name_global = document.getElementById('loggedin-name').value;
    window.loggedin_tenant_global = document.getElementById('loggedin-tenant').value.trim();
    window.loggedin_lang_global = document.getElementById('loggedin-lang').value;
}

/* invoked from docs.html */
function uploadFinStatement() {
    month = document.getElementById("rep-month").value.trim();
    year = document.getElementById("rep-year").value.trim();
    if (month.length > 2 || year.length != 4) {
        showMsgBox( gettext("The size of your Month or Year field is incorrect.") );
        return;
    }

    month = parseInt(month, 10);
    if (month > 12 || month < 1) {
        showMsgBox( gettext("The Month field is incorrect. Please fix it.") );
        return;
    }

    if (month < 10) {
        month = '0' + month;
    }

    rep_name = year + '-' + month;
    var varMap = new Map();
    varMap.set('year', year);
    varMap.set('month', month);
    uploadFileProgressEnh(varMap, 'rep-file', 'rep-progress-bar')
}

function uploadFileProgressEnh(varMap, fileControl, barControl) {
    // retrieve the file object from the DOM
    let file = document.getElementById(fileControl).files[0];

    // test to make sure the user chose a file
    if (file == undefined || file == "") {
        showMsgBox( gettext('Please select a file before clicking the upload button.') );
        return;
    }

    //print file details
    console.log("File Name : ",file.name);
    console.log("File size : ",file.size);
    console.log("File type : ",file.type);

    // create form data to send via XHR request
    var formData = new FormData();
    formData.append("file", file);
    formData.append("filesize", ''+file.size); // append only takes string as 2nd arg

    // read and print all varMap's key and value
    for ( const key of varMap.keys() ) {
        formData.append( key, varMap.get(key) );
    }

    //create XHR object to send request
    var request = new XMLHttpRequest();

    var progressBar = document.getElementById(barControl);
    progressBar.value = 0;
    progressBar.style.display="inline";

    // add a progress event handler to the AJAX request
    request.upload.addEventListener('progress', event => {
        let totalSize = event.total; // total size of the file in bytes
        let loadedSize = event.loaded; // loaded size of the file in bytes
        // calculate percentage
        var percent = (event.loaded / event.total) * 100;
        progressBar.value = Math.round(percent);
    });

    // initializes a newly-created request
    post_url = "/" + window.loggedin_tenant_global + "/upload_financial";
    request.open('POST', post_url, true);

    // ask to be notified when the upload is finished
    request.onreadystatechange = () => {
        if (request.readyState == 4 && request.status == 200) {
            progressBar.value = 100;
            showMsgBoxSuccess( gettext('File') + ' ' + file.name + ' ' + gettext('successfully uploaded') );
            progressBar.style.display="none";
            location.reload(true);
        }
    };

    // send request to the server
    request.send(formData);
}

function deleteFinDocsGroup(year) {
    resp = confirm('Are you sure you want to delete entire group for year' + ' ' + year);

    if ( !resp ) {
        return;
    }

    var request = new XMLHttpRequest();
    post_url = "/" + window.loggedin_tenant_global + "/delete_fin_doc_group";
    request.open('POST', post_url, true);

    request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);

      if (request.status >= 200 && request.status < 400) {
          if (json.response.status == 'success') {
              showMsgBoxSuccess( gettext('Group deleted from database') );
          }
          else {
              showMsgBox( gettext('Error deleting group from database') );
          }
      }
      else {
          showMsgBox( gettext('Error deleting group from database') );
      }

      location.reload();
    }

    var requestObj = new Object();
    requestObj.tenant = window.loggedin_tenant_global;
    requestObj.user_id = window.loggedin_userid_global;
    requestObj.year = year;

    // const person = {firstName:"John", lastName:"Doe", age:50, eyeColor:"blue"};
    jsonStr = '{ "request": ' + JSON.stringify(requestObj) + '}';
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(jsonStr);
}

function deleteFile(filepath, filename, protected) {
    deleteFileCommon(filepath, filename, protected);
}

// Description of the link is the key
function deleteLink(link_descr) {
    // here we make a request to "upload_link"
    var request = new XMLHttpRequest();
    post_url = "/" + window.loggedin_tenant_global + "/delete_link";
    request.open('POST', post_url, true);

    request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);

      if (request.status >= 200 && request.status < 400) {
          if (json.response.status == 'error') {
              showMsgBox( gettext('Error uploading a new link') );
          }
          else {
              showMsgBoxSuccess( gettext("Link") + " '" + link_descr + "' " + gettext("deleted from the list") ) ;
              location.reload();
          }
      }
      else {
          showMsgBox( gettext('Error deleting the link') );
      }

      return;
    }

    var requestObj = new Object();
    requestObj.tenant = window.loggedin_tenant_global;
    requestObj.link_descr = link_descr;
    jsonStr = '{ "request": ' + JSON.stringify(requestObj) + '}';
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(jsonStr);
}

