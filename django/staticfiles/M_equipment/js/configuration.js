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

$('#delete_modal').on('show.bs.modal', function(event) {
    var button = $(event.relatedTarget);
    document.getElementById('cloud_name').value = button.data('cloud');
    document.getElementById('main_key').value = button.data('main');
    document.getElementById('sub_key').value = button.data('sub');
    $('#result').text('Will You Delete Registered Information?');
});

$('#delete_accept').on('click', function(event) {
    var cloud = $('#cloud_name').val();
    var main = $('#main_key').val();
    var sub = $('#sub_key').val();
    $.ajax({
        url: 'delete/',
        headers: {
            'X-CSRFToken': getCookie()
        },
        data: {
            cloud: cloud,
            main: main,
            sub: sub
        },
        type: 'post'
    }).done(function(data) {
        $('#result').text(data);
        if (data == 'Deleted Registered Information') {
            $('#result').attr('class', 'text-primary');
            $('#delete_check').remove();
            document.getElementById('delete_complete').type = 'button';
        }
    }).fail(function(data) {
        document.getElementById('success').remove();
    })
});

$('#delete_complete').on('click', function(event) {
    location.reload();
});

function container_trigger(e, type, access_key, secret_key, region_name){
    console.log(access_key, secret_key, region_name)
    var on_off = 0
    var input = $(e.parentNode).find('input.on_off')[0]
    if (input.value != 1){
        on_off = 1
    }
    input.value = on_off
    $.ajax({
        url:`${type}/collection/`,
        headers:{
            'X-CSRFToken': '{{csrf_token}}'
        },
        data:{
            access_key: access_key,
            secret_key: secret_key,
            region_name: region_name,
            isRunning: on_off
        },
        type:'post',
        datatype: 'json'
    }).done(function(response){
        console.log('status: ' + response.isRunning)
        console.log('container id: ' + response.containerId)

        if (response.isCreate == 1){
            alert('Collection Started Successfully \n' + response.containerId)
        } else if (response.isRunning == 1){
            alert('Collection Is Already Running!\n' + response.containerId)
            if (on_off == 1){
                $(e).attr('class', 'btn btn-md btn-teiren')
            } else {
                $(e).attr('class', 'btn btn-md btn-outline-teiren')
            }
        } else{
            alert('Unknown Alert')
        }
    })
}

$('#integration_side').addClass('active');