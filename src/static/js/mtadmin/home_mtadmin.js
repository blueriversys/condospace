

function onLoadAction() {
    window.loggedin_user_user_id_global = document.getElementById('loggedin_user_user_id').value;
    window.loggedin_user_company_id_global = document.getElementById('loggedin_user_company_id').value.trim();
    window.loggedin_lang_global = document.getElementById('loggedin_user_language').value;
    fillCompanyInfo();
}

function fillCompanyInfo() {
    var request = new XMLHttpRequest();
    console.log(`company id ${window.loggedin_user_company_id_global}`);
    get_url = `/multi-condo/${window.loggedin_user_company_id_global}/get_company_info`;
    request.open('GET', get_url, true);

    request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);

      if (request.status >= 200 && request.status < 400) {
          document.getElementById('company_name_header').innerHTML = json['company_name'];
          document.getElementById('company-name').value = json['company_name'];
          document.getElementById('company-email').value = json['email'];
          document.getElementById('company-phone').value = json['phone'];
          document.getElementById('company-address').value = json['address'];
          document.getElementById('company-address-number').value = json['number'];
          document.getElementById('company-address-complement').value = json['complement'];
          document.getElementById('company-zip').value = json['zip'];
          document.getElementById('company-city').value = json['city'];
          document.getElementById('company-state').value = json['state'];
          document.getElementById('company-country').value = json['country'];
      }
      else {
          showMsgBox( gettext('Error retrieving announcements list') );
      }

    }
    request.send();
}

function updateCompanyInfo() {
    company_name = document.getElementById('company-name').value.trim();
    company_email = document.getElementById('company-email').value.trim();
    company_phone = document.getElementById('company-phone').value.trim();
    company_address = document.getElementById('company-address').value.trim();
    company_address_number = document.getElementById('company-address-number').value.trim();
    company_address_complement = document.getElementById('company-address-complement').value.trim();
    company_zip = document.getElementById('company-zip').value.trim();
    company_city = document.getElementById('company-city').value.trim();
    company_state = document.getElementById('company-state').value.trim();
    company_country = document.getElementById('company-country').value.trim();
    const selIndex = document.getElementById("pref-language").selectedIndex;
    const selOption = document.getElementById("pref-language").options[selIndex];
    const company_lang = selOption.value;

    if ( company_name.length == 0  ||  company_address.length == 0  ||  company_city.length == 0  ||  company_state.length == 0 ) {
        showMsgBox( gettext("Company Name, Address, ZIP and Location are required fields") );
        return;
    }

    if ( company_zip.length == 0 ) {
       showMsgBox( gettext('ZIP is a required field') );
       return;
    }

    showSpinner();

    // here we make a request to "upload_link"
    var request = new XMLHttpRequest();
    post_url = `/multi-condo/${window.loggedin_user_company_id_global}/update_company_info`;
    request.open('POST', post_url, true)

    request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);

      if (request.status >= 200 && request.status < 400) {
          if (json.response.status == 'error') {
              showMsgBox( gettext('Error uploading company info') );
          }
          else {
              location.reload(true);
              console.log('here after reload()')
          }
      }
      else {
          showMsgBox( gettext('Error uploading company info') );
      }

      return;
    }

    var requestObj = new Object();
    requestObj.email = company_email;
    requestObj.phone = company_phone;
    requestObj.name = company_name;
    requestObj.address = company_address;
    requestObj.number = company_address_number;
    requestObj.complement = company_address_complement;
    requestObj.zip = company_zip;
    requestObj.city = company_city;
    requestObj.state = company_state;
    requestObj.country = company_country;
    requestObj.language = company_lang;
    jsonStr = '{ "request": ' + JSON.stringify(requestObj) + '}';
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(jsonStr);
}

function handleLogoChange(file_input, img_tag) {
    handlePictureChange(file_input, img_tag);
    post_url = `/multi-condo/${window.loggedin_user_company_id_global}/upload_file`;
    uploadFileNoProgress(file_input, post_url)
}



