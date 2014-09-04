function setType() {
    console.log("set type");
    //TODO: compactify this code (set things to none at the beginning, then change things.)
    //Sets the type of question, sets up view elements for the modal dialogue.
    //This setup is carried through into the questions created for the survey.
    if (document.getElementById("type").value == "1") {
        document.getElementById("values_defaults").style.display="none";
        document.getElementById("answers").style.display="none";
        document.getElementById("text_field_type").style.display="none";
    } else if (document.getElementById("type").value == "2") {
        document.getElementById("values_defaults").style.display="inline";
        document.getElementById("answers").style.display="none";
        document.getElementById("text_field_type").style.display="none";
    } else if (document.getElementById("type").value == "5") {
        document.getElementById("values_defaults").style.display="none";
        document.getElementById("answers").style.display="none";
        document.getElementById("text_field_type").style.display="inline";
    } else {
        document.getElementById("values_defaults").style.display="none";
        document.getElementById("answers").style.display="inline";
        document.getElementById("text_field_type").style.display="none";
    }
}

function clearModal() {
    console.log("clear modal");
    //resets the modal dialogue values to empty, used when creating a new question.
    /*loop sets all attributes of the modal dialogue to empty/default values.*/
    var attrs = ["name","text","valnum","defnum","anstxt","tfttxt","values_defaults", "answers", "text_field_type"];
    for (var i = 0; i < attrs.length; i++) {
        if (i<=5) { document.getElementById(attrs[i]).value = ""; }
        if (i>5) { document.getElementById(attrs[i]).style.display = "none"; }
    }
    document.getElementById("type").value="1";
    document.getElementById("saveQuestion").onclick=createQuestion;
}

function setModal(question_name) {
    //TODO: only answerID is used more than once in the logic.
    //TODO: typeid is only ever used as part of document.getElementById(typeid).textContent
    console.log("setModal");
    document.getElementById("saveQuestion").onclick=changeQuestion;
    var nameid = question_name + 'name';
    document.getElementById("name").value = document.getElementById(nameid).textContent;
    var textid = question_name + 'text';
    document.getElementById("text").value = document.getElementById(textid).textContent;

    var rangeid = question_name + 'range';
    var typeid = question_name + 'type';
    var defaultid = question_name + 'default';
    var tftid = question_name + 'tft';
    var answersid = question_name + 'answers';

    document.getElementById("oldName").value = question_name;
    if (document.getElementById(typeid).textContent == "slider") {
        console.log("slider");
        document.getElementById("type").value = "2";
        document.getElementById("valnum").value = document.getElementById(rangeid).textContent;
        document.getElementById("defnum").value = document.getElementById(defaultid).textContent;
    } else if (document.getElementById(typeid).textContent == "radio_button") {
        console.log("radio");
         document.getElementById("type").value = "3";
        document.getElementById("anstxt").value = document.getElementById(answersid).textContent;
    } else if (document.getElementById(typeid).textContent == "checkbox") {
        console.log("checkbox");
        document.getElementById("type").value = "4";
        document.getElementById("anstxt").value = document.getElementById(answersid).textContent;
    } else if (document.getElementById(typeid).textContent == "free_response") {
        console.log("free");
        document.getElementById("type").value = "5";
        document.getElementById("tfttxt").value = document.getElementById(tftid).textContent;
    } else {
        console.log("info");
        document.getElementById("type").value = "1";
    }
}

function changeQuestion() {
    // Replaces the saved question with the contents of the working question.
    console.log("change");
    createQuestion();
    var x = document.question.oldName.value;
    deleteQuestion(x);
}

function deleteQuestion(x) {
    //TODO: track down exactly what x is, rename variable accordingly.
    // deletes a question.
    console.log("delete");
    var old = document.getElementById(x);
    old.parentNode.removeChild(old);
}

