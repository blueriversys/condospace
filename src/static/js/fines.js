function onLoadAction() {
    window.loggedin_id_global = document.getElementById('loggedin-id').value;
    window.loggedin_userid_global = document.getElementById('loggedin-userid').value;
    window.loggedin_unit_global = document.getElementById('loggedin-unit').value;
    window.loggedin_name_global = document.getElementById('loggedin-name').value;
    window.loggedin_tenant_global = document.getElementById('loggedin-tenant').value.trim();
    window.loggedin_lang_global = document.getElementById('loggedin-lang').value;
    /*retrievePayments(window.loggedin_tenant_global);*/
}

function retrieveUser() {
    user_id =  document.getElementById("user_id").value;
    name = document.getElementById(user_id + '_name').value.trim();
    email = document.getElementById(user_id + '_email').value.trim();
    phone = document.getElementById(user_id + '_phone').value.trim();
    document.getElementById('name').value = name;
    document.getElementById('email').value = email;
    document.getElementById('phone').value = phone;
}

function storeFineData(index) {
    window.user_id = document.getElementById(index + "_user_id").value;
    window.fine_id = document.getElementById(index + "_fine_id").value;
    window.name = document.getElementById(index + "_name").value;
    window.email = document.getElementById(index + "_email").value;
    window.amount = document.getElementById(index + "_amount").value;
    window.descr = document.getElementById(index + "_descr").value;
    window.due_date_y = document.getElementById(index + "_due_date_y").value;
    window.due_date_m = document.getElementById(index + "_due_date_m").value;
    window.due_date_d = document.getElementById(index + "_due_date_d").value;
}

function setFinePaymentDate() {
    date_str = document.getElementById('paid_date').value;

    if (date_str === '') {
        showMsgBox( gettext("Please choose a Payment Date") );
        return;
    }

    date = new Date(date_str);
    date_y = date.getFullYear();
    date_m = date.getMonth()+1;
    date_d = date.getDate()+1;
    var request = new XMLHttpRequest();
    post_url = "/" + window.loggedin_tenant_global + "/setpayment";
    request.open('POST', post_url, true);

    /* retrieve fields from browser's memory */
    user_id = window.user_id;
    fine_id = window.fine_id;

    request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);

      if (request.status >= 200 && request.status < 400) {
          if (json.response.status == 'success') {
              showMsgBoxSuccess( gettext('Record saved to database') );
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

    var requestObj = new Object();
    requestObj.tenant = loggedin_tenant_global;
    requestObj.user_id = user_id;
    requestObj.fine_id = fine_id;
    requestObj.date = {"y": date_y, "m": date_m,  "d": date_d};
    jsonStr = '{ "payment": ' + JSON.stringify(requestObj) + '}';
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(jsonStr);

    /* close modal window */
    document.getElementById('modal-close').click();
}

function deleteFine( index ) {
    var request = new XMLHttpRequest();
    post_url = "/" + window.loggedin_tenant_global + "/deletefine";
    request.open('POST', post_url, true);

    /* retrieve fields from browser's memory */
    user_id = document.getElementById(index + "_user_id").value;
    fine_id = document.getElementById(index + "_fine_id").value;

    request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);

      if (request.status >= 200 && request.status < 400) {
          if (json.response.status == 'success') {
              showMsgBoxSuccess( gettext('Record deleted from the database') );
          }
          else {
              showMsgBox( gettext('Error deleting record') );
          }
      }
      else {
          showMsgBox( gettext('Error deleting record') );
      }

      location.reload();
    }

    var requestObj = new Object();
    requestObj.tenant = loggedin_tenant_global;
    requestObj.user_id = user_id;
    requestObj.fine_id = fine_id;
    jsonStr = '{ "fine": ' + JSON.stringify(requestObj) + '}';
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(jsonStr);
}

