function setType() {
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
	document.getElementById("values_defaults").style.display="none";
	document.getElementById("answers").style.display="none";
	document.getElementById("text_field_type").style.display="none";
	document.getElementById("name").value="";
	document.getElementById("text").value="";
	document.getElementById("type").value="1";
	document.getElementById("valnum").value="";
	document.getElementById("defnum").value="";
	document.getElementById("anstxt").value="";
	document.getElementById("tfttxt").value="";
	document.getElementById("saveQuestion").onclick=createQuestion;
}

function setModal(x) {
	document.getElementById("saveQuestion").onclick=changeQuestion;
	nameid = x + 'name';
	typeid = x + 'type';
	textid = x + 'text';
	rangeid = x + 'range';
	defaultid = x + 'default';
	answersid = x + 'answers';
	tftid = x + 'tft';
	document.getElementById("name").value = document.getElementById(nameid).textContent;
	document.getElementById("oldName").value = x;
	document.getElementById("text").value = document.getElementById(textid).textContent;	
	if (document.getElementById(typeid).textContent == "slider") {
		document.getElementById("type").value = "2";
		document.getElementById("valnum").value = document.getElementById(rangeid).textContent;
		document.getElementById("defnum").value = document.getElementById(defaultid).textContent;
	} else if (document.getElementById(typeid).textContent == "radio_button") {
	 	document.getElementById("type").value = "3";
		document.getElementById("anstxt").value = document.getElementById(answersid).textContent;
	} else if (document.getElementById(typeid).textContent == "checkbox") {
		document.getElementById("type").value = "4";
		document.getElementById("anstxt").value = document.getElementById(answersid).textContent;
	} else if (document.getElementById(typeid).textContent == "free_response") {
		document.getElementById("type").value = "5";
		document.getElementById("tfttxt").value = document.getElementById(tftid).textContent;
	} else {
		document.getElementById("type").value = "1";
	}
}

function changeQuestion() {
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
		document.getElementById(typeid).value = "informational_text";
	}*/
}

function createQuestion() {
	name = document.question.name.value;
	html = '<div id="' + name + '" class="row">';
	html += '<h3 id="' + name + 'name">' + name + '</h3>';
	if (document.getElementById("type").value == '2') {
		html += '<p>Question type: <div id="' + name + 'type">slider</div></p>';
            	html += '<p>Question text: <div id="' + name + 'text">' + document.question.text.value + '</div></p>';
		html += '<p>Slider range: <div id="' + name + 'range">' + document.question.valnum.value + '</div>;';
		html += 'default: <div id="' + name + 'default">' + document.question.defnum.value + '</div></p>';
	} else if (document.getElementById("type").value == '3') {
		html += '<p>Question type: <div id="' + name + 'type">radio_button</div></p>';
            	html += '<p>Question text: <div id="' + name + 'text">' + document.question.text.value + '</div></p>';
	 	html += '<p>Answers:';
		html += '<div id="' + name + 'answers">';
		html += document.getElementById('anstxt').value + '</div></p>';
	} else if (document.getElementById("type").value == '4') {
		html += '<p>Question type: <div id="' + name + 'type">checkbox</div></p>';
            	html += '<p>Question text: <div id="' + name + 'text">' + document.question.text.value + '</div></p>';
		html += '<p>Answers:';
		html += '<div id="' + name + 'answers">';
		html += document.question.anstxt.value + '</div></p>'
	} else if (document.getElementById("type").value == '5') {
		html += '<p>Question type: <div id="' + name + 'type">free_response</div></p>';
            	html += '<p>Question text: <div id="' + name + 'text">' + document.question.text.value + '</div></p>';
		html += '<p>Text Field Type: <div id="' + name + 'tft">' + document.question.tfttxt.value + '</div></p>';
	} else {
		html += '<p>Question type: <div id="' + name + 'type">informational_text</div></p>';
            	html += '<p>Question text: <div id="' + name + 'text">' + document.question.text.value + '</div></p>';
	}
	html += '<p><button class="btn btn-primary" data-toggle="modal" data-target="#myModal" onclick="setModal(\'' + name + '\')">Edit</button>' 
	html += '<button class="btn btn-primary" onclick="deleteQuestion(\'' + name + '\')">Delete</button>'
	addHTML(html);
}

function deleteQuestion(x) {
	old = document.getElementById(x);
	old.parentNode.removeChild(old);
}

function addHTML (html) {
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
