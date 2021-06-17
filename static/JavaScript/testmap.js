setTimeout(function() {
  //code for initializing the google map
  
defaultLatLong = {
  lat: 40.7127753,
  lng: -74.0059728
};

var map = new google.maps.Map(document.getElementById('map'), {
  center: defaultLatLong,
  zoom: 17,
  tilt: 0,
  mapTypeId: 'satellite'
});

var input = document.getElementById('validationServer03');

var autocomplete = new google.maps.places.Autocomplete(input);


var marker = new google.maps.Marker({
  map: map,
  position: defaultLatLong,
  draggable: true,
  clickable: true
});

google.maps.event.addListener(marker, 'dragend', function(marker) {
  var latLng = marker.latLng;

  //Gets the lat and long coordinates based on the google maps marker
  currentLatitude = latLng.lat();
  currentLongitude = latLng.lng();
  var latlng = {
    lat: currentLatitude,
    lng: currentLongitude
  }

  // This bit shows the Lat and Long coordinates in my HTML page 
  document.getElementById("coordinates").innerHTML = '<p> Lat: ' + currentLatitude + ', Lng: ' + currentLongitude + '</p>';
  
  console.log(currentLatitude)

  // This bit passes the currentLatitude value
  document.getElementById('currentLatitude').value = currentLatitude;

  // This bit passes the currentLongitude value
  document.getElementById('currentLongitude').value = currentLongitude;

  
  
  var geocoder = new google.maps.Geocoder;
  geocoder.geocode({
    'location': latlng
  }, function(results, status) {
    if (status === 'OK') {
      if (results[0]) {
        input.value = results[0].formatted_address;
      } else {
        window.alert('No results found');
      }
    } else {
      window.alert('Geocoder failed due to: ' + status);
    }
  });

});

 
autocomplete.addListener('place_changed', function() {
  var place = autocomplete.getPlace();
  if (!place.geometry) {
    return;
  }
  if (place.geometry.viewport) {
    map.fitBounds(place.geometry.viewport);
  } else {
    map.setCenter(place.geometry.location);
  }

  marker.setPosition(place.geometry.location);

  currentLatitude = place.geometry.location.lat();
  currentLongitude = place.geometry.location.lng();

});


}, 1000);

