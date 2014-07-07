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
}
