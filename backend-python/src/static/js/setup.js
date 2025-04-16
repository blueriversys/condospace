/*
   This is invoked by setup.html to handle announcement related operations.
   Also used by setup.html to load units, loadSetup()
*/


const ADMIN_TYPE = 0;
const BOARD_MEMBER_TYPE = 1;
const SECRETARY_TYPE = 2;
const RESIDENT_TYPE = 3;

var resident_type = RESIDENT_TYPE;

var uiSetupMap = new Map();
uiSetupMap.set('unit', "unit");
uiSetupMap.set('restype', "resident_type");
uiSetupMap.set('user_id', "user_id");
uiSetupMap.set('password', "password");
uiSetupMap.set('name', "name");
uiSetupMap.set('email', "email");
uiSetupMap.set('phone', "phone");
uiSetupMap.set('startdt_month', 'startdt_month');
uiSetupMap.set('startdt_year', 'startdt_year');
uiSetupMap.set('occup1_name', 'occup1_name');
uiSetupMap.set('occup1_email', 'occup1_email');
uiSetupMap.set('occup1_cc', 'occup1_cc');
uiSetupMap.set('occup1_phone', 'occup1_phone');
uiSetupMap.set('occup1_has_key', 'occup1_has_key');
uiSetupMap.set('occup2_name', 'occup2_name');
uiSetupMap.set('occup2_email', 'occup2_email');
uiSetupMap.set('occup2_cc', 'occup2_cc');
uiSetupMap.set('occup2_phone', 'occup2_phone');
uiSetupMap.set('occup2_has_key', 'occup2_has_key');
uiSetupMap.set('occup3_name', 'occup3_name');
uiSetupMap.set('occup3_email', 'occup3_email');
uiSetupMap.set('occup3_cc', 'occup3_cc');
uiSetupMap.set('occup3_phone', 'occup3_phone');
uiSetupMap.set('occup3_has_key', 'occup3_has_key');
uiSetupMap.set('occup4_name', 'occup4_name');
uiSetupMap.set('occup4_email', 'occup4_email');
uiSetupMap.set('occup4_cc', 'occup4_cc');
uiSetupMap.set('occup4_phone', 'occup4_phone');
uiSetupMap.set('occup4_has_key', 'occup4_has_key');
uiSetupMap.set('occup5_name', 'occup5_name');
uiSetupMap.set('occup5_email', 'occup5_email');
uiSetupMap.set('occup5_cc', 'occup5_cc');
uiSetupMap.set('occup5_phone', 'occup5_phone');
uiSetupMap.set('occup5_has_key', 'occup5_has_key');
uiSetupMap.set('emerg_name', 'emerg_name');
uiSetupMap.set('emerg_email', 'emerg_email');
uiSetupMap.set('emerg_phone', 'emerg_phone');
uiSetupMap.set('emerg_has_key', 'emerg_has_key');
uiSetupMap.set('owner_name', 'owner_name');
uiSetupMap.set('owner_email', 'owner_email');
uiSetupMap.set('owner_phone', 'owner_phone');
uiSetupMap.set('owner_address', 'owner_address');
uiSetupMap.set('rental_unit_checkbox', 'rental_unit_checkbox');
uiSetupMap.set('oxygen_equipment', 'oxygen_equipment');
uiSetupMap.set('limited_mobility', 'limited_mobility');
uiSetupMap.set('routine_visits', 'routine_visits');
uiSetupMap.set('has_pet', 'has_pet');
uiSetupMap.set('bike_count', 'bike_count');
uiSetupMap.set('insurance_carrier', 'insurance_carrier');
uiSetupMap.set('knob_radio', 'knob_radio');
uiSetupMap.set('lever_radio', 'lever_radio');
uiSetupMap.set('vehicle_checkbox', 'vehicle_checkbox');
uiSetupMap.set('make_model_0', 'make_model_0');
uiSetupMap.set('plate_0', 'plate_0');
uiSetupMap.set('color_0', 'color_0');
uiSetupMap.set('year_0', 'year_0');
uiSetupMap.set('make_model_1', 'make_model_1');
uiSetupMap.set('plate_1', 'plate_1');
uiSetupMap.set('color_1', 'color_1');
uiSetupMap.set('year_1', 'year_1');
uiSetupMap.set('notes', 'notes');

