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

function clearModal() {
    //this method replaces function clearModal()
    /*loop sets all attributes of the modal dialogue to empty/default values.*/
    var attrs = ["name","text","valnum","defnum","anstxt","tfttxt","values_defaults", "answers", "text_field_type"];
    for (var i = 0; i < attrs.length; i++) {
        if (i<=5) { document.getElementById(attrs[i]).value = ""; }
        if (i>5) { document.getElementById(attrs[i]).style.display = "none"; }
    }
    document.getElementById("type").value="1";
    document.getElementById("saveQuestion").onclick=createQuestion;
}


//TODO: setModal is generated in the HTML generation in surveys...
function setModal(x) {
    document.getElementById("saveQuestion").onclick=changeQuestion;
    var type = document.getElementById(x + 'type').textContent;

    var answersid = x + 'answers';
    var defaultid = x + 'default';
    var rangeid = x + 'range';
    var text_field_type = x + 'tft';

    if (type == "slider") {
        document.getElementById("defnum").value = document.getElementById(defaultid).textContent;
        document.getElementById("valnum").value = document.getElementById(rangeid).textContent;
        set_element_type(2);
    } else if (type == "radio_button") {
        document.getElementById("anstxt").value = document.getElementById(answersid).textContent;
        set_element_type(3);
    } else if (type == "checkbox") {
        document.getElementById("anstxt").value = document.getElementById(answersid).textContent;
        set_element_type(4);
    } else if (type == "free_response") {
        document.getElementById("tfttxt").value = document.getElementById(text_field_type).textContent;
        set_element_type(5);
    } else { set_element_type(1); }

    var textid = x + 'text';
    var nameid = x + 'name';
    document.getElementById("name").value = document.getElementById(nameid).textContent;
    document.getElementById("oldName").value = x;
    document.getElementById("text").value = document.getElementById(textid).textContent;
}


function create_form(){
    //this is an example, we are not using php
    var form = document.createElement("form");
    form.setAttribute('method',"post");
    form.setAttribute('action',"submit.php");
}

