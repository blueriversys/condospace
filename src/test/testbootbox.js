
            function showDialog2(text_color) {
                const msg = `<label style='color:${text_color};'>The fields Name, email and phone are all required.</label>`;
                console.log(msg);
                var dialog = bootbox.dialog({
                    message: msg,
                    closeButton: false,
                    backdrop: false,
                    onEscape: true,
                    buttons: {
                            ok: {
                                label: "OK",
                                className: 'btn-info',
                                callback: function(){
                                    //alert('Custom OK clicked');
                                }
                            }
                    }
                });
            }


