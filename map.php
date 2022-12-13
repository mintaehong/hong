
<?php
// GET방식 초기값 설정
if(empty($_GET['loc']))
{
  $_GET['loc']="구를 입력해주세요";
}
if(empty($_GET['max']))
{
  $_GET['max']=999999999;
}
foreach(['cate', 'adv'] as $value)
{
  if(empty($_GET[$value]))
  {
    $_GET[$value]='';
  }
}
foreach(['star', 'review', 'min'] as $value)
{
  if(empty($_GET[$value]))
  {
    $_GET[$value]=0;
  }
}

// 변수에 전달
$loc = $_GET['loc'];
$cate = $_GET['cate'];
$star = $_GET['star'];
$review = $_GET['review'];
$min = $_GET['min'];
$max = $_GET['max'];
$adv = $_GET['adv'];

// MySQL 서버에 필요한 정보
$server = "localhost";
$user = "min";
$password = "pass";
$dbname = "map";

// 입력받은 필터 값으로 원하는 음식점 조회
$sql = "SELECT * FROM restaurant, location as l where id = l.r_id and  id like '$loc%' and category like '%$cate%' and star > $star and (visitor_review + blog_review) > $review and id in (select r_id from menu group by r_id having avg(price) > $min and avg(price) < $max) and id in (select r_id from r_character where advantages like '%$adv%')";
$conn = new mysqli($server, $user, $password, $dbname);
$result = mysqli_query($conn, $sql);

// 조회한 음식점 리스트화
$list_data = array();
while($row = mysqli_fetch_array($result)) {
  array_push($list_data, [$row['address'],$row['latitude'],$row['longitude'],$row['name'],$row['category'],$row['star'],$row['visitor_review'],$row['blog_review'],$row['phone'],$row['id']]);
}

// 입력 받은 필터 값으로 메뉴 조회
$sql = "SELECT * FROM restaurant, location as l, menu as m where id = l.r_id and id = m.r_id and id like '$loc%' and category like '%$cate%' and star > $star and (visitor_review + blog_review) > $review and id in (select r_id from menu group by r_id having avg(price) > $min and avg(price) < $max) and id in (select r_id from r_character where advantages like '%$adv%')";
$conn = new mysqli($server, $user, $password, $dbname);
$result = mysqli_query($conn, $sql);

// 조회한 메뉴 리스트화
$menu_data = array();
while($row = mysqli_fetch_array($result)) {
  array_push($menu_data, [$row['id'], $row['menu'],$row['price']]);
}

// 음식점 장점 input 자동완성을 위하여 조회
$sql = "select replace(advantages, '\"', '') as adv from r_character group by(advantages)";

$conn = new mysqli($server, $user, $password, $dbname);
$result = mysqli_query($conn, $sql);

// 음식점 장점 리스트화
$advantages_data = array();
while($row = mysqli_fetch_array($result)) {
  array_push($advantages_data, $row['adv']);
}

?>
<!-- 네이버 지도 API 기본 틀 -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=no">
    <title>지도 서치</title>
    <link rel="stylesheet" href="mapstyles.css">
    <script type="text/javascript" src="https://openapi.map.naver.com/openapi/v3/maps.js?ncpClientId=w0lbb7bbke"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.js" integrity="sha256-H+K7U5CnXl1h5ywQfKtSj8PCmoN9aaq30gDh27Xc0jk=" crossorigin="anonymous"></script>
    <script type="text/javascript" src="autocomplate.js"></script>
    <!-- <script type="text/javascript" src="animal.js"></script> -->
</head>
<!-- 음식점 필터링을 하기위한 form -->
<body onload="init()">
<div class="fo">
  <form action="map.php" method="get">
      <div><a class="input">지역</a><input class = "input" type="text" name="loc" value = "<?=$_GET['loc']?>"></div><br><br>
      <div><a class="input">카테고리</a><input class = "input"  type="text" name="cate" value = "<?=$_GET['cate']?>"></div><br><br>
      <div><a class="input">별점</a><input class = "input"  type="text" name="star"></div><br><br>
      <div><a class="input">리뷰 수</a><input class = "input"  type="text" name="review"></div><br><br>
      <div><a class="input">가격</a><input  class = "input"  type="text" name="min"><br><input class = "input" type="text" name="max"></div><br><br>
      <div class="srch_form autocomplete"><input style = "width: 90%;height:20px;" id="autoInput" type="text" name="adv" placeholder="장점 EX) 음식이 맛있어요"></div><br><br>
  <input class="submit" type="submit" value="검색">
