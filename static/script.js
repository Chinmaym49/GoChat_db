$(document).ready(function() {
    $("#accreq").on("submit",function(event) {
        $.ajax( {
            data: {
                handle:$("button[name='accept']").val()
            },
            type:"POST",
            url:"/accept"
        })
        .done(function(data) {
            location.reload();
        });
        event.preventDefault();
    });

    $("#sndmsg").on("submit",function(event) {
        $.ajax( {
            data: {
                rcvr:$("#rcvr").val(),
                msg:$("#msg").val()
            },
            type:"POST",
            url:"/sndrcv"
        })
        .done(function(data) {
            console.log(data);
            $("#msgblock").append('<div class="containerr darker" style="float: right;"><p>'+$("#msg").val()+'</p><span class="time-left"><b>'+data["sender"]+'</b> '+data["timestamp"]+'</span></div>');
            $("#msg").val("");
        });
        event.preventDefault();
    });
});