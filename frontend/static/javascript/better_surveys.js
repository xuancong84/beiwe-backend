function set_type() {
    //this method replaces function setType()
    //sets up fields? for form question submission?
    document.getElementById("answers").style.display="none";
    document.getElementById("values_defaults").style.display="none";
    document.getElementById("text_field_type").style.display="none";
    var type = document.getElementById("type").value;
    if (type == "2") { document.getElementById("values_defaults").style.display="inline"; }
    else if (type == "5") { document.getElementById("text_field_type").style.display="inline"; }
    else { document.getElementById("answers").style.display="inline"; }
}

function create_question() {
    //replaces createQuestion()
    // grabs the question type, runs the correct logic to make a question.
    var type = document.getElementById("type").value;
    if (type == '1') { create_question_informational_text(); }
    else if (type == '2') { create_question_slider(); }
    else if (type == '3') { create_question_radio_button(); }
    else if (type == '4') { create_question_checkbox(); }
    else if (type == '5') { create_question_freeresponse(); }
}

function clear_modal() {
    //this method replaces function clearModal()
    /* Sets all attributes of the modal dialogue to empty/default values. */
    var attrs = ["name","text","valnum","defnum","anstxt","tfttxt"];
    for (var i = 0; i < attrs.length; i++) {
        document.getElementById(attrs[i]).value = ""; }
    var attrs2 = ["values_defaults", "answers", "text_field_type"];
    for (i = 0; i < attrs2.length; i++) {
        document.getElementById(attrs2[i]).value = "none"; }
    document.getElementById("type").value="1";
}

function set_modal(x) {
    document.getElementById("saveQuestion").onclick=changeQuestion;
    var nameid = x + 'name';
    var typeid = x + 'type';
    var textid = x + 'text';
    var rangeid = x + 'range';
    var defaultid = x + 'default';
    var answersid = x + 'answers';
    var text_field_type = x + 'tft';

    var type = document.getElementById(typeid).textContent;

    if (type == "slider") {
        document.getElementById("defnum").value = document.getElementById(defaultid).textContent;
        document.getElementById("valnum").value = document.getElementById(rangeid).textContent;
        set_element_type(2); }
    else if (type == "radio_button") {
        document.getElementById("anstxt").value = document.getElementById(answersid).textContent;
        set_element_type(3); }
    else if (type == "checkbox") {
        document.getElementById("anstxt").value = document.getElementById(answersid).textContent;
        set_element_type(4); }
    else if (type == "free_response") {
        document.getElementById("tfttxt").value = document.getElementById(text_field_type).textContent;
        set_element_type(5); }
    else { set_element_type(1); }
    
    document.getElementById("name").value = document.getElementById(nameid).textContent;
    document.getElementById("oldName").value = x;
    document.getElementById("text").value = document.getElementById(textid).textContent;
}

//Function unchanged from original
function changeQuestion() {
    create_question();
    delete_question( document.question.oldName.value );
}
function delete_question(a_question) {
    var old = document.getElementById(a_question);
    old.parentNode.removeChild(old);
}
function set_element_type(number) {
    document.getElementById("type").value = number.toString();
}

function create_weekly_form() {
    /*Sample method to create a form that submits to update_weekly.
    This isn't needed, only demostrates setAttribute */
    var form = document.createElement("form");
    form.setAttribute('method',"post");
    form.setAttribute('action',"/update_weekly");
}

function add_Q_header() {
    var name = document.question.name.value;
    var header = '<div id="' + name + '" class="row">';
    header += '<h3 id="' + name + 'name">' + name + '</h3>';
    header += '<input type="text" style="display:none;" name="' + name + '" value="' + name + '"></input>';
    add_to_survey(header);
}

function add_Q_footer() {
    var name = document.question.name.value;
    var footer = '<p><button class="btn btn-primary" data-toggle="modal" data-target="#myModal" onclick="setModal(\'' + name + '\'); return false;">Edit</button>';
    footer += '<button class="btn btn-primary" onclick="deleteQuestion(\'' + name + '\'); return false;">Delete</button>';
    add_to_survey(footer);
}

/* This is an example template for the functions below.
function sample_create_question_type() {
    add_Q_header();
    //Here add logic to create HTML tags/inputs with appropriate attributes
    var i = document.createElement("input");
    i.type = "text";
    i.name = document.question.name.value;
    i.id = "???";
    i.style="display:none;";
    add_Q_footer();
    add_to_survey(i); }
*/


// question type 1 is not a question, it is a blob of text
function create_question_informational_text() {
    var i = document.createElement("input");
    i.type = "text";
    i.name = document.question.name.value;
    add_to_survey(i);
}
// question type 2 is a slider
function create_question_slider() {
    var i = document.createElement("input");
    i.type = "text";
    i.name = document.question.name.value;
    add_to_survey(i);
}
// question type 3 is a radio button
function create_question_radio_button() {
    var i = document.createElement("input");
    i.type = "text";
    i.name = document.question.name.value;
    add_to_survey(i);
}
// question type 4 is a checkbox
function create_question_checkbox() {
    var i = document.createElement("input");
    i.type = "checkbox";
    i.name = document.question.name.value;
    add_to_survey(i);
}
// question type 5 is a free response
function create_question_freeresponse() {
    var i = document.createElement("input");
    i.type = "text";
    i.name = document.question.name.value;
    add_to_survey(i);
}

function add_to_survey(q) {
    // add the question inside the survey
    // ignore the $ unimported, jquery is imported on the webpage.
    $("survey").append(q);
}

function submit() {
    var payload = JSON.stringify($('#survey').serializeArray());
    console.log(payload);
    $.post("/update_weekly", payload);
}