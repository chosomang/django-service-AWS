//체크박스 전체선택
function selectAll(selectAll, type) {
    $('input.'+type).each(function(){
        if ($(this).val() == 'regex'){
            this.checked = false
            $(`#${type}_regex`).slideUp('fast')
            $(`#${type}_regex input`).val('')
            return 1
        }
        this.checked = selectAll.checked
    })
}

//체크박스 전체선택 해제
function selectcheck(e, type){
    if(e.checked == false){
        $('input[name='+type+'_all]')[0].checked = e.checked
        $(`#${type}_regex`).slideUp('fast')
        $(`#${type}_regex input`).val('')
    }
    else if($(e).val()=='regex'){
        $('input.'+type).each(function(){
            if(this == e){
                return 1
            }
            this.checked = false
        })
        $(e).parent().parent().parent().parent().find('.search-dropdown-menu').hide()
        $(`#${type}_regex`).slideDown('fast')
        $(`#${type}_regex`).focus()
    }
    else{
        var count = 0
        $(`#${type}_regex`).slideUp('fast')
        $(`#${type}_regex input`).val('')
        $('input.'+type).each(function(){
            if($(this).val()== 'regex'){
                this.checked = false
            }
            if(this.checked == true){
                if(($(this).val()== 'regex')){
                    return 1
                }
                count += 1 
            }
        })
        if( count ==  $('input.'+type).length - 1 ){
            $('input[name='+type+'_all]')[0].checked = true
        }
    }
}
/// 체크박스 자동 표시/숨김
$('.searchbox-input').on('focus', function(){
    $(this).parent().find('.search-dropdown-menu').slideDown('fast')
})

$('.searchbox-input').on('blur', function(){
    var dropdown = $(this).parent().find('.search-dropdown-menu')
    var this_var = this
    setTimeout(function() {
        if (!$('.dropdown-item:hover').length){
            if (!$(':checkbox:focus').length){
                dropdown.slideUp('fast');
            }
        }else{
            this_var.focus()
        }
    }, 10);
})
$(':checkbox').on('blur', function(e) {
    var dropdown = $(this).parent().parent().parent().parent().find('.search-dropdown-menu')
    var this_var = this
    setTimeout(function() {
        if (!$('.dropdown-item:hover').length){
            if (!$(':checkbox:focus').length){
                dropdown.slideUp('fast');
            }
        }else{
            this_var.focus()
        }
    }, 10);
});

$('.searchbox-input').on('input', function() {
    var input = $(this).val();

    // Iterate over each checkbox
    $(this).parent().find('.search-dropdown-menu li input[type="checkbox"]').each(function() {
        var checkboxValue = $(this);
        // If the checkbox value doesn't contain the input string, hide it
        if (!new RegExp(input, 'i').test(checkboxValue.val())) {
            $(this).parent().parent().hide();
        } else {
            $(this).parent().parent().show();
        }
    });
});


/// Search_Filter
function searchFilter(e){
    console.log($('#search').serializeArray())
}


$('.btn-collapse').on('click', function(){
    var chevron = $($(this).find('.material-symbols-outlined')[0])
    if ($.trim(chevron.text()) == 'expand_more'){
        chevron.text('expand_less')
        $('.searchcard-collapse').fadeIn()
        $('.collapsecard').slideDown()
    } else {
        chevron.text('expand_more')
        $('.collapsecard').slideUp()
        $('.searchcard-collapse').fadeOut()
    }
})

$('.btn-reset').hover(
    function(){
        $('.btn-reset .material-symbols-outlined').toggleClass('fa-spin fa-spin-reverse')
    },
    function(){
        $('.btn-reset .material-symbols-outlined').toggleClass('fa-spin fa-spin-reverse')
    }
)

$('.btn-info').hover(
    function(){
        $('.btn-info .material-symbols-outlined').toggleClass('fa-bounce')
    },
    function(){
        $('.btn-info .material-symbols-outlined').toggleClass('fa-bounce')
    }
)