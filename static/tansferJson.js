//if we don't want to change page, we must transfer data with json or others.

<!--the format of itation in html is very important！-->
////<form width="202" border="0" align="center" cellpadding="05" cellspacing="0" id="logintable" action="/login">

$('#btn_sublime').on('click', function () {//onclick
    var message = document.getElementById("input_box");

    //var n = {
        //'name':name,
       // 'password':password
    //};

    var data = JSON.stringify(message)//把原来是对象的类型转换成易传递的json编码的字符串类型：data is Json type

    $.ajax({
        url: "/chat",
        type: 'POST',//post data to flask.
        contentType: "application/json",
        success: function (data) {//Ajax请求成功后自动调用的回调函数。参数data是客户端请求后台，由后台返回的值。
            console.log(data)
            if (data.message == "SUCCESS") {//调用接口成功后自定义操作
                alert("send successfully!");
                //window.open ("C:\Users\lvxinyue\Desktop\frontEnd\HTML\register.html")//展示弹窗
                window.location.href = "localhost/chat";
            } else {
                alert("send unsuccessfully!");
                $('.check-pas').css('display', 'block')
            }
        },
        error: function (data) {//调用接口失败后自定义操作
            console.log(data)
            //window.open ("C:\Users\lvxinyue\Desktop\frontEnd\HTML\login.html",'http://127.0.0.1:5000/')//展示弹窗

        }
    })
})

