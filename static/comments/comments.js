//For getting CSRF token
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {

        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            var csrftoken = getCookie('csrftoken');
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

// Подгружаем аяксом при клике на ссылку нужную форму.
$(document).on('click', 'a.ajax', function(e) {
    e.preventDefault();
    var $this = $(this);
    $this.hide();
    var url = $this.attr('href');
    var modal = $('<div/>', {
        class: 'modal comment'
    });
    var closeButton = $('<a/>', {
                href: '#close',
                class: 'close-button',
                text: 'x',
                click: function(e) {
                     e.preventDefault();
                     modal.remove();
                },
            });

    $.ajax({
        type: "GET",
        url: url,
        cache: false,
        success: function(data) {
            modal.addClass('sucess');
            var formData = $(data.form).prepend(closeButton);
            modal = modal.html(formData);
            $('form', modal).attr('action', url);
            $('#comments').prepend(modal);
            $this.show();
        },
        error: function(data) {
            modal.addClass('error');
            $('#comments').prepend(modal);
            modal.prepend(closeButton);

            var errors = $.parseJSON(data.responseText);
            $.each(errors, function(index, value) {
                msg = '<div class="error-message">' + value + '</div>';
                modal.prepend(msg);
            });
        }
    });
});

// Обрабатываем подгруженную аяксом форму.
$(document).on('submit', '.modal form', function(e) {
    e.preventDefault();
    var data = {};
    $.each($(':input', '.modal form'),function(k){
        data[$(this).attr('name')] = $(this).val();
    });

    var $this = $(this);
    var modal = $this.parents('.modal');
    modal.hide();

    $.ajax({
        type: "POST",
        data: data,
        url: $this.attr('action'),
        cache: false,
        success: function(data) {
            if (data.is_update_view) {
                $('#comment-' + data.comment_id).html(data.comment);
            } else {
                $('#comments-header').after(data.comment);
            }
            if (data.flash_message) {
                var msg = $('<div/>', {
                    'class': 'messages-ajax info',
                }).html(data.flash_message);
                $this.parent('.form-wraper').addClass('message info').html(msg);
                modal.show();
                setTimeout(function() {
                    modal.remove();
                }, 4000);
            }
            else{
                modal.remove();
            }
            $('a.ajax').show();
        },
        error: function(data) {
            var errors = $.parseJSON(data.responseText);
            var msg, idx;
            $('.error-message').hide();
            $.each(errors, function(index, value) {
                msg = '<div class="error-message">' + value + '</div>';
                if (index == '__all__') {
                    if (data.status == 403) {
                        $this.html(msg);
                        return;
                    }
                    $this.prepend(msg);
                }
                else {
                    idx = $("#id_" + index);
                    idx.css('border', '2px solid red');
                    idx.before(msg);
                }
            });
        }
    });
});
