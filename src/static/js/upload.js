

function onLoadAction() {
    window.loggedin_id_global = document.getElementById('loggedin-id').value;
    window.loggedin_userid_global = document.getElementById('loggedin-userid').value;
    window.loggedin_unit_global = document.getElementById('loggedin-unit').value;
    window.loggedin_name_global = document.getElementById('loggedin-name').value;
    window.loggedin_tenant_global = document.getElementById('loggedin-tenant').value.trim();
    window.loggedin_lang_global = document.getElementById('loggedin-lang').value;
    document.getElementById("email-progress-bar").style.display = "none";
    fillSystemSettings();
}


function fillSystemSettings() {
    var request = new XMLHttpRequest()
    console.log('tenant global: ${window.loggedin_tenant_global}');
    get_url = `/${window.loggedin_tenant_global}/get_system_settings`;
    request.open('GET', get_url, true)

    request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);
      var pix_key = '';
      var fine_template = '';
      var fine_email_title = '';
      var pay_pix_key = '';
      var pay_template = '';
      var pay_email_title = '';

      if (request.status >= 200 && request.status < 400) {
          if ( 'pix_key' in json ) {
              pix_key = json['pix_key'];
          }

          if ( 'fine_template' in json ) {
              fine_template = json['fine_template'];
          }

          if ( 'fine_title' in json ) {
              fine_email_title = json['fine_title'];
          }

          if ( 'pay_pix_key' in json ) {
              pay_pix_key = json['pay_pix_key'];
          }

          if ( 'pay_template' in json ) {
              pay_template = json['pay_template'];
          }

          if ( 'pay_title' in json ) {
              pay_email_title = json['pay_title'];
          }

          document.getElementById('condo-name').value = json['condo_name'];
          document.getElementById('condo-tagline').value = json['tagline'];
          document.getElementById('condo-address').value = json['address'];
          document.getElementById('condo-address-number').value = json['address_number'];
          document.getElementById('condo-zip').value = json['zip'];
          document.getElementById('condo-city').value = json['condo_city'];
          document.getElementById('condo-state').value = json['condo_state'];
          document.getElementById('home-page-title').value = json.home_message.title;
          document.getElementById('about-page-title').value = json.about_message.title;
          document.getElementById('home-page-text').value = json.home_message.text;
          document.getElementById('about-page-text').value = json.about_message.text;
          document.getElementById('fine_email_title').value = fine_email_title;
          document.getElementById('pix_key').value = pix_key;
          document.getElementById('fine_template').value = fine_template;
          document.getElementById('pay_email_title').value = pay_email_title;
          document.getElementById('pay_pix_key').value = pay_pix_key;
          document.getElementById('pay_template').value = pay_template;
      }
      else {
          showMsgBox( gettext('Error retrieving announcements list') );
      }

    }
    request.send();
}

function updateSystemSettings() {
    condo_name = document.getElementById('condo-name').value.trim();
    condo_tagline = document.getElementById('condo-tagline').value.trim();
    condo_address = document.getElementById('condo-address').value.trim();
    condo_address_number = document.getElementById('condo-address-number').value.trim();
    condo_zip = document.getElementById('condo-zip').value.trim();
    condo_city = document.getElementById('condo-city').value.trim();
    condo_state = document.getElementById('condo-state').value.trim();
    home_page_title = document.getElementById('home-page-title').value.trim();
    home_page_text = document.getElementById('home-page-text').value.trim();
    about_page_title = document.getElementById('about-page-title').value.trim();
    about_page_text = document.getElementById('about-page-text').value.trim();
    pix_key = document.getElementById('pix_key').value.trim();
    fine_template = document.getElementById('fine_template').value.trim();
    fine_email_title = document.getElementById('fine_email_title').value.trim();
    pay_pix_key = document.getElementById('pay_pix_key').value.trim();
    pay_template = document.getElementById('pay_template').value.trim();
    pay_email_title = document.getElementById('pay_email_title').value.trim();

    if ( condo_name.length == 0  ||  condo_tagline.length == 0  ||  condo_address.length == 0  ||  condo_city.length == 0  ||  condo_state.length == 0 ) {
        showMsgBox( gettext("Condo Name, Tagline, Address, ZIP and Location are required fields") );
        return;
    }

    if ( condo_zip.length == 0 ) {
       showMsgBox( gettext('ZIP is a required field') );
       return;
    }

    showSpinner();

    // here we make a request to "upload_link"
    var request = new XMLHttpRequest();
    post_url = "/" + window.loggedin_tenant_global + "/update_system_settings";
    request.open('POST', post_url, true)

    request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);

      if (request.status >= 200 && request.status < 400) {
          if (json.response.status == 'error') {
              showMsgBox( gettext('error uploading system settings') );
          }
          else {
              //showMsgBoxSuccess( gettext('Settings successfully uploaded to the server') );
              location.reload(true);
          }
      }
      else {
          showMsgBox( gettext('Error uploading the settings') );
      }

      return;
    }

    var requestObj = new Object();
    requestObj.condo_name = condo_name;
    requestObj.condo_tagline = condo_tagline;
    requestObj.condo_address = condo_address;
    requestObj.condo_address_number = condo_address_number;
    requestObj.condo_zip = condo_zip;
    requestObj.condo_city = condo_city;
    requestObj.condo_state = condo_state;
    requestObj.home_page_title = home_page_title;
    requestObj.about_page_title = about_page_title;
    requestObj.home_page_text = home_page_text;
    requestObj.about_page_text = about_page_text;
    requestObj.pix_key = pix_key;
    requestObj.fine_template = fine_template;
    requestObj.fine_email_title = fine_email_title;
    requestObj.pay_pix_key = pay_pix_key;
    requestObj.pay_template = pay_template;
    requestObj.pay_email_title = pay_email_title;
    jsonStr = '{ "request": ' + JSON.stringify(requestObj) + '}';
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(jsonStr);
}