</div>
<!-- 네이버 지도 -->
<div id="map" class="map"></div>
<script>

$(function() {

	initMap();

});
function initMap() {
  // 음식점 리스트 data 변수에 저장
  var data = <?php echo json_encode($list_data)?>;
	var areaArr = new Array();
  // 함수가 딕셔너리를 인식하기 때문에 딕셔너리로 데이터 저장
  for(var idx=0; idx<data.length; idx++) {
    var dictObject = {}
    dictObject['location'] = data[idx][0];
    dictObject['lat'] = data[idx][1];
    dictObject['lng'] = data[idx][2];
    dictObject['name'] = data[idx][3];
    dictObject['category'] = data[idx][4];
    dictObject['star'] = data[idx][5];
    dictObject['visitor_review'] = data[idx][6];
    dictObject['blog_review'] = data[idx][7];
    dictObject['phone'] = data[idx][8];
    dictObject['id'] = data[idx][9];
    areaArr.push(dictObject);
}
// 검색 후 지도 중심 위치 설정
  var center_lat = 0;
  var center_lng = 0;
  for(var idx=0; idx<areaArr.length; idx++) {
    center_lat += Number(Object.values(areaArr[1])[1])
    center_lng += Number(Object.values(areaArr[1])[2])
}

  let markers = new Array();
  let infoWindows = new Array();
  if (center_lat == 0){
  var map = new naver.maps.Map('map', {
          center: new naver.maps.LatLng(37.552758094502494, 126.98732600494576), //지도 시작 지점
          zoom: 14
        });
  }else{
    var map = new naver.maps.Map('map', {
        center: new naver.maps.LatLng(center_lat/areaArr.length, center_lng/areaArr.length), //지도 시작 지점
        zoom: 14
        });
  }

  for (var i = 0; i < areaArr.length; i++) {
    var marker = new naver.maps.Marker({
      map: map,
      title: areaArr[i].location, // 지역구 이름
      position: new naver.maps.LatLng(areaArr[i].lat , areaArr[i].lng) // 지역구의 위도 경도 넣기
    });

    var menu_list = <?php echo json_encode($menu_data)?>;
      /* 정보창 */
    var infoWindow = new naver.maps.InfoWindow({
      content: '<div class="mapback"> <a class="title">' + areaArr[i].name +'</a> <a class="cate">'+ areaArr[i].category +'</a> <br> <a class="star">별점 : '+ areaArr[i].star + '</a> <br> <a class="visitor_review"> 방문자 리뷰수 : '+areaArr[i].visitor_review+'</a> <a class = "blog_review"> 블로그 리뷰수 : '+areaArr[i].blog_review+'</a> <hr class="line"><div class = "menu"> <a class=menu> 메뉴 </a> <a class="price"> 가격 </a> <br>'
    });
    // 메뉴 전달을 위해 for 문을 사용
    for (var idx=0; idx<menu_list.length; idx++) {
      if (menu_list[idx][0] == areaArr[i].id){
        infoWindow.content = infoWindow.content + '<a class=menu>' + menu_list[idx][1] + '</a> <a class="price">' + menu_list[idx][2].toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',') + '원</a> <br>'
      }
    }
    var infoWindow = new naver.maps.InfoWindow({
      content: infoWindow.content + '</div>'}); // 클릭했을 때 띄워줄 정보 HTML 작성<>
    markers.push(marker); // 생성한 마커를 배열에 담는다.
    infoWindows.push(infoWindow); // 생성한 정보창을 배열에 담는다.
  }

  function getClickHandler(seq) {

              return function(e) {  // 마커를 클릭하는 부분
                  var marker = markers[seq], // 클릭한 마커의 시퀀스로 찾는다.
                      infoWindow = infoWindows[seq]; // 클릭한 마커의 시퀀스로 찾는다

                  if (infoWindow.getMap()) {
                      infoWindow.close();
                  } else {
                      infoWindow.open(map, marker); // 표출
                  }
      		}
      	}
  for (var i=0, ii=markers.length; i<ii; i++) {
      	// console.log(markers[i] , getClickHandler(i));
        naver.maps.Event.addListener(markers[i], 'click', getClickHandler(i)); // 클릭한 마커 핸들러
      }
  }

// 장점 input의 자동 완성을 위한 코드 -> https://minaminaworld.tistory.com/104
var advantages = <?php echo json_encode($advantages_data)?>;
window.onload = function () {
          autocomplete.setAutocomplete(document.getElementById("autoInput"), advantages)
      }
console.log(advantages);

</script>
</body>
</html>
