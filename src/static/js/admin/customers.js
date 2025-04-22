function onLoadAction() {
}

function retrieveCustomer() {
    if ( document.getElementById("customer_id").selectedIndex == 0 ) {
        alert('Customer is a required field.');
        return;
    }

    var request = new XMLHttpRequest();
    request.open('POST', "/admin/retrieve_customer", true);

    request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);

      if (request.status >= 200 && request.status < 400) {
          if (json.response.status == 'success') {
              populateScreen(json.response);
          }
          else
          if (json.response.status == 'not_found') {
              showMsgBox( 'Customer not found' );
          }
          else {
              showMsgBox( 'Error getting record from database' );
          }
      }
      else {
          showMsgBox( 'Error getting record from database' );
      }
    }

    var requestObj = new Object();
    requestObj.tenant = document.getElementById('customer_id').value;
    jsonStr = '{ "customer": ' + JSON.stringify(requestObj) + '}';
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(jsonStr);
}

function populateScreen(json) {
    document.getElementById('adm_userid').value = json.admin_userid;
    document.getElementById('adm_pass').value = json.admin_pass;
    document.getElementById('adm_email').value = json.admin_email;
    document.getElementById('adm_phone').value = json.admin_phone;
    console.log('date: '+json.license_pay_date);
    document.getElementById('lic_date').value = json.license_pay_date;
    document.getElementById('lic_amount').value = json.license_pay_amount;
    document.getElementById('lic_term').value = json.license_term;
}

function saveCustomer() {
    if ( document.getElementById("customer_id").selectedIndex == 0 ) {
        alert('Customer is a required field.');
        return;
    }

    date_str = document.getElementById('lic_date').value;

    if (date_str === '') {
        showMsgBox( "Please choose a Payment Date" );
        return;
    }


    var request = new XMLHttpRequest();
    request.open('POST', "/admin/save_customer", true);

    request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);

      if (request.status >= 200 && request.status < 400) {
          if (json.response.status == 'success') {
              showMsgBoxSuccess( 'Record saved to database' );
          }
          else {
              showMsgBox( 'Error saving record to database' );
          }
      }
      else {
          showMsgBox( 'Error saving record to database' );
      }
    }

    var requestObj = new Object();
//    date = new Date(date_str);
//    date = document.getElementById('lic_date').valueAsDate;
//    date_y = date.getFullYear();
//    date_m = date.getMonth()+1;
//    date_d = date.getDate();

    requestObj.tenant = document.getElementById('customer_id').value;
    requestObj.user_id = document.getElementById('adm_userid').value;
    requestObj.date = date_str;  // in the format YYYY-MM-DD
    requestObj.user_pass = document.getElementById('adm_pass').value;
    requestObj.user_email = document.getElementById('adm_email').value;
    requestObj.user_phone = document.getElementById('adm_phone').value;
    requestObj.lic_amount = document.getElementById('lic_amount').value;
    requestObj.lic_term = document.getElementById('lic_term').value;
    jsonStr = '{ "customer": ' + JSON.stringify(requestObj) + '}';
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(jsonStr);
}

function deleteCustomer( index ) {
    console.log('index '+index);

    /* retrieve fields from browser's memory */
    customer_id = document.getElementById(index + "_customer_id").value;

    resp = confirm('Want to delete ' + customer_id + '?');
    if (resp == false) {
        return;
    }

    var request = new XMLHttpRequest();
    post_url = "/admin/delete_customer";
    request.open('POST', post_url, true);

    request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);

      if (request.status >= 200 && request.status < 400) {
          if (json.response.status == 'success') {
              showMsgBoxSuccess( 'Record deleted from the database' );
          }
          else {
              showMsgBox( 'Error deleting record' );
          }
      }
      else {
          showMsgBox( 'Error deleting record' );
      }

      location.reload();
    }

    var requestObj = new Object();
    requestObj.tenant = customer_id;
    jsonStr = '{ "customer": ' + JSON.stringify(requestObj) + '}';
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(jsonStr);
}

function amountOnBlur(e) {
//    amount = document.getElementById("amount").value;
//    if ( !isFraction(amount) ) {
//        if ( amount.indexOf('.') == -1) {
//            document.getElementById("amount").value = amount + '.00';
//        }
//    }
}

