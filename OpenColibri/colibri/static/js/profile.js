window.onload = function () {
    this.appendableActiveGroupTable = $('#table-active-groups-appendable');
    _this = this;
    ajaxCall = function (url) {
        $.ajax({
            type: "GET",
            url: url,
            dataType: 'json',

            success: function (json) {
                var groups = JSON.parse(json.groups);
                html = '';
                var len = groups.length;
                console.log(groups);
                for (var i = 0; i < groups.length; ++i) {
                    var members = 'This group does not have any members yet';
                    var users = JSON.parse(groups[i].users)
                    if (users.length) {
                        members = '';
                        for (var j = 0; j < users.length; j++) {
                            var username = users[j].username;
                            var firstName = users[j].firstName ? '' + users[j].firstName : '';
                            var lastName = users[j].lastName ? ' ' + users[j].lastName : '';
                            var parenthesis = ''
                            if ((firstName != '') || (lastName != '')) {
                                members += '<a style="color:#495961" href="/profile/' + users[j].userID + '">' + '<span style="font-size:15px"><b>' + username + '</b></span>' + ' (' + firstName + lastName + ') </a>';
                            }
                            else {
                                members += '<a style="color:#495961" href="/profile/' + users[j].userID + '">' + '<span style="font-size:15px"><b>' + username + '</b></span>' + firstName + lastName + '</a>';
                            }
                            if (j != users.length - 1) {
                                members += '<br/> ';
                            }
                        }
                    }
                    html += '<tr id="group-' + groups[i].id + '">' +
                        '<td>' + groups[i].name +
                        renderEdit(groups[i]) +
                        renderDelete(groups[i]) + '</td>' +
                        '<td>' + members + '</td>' +
                        '<td>' + groups[i].role + renderLeaveGroup(groups[i]) + '</td>' +
                        '</tr>';
                }
                _this.appendableActiveGroupTable.html(html);
                $('.delete-button').each(function (element) {
                    $(this).click(function () {
                        var answer = confirm("Are you sure you want to delete this group?")
                        var groupID = $(this).data('groupid');
                        if (answer) {
                            $.ajax({
                                type: "POST",
                                url: $(this).data('url'),

                                success: function (json) {
                                    var messageTag = "#delete-success-message-" + groupID;
                                    var groupTag = "#group-" + groupID;
                                    $(messageTag).show('slow', function () {
                                        setTimeout(function () {
                                            $(groupTag).remove();
                                        }, 1250);
                                    });
                                }
                            });
                        }
                    })
                });
                $('div[id^="leave-group-"]').each(function (element) {
                    $(this).click(function () {
                        var answer = confirm("Are you sure you want to leave this group?")
                        var groupID = $(this).data('groupid');
                        if (answer) {
                            $.ajax({
                                type: "POST",
                                data: {
                                    'organizationID': groupID
                                },
                                url: '/api/colibri/organizationuser/leave-group/?format=json',
                                dataType: 'json',

                                success: function (json) {
                                    var messageTag = "#leave-group-success-message-" + groupID;
                                    $(messageTag).show('slow', function () {
                                        setTimeout(function () {
                                            var radioIDSelector = "#" + $('input[name=groups]:checked', '#groups-form').attr('id');
                                            $(radioIDSelector).change();
                                        }, 1250);
                                    });
                                },

                                error: function (error, description, s) {
                                    console.log(error);
                                    console.log(s);
                                }
                            });
                        }
                    })
                });
            },

            error: function (error, description) {
                console.log(error);
                console.log(description);
            }
        });
    };

    removeRows = function () {
        $("[id^='row-group-']").each(function (i) {
            $(this).remove();
        });
    };

    $('#groups-all').change(function () {
        removeRows();
        ajaxCall('/api/colibri/organization/all/?format=json')
    });
    $('#groups-admin').change(function () {
        removeRows();
        ajaxCall('/api/colibri/organization/i-admin/?format=json')
    });
    $('#groups-member').change(function () {
        removeRows();
        ajaxCall('/api/colibri/organization/i-member/?format=json')
    });
    $('#groups-all').change();

    renderDelete = function (object) {
        if (object.role == 'Owner') {
            return ' &nbsp; <a class="delete-button" data-groupid="' + object.id + '" data-url="/groups/' + object.id + '/delete/">' +
                '<img src="/s/imgs/icon_deletelink.gif" alt="Delete the Group"/>' +
                '</a><div id="delete-success-message-' + object.id + '" class = "hidden colibrimsg" >You successfully deleted group ' + object.name + '!</div>';
        }
        return '';
    };

    renderEdit = function (object) {
        if (object.role == 'Admin' || object.role == 'Owner') {
            return '&nbsp; '
//               <a href="/groups/' + object.id + '/edit/">' +
//               '<img src="/s/imgs/icon_changelink.gif" alt="Edit the Group"/>' +
//           '</a>';
        }
        return '';
    };

    renderLeaveGroup = function (object) {
        if (object.role == 'Admin' || object.role == 'Member') {
            return '<div id="leave-group-' + object.id + '" ' +
                'class="float-right button rosy small"' +
                'data-groupid="' + object.id + '">' +
                'Leave group' +
                '</div><div id="leave-group-success-message-' + object.id + '" class = "hidden colibrimsg" >You successfully left group ' + object.name + '!</div>';
        }
        return '';
    };

}



