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


$('#integration_side').addClass('active');