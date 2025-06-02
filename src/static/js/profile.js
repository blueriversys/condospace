const ADMIN_TYPE = 0;
const BOARD_MEMBER_TYPE = 1;
const SECRETARY_TYPE = 2;
const RESIDENT_TYPE = 3;

var resident_type = RESIDENT_TYPE;

function onLoadAction() {
    // I have to find a better way to tell which is the logged-in user, other
    // than asking the server
    //loadResident();
    window.loggedin_id_global = document.getElementById('loggedin-id').value;
    window.loggedin_userid_global = document.getElementById('loggedin-userid').value;
    window.loggedin_unit_global = document.getElementById('loggedin-unit').value;
    window.loggedin_name_global = document.getElementById('loggedin-name').value;
    window.loggedin_tenant_global = document.getElementById('loggedin-tenant').value.trim();
    window.loggedin_lang_global = document.getElementById('loggedin-lang').value;

    const isMultiCondo = document.getElementById("loggedin-multi-condo").value;
    if (isMultiCondo) {
        console.log(`user type is SUPER_ADMIN`);
        return;
    }

    retrieveLoggedinResident(window.loggedin_userid_global);
}

/*
function loadResident() {
  var request = new XMLHttpRequest();
  request.open('GET', '/getloggedinuser', true);
  request.send();

  request.onload = function () {
    // Begin accessing JSON data here
    var json = JSON.parse(this.response);

    if (request.status >= 200 && request.status < 400) {
        if (json.response.status == 'not_found') {
            alert('Error trying to retrieve logged in user.');
            return;
        }

        loggedin_user = json.response.resident.userid;
        loggedin_unit = json.response.resident.unit;

        if ( loggedin_user.startsWith("admin")) {
            return;
        }

        retrieveLoggedinResident(loggedin_user);
    }
    else {
        alert('Error retrieving user')
    }
  }
}
*/

function retrieveLoggedinResident(userid) {
  var request = new XMLHttpRequest();
  post_url = "/" + window.loggedin_tenant_global + "/getresident";
  request.open('POST', post_url, true)

  var requestObj = new Object();
  requestObj.type = 'user';
  requestObj.tenant = window.loggedin_tenant_global;
  requestObj.id = userid;

  jsonStr = '{ "request": ' + JSON.stringify(requestObj) + '}';
  request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  request.send(jsonStr);

  request.onload = function () {
    // Begin accessing JSON data here
    var json = JSON.parse(this.response);

    if (request.status >= 200 && request.status < 400) {
        if (json.response.status == 'not_found') {
            alert('Record not found for unit '+requestObj.id);
            return;
        }

        resident_type = json.response.resident.type;

        if (resident_type != 3) {
            // document.getElementById('profile_unit').value = json.response.resident.unit;
        }

        document.getElementById('curr_password').value = '';
        document.getElementById('new_password').value = '';
        document.getElementById('repeat_password').value = '';

        populateScreen(json);
    }
    else {
        alert('Error retrieving user');
        return;
    }
  }
}



