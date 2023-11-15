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

$('#help').on('show.bs.modal', function () {
    $.ajax({
        url: '/logs/modal/help/',
        headers: {
            'X-CSRFToken': getCookie()
        },
        type: 'POST'
    }).done(function (data) {
        $('#help-body').html(data)
    })
})
$('#detail-modal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget);
    var id = button.data('id')
    var cloud = button.data('cloud')
    $.ajax({
        url: '/logs/modal/details/',
        headers: {
            'X-CSRFToken': getCookie()
        },
        data: {
            id: id,
            cloud: cloud
        },
        type: 'post'
    }).done(function (data) {
        $('#detail').html(data)
    }).fail(function (data) {
        $('#detail').html('fail')
    })
})
$(function () {
    $('#log_top').addClass('show')
})


/// Search_Filter
function searchFilter(e) {
    $('#log_table').fadeOut('normal')
    if (e == 'reset') {
        data = `page=1&cloud=${cloud}`
        var checkbox = $('#search input[type="checkbox"]')
        checkbox.each(function () {
            this.checked = false
        })
        $('.regex').slideUp('fast')
    } else {
        data = $('#search').serialize() + `&page=${e}&cloud=${cloud}`
    }
    $.ajax({
        url: '/logs/filter/',
        headers: {
            'X-CSRFToken': getCookie()
        },
        data: data,
        type: 'post'
    }).done(function (response) {
        if (!response.startsWith('<div')) {
            window.location.reload()
        }
        $('#searchCollapse').removeClass('show')
        $('#log_table').html(response)
        $('#log_table').fadeIn('fast')
    }).fail(function(e){
        window.location.reload()
    })
}
$('#log_side').addClass('active')