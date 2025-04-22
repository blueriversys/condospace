function onLoadAction() {
}


function togglePassVisibility() {
    var pass_field = document.getElementById("pass_field");
    if (pass_field.type === "password") {
        pass_field.type = "text";
    }
    else {
        pass_field.type = "password";
    }
}

function retrievePassword() {
    user_id = document.getElementById("user_id").value.trim();

    if (user_id.length == 0) {
        showMsgBox( gettext('User Id is a required field') );
        return;
    }

    var request = new XMLHttpRequest();
    post_url = "/" + window.loggedin_tenant_global + "/forgot_password";
    request.open('POST', post_url, true);

    request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);

      if (request.status >= 200 && request.status < 400) {
          if (json.response.status == 'success') {
              showMsgBoxSuccess( gettext('A message was sent to your email in the system') );
              //location.reload();
          }
          else {
              showMsgBox( gettext(json.response.message) );
          }
      }
      else {
          showMsgBox( gettext('Error processing this request') );
      }

      //location.reload();
    }

    var requestObj = new Object();
    requestObj.tenant = window.loggedin_tenant_global;
    requestObj.user_id = user_id;
    jsonStr = '{ "request": ' + JSON.stringify(requestObj) + '}';
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(jsonStr);
}


