$(document).ready(function() {
    var locationArray = window.location.href.split('/');
    var registerPage = false;
    for (let part of locationArray) {
        if (part === "register") {
            registerPage = true;
        }
    }
    if (registerPage) {
        initRegisterPage();
    } else {
        initTablePage();
    }
    $('.statistics-modal-activator').click(showStatisticsModal);
    $('#statistics-modal').on('shown.bs.modal', function() {
        $('#statistics-modal .modal-body').height($('#statistics-modal table').height());
        $(this).css('opacity', '1');
        $('#statistics-modal .modal-dialog').css('transform', '');
    });
    $('.flashed-message').slideDown(750).fadeIn(750);
    setTimeout(function() {
        $('.flashed-message').slideUp(750).fadeOut(750);
    }, 2000);
});

function initTablePage() {
    attachTableListeners();
    $('#residents-modal').on('shown.bs.modal', function() {
        $('#residents-modal .modal-body').height($('#residents-modal table').height());
        $(this).css('opacity', '1');
        $('#residents-modal .modal-dialog').css('transform', '');
    });
}

function initRegisterPage() {
    $('#username').focusout(function() {
        var username = $(this).val();
        $.ajax({
            url: `/check-user?username=${username}`,
            success: usernameValid
        });
    });
    $('#password-verify').keyup(checkPasswords);
}

function checkPasswords() {
    if ($('#password-verify').val() !== $('#password').val()) {
        $('#password-verify').parents('.form-group').addClass('has-error');
        $('#password-verify').parents('.form-group').removeClass('has-success');
    } else {
        $('#password-verify').parents('.form-group').addClass('has-success');
        $('#password-verify').parents('.form-group').removeClass('has-error');
    }
}

function usernameValid(response) {
    if (response === "True") {
        $('#username').parents('.form-group').addClass('has-error');
        $('#username').parents('.form-group').removeClass('has-success');
    } else {
        $('#username').parents('.form-group').addClass('has-success');
        $('#username').parents('.form-group').removeClass('has-error');
    }
}

function attachTableListeners() {
    $('#prev-page').click(pageButtonClick);
    $('#next-page').click(pageButtonClick);
    $('.residents-modal-activator').click(loadModalData);
    $('.vote-btn').click(voteForPlanet);
}

function showStatisticsModal() {
    var button = $(this);
    var oldText = button.html();
    button.html('Loading...');
    $.ajax({
        url: '/get-statistics',
        success: function(response) {
            var data = JSON.parse(response);
            var tableBody = $('#statistics-modal table tbody');
            var heading = generateHeading();
            tableBody.empty().append(heading);
            for (let planet of data) {
                let row = generateRow(planet);
                tableBody.append(row);
            }
            $('#statistics-modal').modal('show').css('opacity', '0');
            $('#statistics-modal .modal-dialog').css('transform', 'translate(0,-25%)');
            button.html(oldText);
        }
    });
}

function generateHeading() {
    var heading = document.createElement('tr');
    var nameHeading = document.createElement('th');
    var votesHeading = document.createElement('th');
    nameHeading.appendChild(document.createTextNode('Planet'));
    votesHeading.appendChild(document.createTextNode('Votes'));
    heading.appendChild(nameHeading);
    heading.appendChild(votesHeading);
    return heading;
}

function generateRow(planet) {
    let row = document.createElement('tr');
    let name = document.createElement('td');
    let votes = document.createElement('td');
    name.appendChild(document.createTextNode(planet[0]));
    votes.appendChild(document.createTextNode(planet[1]));
    row.appendChild(name);
    row.appendChild(votes);
    return row;
}

function voteForPlanet() {
    var button = $(this);
    var pname = button.data('pname');
    $.ajax({
        url: `/vote-for-planet?pname=${pname}`,
        success: function(result) {
            $('#flash-wrapper').empty().append(result);
            $('.flashed-message').slideDown(750).fadeIn(750);
            setTimeout(function() {
                $('.flashed-message').slideUp(750).fadeOut(750);
            }, 2000);
        }
    });
}

function loadModalData(event) {
    var button = $(this);
    var oldText = button.html();
    button.html('Loading...');
    var url = button.data('purl');
    $('#residents-modal .modal-content').load(`/get-modal-content?url=${url}`, function() {
        $('#residents-modal').modal('show').css('opacity', '0');
        $('#residents-modal .modal-dialog').css('transform', 'translate(0,-25%)');
        button.html(oldText);
    });
}

function pageButtonClick() {
    var dataUrl = $(this).data('url');
    $('#content-wrapper').load(`/get-table?url=${dataUrl}`, function() {
        attachTableListeners();
    });
}