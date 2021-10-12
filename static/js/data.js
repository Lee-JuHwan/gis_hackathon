var positions = new Array();


document.writeln(data_lat)

// 데이터를 positions 배열에 넣는 부분 특성을 여러개 넣을 수 있음
positions.push({content: 'TITLE : ' + data_title +
                    '<br>ADDRESS : ' + data_address +
                    '<br>SCORE :' + data_score + '<br>',
                latlng: new kakao.maps.LatLng(data_lat, data_lng)
                });