// shall henceforth be referred to as "The Monster"
function createQuestion() {
    var name = document.question.name.value;
    var html = '<div id="' + name + '" class="row">';
    html += '<h3 id="' + name + 'name">' + name + '</h3>';
    html += '<input type="text" style="display:none;" name="' + name + '" value="' + name + '"></input>';
    if (document.getElementById("type").value == '2') {
        html += 'Question type: <div id="' + name + 'type">slider</div>';
        html += 'Question text: <div id="' + name + 'text">' + document.question.text.value + '</div>';
        html += 'Slider range: <div id="' + name + 'range">' + document.question.valnum.value + '</div>';
        html += 'default: <div id="' + name + 'default">' + document.question.defnum.value + '</div>';
        html += '<input type="text" style="display:none;" name="' + name + 'type" value="slider"></input>';
        html += '<input type="text" style="display:none;" name="' + name + 'text" value="' + document.question.text.value + '"></input>';
        html += '<input type="text" style="display:none;" name="' + name + 'range" value="' + document.question.valnum.value + '"></input>';
        html += '<input type="text" style="display:none;" name="' + name + 'default" value="' + document.question.defnum.value + '"></input>';
    } else if (document.getElementById("type").value == '3') {
        html += 'Question type: <div id="' + name + 'type">radio_button</div>';
        html += 'Question text: <div id="' + name + 'text">' + document.question.text.value + '</div>';
        html += 'Answers:';
        html += '<div id="' + name + 'answers">';
        html += document.getElementById('anstxt').value + '</div>';
        html += '<input type="text" style="display:none;" name="' + name + 'type" value="radio_button"></input>';
        html += '<input type="text" style="display:none;" name="' + name + 'text" value="' + document.question.text.value + '"></input>';
        html += '<input type="text" style="display:none;" name="' + name + 'answers" value="' + document.question.anstxt.value + '"></input>';
    } else if (document.getElementById("type").value == '4') {
        html += ' <div id="' + name + 'type">Question type:checkbox</div>';
        html += 'Question text: <div id="' + name + 'text">' + document.question.text.value + '</div>';
        html += 'Answers:';
        html += '<div id="' + name + 'answers">';
        html += document.question.anstxt.value + '</div>';
        html += '<input type="text" style="display:none;" name="' + name + 'type" value="checkbox"></input>';
        html += '<input type="text" style="display:none;" name="' + name + 'text" value="' + document.question.text.value + '"></input>';
        html += '<input type="text" style="display:none;" name="' + name + 'answers" value="' + document.question.anstxt.value + '"></input>';
    } else if (document.getElementById("type").value == '5') {
        html += 'Question type: <div id="' + name + 'type">free_response</div>';
        html += 'Question text: <div id="' + name + 'text">' + document.question.text.value + '</div>';
        html += 'Text Field Type: <div id="' + name + 'tft">' + document.question.tfttxt.value + '</div>';
        html += '<input type="text" style="display:none;" name="' + name + 'type" value="free_response"></input>';
        html += '<input type="text" style="display:none;" name="' + name + 'text" value="' + document.question.text.value + '"></input>';
        html += '<input type="text" style="display:none;" name="' + name + 'tft" value="' + document.question.tfttxt.value + '"></input>';
    } else {
        html += 'Question type: <div id="' + name + 'type">informational_text</div>';
        html += 'Question text: <div id="' + name + 'text">' + document.question.text.value + '</div>';
        html += '<input type="text" style="display:none;" name="' + name + 'type" value="informational_text"></input>';
        html += '<input type="text" style="display:none;" name="' + name + 'text" value="' + document.question.text.value + '"></input>';
    }
    html += '<button class="btn btn-primary" data-toggle="modal" data-target="#myModal" onclick="setModal(\'' + name + '\'); return false;">Edit</button>';
    html += '<button class="btn btn-primary" onclick="deleteQuestion(\'' + name + '\'); return false;">Delete</button>';
    addHTML(html);
}


//Accourding to Mike, we are probably good as long as they are running something newer than i.e. 7
//TODO: put in a check somewhere about browser version.
function addHTML(html) {
    document.getElementById("newQuestions").insertAdjacentHTML('beforeEnd', html);
//from following the code flow, the first one (document.all) must be the one that passes on modern browsers, and then the document
//     if (document.all) { //document.all is a MS proprietary command, I believe this is code to handle IE.
//         document.getElementById("newQuestions").insertAdjacentHTML('beforeEnd', html);
//     }
//     else if (document.createRange) { //handles another case, only works in ie and Opera (but works on chris's firefox
//         var range = document.createRange();
//         range.setStartAfter(document.body.lastChild);
//         var cFrag = range.createContextualFragment(html);
//         document.getElementById("newQuestions").appendChild(cFrag);
//     }
//     else if (document.layers) { //and this is some old Netscape compatible javascript
//         var X = new Layer(window.innerWidth);
//         X.document.open();
//         X.document.write(html);
//         X.document.close();
//         X.top = document.height;
//         document.height += X.document.height;
//         X.visibility = 'show';
//     }
}


function end() {
    //TODO: work out the python command to pull this of the form submission,
    // I think json.dumps(request.files["survey"])).
    //old: var payload = JSON.stringify($('#survey').serializeArray());

    //this works
    var payload = JSON.stringify($( document.getElementsByName("survey") ).serializeArray());
    console.log(payload);
    $.post("/update_weekly", payload);
}



function get_survey(){
    return document.getElementByName("survey");

}