/*
   invoked when a unit is selected from the dropdown box
*/
function populateScreen(json) {
    document.getElementById('user_id_adm').value = json.response.resident.userid;

    if ( document.getElementById('password') != null) {
        document.getElementById('password').value = json.response.resident.password;
    }

    if ( document.getElementById('resident_type') != null) {
        document.getElementById('resident_type').value = json.response.resident.type;
    }


    document.getElementById('name').value = json.response.resident.name;
    document.getElementById('email').value = json.response.resident.email;
    document.getElementById('phone').value = json.response.resident.phone;

    document.getElementById('startdt_month').value = json.response.resident.startdt.month;
    document.getElementById('startdt_year').value  = json.response.resident.startdt.year;

/*
    last_upd_pieces = json.response.resident.last_update_date.split("/");
    month = last_upd_pieces[0];
    day = last_upd_pieces[1];
    if ( month.length < 2) {
        month = "0"+month;
    }
    if ( day.length < 2) {
        day = "0"+day;
    }
    document.getElementById('last_update_date').value = last_upd_pieces[2] + "-" + month + "-" + day;
*/
    document.getElementById('last_update_date').value = json.response.resident.last_update_date;

    if ( json.response.resident.occupants.length != 0) {
        document.getElementById('occup1_name').value = json.response.resident.occupants[0].name;
        document.getElementById('occup1_email').value = json.response.resident.occupants[0].email;
        document.getElementById('occup1_cc').checked = json.response.resident.occupants[0].cc;
        document.getElementById('occup1_phone').value = json.response.resident.occupants[0].phone;
        document.getElementById('occup1_has_key').checked = json.response.resident.occupants[0].has_key;
        document.getElementById('occup2_name').value = json.response.resident.occupants[1].name;
        document.getElementById('occup2_email').value = json.response.resident.occupants[1].email;
        document.getElementById('occup2_cc').checked = json.response.resident.occupants[1].cc;
        document.getElementById('occup2_phone').value = json.response.resident.occupants[1].phone;
        document.getElementById('occup2_has_key').checked = json.response.resident.occupants[1].has_key;
        document.getElementById('occup3_name').value = json.response.resident.occupants[2].name;
        document.getElementById('occup3_email').value = json.response.resident.occupants[2].email;
        document.getElementById('occup3_cc').checked = json.response.resident.occupants[2].cc;
        document.getElementById('occup3_phone').value = json.response.resident.occupants[2].phone;
        document.getElementById('occup3_has_key').checked = json.response.resident.occupants[2].has_key;
        document.getElementById('occup4_name').value = json.response.resident.occupants[3].name;
        document.getElementById('occup4_email').value = json.response.resident.occupants[3].email;
        document.getElementById('occup4_cc').checked = json.response.resident.occupants[3].cc;
        document.getElementById('occup4_phone').value = json.response.resident.occupants[3].phone;
        document.getElementById('occup4_has_key').checked = json.response.resident.occupants[3].has_key;
        document.getElementById('occup5_name').value = json.response.resident.occupants[4].name;
        document.getElementById('occup5_email').value = json.response.resident.occupants[4].email;
        document.getElementById('occup5_cc').checked = json.response.resident.occupants[4].cc;
        document.getElementById('occup5_phone').value = json.response.resident.occupants[4].phone;
        document.getElementById('occup5_has_key').checked = json.response.resident.occupants[4].has_key;
    }
    else {
        document.getElementById('occup1_name').value = '';
        document.getElementById('occup1_email').value = '';
        document.getElementById('occup1_cc').checked = false;
        document.getElementById('occup1_phone').value = '';
        document.getElementById('occup1_has_key').checked = false;
        document.getElementById('occup2_name').value = '';
        document.getElementById('occup2_email').value = '';
        document.getElementById('occup2_cc').checked = false;
        document.getElementById('occup2_phone').value = '';
        document.getElementById('occup2_has_key').checked = false;
        document.getElementById('occup3_name').value = '';
        document.getElementById('occup3_email').value = '';
        document.getElementById('occup3_cc').checked = false;
        document.getElementById('occup3_phone').value = '';
        document.getElementById('occup3_has_key').checked = false;
        document.getElementById('occup4_name').value = '';
        document.getElementById('occup4_email').value = '';
        document.getElementById('occup4_cc').checked = false;
        document.getElementById('occup4_phone').value = '';
        document.getElementById('occup4_has_key').checked = false;
        document.getElementById('occup5_name').value = '';
        document.getElementById('occup5_email').value = '';
        document.getElementById('occup5_cc').checked = false;
        document.getElementById('occup5_phone').value = '';
        document.getElementById('occup5_has_key').checked = false;
    }

    // emergency contact
    document.getElementById('emerg_name').value = json.response.resident.emerg_name;
    document.getElementById('emerg_email').value = json.response.resident.emerg_email;
    document.getElementById('emerg_phone').value = json.response.resident.emerg_phone;
    document.getElementById('emerg_has_key').checked = json.response.resident.emerg_has_key;

    // owner info (if rental)
    document.getElementById('rental_unit_checkbox').checked = json.response.resident.isrental;
    if ( json.response.resident.isrental ) {
        set_rental_disability(false);
        document.getElementById('owner_name').value = json.response.resident.ownername;
        document.getElementById('owner_email').value = json.response.resident.owneremail;
        document.getElementById('owner_phone').value = json.response.resident.ownerphone;
        document.getElementById('owner_address').value = json.response.resident.owneraddress;
    }
    else {
        blank_and_disable_rental();
    }

    // additional info
    document.getElementById('oxygen_equipment').checked = json.response.resident.oxygen_equipment;
    document.getElementById('limited_mobility').checked = json.response.resident.limited_mobility;
    document.getElementById('routine_visits').checked = json.response.resident.routine_visits;
    document.getElementById('has_pet').checked = json.response.resident.has_pet;
    document.getElementById('bike_count').value = json.response.resident.bike_count;
    document.getElementById('insurance_carrier').value = json.response.resident.insurance_carrier;

    // water shut off type
    // 0-don't know,  1-knob,  2-lever
    if (json.response.resident.valve_type == 0) {
        document.getElementById('dont_know_radio').checked = true;
    }
    else
    if (json.response.resident.valve_type == 1) {
        document.getElementById('knob_radio').checked = true;
    }
    else {
        document.getElementById('lever_radio').checked = true;
    }

    // vehicles
    document.getElementById('vehicle_checkbox').checked = json.response.resident.no_vehicles;
    if ( json.response.resident.no_vehicles ) {
        blank_and_disable_vehicles();
    }
    else {
        set_vehicles_disability(false);
        document.getElementById('make_model_0').value = json.response.resident.vehicles[0].make_model;
        document.getElementById('plate_0').value = json.response.resident.vehicles[0].plate;
        document.getElementById('color_0').value = json.response.resident.vehicles[0].color;
        document.getElementById('year_0').value = json.response.resident.vehicles[0].year;
        document.getElementById('make_model_1').value = json.response.resident.vehicles[1].make_model;
        document.getElementById('plate_1').value = json.response.resident.vehicles[1].plate;
        document.getElementById('color_1').value = json.response.resident.vehicles[1].color;
        document.getElementById('year_1').value = json.response.resident.vehicles[1].year;
    }

    document.getElementById('notes').value = json.response.resident.notes;
}

