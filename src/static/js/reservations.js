
var rsv_date = new Map();
var rsv_time_from = new Map();
var rsv_time_to = new Map();

function onLoadAction() {
    window.loggedin_id_global = document.getElementById('loggedin-id').value;
    window.loggedin_userid_global = document.getElementById('loggedin-userid').value;
    window.loggedin_unit_global = document.getElementById('loggedin-unit').value;
    window.loggedin_name_global = document.getElementById('loggedin-name').value;
    window.loggedin_tenant_global = document.getElementById('loggedin-tenant').value.trim();
    window.loggedin_lang_global = document.getElementById('loggedin-lang').value;
    changeTableDateTime();
}

function getMonthExt(month) {
    month -= 1;
    month_ext_en = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    month_ext_pt = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
    if (window.loggedin_lang_global === 'en') {
        return month_ext_en[month];
    }
    return month_ext_pt[month];
}

function changeTableDateTime() {
    counter = 0;
    while (true) {
        if ( document.getElementById(`time_from_h_${counter}`) == null) {
            break;
        }

        amenity_id = document.getElementById('amenity_id_'+counter).value;
        date_y = document.getElementById('date_y_'+counter).value;
        date_m = document.getElementById('date_m_'+counter).value;
        date_d = document.getElementById('date_d_'+counter).value;
        time_from_h = document.getElementById('time_from_h_'+counter).value;
        time_from_m = document.getElementById('time_from_m_'+counter).value;
        time_to_h = document.getElementById('time_to_h_'+counter).value;
        time_to_m = document.getElementById('time_to_m_'+counter).value;

        // save this data on the global vars for validation later
        if ( rsv_date.get(amenity_id) == null ) {
           rsv_date.set(amenity_id, new Array());
           rsv_time_from.set(amenity_id, new Array());
           rsv_time_to.set(amenity_id, new Array());
        }

        date_arr = rsv_date.get(amenity_id);
        time_from_arr = rsv_time_from.get(amenity_id);
        time_to_arr = rsv_time_to.get(amenity_id);

        date_arr.push( {'y': date_y, 'm': date_m, 'd': date_d} );
        time_from_arr.push( {'h': time_from_h, 'm': time_from_m} );
        time_to_arr.push( {'h': time_to_h, 'm': time_to_m} );

        rsv_date.set(amenity_id, date_arr);
        rsv_time_from.set(amenity_id, time_from_arr);
        rsv_time_to.set(amenity_id, time_to_arr);

        month_ext = getMonthExt( date_m );

        if (date_d < 10) {
            date_d = '0' + date_d;
        }

        if ( time_from_h < 10 ) {
            time_from_h = '0'+time_from_h;
        }

        if ( time_from_m < 10 ) {
            time_from_m = '0'+time_from_m;
        }

        if ( time_to_h < 10 ) {
            time_to_h = '0'+time_to_h;
        }

        if ( time_to_m < 10 ) {
            time_to_m = '0'+time_to_m;
        }

        // set date and time on the screen
        document.getElementById(`td_date_id_${counter}`).innerText = `${date_d}-${month_ext}-${date_y}`;
        document.getElementById(`td_time_id_${counter}`).innerText = `${time_from_h}:${time_from_m} - ${time_to_h}:${time_to_m}`;

        counter += 1;
    }
}

function retrieveUser() {
    user_id =  document.getElementById("user_id").value;
    name = document.getElementById(user_id + '_name').value.trim();
    email = document.getElementById(user_id + '_email').value.trim();
    phone = document.getElementById(user_id + '_phone').value.trim();
    document.getElementById('name').value = name;
    document.getElementById('email').value = email;
    document.getElementById('phone').value = phone;
}

function storeFineData(index) {
    window.user_id = document.getElementById(index + "_user_id").value;
    window.fine_id = document.getElementById(index + "_fine_id").value;
    window.name = document.getElementById(index + "_name").value;
    window.email = document.getElementById(index + "_email").value;
    window.amount = document.getElementById(index + "_amount").value;
    window.descr = document.getElementById(index + "_descr").value;
    window.due_date_y = document.getElementById(index + "_due_date_y").value;
    window.due_date_m = document.getElementById(index + "_due_date_m").value;
    window.due_date_d = document.getElementById(index + "_due_date_d").value;
}

