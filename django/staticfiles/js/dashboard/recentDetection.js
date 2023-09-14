function threat(e) {
    var data = $(e).serialize()
    $.ajax({
        url: "/neo4j/",
        data: data,
        type: "post"
    }).done(function(res) {
        $("#gdb_dashboard").html(res)
        $('#threat_form').append($(e).find('input[type=hidden]').clone())
        $('#threat_form').append('<button class="btn btn-block btn-teiren mb-2">상세보기</button>')
    })
}
var e = $('.gdb_threat').clone()[0]
threat(e)