function changeQuestion() {
    //Function unchanged from original
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


/*###########################################################################
#############################   Common components  ##########################
###########################################################################*/


//blah, these are not going to be for production.
function add_Q_header(question_id) {
    var header = '<div id="' + question_id + '" class="row">';
    //TODO: make an h3 element ...
    header += '<h3 id="' + question_id + 'question_id">' + question_id + '</h3>';
    header += '<input type="text" style="display:none;" question_id="' + question_id + '" value="' + question_id + '"></input>';
    add_to_survey(header);
}

function add_Q_footer(question_id) {
    var footer = '<p><button class="btn btn-primary" data-toggle="modal" data-target="#myModal" onclick="setModal(\'' + question_id + '\'); return false;">Edit</button>';
    footer += '<button class="btn btn-primary" onclick="deleteQuestion(\'' + question_id + '\'); return false;">Delete</button>';
    add_to_survey(footer);
}

function add_to_survey(q) {
    // add the question inside the survey
    // ignore the $ unimported, jquery is imported on the webpage.
    $("#survey").append(q);
}

/* Example template for question functions below.

function sample_create_question_type() {
    add_Q_header();
    //Here add logic to create HTML tags/inputs with appropriate attributes
    var i = document.createElement("input");
    i.type = "text";
    i.question_id = document.question.name.value;
    i.id = "???";
    i.style="display:none;";
    add_Q_footer();
    add_to_survey(i); }
*/


/*###########################################################################
############################## Element constructors #########################
###########################################################################*/

function create_question() {
    //replaces createQuestion()
    //this is actually a... quesion identifier of some form?
    /* creates new question, adds header and footer, */
    question_id = document.question.value
    add_Q_header(question_id);
    var type = document.getElementById("type").value;
    if (type == '1') { create_question_informational_text( question_id ); }
    else if (type == '2') { create_question_slider( question_id ); }
    else if (type == '3') { create_question_radio_button( question_id ); }
    else if (type == '4') { create_question_checkbox( question_id ); }
    else if (type == '5') { create_question_freeresponse( question_id ); }
    add_Q_footer(question_id);
}

//question_id is document.question.name.value
function setup_input_field(question_id, input_field_label, info_type, value) {
    // setup_input_field("info text", "informational_text", "text", "sentence") results in the following element:
    // <input type=​"text" style=​"display:​none;​" question_id=​"info text" input_field_label=​"informational_text" value=​"sentence">​
    var input_field = document.createElement( "input" );
    input_field.setAttribute( "type", info_type );
    input_field.setAttribute( "style", "display:none;" );
    input_field.setAttribute( "question_id", question_id );
    input_field.setAttribute( "input_field_label", input_field_label );
    input_field.setAttribute( "value", value );
    return input_field;
}

//type is unused
function create_div(question_id, input_field_label, type) {
    // create_div("abcdefg", "12345") results in...
    // <div id=​"abcdefg" our_type=​"a_type">​12345​</div>​
    var div = document.createElement( "div" );
    div.setAttribute("id", question_id );
    div.setAttribute( "our_type", type );
    div.appendChild( document.createTextNode( input_field_label ) );
    return div;
}


/*###########################################################################
####################################  Questions  ############################
###########################################################################*/


// not sure if this output is correct, test by shoving it into existing HTML += things.
// html += '<div id=​"1234567890" our_type=​"text">​informational text​</div>​'
// html += '<div id=​"1234567890" our_type=​"type">​informational text​</div>​'
// html += '<input type=​"text" style=​"display:​none;​" question_id=​"1234567890" input_field_label=​"informational_text" value=​"data">​'
// html += '<input type=​"type" style=​"display:​none;​" question_id=​"1234567890" input_field_label=​"informational_text" value=document.question.text.value>​'


// question type 1 is not a question, it is a blob of text
function create_question_informational_text( question_id ) {
    var div1 = create_div(1234567890, "informational text", "text");
    var div2 = create_div(1234567890, "informational text", "type");
    var input1 = setup_input_field(1234567890, "informational_text", "text", "data");
    var input2 = setup_input_field(1234567890, "informational_text", "type", document.question.text.value );
    // add_to_survey(i);
}

// question type 1 is not a question, it is a blob of text
// function create_question_informational_text( question_id ) {
//     console.log( div = create_div(1234567890, "informational text", "text") );
//     console.log( div = create_div(1234567890, "informational text", "type") );
//     console.log( input1 = setup_input_field(1234567890, "informational_text", "text", "data") );
//     console.log( input2 = setup_input_field(1234567890, "informational_text", "type", document.question.text.value ) );
//     // add_to_survey(i);
// }

// question type 2 is a slider
function create_question_slider() {
    var i = document.createElement("input");
    i.type = "text";
    i.question_id = document.question.name.value;
    add_to_survey(i);
}
// question type 3 is a radio button
function create_question_radio_button() {
    var i = document.createElement("input");
    i.type = "text";
    i.question_id = document.question.name.value;
    add_to_survey(i);
}
// question type 4 is a checkbox
function create_question_checkbox() {
    var i = document.createElement("input");
    i.type = "checkbox";
    i.question_id = document.question.name.value;
    add_to_survey(i);
}
// question type 5 is a free response
function create_question_freeresponse() {
    var i = document.createElement("input");
    i.type = "text";
    i.question_id = document.question.name.value;
    add_to_survey(i);
}




function submit() {
    // replaces end()
    var payload = JSON.stringify($('#survey').serializeArray());
    console.log(payload);
    $.post("/update_weekly", payload);
}





/* JOSH EXPERIMENTAL CODE FOR RADIO BUTTON AND CHECKBOX QUESTIONS
3 LINES OF NECESSARY HTML:
<div id="fieldsDiv">
</div>
<button type="button" onclick="addField()">Add new field</button>
*/
function addField() {
    /* TODO: give the input fields unique IDs! */
    var fieldsDiv = document.getElementById('fieldsDiv');
    var newField = document.createElement("div");
    newField.innerHTML = '<input type="text" name="option' + 2 + '"></input><button type="button" onclick="deleteField(this)">Delete</button><br><br>';
    /*alert(newField.innerHTML);*/
    fieldsDiv.appendChild(newField);
}

function deleteField(elem) {
    elem.parentNode.remove();
}