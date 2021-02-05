odoo.define('adm.inquiry', require => {
    "use strict"

    require('web.core');

    var studentCount = 1;

    function removeStudent(idStudent) {
        studentCount--;
        $(`#navStudent${idStudent}`).remove();
        $(`#student${idStudent}`).remove();
    }

    function addStudent() {
        studentCount++;
        var htmlTab =
            `<li class="nav-item" style="position: relative" id="navStudent${studentCount}">
        <a class="nav-link" id="student${studentCount}-tab" data-toggle="tab" href="#student${studentCount}"
            role="tab" aria-controls="student${studentCount}" aria-selected="false">Student ${studentCount}</a>
            <i class="fa fa-times" style="position: absolute; top: -0.5em; right: 0.1em; font-size: 1.4em; color: orangered; cursor: pointer;"
            onclick="removeStudent(${studentCount})"></i>
    </li>`;


        $(htmlTab).insertBefore($(this).parent());

        $('#studentsCount').val(studentCount);

        var studentClonnable = document.getElementById("student1").cloneNode(true);
        var studentTabContent = document.getElementById("studentsTabContent");

        studentTabContent.appendChild(studentClonnable);

        // Reassign ids
        $(studentClonnable).attr("id", "student" + studentCount);
        $(studentClonnable).attr("aria-labelledby", "student" + studentCount + "-tab");
        $(studentClonnable).removeClass("active");
        $(studentClonnable).removeClass("show");

        $(studentClonnable).find("input").each(function () {
            $(this).val("");
        });

        // Grade Level List
        var optionsGradeLevel = $('select#selStudent1CurrentGradeLevel option').clone();
        $('#selStudent' + studentCount + 'CurrentGradeLevel').append(optionsGradeLevel);

        //   document.querySelectorAll(".selectSchoolCode").forEach(function(element){
        //         element.addEventListener("change", function(){
        //             var schoolCodeID = $(this).find("option:selected").data("id");
        //             $(this).parent().parent().children().last().find("option").each(function(element){
        //                 var school_option_id = $(this).data("schoolid");
        //                 if(schoolCodeID != -1 && schoolCodeID == school_option_id)
        //                     $(this).removeClass('d-none')
        //                 else
        //                     $(this).addClass('d-none')
        //             })
        //             $(this).parent().parent().children().last().find("select").val(-1);
        //         })
        //     });
    }

    function getStates() {
        $('#selState').html("<option value='-1'>-Select a state-</option>");
        $.ajax({
            url: '/admission/states',
            type: 'GET',
            data: {'country_id': $('#selCountry').val()},
            success: function (data) {
                $.each(JSON.parse(data), function (i, state) {
                    // console.log(`<option
                    // value='${state.id}'>${state.name}</option>`);
                    $('#selState').append(`<option value='${state.id}'>${state.name}</option>`)
                })
            },
            error: function () {
                console.error("Un error ha ocurrido al cargar los states");
            }
        });

    }

    function changeState() {
        var select_state = $('#selState')
        select_state.children("option:gt(0)").hide();
        select_state.children("option[data-country='" + $(this).val() + "']").show();

        if (select_state.children("option:selected").is(":hidden")) {
            select_state.children("option:nth(0)").prop("selected", true);
        }
    }

//    function ready(fn) {
//        if (document.readyState != 'loading') {
//            fn();
//        } else {
//            document.addEventListener('DOMContentLoaded', fn);
//        }
//    }

    function toggleSecondParent() {
        $("#section_parent_2").toggle();

        if ($("#section_parent_2").css("display") == "none") {
            $("#section_parent_2 input").attr("disabled", true);
            $("#section_parent_2 select").attr("disabled", true);
        } else {
            $("#section_parent_2 input").attr("disabled", false);
            $("#section_parent_2 select").attr("disabled", false);
        }
    }

    function hideDataParents() {
        $(".hide_parent").toggle();
        $("#input_family_id").toggle();

        if ($("#checkbox_family_id").prop("checked"))
            $("#section_parent_2").hide()

        if ($(".hide_parent").css("display") == "none") {
            $(".hide_parent input").attr("disabled", true);
            $(".hide_parent select").attr("disabled", true);
        } else {
            $(".hide_parent input").attr("disabled", false);
            $(".hide_parent select").attr("disabled", false);
        }

        if ($("#input_family_id").css("display") == "none")
            $(".input_family_id input").attr("disabled", true);
        else
            $(".input_family_id input").attr("disabled", false);

    }

    function checkDuplicateContact() {
        var first_name = $(this).parent().parent().parent().find(".firstname");
        var last_name = $(this).parent().parent().parent().find(".lastname");
        var email = $(this).parent().parent().parent().find(".email");
        var cellphone = $(this).parent().parent().parent().find(".phone");

        if (first_name.val() != undefined && first_name.val() != '' &&
            last_name.val() != undefined && last_name.val() != '' &&
            email.val() != undefined && email.val() != '' &&
            cellphone.val() != undefined && cellphone.val() != '') {

            $.ajax({
                url: "/admission/checkDuplicateContact",
                type: "POST",
                data: {
                    "firstname": first_name.val(),
                    "lastname": last_name.val(),
                    "email": email.val(),
                    "cellphone": cellphone.val()
                },
                success: function (data) {
                    var jsonData = JSON.parse(data);
                    //var element_event = elem;
                    if (jsonData.parent_name || jsonData.email || jsonData.cellphone) {
                        $("#emailChecked").text(jsonData.email);
                        $("#modalError").modal('show');
                        var messageResponse = '';
                        //element_event.val('');

                        messageResponse = 'Hi, ' + first_name.val() + ' ' + last_name.val() + '<br>'

                        if (jsonData.parent_name)
                            messageResponse += 'In the system exists a contact with same name.<br>'

                        if (jsonData.email)
                            messageResponse += 'The email <b>' + email.val() + '</b> exists in the system.<br>'

                        if (jsonData.cellphone)
                            messageResponse += 'The mobile <b>' + cellphone.val() + '</b> exists in the system.<br>'

                        messageResponse += "If you want to add this person to the family. Please contact with the admission support to <b>support@iae.edu</b>."

                        $("#bodyMessageIssue").html(messageResponse);
                    }

                }
            })
        }
    }

    $(document).ready(function () {
        document.querySelector("#add-tab").addEventListener("click", addStudent)
        document.querySelectorAll(".checkDuplicated").forEach(
            function (element) {
                element.addEventListener("change", checkDuplicateContact)
            }
        );
        $('#showSecondParent').on('click',toggleSecondParent)
        $('#checkbox_family_id').on('click',hideDataParents)
        $('#selCountry').on('change',getStates)
        //document.querySelector("#selCountry").addEventListener("change", changeState)

        document.querySelectorAll(".custom-file-input").forEach(function (element) {
            element.addEventListener("change", function () {
                var fileName = this.files[0].name
                $(this).next("label").text(fileName);
            })
        })

        var optionValues = [];
        document.querySelectorAll(".selectSchoolCode option").forEach(function (element) {
            if (optionValues.indexOf(element.value) > -1) {
                element.remove();
            } else {
                optionValues.push(element.value);
            }
        })
        document.querySelectorAll(".selectSchoolCode").forEach(function (element) {
            element.addEventListener("change", function () {
                var schoolCodeID = $(this).find("option:selected").data("id");
                $(this).parent().parent().children().last().find("option").each(function (element) {
                    var school_option_id = $(this).data("schoolid");
                    if (schoolCodeID != -1 && schoolCodeID == school_option_id)
                        $(this).removeClass('d-none')
                    else
                        $(this).addClass('d-none')
                })
                $(this).parent().parent().children().last().find("select").val(-1);
            })
        });

        document.querySelectorAll("#inquiry_country_id").forEach(function (element) {
            element.addEventListener("change", function () {
                var countryCode = $(this).find("option:selected").val();
                $(this).parent().parent().children().last().find("option").each(function (element) {
                    var country_option_id = $(this).data("country");
                    if (countryCode != -1 && countryCode == country_option_id)
                        $(this).removeClass('d-none')
                    else
                        $(this).addClass('d-none')
                })
                if ($("#inquiry_state_id option:not(.d-none)").length > 0)
                    $("#inquiry_state_id option:not(.d-none)").first().attr("selected", "selected");
                else
                    $("#inquiry_state_id").val(-1);
            })
        });
    });
});