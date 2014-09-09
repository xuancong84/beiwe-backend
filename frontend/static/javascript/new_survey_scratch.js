function clearModal() {
    //this method replaces function clearModal()
    /*loop sets all attributes of the modal dialogue to empty/default values.*/
    var attrs = ["name","text","min","max","anstxt","tfttxt","min_value", "max_value", "answers", "fields_div", "text_field_type"];
    for (var i = 0; i < attrs.length; i++) {
        if (i<=5) { document.getElementById(attrs[i]).value = ""; }
        if (i>5) { document.getElementById(attrs[i]).style.display = "none"; }
    }
    document.getElementById("type").value="1";
    document.getElementById("saveQuestion").onclick=createQuestion;
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
    var footer = '<p><button class="btn btn-primary" data-toggle="modal" data-target="#editQuestionModal" onclick="setModal(\'' + question_id + '\'); return false;">Edit</button>';
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
    var question_id = document.question.value;
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
function create_div(question_id, input_field_label, inner_text) {
    // create_div("abcdefg", 'x', 'y') results in...
    //     <div id=​"abcdefg">​
    //         "x"
    //         "y"
    //     </div>​
    var div = document.createElement( "div" );
    div.setAttribute("id", question_id );
    div.appendChild( document.createTextNode( input_field_label ) );
    div.appendChild( document.createTextNode( inner_text ) );
    //we don't know exactly the da
    return div;
}

function create_question_type_div(question_id, inner_text){ return create_div(question_id, "Question Type: ", inner_text); }
function create_question_text_div(question_id, inner_text){ return create_div(question_id, "Question Text: ", inner_text); }
function create_text_field_div(question_id, inner_text){ return create_div(question_id, "Text Field Type: ", inner_text); }

/*###########################################################################
####################################  Questions  ############################
###########################################################################*/


function create_question_informational_text( question_id ) {
    var div1 = create_question_type_div(question_id, "text");
    var div2 = create_question_text_div(question_id, "type");
    var input1 = setup_input_field(question_id, "informational_text", "text", "data");
    var input2 = setup_input_field(question_id, "informational_text", "type", document.question.text.value );
    // add_to_survey(i);
}


// question type 2 is a slider
function create_question_slider( question_id ) {
    var div1 = create_question_type_div(question_id, "text");
    var div2 = create_question_text_div(question_id, "type");
    var div3 = create_div(question_id, "Values: ", "range");
    var div4 = create_div(question_id, "Default: ", "default");
    var input1 = setup_input_field(question_id, "slider", "text", "data");
    var input2 = setup_input_field(question_id, "slider", "type", document.question.text.value );
    var input3 = setup_input_field(question_id, "slider", "range", document.question.min.value );
    var input4 = setup_input_field(question_id, "slider", "default", document.question.max.value );
}
// question type 3 is a radio button
function create_question_radio_button( question_id ) {
    var div1 = create_question_type_div(question_id, "text");
    var div2 = create_question_text_div(question_id, "type");
    var div3 = create_div(question_id, "Answers: ", inner_text);
    var input1 = setup_input_field(question_id, "informational_text", "text", "data");
    var input2 = setup_input_field(question_id, "informational_text", "type", document.question.text.value );
    var input3 = setup_input_field(question_id, "informational_text", "type", document.question.anstxt.value );
}
// question type 4 is a checkbox
function create_question_checkbox( question_id ) {
    var div1 = create_question_type_div(question_id, "text");
    var div2 = create_question_text_div(question_id, "type");
    var div3 = create_div(question_id, "Answers: ", inner_text);
    var input1 = setup_input_field(question_id, "informational_text", "text", "data");
    var input2 = setup_input_field(question_id, "informational_text", "type", document.question.text.value );
    var input3 = setup_input_field(question_id, "informational_text", "type", document.question.anstxt.value );
}
// question type 5 is a free response
function create_question_freeresponse( question_id ) {
    var div1 = create_question_type_div(question_id, "text");
    var div2 = create_question_text_div(question_id, "type");
    var div3 = create_text_field_div(question_id, "tft");
    var input1 = setup_input_field(question_id, "informational_text", "text", "data");
    var input2 = setup_input_field(question_id, "informational_text", "type", document.question.text.value );
    var input3 = setup_input_field(question_id, "informational_text", "type", document.question.tfttxt.value );
}




function submit() {
    // replaces end()
    var payload = JSON.stringify($('#survey').serializeArray());
    console.log(payload);
    $.post("/update_weekly", payload);
}