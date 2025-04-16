
function onLoadAction() {
    window.loggedin_id_global = document.getElementById('loggedin-id').value;
    window.loggedin_userid_global = document.getElementById('loggedin-userid').value;
    window.loggedin_unit_global = document.getElementById('loggedin-unit').value;
    window.loggedin_name_global = document.getElementById('loggedin-name').value;
    window.loggedin_tenant_global = document.getElementById('loggedin-tenant').value.trim();
    window.loggedin_lang_global = document.getElementById('loggedin-lang').value;
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


// TODO: uploadFileProgress() is a duplication of a function by the same name in upload.js.
function uploadFileProgress(convname, fileControl, barControl) {
    // retrieve the file object from the DOM
    let file = document.getElementById(fileControl).files[0];

    // test to make sure the user chose a file
    if (file == undefined || file == "") {
        showMsgBox( gettext('Please select a file before clicking the upload button.') );
        return;
    }

    //print file details
    console.log("File Name : ",file.name);
    console.log("File size : ",file.size);
    console.log("File type : ",file.type);

    // create form data to send via XHR request
    var formData = new FormData();
    formData.append("file", file);
    formData.append("filesize", ''+file.size); // append only takes string as 2nd arg
    formData.append("convname", convname);

    //create XHR object to send request
    var request = new XMLHttpRequest();

    var progressBar = document.getElementById(barControl);
    progressBar.value = 0;
    progressBar.style.display="inline";

    // add a progress event handler to the AJAX request
    request.upload.addEventListener('progress', event => {
        let totalSize = event.total; // total size of the file in bytes
        let loadedSize = event.loaded; // loaded size of the file in bytes
        // calculate percentage
        var percent = (event.loaded / event.total) * 100;
        progressBar.value = Math.round(percent);
    });

    // initializes a newly-created request
    post_url = "/" + window.loggedin_tenant_global + "/upload";
    request.open('POST', post_url, true);

    // ask to be notified when the upload is finished
    request.onreadystatechange = () => {
        if (request.readyState == 4 && request.status == 200) {
            progressBar.value = 100;
            showMsgBoxSuccess( gettext('File') + ' ' + file.name + ' ' + gettext('successfully uploaded') );
            progressBar.style.display="none";
            location.reload();
        }
    };

    // send request to the server
    request.send(formData);
}

function deleteFile(filepath, filename) {
    deleteFileCommon(filepath, filename, 'no');
}