function saveAmenity() {
    user_id = loggedin_userid_global;
    descr = document.getElementById("descr").value.trim();
    use_default_img = document.getElementById('use-default-img');
    paid_amenity = document.getElementById("paid_radio").checked ? true : false;

    if ( paid_amenity ) {
        send_email = document.getElementById('send_email_checkbox').checked ? true : false;
    }
    else {
        send_email = false;
    }

    if ( descr.length == 0) {
        showMsgBox( gettext('Description is a required field') );
        return;
    }

    var request = new XMLHttpRequest();
    post_url = "/" + window.loggedin_tenant_global + "/save_amenity";
    request.open('POST', post_url, true);

    showSpinner();

    request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);

      if (request.status >= 200 && request.status < 400) {
          if (json.response.status == 'success') {
              //showMsgBoxSuccess( gettext('Record saved to database') );
          }
          else {
              showMsgBox( gettext('Error saving record to database') );
          }
      }
      else {
          showMsgBox( gettext('Error saving record to database') );
      }

      location.reload();
    }

    // create form data to send via XHR request
    var formData = new FormData();
    formData.append('tenant', loggedin_tenant_global);
    formData.append('created_by', user_id);
    formData.append('descr', descr);
    formData.append('paid_amenity', String(paid_amenity));
    formData.append('send_email', String(send_email));

    if ( use_default_img.checked ) {
        index = document.getElementById('default_img_id').selectedIndex;
        default_img_name = document.getElementById('default_img_id').options[index].value;

        if ( default_img_name == 'none' ) {
            showMsgBox( gettext('Selecting a default image name is required') );
            return;
        }

        formData.append("use_default_img", "yes");
        formData.append("default_img_name", default_img_name);
    }
    else {
        formData.append("use_default_img", "no");
        img_file = document.getElementById('amenity_img_file').files[0];

        if ( img_file == null ) {
            showMsgBox( gettext("You should either check the 'Use a default picture' box or select a picture file") );
            return;
        }

        formData.append("amenity_pic",  img_file);
    }

    request.send(formData);
}


function pictureSelectAction(img_file_control, img_control) {
    file = document.getElementById('amenity_img_file').files[0];
    var reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = function (e) {
        var image = new Image();
        image.src = e.target.result;
        image.onload = function () {
            document.getElementById('amenity_img_1').src = image.src;
            document.getElementById('amenity_img_1').style.display = 'block';
        };
    }
}

function defaultImageHandler() {
    pic_chosen = document.getElementById('default_img_id').value;
    document.getElementById('amenity_img_2').src = pic_chosen;
    document.getElementById('amenity_img_2').style.display = 'block';
}


function useDefaultImgClicked(button_div, img_div, dropdown_div) {
    if (document.getElementById('use-default-img').checked) {
        document.getElementById('img_group_1').style.display = 'none';  // hide the button's div
        document.getElementById('img_group_2').style.display = 'block';
    }
    else {
        document.getElementById('img_group_1').style.display = 'block';
        document.getElementById('img_group_2').style.display = 'none';
    }
}

function deleteAmenity( index ) {
    var request = new XMLHttpRequest();
    post_url = "/" + window.loggedin_tenant_global + "/delete_amenity";
    request.open('POST', post_url, true);

    /* retrieve fields from browser's memory */
    //user_id = document.getElementById("user_id").value;
    amenity_id = index;

    request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);

      if (request.status >= 200 && request.status < 400) {
          if (json.response.status == 'success') {
              showMsgBoxSuccess( gettext('Record deleted from the database') );
          }
          else
          if ( json.response.status == 'found_rsv' ) {
              showMsgBox( gettext('Cannot delete, reservation found for this amenity') );
          }
          else {
              showMsgBox( gettext('Error deleting record') );
          }
      }
      else {
          showMsgBox( gettext('Error deleting record') );
      }

      location.reload();
    }

    var requestObj = new Object();
    requestObj.tenant = loggedin_tenant_global;
    //requestObj.user_id = user_id;
    requestObj.amenity_id = amenity_id;
    jsonStr = '{ "amenity": ' + JSON.stringify(requestObj) + '}';
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(jsonStr);
}

function storeReservationData(index, send_email) {
    window.amenity_id = index;
    window.send_email = send_email;
}

function getIntegerTime(time_h, time_m) {
    time_h = Number(time_h);
    time_m = Number(time_m);
    ret_time = time_h * 100;
    ret_time = ret_time + time_m;
    console.log('calc time: '+ time_h + ':' + time_m + ' = ' +ret_time);
    return ret_time;
}

function validateTime(date_y, date_m, date_d, from_h, from_m, to_h, to_m) {
    result = true;
    from_time = getIntegerTime(from_h, from_m);
    to_time = getIntegerTime(to_h, to_m);

    if ( from_time >= to_time) {
        result = false;
    }
    return result;
}

function checkConflict(amenity_id, date_y, date_m, date_d, from_h, from_m, to_h, to_m) {
    result = true;
    from_time = getIntegerTime(from_h, from_m);
    to_time = getIntegerTime(to_h, to_m);

    amenity_id = amenity_id.toString();
    date_arr = rsv_date.get(amenity_id);
    time_from_arr = rsv_time_from.get(amenity_id);
    time_to_arr = rsv_time_to.get(amenity_id);

    if (date_arr == null || time_from_arr == null || time_to_arr == null ) {
        //alert('some array is equals to null');
        return true;
    }

    for (i=0; i<date_arr.length; i++) {
        if ( date_y == date_arr[i].y && date_m == date_arr[i].m && date_d == date_arr[i].d ) {

            e_from_time = getIntegerTime(time_from_arr[i].h, time_from_arr[i].m);
            e_to_time = getIntegerTime(time_to_arr[i].h, time_to_arr[i].m);

            if (from_time == e_from_time &&  to_time == e_to_time ) {
                result = false;
                //alert('break 1');
                break;
            }

            // compare from_time
            if ( (from_time >= e_from_time && from_time < e_to_time) ) {
                //console.log('from time invalid');
                result = false;
                //alert('break 2');
                break;
            }

            // compare to_time
            if ( to_time > e_from_time && to_time <= e_to_time ) {
                //console.log('to time invalid');
                result = false;
                //alert('break 3');
                break;
            }
        }
    }

    return result;
}

