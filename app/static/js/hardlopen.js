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

function createNotification(message, color) {
  //Start values before 'flying in'
  const cssStart = { top: '58px', opacity: '0', 'margin-bottom': '10px'};

  $('<div class="notification is-' + color + ' is-light">' +
    message + '</div>')
    .css(cssStart)
    .appendTo('#notification-list')
    .animate({ top: '0', opacity: 1 }, 250)  //Fly-in animation
    .delay(6500)
    .animate({ top: '-58px', opacity: 0, 'margin-bottom': '-48px' }, 250)  //Fly-out animation
    .queue(function () { $(this).remove() });
}


function scan_ajax_submit() {
  var barcode = $("#barcode").val()
  //Send AJAX request
  $.ajax({
    url: "/tijd/scan",
    type: "POST",
    data: JSON.stringify({
      'barcode': barcode
    }),
    contentType: 'application/json; charset=utf-8',
    dataType: "json",
    success: function (data) {
      //Show message from server on succes
      createNotification(data['message'], data['messageColor'])
    },
    error: function (error) {
      if (error.responseJSON) {
        //Show error message from server if a response exists
        createNotification(error.responseJSON['message'], 'danger')
      } else {
        //Show general error message
        createNotification('Request to server for <b>' + barcode + '</b> failed.', 'danger')
      }
    }
  });
  //Reset input field
  $("#barcode").val('')
  $("#barcode").focus()
}
