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
function gettext(msgid) {
  var value = catalog[msgid];
  if (typeof(value) == 'undefined') {
    return msgid;
  } else {
    return (typeof(value) == 'string') ? value : value[0];
  }
}
function fill(station) {
  if (field == 'from') {
    from_station = station;
    $('#from_link').text(gettext('From: ') + station);
  } else {
    to_station = station;
    $('#to_link').text(gettext('To: ') + station);
  }
  if (supports_html5_storage()) {
    localStorage.setItem(field + '_station', station);
    if (localStorage.hist) {
      var hist = localStorage.hist.split(',');
      if (hist.indexOf(station) == -1) {
        hist.push(station);
        if (hist.length > 10) {
          hist.shift();
        }
        localStorage.hist = hist.join(',');
      }
    } else {
      localStorage.hist = station;
    }
  }
  jqt.goTo('#home', 'slideright');
}
$(function() {
  if (supports_html5_storage()) {
    if (localStorage.from_station) {
      from_station = localStorage.from_station;
      $('#from_link').text(gettext('From: ') + from_station);
    }
    if (localStorage.to_station) {
      to_station = localStorage.to_station;
      $('#to_link').text(gettext('To: ') + to_station);
    }
  }
  var today = new Date();
  if (today.getDay() == 0 ||
      today.getMonth() == 7 && today.getDate() >= 14 && today.getDate() <= 16 ||
      today.getMonth() == 11 && today.getDate() >= 29 ||
      today.getMonth() == 0 && today.getDate() <= 4 ||
      HolidayHelper.isHoliday(today)) {
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
    $('#from_link').text(gettext('From: ') + from_station);
    $('#to_link').text(gettext('To: ') + to_station);
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
    if (supports_html5_storage()) {
      var hist = [];
      if (localStorage.hist) {
        hist = localStorage.hist.split(',');
      } else {
        if (localStorage.from_station) {
          hist.push(from_station);
        }
        if (localStorage.to_station) {
          hist.push(to_station);
        }
        if (hist.length) {
          localStorage.hist = hist.join(',');
        }
      }
      if (hist.length) {
        if (!$(this).data('loaded')) {
          $('#selection').append($('<h2>履歴</h2>'));
          $('#selection').append($('<ul id="hist"></ul>'));
          $(this).data('loaded', true);
        }
        $('#hist').html('');
        hist.reverse().forEach(function (s) {
          $('#hist').append(
              $('<li><a href="#" onclick="fill(\'' + s + '\')">' +
                s + '</a></li>'));
        });
      }
    }
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
    var southWest = new google.maps.LatLng(34.88, 135.62);
    var northEast = new google.maps.LatLng(35.1, 135.82);
    var bounds = new google.maps.LatLngBounds(southWest, northEast);
    geocoder.geocode({address: $(this).val(), bounds: bounds, region: 'JP'},
                     function(results, status) {
      if (status == google.maps.GeocoderStatus.OK) {
        var latlng;
        for (var i = 0; i < results.length; i++) {
          if (bounds.contains(results[i].geometry.location)) {
            latlng = results[i].geometry.location;
            break;
          }
        };
        if (latlng) {
          $('#query_stations').load(
              '/nearby/?lat=' + latlng.lat() + '&lng=' + latlng.lng(),
              function() { $('#status').parent().hide(); });
        } else {
          $('#status').empty().append(
              '見つかりませんでした。別のキーワードでもう一度お試しください。');
        }
      } else {
        $('#status').empty().append(
            '見つかりませんでした。もう一度お試しください。');
      }
    });
  });
});