function makeReservation() {
    date_str = document.getElementById('res_date').value;
    time_from_str = document.getElementById('res_time_from').value;
    time_to_str = document.getElementById('res_time_to').value;

    if (date_str === '' || time_from_str === '' || time_to_str === '') {
        showMsgBox( gettext("All reservation fields are required") );
        return;
    }

    date_from = new Date(date_str + ' ' + time_from_str);
    date_y = date_from.getFullYear();
    date_m = date_from.getMonth()+1;
    date_d = date_from.getDate();
    hour_from = date_from.getHours();
    min_from = date_from.getMinutes();

    date_to = new Date(date_str + ' ' + time_to_str);
    hour_to = date_to.getHours();
    min_to = date_to.getMinutes();

    isTimeValid = validateTime(date_y, date_m, date_d, hour_from, min_from, hour_to, min_to);

    if ( !isTimeValid ) {
        showMsgBox( gettext('something is wrong with your time interval') );
        return false;
    }

    /* retrieve fields from browser's memory */
    user_id = window.loggedin_userid_global;
    amenity_id = window.amenity_id;

    isValidTime = checkConflict(amenity_id, date_y, date_m, date_d, hour_from, min_from, hour_to, min_to);
    if ( !isValidTime ) {
        showMsgBox( gettext("This conflicts with existing reservation") );
        return;
    }

    showSpinner();

    var request = new XMLHttpRequest();
    post_url = "/" + window.loggedin_tenant_global + "/make_reservation";
    request.open('POST', post_url, true);

    request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);

      if (request.status >= 200 && request.status < 400) {
          if (json.response.status == 'success') {
              //showMsgBoxSuccess( gettext('Record saved to database') );
          }
          else {
              showMsgBox( gettext('Error saving record to database') );
          }
      }
      else {
          showMsgBox( gettext('Error saving record to database') );
      }

      location.reload();
    }

    showSpinner();

    var requestObj = new Object();
    requestObj.tenant = loggedin_tenant_global;
    requestObj.user_id = user_id;
    requestObj.amenity_id = amenity_id;
    requestObj.date = {"y": date_y, "m": date_m,  "d": date_d};
    requestObj.time_from = {"h": hour_from, "m": min_from};
    requestObj.time_to = {"h": hour_to, "m": min_to};
    requestObj.send_email = String(window.send_email);  // this sends the string 'yes' or 'no'
    jsonStr = '{ "reservation": ' + JSON.stringify(requestObj) + '}';
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(jsonStr);

    /* close modal window */
    document.getElementById('modal-close').click();
}

function deleteReservation(user_id, rsv_id, amenity_id ) {
    console.log(user_id + ' ' + rsv_id + ' ' + amenity_id)
    //alert("user_id " + user_id + ',   rsv_id ' + rsv_id + ',   amenity_id ' + amenity_id);

    var request = new XMLHttpRequest();
    post_url = "/" + window.loggedin_tenant_global + "/delete_reservation";
    request.open('POST', post_url, true);

    request.onload = function () {
      // Begin accessing JSON data here
      var json = JSON.parse(this.response);

      if (request.status >= 200 && request.status < 400) {
          if (json.response.status == 'success') {
              showMsgBoxSuccess( gettext('Record deleted from the database') );
          }
          else {
              showMsgBox( gettext('Error deleting record') );
          }
      }
      else {
          showMsgBox( gettext('Error deleting record') );
      }

      location.reload();
    }

    var requestObj = new Object();
    requestObj.tenant = loggedin_tenant_global;
    requestObj.user_id = user_id;
    requestObj.rsv_id = rsv_id;
    jsonStr = '{ "reservation": ' + JSON.stringify(requestObj) + '}';

    //alert('index '+index +', user_id '+requestObj.user_id + ', rsv_id '+requestObj.rsv_id);

    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    request.send(jsonStr);
}


function paidAmenityChanged() {
    if ( document.getElementById('paid_radio').checked ) {
        document.getElementById('send_email_div_id').style.display = 'block';
        document.getElementById('send_email_checkbox').checked = true;
    }

    if ( document.getElementById('free_radio').checked ) {
        document.getElementById('send_email_div_id').style.display = 'none';
        document.getElementById('send_email_checkbox').checked = false;
    }
}