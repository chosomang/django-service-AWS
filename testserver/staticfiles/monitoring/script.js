function fetchMetrics() {
    $.ajax({
        url: 'http://127.0.0.1:8000/api/v1/receive-metrics/', // Django API 엔드포인트
        method: 'GET',
        success: function(data) {
            // 데이터를 HTML 요소에 표시
            $('#metrics').html(JSON.stringify(data, null, 2));
        },
        error: function(error) {
            console.error('Error fetching data: ', error);
        }
    });
}

// 1초마다 fetchMetrics 함수를 호출
setInterval(fetchMetrics, 1000);
