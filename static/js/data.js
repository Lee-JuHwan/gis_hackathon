// 데이터 부분
var list_lat = [35.1831859, 35.1835848, 35.1832847, 35.1831849]
var list_lng = [126.8387464, 126.8387464, 126.8384464, 126.8386465]
var list_title = ['장소A', '장소B', '장소C', '장소D']
var list_type = ['체육', '문화', '문화', '문화']

// var list_lat = document.getElementById("facility_lat").innerText.split(',');
// var list_lng = document.getElementById("facility_lng").innerText.split(',');

var positions = new Array();

for(var idx=0; idx<list_lat.length; idx++) {

    // var data = list[idx];
    var data_lat = list_lat[idx];
    var data_lng = list_lng[idx];
    var data_title = list_title[idx];
    var data_type = list_type[idx];

    // 데이터를 positions 배열에 넣는 부분 특성을 여러개 넣을 수 있음
    positions.push({content: 'TITLE : ' + data_title +'<br>TYPE : ' + data_type + '111111111111111111111111<br>' +'2<br>' + '3<br>' + '4<br>' + '<br>',
                    latlng: new kakao.maps.LatLng(data_lat, data_lng)
                    });
}