function retrieveUserByUnit() {
  var user_id = document.getElementById('user_id').value;
  var request = new XMLHttpRequest();
  post_url = "/" + window.loggedin_tenant_global + "/getresident";
  request.open('POST', post_url, true)

  request.onload = function () {
    // Begin accessing JSON data here
    var json = JSON.parse(this.response);

    if (request.status >= 200 && request.status < 400) {
        if (json.response.status == 'not_found') {
            alert('Record not found for unit '+unit);
            cleanScreen();
            return;
        }

        // populate table
        populateScreen(json);
    }
    else {
        alert('Error retrieving unit');
    }

  }

  var requestObj = new Object();
  requestObj.type = 'user';
  requestObj.tenant = document.getElementById('loggedin-tenant').value;
  requestObj.id = user_id;

  // const person = {firstName:"John", lastName:"Doe", age:50, eyeColor:"blue"};
  jsonStr = '{ "request": ' + JSON.stringify(requestObj) + '}';
  request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  request.send(jsonStr);
}

/*
function saveResident() {
    var request = new XMLHttpRequest();
    request.open('POST', '/saveresident', true)

    request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);

      if (request.status >= 200 && request.status < 400) {
          alert('Record saved to database');
      }
      else {
          alert('Error saving record to database')
      }
    }

    var requestObj = new Object();
    if (resident_type == ADMIN_TYPE) {
        requestObj.userid = document.getElementById('user_id').value;
        requestObj.unit = parseInt(document.getElementById('unit').value);
        requestObj.type = parseInt(document.getElementById('resident_type').value);
    }
    else
    if (resident_type == BOARD_MEMBER_TYPE || resident_type == SECRETARY_TYPE) {
        requestObj.userid = document.getElementById('user_id').value;
        requestObj.unit = parseInt(document.getElementById('unit').value);
        requestObj.type = parseInt(resident_type);
    }
    else { // this is for RESIDENT_TYPE
        requestObj.userid = document.getElementById('user_id').value;
        requestObj.unit = parseInt(document.getElementById('unit').value);
        requestObj.type = parseInt(resident_type);
    }


    if ( document.getElementById('password') != null) {
        requestObj.password = document.getElementById('password').value;
    }

    if ( document.getElementById('resident_type') != null) {
        requestObj.type = document.getElementById('resident_type').value;
    }

    requestObj.name = document.getElementById('name').value;
    requestObj.email = document.getElementById('email').value;
    requestObj.phone = document.getElementById('phone').value;

    const occupants = [];
    occupants[0]= new Object();
    occupants[1]= new Object();
    occupants[2]= new Object();
    occupants[3]= new Object();
    occupants[4]= new Object();

    startdt = new Object();
    startdt.month = parseInt(document.getElementById('startdt_month').value);
    startdt.year = parseInt(document.getElementById('startdt_year').value);
    requestObj.startdt = startdt;

    occupants[0].name = document.getElementById('occup1_name').value;
    occupants[0].email = document.getElementById('occup1_email').value;
    occupants[0].cc = document.getElementById('occup1_cc').checked;
    occupants[0].phone = document.getElementById('occup1_phone').value;
    occupants[0].has_key = document.getElementById('occup1_has_key').checked;

    occupants[1].name = document.getElementById('occup2_name').value;
    occupants[1].email = document.getElementById('occup2_email').value;
    occupants[1].cc = document.getElementById('occup2_cc').checked;
    occupants[1].phone = document.getElementById('occup2_phone').value;
    occupants[1].has_key = document.getElementById('occup2_has_key').checked;

    occupants[2].name = document.getElementById('occup3_name').value;
    occupants[2].email = document.getElementById('occup3_email').value;
    occupants[2].cc = document.getElementById('occup3_cc').checked;
    occupants[2].phone = document.getElementById('occup3_phone').value;
    occupants[2].has_key = document.getElementById('occup3_has_key').checked;

    occupants[3].name = document.getElementById('occup4_name').value;
    occupants[3].email = document.getElementById('occup4_email').value;
    occupants[3].cc = document.getElementById('occup4_cc').checked;
    occupants[3].phone = document.getElementById('occup4_phone').value;
    occupants[3].has_key = document.getElementById('occup4_has_key').checked;

    occupants[4].name = document.getElementById('occup5_name').value;
    occupants[4].email = document.getElementById('occup5_email').value;
    occupants[4].cc = document.getElementById('occup5_cc').checked;
    occupants[4].phone = document.getElementById('occup5_phone').value;
    occupants[4].has_key = document.getElementById('occup5_has_key').checked;

    requestObj.occupants = occupants;

    // emergency contact
    requestObj.emerg_name = document.getElementById('emerg_name').value;
    requestObj.emerg_email = document.getElementById('emerg_email').value;
    requestObj.emerg_phone = document.getElementById('emerg_phone').value;
    requestObj.emerg_has_key = document.getElementById('emerg_has_key').checked;

    // owner info (if rental)
    requestObj.ownername = document.getElementById('owner_name').value;
    requestObj.owneremail = document.getElementById('owner_email').value;
    requestObj.ownerphone = document.getElementById('owner_phone').value;
    requestObj.owneraddress = document.getElementById('owner_address').value;
    requestObj.isrental = document.getElementById('rental_unit_checkbox').checked;

    // additional info
    requestObj.oxygen_equipment = document.getElementById('oxygen_equipment').checked;
    requestObj.limited_mobility = document.getElementById('limited_mobility').checked;
    requestObj.routine_visits = document.getElementById('routine_visits').checked;
    requestObj.has_pet = document.getElementById('has_pet').checked;
    requestObj.bike_count = parseInt(document.getElementById('bike_count').value);
    requestObj.insurance_carrier = document.getElementById('insurance_carrier').value;

    // shutoff type
    // 0-don't know,  1-knob,  2-lever
    var valve_type = 0;
    if (document.getElementById('knob_radio').checked) {
           valve_type = 1;
       }
    else
    if (document.getElementById('lever_radio').checked) {
           valve_type = 2;
    }

    requestObj.valve_type = valve_type;

    // vehicles
    requestObj.no_vehicles = document.getElementById('vehicle_checkbox').checked;
    const vehicles = [];
    vehicles[0]= new Object();
    vehicles[1]= new Object();
    vehicles[0].make_model = document.getElementById('make_model_0').value;
    vehicles[0].plate = document.getElementById('plate_0').value;
    vehicles[0].color = document.getElementById('color_0').value;
    vehicles[0].year = parseInt(document.getElementById('year_0').value);
    vehicles[1].make_model = document.getElementById('make_model_1').value;
    vehicles[1].plate = document.getElementById('plate_1').value;
    vehicles[1].color = document.getElementById('color_1').value;
    vehicles[1].year = parseInt(document.getElementById('year_1').value);

    // assign vehicles to requestObj
    requestObj.vehicles = vehicles;

    if (resident_type == RESIDENT_TYPE) {
        requestObj.last_update_date = new Date().toLocaleDateString();
    }
    else
    if ( loggedin_user == document.getElementById('user_id').value) {
        requestObj.last_update_date = new Date().toLocaleDateString();
    }
    else {
        requestObj.last_update_date = document.getElementById('last_update_date').value;
    }

    requestObj.notes = document.getElementById('notes').value;

    if (requestObj.userid === '') {
        alert('User Id is a required field');
        return;
    }

    if (requestObj.name === '') {
        alert('Head of household name is a required field');
        return;
    }

    // const person = {firstName:"John", lastName:"Doe", age:50, eyeColor:"blue"};
    jsonStr = '{ "resident": ' + JSON.stringify(requestObj) + '}';
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(jsonStr);
}
*/


