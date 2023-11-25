function getCookie(name = 'csrftoken') {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function checkModal(e, modal_type){
    var data = $(e.parentNode).serialize()
    $.ajax({
        url:'config/modal/',
        headers: {
            'X-CSRFToken': getCookie()
        },
        data: data,
        type: 'post'
    }).done(function(response){
        $(`#${modal_type}_form`).html(response)
        if(modal_type == 'trigger'){
            var on_off = $(e.parentNode).find('input[name="on_off"]').val()
            if(on_off == '0'){
                $('#trigger_accept').html('Turn Collection On')
            } else {
                $('#trigger_accept').html('Turn Collection Off')
            }
        }
        $(`#${modal_type}_modal`).modal('show')
    })
}

$('#delete_accept').on('click', function() {
    var data = $('#delete_form').serialize()
    $.ajax({
        url: 'config/delete/',
        headers: {
            'X-CSRFToken': getCookie()
        },
        data: data,
        type: 'post'
    }).done(function(response) {
        if('error' in response){
            alert(response.error)
            return 0
        }
        if (response.result == 'Deleted Registered Information') {
            $('#delete_message').text(response.result);
            $('#delete_message').attr('class', 'text-teiren');
            $('#delete_check').remove();
            $('#delete_complete').attr('type', 'button');
        } else {
            alert(response.result)
        }
    }).fail(function() {
        alert('Failed to Delete Information');
    })
});

$('#delete_complete').on('click', function(event) {
    location.reload();
});


$('#trigger_accept').on('click', function() {
    var data = $('#trigger_form').serialize()
    $.ajax({
        url: 'config/trigger/',
        headers: {
            'X-CSRFToken': getCookie()
        },
        data: data,
        type: 'post'
    }).done(function(response) {
        if ('error' in response){
            alert(response.error)
            return 0
        } else {
            alert(response)
        }
        // if(response.startsWith('error')){
        //     alert(response.slice(6))
        //     return 0
        // }
        // $('#result').text(response);
        // if (response == 'triggerd Registered Information') {
        //     $('#result').addclass('text-teiren');
        //     $('#delete_check').remove();
        //     $('#delete_complete').attr('type','button');
        // }
    }).fail(function() {
        $('#result').addclass('text-danger');
        $('#result').text('Failed to Delete Information');
    })
});

// function container_trigger(e, type, access_key, secret_key, region_name, log_type, group_name){
//     var on_off = 0
//     var input = $(e.parentNode).find('input.on_off')[0]
//     if (input.value != 1){
//         on_off = 1
//     }
//     input.value = on_off
//     $.ajax({
//         url:`${type}/collection/`,
//         headers:{
//             'X-CSRFToken': getCookie()
//         },
//         data:{
//             access_key: access_key,
//             secret_key: secret_key,
//             region_name: region_name,
//             log_type: log_type,
//             group_name: group_name,
//             isRunning: on_off,
//         },
//         type:'post',
//         datatype: 'json'
//     }).done(function(response){
//         console.log('status: ' + response.isRunning)
//         console.log('container id: ' + response.containerId)

//         if (response.isCreate == 1){
//             alert('Collection Started Successfully \n' + response.containerId)
//         } else if (response.isRunning == 1){
//             alert('Collection Is Already Running!\n' + response.containerId)
//             if (on_off == 1){
//                 $(e).attr('class', 'btn btn-md btn-teiren')
//             } else {
//                 $(e).attr('class', 'btn btn-md btn-outline-teiren')
//             }
//         } else{
//             alert('Unknown Alert')
//         }
//     })
// }

$(function(){
    $("#dataTable").DataTable({
        destroy: false,
        // 표시 건수기능 숨기기
        lengthChange: true,
        // 검색 기능 숨기기
        searching: true,
        // 정렬 기능 숨기기
        ordering: true,
        // 정보 표시 숨기기
        info: true,
        // 페이징 기능 숨기기
        paging: true
    });
});

$('#integration_side').addClass('active');
$('td').attr('style', 'vertical-align: middle')