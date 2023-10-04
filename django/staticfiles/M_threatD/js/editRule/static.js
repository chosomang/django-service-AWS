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

function ruleEditAction(event){
    var data = $('#edit_form').serialize()
    $.ajax({
        url: '/threat/custom/edit/',
        headers:{
            'X-CSRFToken': getCookie()
        },
        data: data,
        type: 'post'
    }).done(function(data){
        alert(data)
        if (data == '정책 추가 완료'){
            $('.modal').modal('hide')
            window.location.reload()
        }
    }).fail(function(data){
        alert('다시 시도해주세요')
    })
}

function addProperty(cloud){
    var count = $('#properties').find('.prop').length + 1
    $.ajax({
        url:'/threat/custom/add/static_slot/',
        headers:{
            'X-CSRFToken': getCookie()
        },
        type: 'post',
        data:{
            count: count,
            cloud: cloud
        }
    }).done(function(data){
        $('#properties').append(data)
        $('#properties').find('#property'+count).hide().slideDown('normal')
    })
}

function deleteProperty(e){
    var prop = $(e).parent().parent().parent()
    prop.slideUp('normal')
    setTimeout(function(){
        prop.remove()
        resetStaticNumbers('.prop')
    }, 300)
}

function resetStaticNumbers(e){
    for (var i=0; i<$(e).length; i++){
        $(e)[i].id = $(e)[i].id.slice(0,-1)+(i+1)
        var input = $($(e)[i]).find('input')
        input.each(function(){
            if ($(this)[0].list){
                var datalist = $(this)[0].list.id.slice(0,-1)+(i+1)
                $(this)[0].list.id = datalist
                $($(this)[0]).attr('list', datalist)
            }
            $($(this)[0]).attr('name', $(this)[0].name.slice(0,-1)+(i+1))
            $($(this)[0]).attr('placeholder', $(this)[0].placeholder.slice(0,-1)+(i+1))
            var span = $($(this)[0]).parent().children('span')[0]
            span.innerText = span.innerText.slice(0,-1)+(i+1)
        })
    }
}

function newPropertyKey(e){
    var num = e.name.slice(-1)
    if(e.value == '새로운 정책 속성'){
        $("#properties").find("#property"+num).append(
            `
            <div id="property_key_custom_${num}" class="col-4">
                <span>새로운 정책 속성</span>
                <input type="text-area" class="form-control form-control-user" name="property_custom_${num}" placeholder="새로운 정책 속성">
            </div>
            `
        )
    } else {
        if($("#property_key_custom_"+num).length > 0){
            $("#property_key_custom_"+num).remove()
        }
    }
}