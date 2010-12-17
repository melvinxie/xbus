var jqt = $.jQTouch({
  debug: false,
  icon: '/static/icon.png',
  icon4: '/static/icon4.png',
  statusBar: 'black-translucent'
});
var field = 'from';
var from_station = '';
var to_station = '';
function supports_html5_storage() {
  try {
    return 'localStorage' in window && window['localStorage'] !== null;
  } catch (e) {
    return false;
  }
}
function fill(station) {
  if (field == 'from') {
    from_station = station;
    $('#from_link').text('出発地：' + station);
    if (supports_html5_storage()) {
      localStorage.from_station = station;
    }
  } else {
    to_station = station;
    $('#to_link').text('目的地：' + station);
    if (supports_html5_storage()) {
      localStorage.to_station = station;
    }
  }
  jqt.goTo('#home', 'slideright');
}
$(function() {
  if (supports_html5_storage()) {
    if (localStorage.from_station) {
      from_station = localStorage.from_station;
      $('#from_link').text('出発地：' + from_station);
    }
    if (localStorage.to_station) {
      to_station = localStorage.to_station;
      $('#to_link').text('目的地：' + to_station);
    }
  }
  var today = new Date();
  if (today.getDay() == 0) {
    $('#day').val('holiday');
  } else if (today.getDay() == 6) {
    $('#day').val('saturday');
  } else {
    $('#day').val('weekday');
  }
  $('#hour').val(String(today.getHours()));
  $('#minute').val(String(today.getMinutes()));
  $('#from_link').click(function() { field = 'from'; });
  $('#to_link').click(function() { field = 'to'; });
  $('#swap').click(function() {
    var tmp = from_station;
    from_station = to_station;
    to_station = tmp;
    $('#from_link').text('出発地：' + from_station);
    $('#to_link').text('目的地：' + to_station);
    if (supports_html5_storage()) {
      localStorage.from_station = from_station;
      localStorage.to_station = to_station;
    }
  });
  function display(text) {
    $('#message').empty().append(text);
    $('#message').parent().show();
  }
  $('#selection').bind('pageAnimationEnd', function(e, info) {
    $('.toolbar h1', this).text({'from': '出発地', 'to': '目的地'}[field]);
  });
  $('#nearby').bind('pageAnimationEnd', function(e, info) {
    if (!$(this).data('loaded')) {
      var lookup = jqt.updateLocation(function(coords) {
        if (coords) {
          $('#nearby_stations').load(
              '/nearby/?lat=' + coords.latitude + '&lng=' + coords.longitude,
              function() {
                $(this).parent().data('loaded', true);
                $('#message').parent().hide();
              });
        } else {
          display('Device not capable of geo-location.');
        }
      });
      if (lookup) {
        display('検索中...');
      }
    }
  });
  $('#direction').bind('pageAnimationEnd', function(e, info) {
    $('#results').html('');
    $('#msg').parent().show();
    if (from_station && to_station && from_station != to_station) {
      $('#msg').empty().append('検索中...');
      $('#results').load(
          '/direction/?from_station=' + encodeURI(from_station) +
          '&to_station=' + encodeURI(to_station) + '&day=' + $('#day').val() +
          '&hour=' + $('#hour').val() + '&minute=' + $('#minute').val(),
          function() { $('#msg').parent().hide(); });
    } else {
      $('#msg').empty().append('まず出発地と目的地をお選びください。');
    }
  });
  $('#query').change(function() {
    $('#status').empty().append('検索中...');
    $('#status').parent().show();
    var geocoder = new google.maps.Geocoder();
    geocoder.geocode({'address': $(this).val()},
                     function(results, status) {
      if (status == google.maps.GeocoderStatus.OK) {
        var latlng = results[0].geometry.location;
        $('#query_stations').load(
            '/nearby/?lat=' + latlng.lat() + '&lng=' + latlng.lng(),
            function() {
              $('#status').parent().hide();
            });
      } else {
        $('#status').empty().append(status);
      }
    });
  });
});
