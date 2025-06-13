
function onLoadAction() {
    window.loggedin_id_global = document.getElementById('loggedin-id').value;
    window.loggedin_userid_global = document.getElementById('loggedin-userid').value;
    window.loggedin_unit_global = document.getElementById('loggedin-unit').value;
    window.loggedin_name_global = document.getElementById('loggedin-name').value;
    window.loggedin_tenant_global = document.getElementById('loggedin-tenant').value.trim();
    window.loggedin_lang_global = document.getElementById('loggedin-lang').value;

//    document.getElementById("myAnchor").addEventListener("click", function(event){
//        handlesDeleteListingButton(event);
//        event.preventDefault()
//    });
}

function handleUnitSelected() {
    const selIndex = document.getElementById("unit").selectedIndex;
    if (selIndex == 0) {
        return;
    }
    const selOption = document.getElementById("unit").options[selIndex];
    const user_id = selOption.value;
    request = retrieveUser(user_id);

    request.onload = function () {
        // Begin accessing JSON data here
        var json = JSON.parse(this.response);

        if (request.status >= 200 && request.status < 400) {
            if (json.response.status == 'not_found') {
                console.log('not_found');
            }

            if (json.response.status === 'success') {
                document.getElementById('email').value = json.response.resident.email;
                document.getElementById('phone').value = json.response.resident.phone;
            }
        }
    }
}

/* this makes the text be only numbers, no decimal sign */
function isNumberKey(txt, evt) {
    var charCode = (evt.which) ? evt.which : evt.keyCode;
    /*
    if (charCode == 46) {
        //Check if the text already contains the . character
        if (txt.value.indexOf('.') === -1) {
            return true;
        }
        return false;
    }
    */
    if (charCode < 48 || charCode > 57) {
        return false;
    }
    return true;
}

