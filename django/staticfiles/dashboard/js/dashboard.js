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

var grid = GridStack.init({
    float: false,
    resizable: { handles: 'all' },
    fitToContent: true,
    cellHeight: 10,
    margin: 1,
    staticGrid: true,
});

$('#no_data').hide()
$('body').append(
    `<div id="loader" style="width:100vw; height:100vh; background-color:rgba(156, 154, 154, 0.1); position:absolute; top:0">
        <div class="spinner-border-lg text-teiren" style="margin:40vh 46vw"></div>
    </div>`
)
$('.grid-stack').append(
    `<div id="temp" style="margin:80vh 46vw"></div>`
)
$.ajax({
    url: '/grid/load/',
    headers: {
        'X-CSRFToken': getCookie()
    },
    data: {
        name: 'default'
    },
    type: 'post'
}).done(function (data) {
    var data = JSON.parse(data)
    $('#loader').fadeOut()
    $('#temp').remove()
    $('#no_data').remove()
    grid.removeAll()
    grid.load(data)
    for (i in data) {
        if (data[i].id === 'graphitem') {
            continue
        }
        var scripts = $(data[i].content).filter('script:not([src])');
        if (scripts.length >= 1) {
            $.each(scripts, function (idx, script) {
                var jsvar = JSON.parse(script.text)
                for (var key in jsvar) {
                    window[key] = jsvar[key]
                }
            })
        }
        var scriptSrc = $(data[i].content).filter('script').attr('src')
        if (scriptSrc) {
            $.getScript(scriptSrc)
        }
    }
}).fail(function() {
    $('#loader').fadeOut()
    $('#temp').remove()
    $('#no_data').show()
    grid.removeAll()
});