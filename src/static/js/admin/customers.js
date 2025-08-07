function onLoadAction() {
    document.getElementById("current_page").value = "1";
    document.getElementById("page_number_id").value = 1;
    document.getElementById("regis_date_id").value = '';
}

function retrievePreviousPage() {
    reg_input_date = document.getElementById("regis_date_id").value;
    page = document.getElementById("current_page").value;
    page = parseInt(page) - 1;
    retrieveCustomersPage(reg_input_date, page);
}

function retrieveNextPage() {
    reg_input_date = document.getElementById("regis_date_id").value;
    page = document.getElementById("current_page").value;
    page = parseInt(page) + 1;
    retrieveCustomersPage(reg_input_date, page);
}

function retrieveCustomersByParams() {
    reg_input_date = document.getElementById("regis_date_id").value;
    page = document.getElementById("page_number_id").value;
    if (page < 1) {
        alert("Enter page param to retrieve customers.");
        return;
    }
    retrieveCustomersPage(reg_input_date, page);
}

function retrieveCustomersPage(reg_input_date, page) {
    page = parseInt(page);

    if ( page == 0 ) {
        page = 1;
    }

    console.log(`date is ${reg_input_date}`);

    if (reg_input_date != '') {
        regis_date = new Date(reg_input_date);
        date_y = regis_date.getFullYear();
        date_m = parseInt(regis_date.getMonth()+1);
        date_d = parseInt(regis_date.getDate()+1);
        if (date_m < 10) {
            date_m = `0${date_m}`;
        }
        if (date_d < 10) {
            date_d = `0${date_d}`;
        }
        console.log(`m ${date_m}   d ${date_d}`);
        regis_date_str = `${date_y}${date_m}${date_d}`;
    }
    else {
        regis_date_str = "00000000";
    }

    console.log(`reg input date: ${reg_input_date}   page: ${page}`);

    var request = new XMLHttpRequest();
    console.log(`/admin/customers/condo/${regis_date_str}/${page}`);
    request.open('POST', `/admin/customers/condo/${regis_date_str}/${page}`, true);

    request.onload = function () {
        // Begin accessing JSON data here
        var json = JSON.parse(this.response);

        if (request.status >= 200 && request.status < 400) {
            if (json.response.status == 'success') {
                populateCustomerList(json.response);
                document.getElementById("current_page").value = page;
                document.getElementById("page_number_id").value = page;
                recreateCustomersDropdown(json.response);
            }
            else {
                alert( 'Error getting record from database' );
            }
        }
        else {
            alert( 'Error getting record from database' );
        }
    }

    request.send(''); // the payload for this call is empty
}

function populateCustomerList(json) {
    var table = document.getElementById("customers_table_id");
    var rowCount = table.rows.length - 1;

    for (var i=rowCount; i>0; i--) {
        table.deleteRow(i);
    }

    for (var i=0; i<rowCount; i++) {
        const cust_id = `${i}_customer_id`;
        console.log(`cust id ${cust_id}`);
        const inputElement = document.getElementById(cust_id);
        inputElement.remove();
    }

    for (var i=0; i<json.customers.length; i++) {
        var row = table.insertRow( -1 ); // -1 is insert as last
        var del_btn_cell = row.insertCell( - 1 ); // -1 is insert as last
        var customer_cell = row.insertCell( - 1 ); // -1 is insert as last
        var user_id_cell = row.insertCell( - 1 ); // -1 is insert as last
        var pass_cell = row.insertCell( - 1 ); // -1 is insert as last
        var email_cell = row.insertCell( - 1 ); // -1 is insert as last
        var created_dt_cell = row.insertCell( - 1 ); // -1 is insert as last
        var login_dt_cell = row.insertCell( - 1 ); // -1 is insert as last
        var origin_cell = row.insertCell( - 1 ); // -1 is insert as last
        var lic_dt_cell = row.insertCell( - 1 ); // -1 is insert as last
        var lic_amount_cell = row.insertCell( - 1 ); // -1 is insert as last
        var lic_term_cell = row.insertCell( - 1 ); // -1 is insert as last

        var customer = json.customers[i].domain;
        var user_id = json.customers[i].admin_userid;
        var password = json.customers[i].admin_pass;
        var email = json.customers[i].admin_email;
        var created_dt = json.customers[i].registration_date;
        var last_login_dt = json.customers[i].last_login_date;
        var origin = json.customers[i].origin;
        var license_date = json.customers[i].license_pay_date;
        var license_amount = json.customers[i].license_pay_amount;
        var license_term = json.customers[i].license_term;

        del_btn_cell.innerHTML = `<button id="delete" class="btn btn-danger small-btn" style="height: 20px;" onclick="deleteCustomer(${i});">delete</button>`;
        customer_cell.innerHTML = customer;
        user_id_cell.innerHTML = user_id;
        pass_cell.innerHTML = password;
        email_cell.innerHTML = email;
        created_dt_cell.innerHTML = created_dt;
        login_dt_cell.innerHTML = last_login_dt;
        origin_cell.innerHTML = origin;
        lic_dt_cell.innerHTML = license_date;
        lic_amount_cell.innerHTML = license_amount;
        lic_term_cell.innerHTML = license_term;

        // add the hidden field for condo id
        const hiddenInput = document.createElement('input');
        hiddenInput.setAttribute('type', 'hidden');
        hiddenInput.setAttribute('id', `${i}_customer_id`);
        hiddenInput.setAttribute('value', customer);
        document.documentElement.appendChild(hiddenInput);
    }
}

function recreateCustomersDropdown(json) {
    const cust_dropdown_id = "customer_id";
    const container_id = "dropdown_container_id";
    document.getElementById(cust_dropdown_id).remove();
    const selectList = document.createElement("select");
    selectList.id = cust_dropdown_id;

    for (let i=0; i<json.customers.length; i++) {
      const option = document.createElement("option");
      option.value = json.customers[i].domain;
      option.text = json.customers[i].domain;
      selectList.appendChild(option);
    }

    const container = document.getElementById(container_id);
    container.appendChild(selectList);

    // add event
    selectList.addEventListener("change", retrieveCustomer);
}

function retrieveCondoCustomer() {
    if ( document.getElementById("customer_id").selectedIndex == 0 ) {
        alert('Customer is a required field.');
        return;
    }

    var request = new XMLHttpRequest();
    request.open('POST', "/admin/customers/condo/retrieve_customer", true);

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

function retrieveCompanyCustomer() {
    if ( document.getElementById("customer_id").selectedIndex == 0 ) {
        alert('Customer is a required field.');
        return;
    }

    var request = new XMLHttpRequest();
    request.open('POST', "/admin/customers/company/retrieve_customer", true);

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

function saveCondoCustomer() {
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
    request.open('POST', "/admin/customers/condo/save_customer", true);

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

function saveCompanyCustomer() {
    if ( document.getElementById("customer_id").selectedIndex == 0 ) {
        alert('Customer is a required field.');
        return;
    }

    date_str = document.getElementById('lic_date').value;

    if (date_str === '') {
        alert( "Please choose a Payment Date" );
        return;
    }


    var request = new XMLHttpRequest();
    request.open('POST', "/admin/customers/company/save_customer", true);

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

    resp = confirm(`Want to delete ${customer_id} ?`);
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