/*
   This is invoked by upload.html to save announcements.
   Unfortunately, this cannot be placed in announcs.js because
   doing so would force us to import announcs.js from upload.html,
   which would create a double "onLoadAction()" function
*/
function saveAnnouncs() {
    var announcs = document.getElementById("announctextfield_id").value;
    var request = new XMLHttpRequest();
    request.open('POST', '/saveannouncs', true)

    var requestObj = new Object();
    requestObj.lines = announcs;
    jsonStr = '{ "announc": ' + JSON.stringify(requestObj) + '}';
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(jsonStr);

    request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);

      if (request.status >= 200 && request.status < 400) {
          if (json.response.status == 'success') {
              showMsgBoxSuccess( gettext('Announcements have been saved.') );
              return;
          }
          else {
              showMsgBox( gettext('There was a problem trying to save the announcements.') );
              return;
          }
      }
      else {
          showMsgBox( gettext('Error saving the announcements.') );
          return;
      }
    }
}

/*
async function uploadFile(filename) {
    let formData = new FormData();
    var fileupload = document.getElementById(filename);

    if (fileupload.files[0] == undefined || fileupload.files[0] == "") {
  	    alert('Please select a document file before clicking the upload button.');
  	    return;
    }

    formData.append("file", fileupload.files[0]);
    formData.append("convname", filename);

    await fetch('/upload', {
      method: "POST",
      body: formData
    }).then(response => {
      if (!response.ok) {
         alert('The file upload has failed.');
      }
      else {
         alert('File upload was successful.');
      }
    });
}
*/

// we retrieve the user data from the database first
// then we use that data to send him an email.
function startSendEmail() {
    var userid = document.getElementById("userid").value;
    var request = new XMLHttpRequest();
    request.open('POST', '/getresident', true)

    var requestObj = new Object();
    requestObj.type = 'user';
    requestObj.id = userid;
    jsonStr = '{ "request": ' + JSON.stringify(requestObj) + '}';
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(jsonStr);

    request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);

      if (request.status >= 200 && request.status < 400) {
          if (json.response.status == 'not_found') {
              showMsgBox( gettext("Record not found for User Id") + ' ' + userid );
              return;
          }

          if (json.response.resident.email.trim().length == 0) {
              showMsgBox( gettext("User doesn't have an email address on file") );
              return;
          }

          sendEmail(json);
      }
      else {
          showMsgBox( gettext('Error retrieving user') );
          return;
      }
    }
}

/*
function retrieveUsers() {
    var request = new XMLHttpRequest()
    post_url = "/" + window.loggedin_tenant_global + "/getresidents";
    request.open('POST', post_url, true)
    var requestObj = new Object();
    requestObj.tenant = window.loggedin_tenant_global;
    jsonStr = '{ "request": ' + JSON.stringify(requestObj) + '}';
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

    request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);

      if (request.status >= 200 && request.status < 400) {
          // populate table
          populateTable(json, 'residents_table_id', 'resident');
      }
      else {
          showMsgBox( gettext('Error retrieving residents list') );
      }

    }

    request.send(jsonStr);
}
*/

function sendEmail(json) {
    var userid = json.response.resident.userid;
    var passw = json.response.resident.password;
    var email = json.response.resident.email;

    // here we make a request to "sendsinglemail"
    var request = new XMLHttpRequest();
    request.open('POST', '/sendsinglemail', true)

    request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);

      if (request.status >= 200 && request.status < 400) {
          if (json.response.status == 'error') {
              showMsgBox( gettext('error sending email to user') );
          }
          else {
              showMsgBoxSuccess( gettext('Email sent to user') );
          }
      }
      else {
          showMsgBox( gettext('Error sending email') );
      }

      return;
    }

    var requestObj = new Object();
    requestObj.emailto = email;
    requestObj.subject = 'Your whitegatecondo.com info';
    requestObj.body = 'Your credential to access whitegatecondo.com:\n\nusername: ' + userid + "\npassword: " + passw ;

    // const person = {firstName:"John", lastName:"Doe", age:50, eyeColor:"blue"};
    jsonStr = '{ "request": ' + JSON.stringify(requestObj) + '}';
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(jsonStr);
}