// TODO: THIS FUNCTION MAY HAVE BECOME OBSOLETE.
// DO A SEARCH AND DELETE IT IF IT IS THE CASE.
function saveUser() {
  var request = new XMLHttpRequest();
  request.open('POST', '/saveresidentpartial', true)

  request.onload = function () {
    // Begin accessing JSON data here
    var json = JSON.parse(this.response);

    if (request.status >= 200 && request.status < 400) {
        alert('Record saved to database');
    }
    else {
        alert('Error saving record to database')
    }
  }

  var requestObj = new Object();
  requestObj.unit = parseInt(document.getElementById('unit').value);
  requestObj.userid = document.getElementById('user_id').value;
  requestObj.password = document.getElementById('user_password').value;

  requestObj.name = document.getElementById('name').value;
  requestObj.email = document.getElementById('email').value;
  requestObj.phone = document.getElementById('phone').value;

  requestObj.ownername = document.getElementById('owner_name').value;
  requestObj.owneremail = document.getElementById('owner_email').value;
  requestObj.ownerphone = document.getElementById('owner_phone').value;

  startdt = new Object();
  startdt.month = document.getElementById('startdt_month').value;
  startdt.year = document.getElementById('startdt_year').value;
  requestObj.startdt = startdt;
  requestObj.type = document.getElementById('resident_type').value;

  const occupants = [];
  occupants[0]= new Object();
  occupants[1]= new Object();
  occupants[2]= new Object();
  occupants[3]= new Object();
  occupants[4]= new Object();
  occupants[0].name = document.getElementById('occup1_name').value;
  occupants[0].email = document.getElementById('occup1_email').value;
  occupants[0].cc = document.getElementById('occup1_cc').checked;
  occupants[0].phone = document.getElementById('occup1_phone').value;
  occupants[1].name = document.getElementById('occup2_name').value;
  occupants[1].email = document.getElementById('occup2_email').value;
  occupants[1].cc = document.getElementById('occup2_cc').checked;
  occupants[1].phone = document.getElementById('occup2_phone').value;
  occupants[2].name = document.getElementById('occup3_name').value;
  occupants[2].email = document.getElementById('occup3_email').value;
  occupants[2].cc = document.getElementById('occup3_cc').checked;
  occupants[2].phone = document.getElementById('occup3_phone').value;
  occupants[3].name = document.getElementById('occup4_name').value;
  occupants[3].email = document.getElementById('occup4_email').value;
  occupants[3].cc = document.getElementById('occup4_cc').checked;
  occupants[3].phone = document.getElementById('occup4_phone').value;
  occupants[4].name = document.getElementById('occup5_name').value;
  occupants[4].email = document.getElementById('occup5_email').value;
  occupants[4].cc = document.getElementById('occup5_cc').checked;
  occupants[4].phone = document.getElementById('occup5_phone').value;
  requestObj.occupants = occupants;

  // emergency contact
  requestObj.emerg_name = document.getElementById('emerg_name').value;
  requestObj.emerg_email = document.getElementById('emerg_email').value;
  requestObj.emerg_phone = document.getElementById('emerg_phone').value;
  requestObj.emerg_has_key = document.getElementById('emerg_has_key').checked;


  if (requestObj.userid === '') {
    alert('User Id is a required field');
    return;
  }

  if (requestObj.name === '') {
    alert('Name is a required field');
    return;
  }

/*
  if (requestObj.email === '') {
    alert('Email is a required field');
    return;
  }
*/

  if (requestObj.type === '') {
    alert('Type of resident must be selected');
    return;
  }

  if (requestObj.password === '') {
    alert('Password must be filled out');
    return;
  }

  jsonStr = '{ "resident": ' + JSON.stringify(requestObj) + '}';
  request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  request.send(jsonStr);
}

