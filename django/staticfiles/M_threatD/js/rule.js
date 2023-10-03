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

function addRuleModal(cloud) {
    $.ajax({
        url: 'add/',
        headers:{
            'X-CSRFToken': getCookie()
        },
        data: {
            cloud: cloud
        },
        type: 'post'
    }).done(function(data) {
        $('#rule_body').html(data);
    })
    $('#rule-modal').modal('show');
}

function ruleDetails(event) {
    var url = event.address.value
    var data = $(event).serialize()
    $.ajax({
        url: url,
        headers:{
            'X-CSRFToken': getCookie()
        },
        data: data,
        type: 'post'
    }).done(function(data) {
        $('#detail_body').html(data)
    }).fail(function(){
        $('#detail_body').html('fail')
    })
}
function editRuleModal() {
    var data = $('#edit_modal_form').serialize()
    $('#edit_message').slideUp('normal')
    $.ajax({
        url: 'edit/',
        headers:{
            'X-CSRFToken': getCookie()
        },
        data: data,
        type: 'post'
    }).done(function(data) {
        $('#edit_body').html(data)
        $('#edit_body').hide().fadeIn()
    })
}

function deleteRuleModal(event) {
    $('#rule_name').html(event.rule_name.value)
    var data = $(event).children('input').clone()
    $('#del_form').html(data)
}

function deleteRuleAction(event) {
    var data = $(event).serialize()
    $.ajax({
        url: '/threat/custom/delete/',
        headers:{
            'X-CSRFToken': getCookie()
        },
        data: data,
        type: 'post'
    }).done(function(data) {
        if (data == '정책 삭제 완료') {
            $('.modal').modal('hide')
            alert(data)
            window.location.reload()
        } else {
            alert(data)
        }
    }).fail(function() {
        alert('다시 시도해주세요')
    })
}

function ruleOnOff(event) {
    var data = $(event.parentNode).serialize()
    $.ajax({
        url: 'on_off/',
        headers:{
            'X-CSRFToken': getCookie()
        },
        data: data,
        type: 'post'
    }).done(function(on_off) {
        $(event.parentNode.on_off).val(on_off)
        if (on_off == '1') {
            $(event).val('  On  ')
            $(event).css('background-color', '')
            $(event).css('border-color', '')
        } else {
            $(event).val('  Off  ')
            $(event).css('background-color', '#D3D3D3')
            $(event).css('border-color', '#D3D3D3')
        }
    })
}
$('#threat_top').addClass('show');