async function updateProgressBar(percent) {
    var element = document.getElementById("status-bar");
    element.style.width = percent + '%';
    element.innerHTML = percent + '%';
}

async function sendBulkEmail() {
    var requestObj = new Object();
    requestObj.subject = document.getElementById('titlefield_id').value;
    requestObj.body = document.getElementById('emailtextfield_id').value;

    if ( requestObj.subject.trim().length == 0 || requestObj.body.trim().length == 0 ) {
        showMsgBox( gettext("Title and Body of the message are required") );
        return;
    }

    // show the progress bar
    document.getElementById("email-progress-bar").style.display = "block";

    // init progress bar data
    updateProgressBar(1);

    try {
      // start a task on the server
      const res = await fetch("/sendmail", {
         // Adding method type
         method: "POST",
         headers: {
             'Accept': 'application/json',
             'Content-Type': 'application/json'
         },
         // Adding body or contents to send
         body: JSON.stringify({
             subject: requestObj.subject,
             body: requestObj.body
         }),
      });

      // init a timer, trigger every 1 second
      timeout = setInterval(getStatus, 1000);
    } catch (e) {
      console.error("Error: ", e);
    }
}

// function will be invoked by the timer until server returns 100 (i.e.100%)
async function getStatus() {
    let status;

    try {
      const res = await fetch("/getstatus");
      status = await res.json();
    } catch (e) {
      console.error("Error: ", e);
    }

    updateProgressBar(status.percent);

    if (status.percent == 100) {
      clearInterval(timeout);
      document.getElementById("progress-bar").style.display = "none";
      showMsgBoxSuccess( gettext('Email sent to all users') );
      document.getElementById('titlefield_id').value = '';
      document.getElementById('emailtextfield_id').value = '';
      return false;
    }
}

async function sendPasswordReset() {
    var requestObj = new Object();
    requestObj.unit_id = document.getElementById('reset_unit').value;
    requestObj.recipient_email = document.getElementById('recipient_email').value;

    if ( requestObj.unit_id < 1 || requestObj.unit_id > 53 ) {
        showMsgBox( gettext("Choose a unit number whose password will be reset") );
        return;
    }

    // start a task on the server
    fetch("/resetpassword", {
       // Adding method type
       method: "POST",
       headers: {
           'Accept': 'application/json',
           'Content-Type': 'application/json'
       },
       // Adding body or contents to send
       body: JSON.stringify({
           unit_id: requestObj.unit_id,
           recipient_email: requestObj.recipient_email
       }),
    }).then( async (resp) => {
        if (resp.ok) {
           resp_json = await resp.json();
           alert('Email sent to '+resp_json.response.owner_email + ' and ' + resp_json.response.authorized_email);
        }
        else {
            console.error("An error occurred while resetting password.");
            showMsgBox( gettext("An error occurred while resetting password. Please try again.") );
        }
    });
}


/*
    // this function was moved into other .js modules
function deleteFile(filepath, filename) {
    var request = new XMLHttpRequest()
    request.open('POST', '/deletefile', true)

    request.onload = function () {
        // Begin accessing JSON data here
        var json = JSON.parse(this.response);

        if (request.status >= 200 && request.status < 400) {
            if (json.status == 'success') {
                showMsgBoxSuccess( gettext("File") + " '" + filename + "' " + gettext("has been deleted") );
                location.reload(true);
            }
            else {
                showMsgBox( gettext("Some error occurred trying to delete file") + " " + filename);
            }
        }
        else {
            showMsgBox( gettext('Error communicating with the server.') );
        }
    }

    var requestObj = new Object();
    requestObj.filepath = filepath;
    requestObj.filename = filename;
    jsonStr = '{ "request": ' + JSON.stringify(requestObj) + '}';
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(jsonStr);
}
*/


/*
  // this function was moved into the docs.js
  // Description of the link is the key
function deleteLink(link_descr) {
    // here we make a request to "upload_link"
    var request = new XMLHttpRequest();
    request.open('POST', '/delete_link', true)

    request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);

      if (request.status >= 200 && request.status < 400) {
          if (json.response.status == 'error') {
              showMsgBox( gettext('error uploading a new link') );
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
    requestObj.link_descr = link_descr;
    jsonStr = '{ "request": ' + JSON.stringify(requestObj) + '}';
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(jsonStr);
}
*/

