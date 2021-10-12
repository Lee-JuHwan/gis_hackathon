var positions = new Array();

var step;
for(step = 1; step<11; step++) {
    var data_title = document.getElementById('title'+step).innerText;
    var data_address = document.getElementById('address'+step).innerText;
    var data_score = document.getElementById('score'+step).innerText;
    var data_lng = document.getElementById('lat'+step).innerText;
    var data_lat = document.getElementById('lng'+step).innerText;

    // 데이터를 positions 배열에 넣는 부분 특성을 여러개 넣을 수 있음
    positions.push({content: '이름 : ' + data_title +
                        '<br>주소 : ' + data_address +
                        '<br>추천도 :' + data_score + '<br>',
                    latlng: new kakao.maps.LatLng(data_lat, data_lng)
                    });
}