function changePassword() {
    var user_id = document.getElementById("user_id_adm").value;
    var curr_password = document.getElementById("curr_password").value;
    var new_password = document.getElementById("new_password").value;
    var repeat_password = document.getElementById("repeat_password").value;

    // check the quality of the new password
    new_password = new_password.trim();
    repeat_password = repeat_password.trim();

    if (new_password != repeat_password) {
        alert("New password and Repeat password fields don't match");
        return;
    }

    if ( new_password.length < 6) {
        alert("New password doesn't have a minimum of 6 characters");
        return;
    }

    // prepare structure to send to backend
    var request = new XMLHttpRequest();
    post_url = "/" + window.loggedin_tenant_global + "/getresident";
    request.open('POST', post_url, true)
    var requestObj = new Object();
    requestObj.type = 'user';
    requestObj.tenant = window.loggedin_tenant_global;
    requestObj.id = user_id;
    jsonStr = '{ "request": ' + JSON.stringify(requestObj) + '}';
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(jsonStr);

    // invoke backend to check if the type current password matches current password
    request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);

      if (request.status >= 200 && request.status < 400) {
          if (json.response.status == 'not_found') {
              alert('Record not found for User Id '+user_id);
              return;
          }

          db_password = json.response.resident.password;

          if (db_password != curr_password) {
              console.log('db pass: '+db_password + ',  curr_password: '+curr_password);
              alert("The current password you entered doesn't match your current password on file");
              return;
          }

          // all is good, let's change the password
          change_db_password(json.response.resident.userid, new_password);
      }
      else {
          alert('Error retrieving user');
          return;
      }
    }
}

