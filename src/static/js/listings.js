
function onLoadAction() {
    window.loggedin_id_global = document.getElementById('loggedin-id').value;
    window.loggedin_userid_global = document.getElementById('loggedin-userid').value;
    window.loggedin_unit_global = document.getElementById('loggedin-unit').value;
    window.loggedin_name_global = document.getElementById('loggedin-name').value;
    window.loggedin_tenant_global = document.getElementById('loggedin-tenant').value.trim();
    window.loggedin_lang_global = document.getElementById('loggedin-lang').value;
}

function handleUnitSelected() {

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

