function set_type() {
    //this method replaces function setType()
}


function clear_modal() {
    //this method replaces function clearModal()

    /* This does something like set all attributes of a modal to none */
    document.getElementById("type").value="1";
    var attrs = ["name","text","valnum","defnum","anstxt","tfttxt"];
    for (var i = 0; i < attrs.length; i++) {
        document.getElementById(attrs[i]).value = "";
    }
    var attrs2 = ["values_defaults", "answers", "text_field_type"];
    for (i = 0; i < attrs2.length; i++) {
        document.getElementById(attrs2[i]).value = "none";
    }
}

function create_weekly_form() {
    /*Sample method to create a form that submits to update_weekly.
    This isn't needed, only demostrates setAttribute */
    var f = document.createElement("form");
    f.setAttribute('method',"post");
    f.setAttribute('action',"/update_weekly");
}

function add_Q_header() {
    /*It seems there exists some HTML that is added to each question added dynamically
      created that can be refactored out and placed here*/
}

function add_Q_footer() {
    /*It seems there exists some HTML that is added to the end of each question
    that can be refactored out and placed here*/
}

/*
// This is an example template for the functions below.
function sample_create_question_type() {
    add_Q_header();
    //Here add logic to create HTML tags/inputs with appropriate attributes
    var i = document.createElement("input");
    i.type = "text";
    i.name = document.question.name.value;
    i.id = "???";
    i.style="display:none;";
    add_Q_footer();
    add_to_survey(i);
}
*/

function create_question_slider() {
    //type 2
    var i = document.createElement("input");
    i.type = "text";
    i.name = document.question.name.value;
    add_to_survey(i);
}

function create_question_radio_button() {
    //type 3
    var i = document.createElement("input");
    i.type = "text";
    i.name = document.question.name.value;
    add_to_survey(i);
}

function create_question_checkbox() {
    //type 4
    var i = document.createElement("input");
    i.type = "checkbox";
    i.name = document.question.name.value;
    add_to_survey(i);
}

function create_question_freeresponse() {
    //type 5
    var i = document.createElement("input");
    i.type = "text";
    i.name = document.question.name.value;
    add_to_survey(i);
}

function create_question_informational_text() {
    //type 1
    var i = document.createElement("input");
    i.type = "text";
    i.name = document.question.name.value;
    add_to_survey(i);
}

function add_to_survey(q) {
    // add the question inside the survey
    $("survey").append(q);
}
