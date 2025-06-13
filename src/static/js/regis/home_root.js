
function onLoadAction() {
    window.loggedin_lang_global = document.getElementById('loggedin-lang').value;
}

function changeCondoIdIcon(type) {
    if (type === 'success') {
        icon = 'fa-check';
        color = 'green';
    }
    else {
        icon = 'fa-times';
        color = 'red';
    }

    var elem = document.getElementById('condo_id_group');
    elem.classList = `fa ${icon}`;
    elem.style = `color: ${color}; display: block; font-size: 20px; padding-left: 3px;`;
}

function condoIdOnBlur() {
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
                changeCondoIdIcon('success');
                return;
            }
            else {
//                var elem = document.getElementById('condo_id_group');
//                elem.classList = "fa fa-times";
//                elem.style = "color: red; display: block; line-height: 40px; padding-left: 3px;";
                changeCondoIdIcon('error');
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


function sendCondoRegistrationForm() {
    company_id = document.getElementById('company-id').value.trim();
    name = document.getElementById('name').value.trim();
    email = document.getElementById('email').value.trim();
    phone = document.getElementById('phone').value.trim();
    pref_language = document.getElementById('pref-language').value;
    condo_id = document.getElementById('condo-id').value.trim();
    condo_name = document.getElementById('condo-name').value.trim();
    condo_tagline = document.getElementById('condo-tagline').value.trim();
    condo_address = document.getElementById('condo-address').value.trim();

    var condo_address_number = '';

    if ( document.getElementById('condo-address-number') != null) {
        condo_address_number = document.getElementById('condo-address-number').value.trim();
    }

    condo_zip = document.getElementById('condo-zip').value.trim();
    condo_city = document.getElementById('condo-city').value.trim();
    condo_state = document.getElementById('condo-state').value.trim();
    use_default_img = document.getElementById('use-default-img');

    if (name.length == 0 ) {
        showMsgBox( gettext("Admin Name cannot be empty") );
        return;
    }

    if (condo_id.length == 0 || condo_id.indexOf(" ") != -1 ) {
        showMsgBox( gettext("Condo Id cannot be empty, cannot have spaces") );
        return;
    }

    validateEmail('email', true);
    validatePhone('phone', true);

    if (condo_name.length == 0 ) {
        showMsgBox( gettext("Condominium Name cannot be empty") );
        return;
    }

    if (condo_city.length == 0  ||  condo_state.length == 0) {
        showMsgBox( gettext("Condominium Location cannot be empty") );
        return;
    }

    //create XHR object to send request
    var request = new XMLHttpRequest();

    // initializes a newly-created request
    request.open('POST', 'register_condo', true);

    // create form data to send via XHR request
    var formData = new FormData();

    if ( !use_default_img.checked ) {
        img_file = document.getElementById('condo-img-file').files[0];
        if ( img_file == null ) {
            showMsgBox( gettext("You should either check the 'Use a default picture' box or select a picture file") );
            return;
        }
        formData.append("home_pic",  img_file);
        formData.append("use_default_img", "no");
    }
    else {
        formData.append("use_default_img", "yes")
    }

    formData.append("company_id", company_id);
    formData.append("name", name);
    formData.append("email", email);
    formData.append("phone", phone);
    formData.append("pref_language", pref_language);
    formData.append("condo_id", condo_id);
    formData.append("condo_name", condo_name);
    formData.append("condo_tagline", condo_tagline);
    formData.append("condo_address", condo_address);
    formData.append("condo_address_number", condo_address_number);
    formData.append("condo_zip", condo_zip);
    formData.append("condo_city", condo_city);
    formData.append("condo_state", condo_state);
    formData.append("invoke_origin", 'web_gui');

    if (pref_language == 'pt')
        formData.append('condo_country', 'BR');
    else
        formData.append('condo_country', 'US');

    registration_result = 'error';
    text = gettext('One moment, as we register your condominium on our database...');

    let dialog = bootbox.dialog({
        title: text,
        message: '<p><i class="fa fa-spinner fa-spin" style="font-size:24px"></i> Loading...</p>',
        buttons: {
                ok: { label: "OK", className: 'btn-info',
                    callback: function() {
                        if (registration_result === 'error') {
                            return;
                        }
                        url = "../" + condo_id + "/" + "login";
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
                    text = gettext('Condo Id entered already exists in the system.');
                    dialog.find('.bootbox-body').html(text);
                }
            }
            else {
                text = gettext('Error registering the new condominium.');
                dialog.find('.bootbox-body').html(text);
            }
        }
    });

}

function pictureSelectAction(fileControl, imageControl) {
    file = document.getElementById(fileControl).files[0];
    var reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = function (e) {
        var image = new Image();
        image.src = e.target.result;
        image.onload = function () {
            document.getElementById(imageControl).src = image.src;
            document.getElementById(imageControl).style.display = 'block';
        };
    }
}

function useDefaultImgClicked() {
    if (document.getElementById('use-default-img').checked) {
        document.getElementById('condo-img-file').style.display = 'none';
        document.getElementById('condo-img').style.display = 'none';
    }
    else {
        document.getElementById('condo-img-file').style.display = 'block';
        //document.getElementById('condo-img').style.display = 'block';
    }
}