var uiProfileMap = new Map();
uiProfileMap.set('unit', "selected_unit");
uiProfileMap.set('restype', "resident_type");
uiProfileMap.set('name', "name");
uiProfileMap.set('email', "email");
uiProfileMap.set('phone', "phone");
uiProfileMap.set('start_month', 'startdt_month');
uiProfileMap.set('start_year', 'startdt_year');
uiProfileMap.set('occup1_name', 'occup1_name');
uiProfileMap.set('occup1_email', 'occup1_email');
uiProfileMap.set('occup1_cc', 'occup1_cc');
uiProfileMap.set('occup1_phone', 'occup1_phone');
uiProfileMap.set('occup1_has_key', 'occup1_has_key');
uiProfileMap.set('occup2_name', 'occup2_name');
uiProfileMap.set('occup2_email', 'occup2_email');
uiProfileMap.set('occup2_cc', 'occup2_cc');
uiProfileMap.set('occup2_phone', 'occup2_phone');
uiProfileMap.set('occup2_has_key', 'occup2_has_key');
uiProfileMap.set('occup3_name', 'occup3_name');
uiProfileMap.set('occup3_email', 'occup3_email');
uiProfileMap.set('occup3_cc', 'occup3_cc');
uiProfileMap.set('occup3_phone', 'occup3_phone');
uiProfileMap.set('occup3_has_key', 'occup3_has_key');
uiProfileMap.set('occup4_name', 'occup4_name');
uiProfileMap.set('occup4_email', 'occup4_email');
uiProfileMap.set('occup4_cc', 'occup4_cc');
uiProfileMap.set('occup4_phone', 'occup4_phone');
uiProfileMap.set('occup4_has_key', 'occup4_has_key');
uiProfileMap.set('occup5_name', 'occup5_name');
uiProfileMap.set('occup5_email', 'occup5_email');
uiProfileMap.set('occup5_cc', 'occup5_cc');
uiProfileMap.set('occup5_phone', 'occup5_phone');
uiProfileMap.set('occup5_has_key', 'occup5_has_key');
uiProfileMap.set('emerg_name', 'emerg_name');
uiProfileMap.set('emerg_email', 'emerg_email');
uiProfileMap.set('emerg_phone', 'emerg_phone');
uiProfileMap.set('emerg_has_key', 'emerg_has_key');
uiProfileMap.set('owner_name', 'owner_name');
uiProfileMap.set('owner_email', 'owner_email');
uiProfileMap.set('owner_phone', 'owner_phone');
uiProfileMap.set('owner_address', 'owner_address');
uiProfileMap.set('rental_unit_checkbox', 'rental_unit_checkbox');
uiProfileMap.set('oxygen_equipment', 'oxygen_equipment');
uiProfileMap.set('limited_mobility', 'limited_mobility');
uiProfileMap.set('routine_visits', 'routine_visits');
uiProfileMap.set('has_pets', 'has_pets');
uiProfileMap.set('bike_count', 'bike_count');
uiProfileMap.set('insurance_carrier', 'insurance_carrier');
uiProfileMap.set('knob_radio', 'knob_radio');
uiProfileMap.set('lever_radio', 'lever_radio');
uiProfileMap.set('vehicle_checkbox', 'vehicle_checkbox');
uiProfileMap.set('make_model_0', 'make_model_0');
uiProfileMap.set('plate_0', 'plate_0');
uiProfileMap.set('color_0', 'color_0');
uiProfileMap.set('year_0', 'year_0');
uiProfileMap.set('make_model_1', 'make_model_1');
uiProfileMap.set('plate_1', 'plate_1');
uiProfileMap.set('color_1', 'color_1');
uiProfileMap.set('year_1', 'year_1');
uiProfileMap.set('notes', 'notes');