function change_db_password(user_id, new_password) {
    var request = new XMLHttpRequest();
    post_url = "/" + window.loggedin_tenant_global + "/changepassword";
    request.open('POST', post_url, true)

    // prepare structure to invoke backend
    console.log('user data: '+window.loggedin_tenant_global + '  ' + user_id + '  ' + new_password);
    var requestObj = new Object();
    requestObj.tenant = window.loggedin_tenant_global;
    requestObj.user_id = user_id;
    requestObj.password = new_password;
    jsonStr = '{ "resident": ' + JSON.stringify(requestObj) + '}';
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(jsonStr);

    // load data obtained from backend
    request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);

      if (request.status >= 200 && request.status < 400) {
          document.getElementById('curr_password').value = '';
          document.getElementById('new_password').value = '';
          document.getElementById('repeat_password').value = '';
          alert('New password saved to database');
      }
      else {
          alert('Error saving password to database');
      }
    }
}

function changeUserid() {
    var userid = document.getElementById("user_id").innerHTML;
    var unit = parseInt(document.getElementById("unit").innerHTML);
    var new_userid = document.getElementById("new_userid").value;
    var curr_password = document.getElementById("changeid_panel_password").value;

    if ( new_userid.length < 1) {
        alert("New user id cannot be blank");
        return;
    }

    // prepare structure to send to backend
    var request = new XMLHttpRequest();
    request.open('POST', '/getresident', true)
    var requestObj = new Object();
    requestObj.type = 'unit';
    requestObj.id = parseInt(unit);
    jsonStr = '{ "request": ' + JSON.stringify(requestObj) + '}';
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(jsonStr);

    // invoke backend to check if the current password typed in matches the current password
    request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);

      if (request.status >= 200 && request.status < 400) {
          if (json.response.status == 'not_found') {
              alert('Record not found for User Id '+userid);
              return;
          }

          db_password = json.response.resident.password;

          if (db_password != curr_password) {
              alert("The current password you entered doesn't match your password on file");
              return;
          }

          // all is good, let's change the password
          change_db_userid(json.response.resident.unit, new_userid);
      }
      else {
          alert('Error retrieving user');
          return;
      }
    }
}

function change_db_userid(unit, new_userid) {
    var request = new XMLHttpRequest();
    request.open('POST', '/changeuserid', true)

    // prepare structure to invoke backend
    var requestObj = new Object();
    requestObj.unit = parseInt(unit);
    requestObj.userid = new_userid;
    jsonStr = '{ "resident": ' + JSON.stringify(requestObj) + '}';
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(jsonStr);

    // load data obtained from backend
    request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);

      if (request.status >= 200 && request.status < 400) {
          document.getElementById('changeid_panel_password').value = '';
          document.getElementById('user_id').innerHTML = new_userid;
          alert('New user id saved to database');
      }
      else {
          alert('Error saving user id to database');
      }
    }
}


