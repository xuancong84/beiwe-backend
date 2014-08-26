function setType() {
    //Sets the type of question, sets view elements of the modal dialogue.
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

// not currently used, *seems* to work when swapped in, probably not easy to debug.
function more_compact_setType() {
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

function setModal(x) {
//     console.log("set");
    document.getElementById("saveQuestion").onclick=changeQuestion;
    var nameid = x + 'name';
    var typeid = x + 'type';
    var textid = x + 'text';
    var rangeid = x + 'range';
    var defaultid = x + 'default';
    var answersid = x + 'answers';
    var tftid = x + 'tft';
    document.getElementById("name").value = document.getElementById(nameid).textContent;
    document.getElementById("oldName").value = x;
    document.getElementById("text").value = document.getElementById(textid).textContent;
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
    console.log("change");
    createQuestion();
    x = document.question.oldName.value;
    deleteQuestion(x);
    /*nameid = x + 'name';
    typeid = x + 'type';
    textid = x + 'text';
    rangeid = x + 'range';
    defaultid = x + 'default';
    answersid = x + 'answers';
    tftid = x + 'tft';
    document.getElementById(nameid).textContent =  document.getElementById("name").value;
    document.getElementById(textid).textContent = document.getElementById("text").value;
    if (document.getElementById("type").value == "2") {
        document.getElementById(typeid).textContent = "slider";
        document.getElementById(rangeid).textContent = document.getElementById("valnum").value;
        document.getElementById(defaultid).textContent = document.getElementById("defnum").value;
    } else if (document.getElementById("type").value == "3") {
         document.getElementById(typeid).textContent = "radio_button";
        document.getElementById(answerid).textContent = document.getElementById("anstxt").value;
    } else if (document.getElementById("type").value == "4") {
        document.getElementById(typeid).textContent = "checkbox";
        document.getElementById(answerid).textContent = document.getElementById("anstxt").value;
    } else if (document.getElementById("type").value == "5") {
        document.getElementById(typeid).textContent = "free_response";
        document.getElementById(tftid).textContent = document.getElementById("tfttxt").value;
    } else {
        document.getElementById(typeid).value = "informational_text";h
    }*/
}

function createQuestion() {
    name = document.question.name.value;
    var html = '<div id="' + name + '" class="row">';
    html += '<h3 id="' + name + 'name">' + name + '</h3>';
    html += '<input type="text" style="display:none;" name="' + name + '" value="' + name + '"></input>';
    if (document.getElementById("type").value == '2') {
        html += 'Question type: <div id="' + name + 'type">slider</div></p>';
        html += 'Question text: <div id="' + name + 'text">' + document.question.text.value + '</div></p>';
        html += 'Slider range: <div id="' + name + 'range">' + document.question.valnum.value + '</div>';
        html += 'default: <div id="' + name + 'default">' + document.question.defnum.value + '</div></p>';
        html += '<input type="text" style="display:none;" name="' + name + 'type" value="slider"></input>';
        html += '<input type="text" style="display:none;" name="' + name + 'text" value="' + document.question.text.value + '"></input>';
        html += '<input type="text" style="display:none;" name="' + name + 'range" value="' + document.question.valnum.value + '"></input>';
        html += '<input type="text" style="display:none;" name="' + name + 'default" value="' + document.question.defnum.value + '"></input>';
    } else if (document.getElementById("type").value == '3') {
        html += '<p>Question type: <div id="' + name + 'type">radio_button</div></p>';
        html += '<p>Question text: <div id="' + name + 'text">' + document.question.text.value + '</div></p>';
        html += '<p>Answers:';
        html += '<div id="' + name + 'answers">';
        html += document.getElementById('anstxt').value + '</div></p>';
        html += '<input type="text" style="display:none;" name="' + name + 'type" value="radio_button"></input>';
        html += '<input type="text" style="display:none;" name="' + name + 'text" value="' + document.question.text.value + '"></input>';
        html += '<input type="text" style="display:none;" name="' + name + 'answers" value="' + document.question.anstxt.value + '"></input>';
    } else if (document.getElementById("type").value == '4') {
        html += '<p>Question type: <div id="' + name + 'type">checkbox</div></p>';
        html += '<p>Question text: <div id="' + name + 'text">' + document.question.text.value + '</div></p>';
        html += '<p>Answers:';
        html += '<div id="' + name + 'answers">';
        html += document.question.anstxt.value + '</div></p>';
        html += '<input type="text" style="display:none;" name="' + name + 'type" value="checkbox"></input>';
        html += '<input type="text" style="display:none;" name="' + name + 'text" value="' + document.question.text.value + '"></input>';
        html += '<input type="text" style="display:none;" name="' + name + 'answers" value="' + document.question.anstxt.value + '"></input>';
    } else if (document.getElementById("type").value == '5') {
        html += '<p>Question type: <div id="' + name + 'type">free_response</div></p>';
        html += '<p>Question text: <div id="' + name + 'text">' + document.question.text.value + '</div></p>';
        html += '<p>Text Field Type: <div id="' + name + 'tft">' + document.question.tfttxt.value + '</div></p>';
        html += '<input type="text" style="display:none;" name="' + name + 'type" value="free_response"></input>';
        html += '<input type="text" style="display:none;" name="' + name + 'text" value="' + document.question.text.value + '"></input>';
        html += '<input type="text" style="display:none;" name="' + name + 'tft" value="' + document.question.tfttxt.value + '"></input>';
    } else {
        html += '<p>Question type: <div id="' + name + 'type">informational_text</div></p>';
        html += '<p>Question text: <div id="' + name + 'text">' + document.question.text.value + '</div></p>';
        html += '<input type="text" style="display:none;" name="' + name + 'type" value="informational_text"></input>';
        html += '<input type="text" style="display:none;" name="' + name + 'text" value="' + document.question.text.value + '"></input>';
    }
    html += '<p><button class="btn btn-primary" data-toggle="modal" data-target="#myModal" onclick="setModal(\'' + name + '\'); return false;">Edit</button>';
    html += '<button class="btn btn-primary" onclick="deleteQuestion(\'' + name + '\'); return false;">Delete</button>';
    addHTML(html);
}

function deleteQuestion(x) {
    console.log("delete");
    var old = document.getElementById(x);
    old.parentNode.removeChild(old);
}

function addHTML(html) {
    if (document.all)
        document.getElementById("newQuestions").insertAdjacentHTML('beforeEnd', html);
    else if (document.createRange) {
        var range = document.createRange();
        range.setStartAfter(document.body.lastChild);
        var cFrag = range.createContextualFragment(html);
        document.getElementById("newQuestions").appendChild(cFrag);
    }
    else if (document.layers) {
        var X = new Layer(window.innerWidth);
        X.document.open();
        X.document.write(html);
        X.document.close();
        X.top = document.height;
        document.height += X.document.height;
        X.visibility = 'show';
    }
}

function end() {
    var payload = JSON.stringify($('#survey').serializeArray());
    console.log(payload);
    $.post("/update_weekly", payload);
}
