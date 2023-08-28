function getCookie(name) {
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

$(function () {
    const csrftoken = getCookie('csrftoken');
    setInterval(function(){
        var topbar_alert_count = $('#topbar_alert_count')
        $.ajax({
            url: '/topbar/alert/',
            headers: {
                'X-CSRFToken': csrftoken
            },
            type:'post'
        }).done(function(data){
            if (data.top_alert){
                topbar_alert_count.removeAttr('hidden')
                $('#topbar_alert').removeAttr('hidden')
                $('#topbar_alert_div').attr('style', 'margin-left:-0.5rem; height:45%;')
                topbar_alert_count.text("\u00A0"+data.top_alert.count+"\u00A0")
            }
            else if (data.no_top_alert){
                $('#topbar_alert_div').attr('style', 'height:45%;')
                topbar_alert_count.attr('hidden', true)
                $('#topbar_alert').attr('hidden', true)
            }
        })
    }, 1000);
})