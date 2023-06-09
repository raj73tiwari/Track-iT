(function ($) {
    "use strict";

    // Spinner
    var spinner = function () {
        setTimeout(function () {
            if ($('#spinner').length > 0) {
                $('#spinner').removeClass('show');
            }
        }, 1);
    };
    spinner();



    // Sidebar Toggler
    $('.sidebar-toggler').click(function () {
        $('.sidebar, .content').toggleClass("open");
        return false;
    });



    // Chart Global Color
    Chart.defaults.color = "#6C7293";
    Chart.defaults.borderColor = "#000000";
    

    if (document.getElementById("dLabel") != null) {
        var dLabel = document.getElementById("dLabel").value;

    }
    if (document.getElementById("dValue") != null) {
        var dValue = document.getElementById("dValue").value;
        
        var ctx3 = $("#line-chart");
        var myChart3 = new Chart(ctx3, {
            type: "line",
            data: {
                labels: dLabel.split(" "),
                datasets: [{
                    label: "Value",
                    fill: false,
                    backgroundColor: "rgba(235, 22, 22, .7)",
                    data: dValue.split(" ").map(Number)
                }]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        type: 'time',

                    },
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }


    var labelsData = document.getElementById("labelsList").value;
    var valuesData = document.getElementById("valuesList").value;
    var typeData = document.getElementById("typeList").value;
    var countData = document.getElementById("countList").value;


    var ctx4 = $("#bar-chart").get(0).getContext("2d");
    var myChart4 = new Chart(ctx4, {
        type: "bar",
        data: {
            labels: labelsData.split(".&."),
            datasets: [{
                label: "Log count",
                backgroundColor: [
                    "rgba(235, 22, 22, .7)",
                    "rgba(235, 22, 22, .6)",
                    "rgba(235, 22, 22, .5)",
                    "rgba(235, 22, 22, .4)",
                    "rgba(235, 22, 22, .3)",
                ],
                data: valuesData.split(".&.").map(Number)

            }]
        },
        options: {
            responsive: true
        }
    });

   
    var ctx6 = $("#doughnut-chart").get(0).getContext("2d");
    var myChart6 = new Chart(ctx6, {
        type: "doughnut",
        data: {
            labels: typeData.split(" "),
            datasets: [{
                backgroundColor: [
                    "rgba(235, 22, 22, .7)",
                    "rgba(235, 22, 22, .6)",
                    "rgba(235, 22, 22, .5)",
                    "rgba(235, 22, 22, .4)",
                    "rgba(235, 22, 22, .3)"
                ],
                data: countData.split(" ").map(Number)
            }]
        },
        options: {
            responsive: true
        }
    });


})(jQuery);