/* invoked by setup.html */
function onLoadAction() {
    window.loggedin_id_global = document.getElementById('loggedin-id').value;
    window.loggedin_userid_global = document.getElementById('loggedin-userid').value;
    window.loggedin_unit_global = document.getElementById('loggedin-unit').value;
    window.loggedin_name_global = document.getElementById('loggedin-name').value;
    window.loggedin_tenant_global = document.getElementById('loggedin-tenant').value.trim();
    window.loggedin_lang_global = document.getElementById('loggedin-lang').value;
    setupRetrieveUsers(window.loggedin_tenant_global);
}

function setupRetrieveUsers(tenant) {
    var request = new XMLHttpRequest()
    post_url = "/" + window.loggedin_tenant_global + "/getresidents";
    request.open('POST', post_url, true);

    var requestObj = new Object();
    requestObj.tenant = tenant;
    jsonStr = '{ "request": ' + JSON.stringify(requestObj) + '}';
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

    request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);

      if (request.status >= 200 && request.status < 400) {
          populateTable(json, 'adm_table_id', 'adm');
          populateTable(json, 'residents_table_id', 'resident');
      }
      else {
          alert('Error retrieving residents list')
      }
    }

    request.send(jsonStr);
}


function retrieveUser() {
  var request = new XMLHttpRequest();
  /*
  var unit_number = parseInt(document.getElementById('unit_delete').value.trim());

  if ( isNaN(unit_number) ) {
      alert('Type or select a unit number to retrieve data');
      return;
  }
*/


  var user_id = document.getElementById('user_id_delete').value;
  post_url = "/" + window.loggedin_tenant_global + "/getresident";
  request.open('POST', post_url, true);

  request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);

      if (request.status >= 200 && request.status < 400) {
          if (json.response.status == 'not_found') {
              alert('Record not found for unit ' + user_id);
              return;
          }

          document.getElementById('name_delete').value = json.response.resident.name;
          document.getElementById('email_delete').value = json.response.resident.email;
          document.getElementById('phone_delete').value = json.response.resident.phone;
      }
      else {
          alert('Error retrieving user')
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


function deleteUser() {
  var request = new XMLHttpRequest();
  var user_id = document.getElementById('user_id_delete').value;

  if (user_id === 'none') {
      alert("Select a unit to be deleted");
      return;
  }

  if ( confirm("Confirm you want to delete unit "+user_id) == false) {
      return;
  }

  request.open('POST', '/deleteresident', true)

  request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);

      if (request.status >= 200 && request.status < 400) {
          if (json.response.status == 'success') {
              alert('Unit '+user_id+' deleted from the database');
              location.reload();
              return;
          }
          else {
              alert('An error happened trying to delete Unit '+user_id);
              return;
          }
      }
      else {
          alert('Error deleting user');
          return;
      }
    }

    var requestObj = new Object();
    requestObj.type = 'user';
    requestObj.tenant = document.getElementById('loggedin-tenant').value;
    requestObj.value = user_id;

    // const person = {firstName:"John", lastName:"Doe", age:50, eyeColor:"blue"};
    jsonStr = '{ "resident": ' + JSON.stringify(requestObj) + '}';
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(jsonStr);
}

function deleteUserParam(user_id) {
  var request = new XMLHttpRequest();

  if (user_id === 'none') {
      alert("Select a unit to be deleted");
      return;
  }

  if ( confirm("Confirm you want to delete unit "+user_id) == false) {
      return;
  }

  request.open('POST', '/deleteresident', true)

  request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);

      if (request.status >= 200 && request.status < 400) {
          if (json.response.status == 'success') {
              alert('Unit '+user_id+' deleted from the database');
              location.reload();
              return;
          }
          else {
              alert('An error happened trying to delete Unit '+user_id);
              return;
          }
      }
      else {
          alert('Error deleting user');
          return;
      }
    }

    var requestObj = new Object();
    requestObj.type = 'user';
    requestObj.tenant = document.getElementById('loggedin-tenant').value;
    requestObj.value = user_id;

    // const person = {firstName:"John", lastName:"Doe", age:50, eyeColor:"blue"};
    jsonStr = '{ "resident": ' + JSON.stringify(requestObj) + '}';
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(jsonStr);
}

