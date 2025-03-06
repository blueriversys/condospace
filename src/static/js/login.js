function onLoadAction() {
}


function togglePassVisibility() {
    var pass_field = document.getElementById("pass_field");
    if (pass_field.type === "password") {
        pass_field.type = "text";
    } else {
        pass_field.type = "password";
    }
}


