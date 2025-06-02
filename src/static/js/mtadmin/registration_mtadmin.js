
function onLoadAction() {
    window.loggedin_lang_global = document.getElementById('loggedin-lang').value;
}

function changeCompanyIdIcon(type) {
    if (type === 'success') {
        icon = 'fa-check';
        color = 'green';
    }
    else {
        icon = 'fa-times';
        color = 'red';
    }

    var elem = document.getElementById('company_id_group');
    elem.classList = `fa ${icon}`;
    elem.style = `color: ${color}; display: block; font-size: 20px; padding-left: 3px;`;
}

function companyIdOnBlur() {
    condo_id = document.getElementById('condo-id').value.trim();

    if (condo_id.length == 0 || condo_id.indexOf(" ") != -1 ) {
        changeCondoIdIcon('error');
        return;
    }

    //create XHR object to send request
    var request = new XMLHttpRequest();

    // initializes a newly-created request
    request.open('POST', 'check_condo_id', true);

    // create form data to send via XHR request
    var formData = new FormData();
    formData.append("condo_id", condo_id);

    request.onload = function () {
        // Begin accessing JSON data here
        var json = JSON.parse(this.response);
        console.log(json);

        if (request.status >= 200 && request.status < 400) {
            if (json.status === 'success') {
//                var elem = document.getElementById('condo_id_group');
//                elem.classList = "fa fa-check";
//                elem.style = "color: green; display: block; line-height: 40px; padding-left: 3px;";
                changeCompanyIdIcon('success');
                return;
            }
            else {
//                var elem = document.getElementById('condo_id_group');
//                elem.classList = "fa fa-times";
//                elem.style = "color: red; display: block; line-height: 40px; padding-left: 3px;";
                changeCompanyIdIcon('error');
                return;
            }
        }
        else {
            showMsgBox( gettext('Error registering new condominium') );
            return;
        }
    }

    // send request to the server
    request.send(formData);
}


function sendCompanyRegistrationForm() {
    company_name = document.getElementById('company-name').value.trim();
    company_email = document.getElementById('company-email').value.trim();
    company_phone = document.getElementById('company-phone').value.trim();
    pref_language = document.getElementById('pref-language').value;
    company_id = document.getElementById('company-id').value.trim();
    company_address = document.getElementById('company-address').value.trim();
    company_address_number = document.getElementById('company-address-number').value.trim();
    company_address_complement = document.getElementById('company-address-complement').value.trim();
    company_zip = document.getElementById('company-zip').value.trim();
    company_city = document.getElementById('company-city').value.trim();
    company_state = document.getElementById('company-state').value.trim();
    company_country = document.getElementById('company-country').value.trim();

    if (company_name.length == 0 ) {
        showMsgBox( gettext("Company Name cannot be empty") );
        return;
    }

    if (company_id.length == 0 || company_id.indexOf(" ") != -1 ) {
        showMsgBox( gettext("Company Id cannot be empty, cannot have spaces") );
        return;
    }

    validateEmail('company-email', true);
    validatePhone('company-phone', true);

    if (company_city.length == 0  ||  company_city.length == 0) {
        showMsgBox( gettext("Company city cannot be empty") );
        return;
    }

    //create XHR object to send request
    var request = new XMLHttpRequest();

    // initializes a newly-created request
    request.open('POST', 'register_company', true);

    // create form data to send via XHR request
    var formData = new FormData();

    formData.append("name", company_name);
    formData.append("email", company_email);
    formData.append("phone", company_phone);
    formData.append("pref_language", pref_language);
    formData.append("company_id", company_id);
    formData.append("address", company_address);
    formData.append("address_number", company_address_number);
    formData.append("address_complement", company_address_complement);
    formData.append("zip", company_zip);
    formData.append("city", company_city);
    formData.append("state", company_state);
    formData.append("country", company_country);
    formData.append("invoke_origin", 'web_gui');

    registration_result = 'error';
    text = gettext('One moment, as we register your company on our database...');

    let dialog = bootbox.dialog({
        title: text,
        message: '<p><i class="fa fa-spinner fa-spin" style="font-size:24px"></i> Loading...</p>',
        buttons: {
                ok: { label: "OK", className: 'btn-info',
                    callback: function() {
                        if (registration_result === 'error') {
                            return;
                        }
                        url =`/multi-condo/${company_id}/login`;
                        window.location.replace(url);
                    }
                }
        }
    });

    dialog.init(function() {
        //setTimeout(function() { dialog.find('.bootbox-body').html('After 5secs, the server has responded!'); }, 5000);

        // send request to the server
        request.send(formData);

        request.onload = function () {
            // Begin accessing JSON data here
            var json = JSON.parse(this.response);
            console.log(json);

            if (request.status >= 200 && request.status < 400) {
                if (json.status === 'success') {
                    text =  gettext('Success! We sent login info as well as instructions to the email provided.');
                    dialog.find('.bootbox-body').html(text);
                    registration_result = 'success';
                }
                else {
                    text = gettext('Company Id entered already exists in the system.');
                    dialog.find('.bootbox-body').html(text);
                }
            }
            else {
                text = gettext('Error registering the new company.');
                dialog.find('.bootbox-body').html(text);
            }
        }
    });

}

