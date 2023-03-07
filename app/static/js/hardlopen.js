var DateTime = luxon.DateTime;

$(function () {
  $('timestamp').each(function () {
    var start_time = DateTime.fromSeconds(parseFloat($(this).attr('time')));
    $(this).text(start_time.toLocaleString(DateTime.TIME_24_WITH_SECONDS));
  });
});

$(function () {
  $.ajax({
    type: "GET",
    url: '/start_tijd',
    success: function (data) {
      setInterval(function updateTime() {
        $('live_clock').each(function () {
          var start_tijd = DateTime.fromSeconds(data.tijd);
          var nu = DateTime.utc();
          $(this).text(nu.diff(start_tijd).toFormat("hh:mm:ss"));
        });
        return updateTime;
      }(), 1000);
    }
  });
});

$(function () {
  $('#start_clock').on('click', function () {
    $.confirm({
      useBootstrap: false,
      title: 'Klok starten',
      icon: 'fa fa-warning',
      content: 'Weet je zeker dat je de klok wil starten? <br> <b>Alle niet opgeslagen uitslagen gaan verloren.</b> <br> <i>Deze actie kan niet ongedaan gemaakt worden.</i>',
      type: 'green',
      typeAnimated: true,
      animateFromElement: false,
      autoClose: 'cancelAction|10000',
      buttons: {
        deleteUser: {
          text: 'Klok starten',
          btnClass: 'button is-success',
          action: function () {
            $.ajax({
              url: '/timer/start',
              type: 'PUT',
              success: function (result) {
                window.location.href = '/tijd/scan';
              }
            });
          }
        },
        cancelAction: {
          text: 'Annuleren',
          btnClass: 'button is-light',
          close: function () { }
        }
      }
    });
  });
});

function deleteButton(deelnemer_id, deelnemer_naam) {
  $('#delete_' + deelnemer_id).on('click', function () {
    $.confirm({
      useBootstrap: false,
      title: 'Deelnemer verwijderen',
      icon: 'fa fa-warning',
      content: 'Weet je zeker dat je \'' + deelnemer_naam + '\' wil verwijderen? <br> Deze actie kan niet ongedaan gemaakt worden.',
      type: 'red',
      typeAnimated: true,
      animateFromElement: false,
      autoClose: 'cancelAction|8000',
      buttons: {
        deleteUser: {
          text: 'Verwijderen',
          btnClass: 'button is-danger',
          action: function () {
            $.ajax({
              url: '/deelnemer/delete/' + deelnemer_id,
              type: 'DELETE',
              success: function (result) {
                window.location.href = '/deelnemers';
              }
            });
          }
        },
        cancelAction: {
          text: 'Annuleren',
          btnClass: 'button is-light',
          close: function () { }
        }
      }
    });
  });
};