function sendFineReminder( index, charge_type ) {
    /* retrieve fields from browser's memory */
    user_id = document.getElementById(index + "_user_id").value;
    fine_id = document.getElementById(index + "_fine_id").value;
    name = document.getElementById(index + "_name").value;
    email = document.getElementById(index + "_email").value;
    amount = document.getElementById(index + "_amount").value;
    descr = document.getElementById(index + "_descr").value;
    due_date_y = document.getElementById(index + "_due_date_y").value;
    due_date_m = document.getElementById(index + "_due_date_m").value;
    due_date_d = document.getElementById(index + "_due_date_d").value;

    if (email === '') {
        showMsgBox( gettext("Email address missing for this fine") );
        return;
    }

    var request = new XMLHttpRequest();
    post_url = "/" + window.loggedin_tenant_global + "/sendfinereminder";
    request.open('POST', post_url, true);

    request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);

      if (request.status >= 200 && request.status < 400) {
          if (json.response.status == 'success') {
              showMsgBoxSuccess( gettext('Reminder sent to resident') );
          }
          else {
              showMsgBox( gettext('Error sending the reminder') );
          }
      }
      else {
          showMsgBox( gettext('Error sending the reminder') );
      }
    }

    var requestObj = new Object();
    requestObj.tenant = loggedin_tenant_global;
    requestObj.user_id = user_id;
    requestObj.fine_id = fine_id;
    requestObj.name = name;
    requestObj.email = email;
    requestObj.amount = amount;
    requestObj.descr = descr;
    requestObj.charge_type = charge_type;
    requestObj.due_date = {"y": due_date_y, "m": due_date_m,  "d": due_date_d};
    jsonStr = '{ "fine": ' + JSON.stringify(requestObj) + '}';
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(jsonStr);
}

function isFraction(num) {
    return num % 1 !== 0;
}

function amountOnBlur(e) {
    amount = document.getElementById("amount").value;
    if ( !isFraction(amount) ) {
        if ( amount.indexOf('.') == -1) {
            document.getElementById("amount").value = amount + '.00';
        }
    }
}

function emailOnBlur(e) {
    email = document.getElementById("email").value.trim();
    saveButton = document.getElementById("save_payment_btn");
    lang = document.getElementById("condo_language").value;
    buttonText1 = gettext('Add This Fine');
    buttonText2 = gettext('Add This Fine and Notify User');
    saveButton.innerText =  email == '' ? buttonText1 : buttonText2;
}

function saveFine() {
    date_str = document.getElementById('due_date').value;
    user_id = document.getElementById("user_id").value;
    name = document.getElementById("name").value;
    email = document.getElementById("email").value;
    phone = document.getElementById("phone").value;
    amount = document.getElementById("amount").value.trim();
    descr = document.getElementById("descr").value.trim();
    charge_type = document.getElementById("pay_radio").checked ? 'pay' : 'fine';

    console.log('charge type:' + charge_type);

    if ( document.getElementById("user_id").selectedIndex == 0 ) {
        showMsgBox( gettext('User is a required field') );
        return;
    }

    if ( user_id === '' || name === '' ) {
        showMsgBox( gettext('Fields User and Name are required') );
        return;
    }

    if (date_str === '') {
        showMsgBox( gettext("Please choose a Due Date") );
        return;
    }

    if (amount === '' || descr === '') {
        showMsgBox( gettext('Fields Amount and Description are required') );
        return;
    }

    if (amount < 0 || amount == 0) {
        showMsgBox( gettext('Field Amount cannot be negative or zero') );
        return;
    }

    var request = new XMLHttpRequest();
    post_url = "/" + window.loggedin_tenant_global + "/savefine";
    request.open('POST', post_url, true);

    var due_date = new Date(date_str);
    due_date_y = due_date.getFullYear();
    due_date_m = due_date.getMonth()+1;
    due_date_d = due_date.getDate()+1;

    request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);

      if (request.status >= 200 && request.status < 400) {
          if (json.response.status == 'success') {
              showMsgBoxSuccess( gettext('Record saved to database') );
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

    var requestObj = new Object();
    requestObj.tenant = loggedin_tenant_global;
    requestObj.user_id = user_id;
    requestObj.name = name;
    requestObj.email = email;
    requestObj.phone = phone;
    requestObj.amount = amount;
    requestObj.descr = descr;
    requestObj.due_date = {"y": due_date_y, "m": due_date_m,  "d": due_date_d};
    requestObj.charge_type = charge_type;
    // const person = {firstName:"John", lastName:"Doe", age:50, eyeColor:"blue"};
    jsonStr = '{ "payment": ' + JSON.stringify(requestObj) + '}';
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(jsonStr);
}

function chargeTypeChanged() {
    legend_text = gettext("Issue a Fine");
    save_button_text = gettext("Add This Fine and Notify User");
    if ( document.getElementById("pay_radio").checked ) {
        legend_text = gettext("Request a Payment");
        save_button_text = gettext("Add This Payment Request and Notify User");
    }
    document.getElementById("legend_id").textContent = legend_text;
    document.getElementById("save_btn_text").innerText = save_button_text;
}
