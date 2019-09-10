/*
Copyright (c) 2017 Wind River Systems, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software  distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
OR CONDITIONS OF ANY KIND, either express or implied.
*/

function popup_message(title, message) {
    $("#popup-dialog .modal-dialog").width(600);
    $("#popup-dialog .modal-title").html(title);
    $("#popup-dialog .modal-body").html(message);
    $("#popup-dialog").modal();
}

$(document).ready(function() {



    $(".blockchain-node-status").each(function() {

        (function(uuid, element) {
            $.ajax({
                url: "/blockchain/nodes/status/" + uuid,
                type: "GET",
                dataType: "json",

                beforeSend: function() {
                },
                success: function(response) {
                    $(element).find(".blockchain-nodes-preload").hide();

                    status = response["status"];
                    $(element).find(".node-status-value")
                        .html(status).addClass("node-status-"
                        + ((status == "Running") ? "running" : "down"));

                },
                error: function(jqXHR, textStatus, errorThrown) {
                    $(element).find(".blockchain-nodes-preload").hide();
                    $(element).find(".node-status-value")
                        .html("Failed: " + errorThrown).addClass("node-status-down");
                }
            });
        })($(this).attr("uuid"), $(this));
    });

    $.ajax({
        url: "/ledger/components",
        type: "GET",
        dataType: "html",

        beforeSend: function() {
        },
        success: function(response) {
            $("#blockchain-components").html(response);
            $("#envelope-count").html($("#envelopes-count-value").val());
            $("#part-count").html($("#parts-count-value").val());
            $("#supplier-count").html($("#suppliers-count-value").val());
            $("#hyperledger-version").html($("#hyperledger-version-value").val());
        },
        error: function(jqXHR, textStatus, errorThrown) {
            popup_message("Error", errorThrown);
        }
    });
});



// only show one popover at a time
$(document).on("click", ".payload-data", function(evt) {
    $('.payload-data').not(this).popover("hide");
    $(this).popover("toggle");

});

$(document).on("click", ".blockchain-node", function(evt) {
    popup_message("Node Details", $(this).find(".blockchain-node-popup-content").html());

    (function(uuid) {
        $.ajax({
            url: "/blockchain/nodes/blocks/" + uuid,
            type: "GET",
            dataType: "html",

            beforeSend: function() {
                $("#popup-dialog .modal-dialog").width(600);
                $(".node-blocks-table-preload").show();
            },
            success: function(response) {
                $(".node-blocks-table-preload").hide();
                $("#popup-dialog .modal-dialog").width(730);
                $("#popup-dialog .node-blocks-table").html(response);
                $('[data-toggle="popover"]').popover({"trigger": "manual"});

            },
            error: function(jqXHR, textStatus, errorThrown) {
                $(".node-blocks-table-preload").hide();
                $("#popup-dialog .modal-dialog").width(600);
                $("#popup-dialog .node-blocks-table").html(errorThrown);
            }
        });
    })($(this).attr("uuid"));

});

$(document).on("click", ".blockchain-app", function(evt) {
    popup_message("App Details", $(this).find(".blockchain-app-popup-content").html());
});

$(document).on("click", ".bc-envelope-link", function(evt) {
    popup_message("Envelope Details",
        $(this).parent().find(".bc-envelope-details-popup").html());
});

$(document).on("click", ".part-name-link", function(evt) {
    popup_message("Part Details",
        $(this).parent().find(".blockchain-part-details-popup").html());
});

$(document).on("click", ".expand-collapse-title", function() {
    $(this).parent().find(".expand-collapse-content").first().toggle();
    var plusminus = $(this).parent().find(".expand-collapse-icon span").first();

    if (plusminus.hasClass("glyphicon-plus")) {
        plusminus.removeClass("glyphicon-plus").addClass("glyphicon-minus");
    } else {
        plusminus.removeClass("glyphicon-minus").addClass("glyphicon-plus");
    }
});