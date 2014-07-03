function setType() {
	if (document.getElementById("type") == "1") {
		docuement.getElementById("values").display.style="none";
		document.getElementById("default").display.style="none";
		document.getElementById("answers").display.style="none";
	} else if (document.getElementById("type") == "2" {
		docuement.getElementById("values").display.style="inline";
		document.getElementById("default").display.style="inline";
		document.getElementById("answers").display.style="none";
	} else {
		docuement.getElementById("values").display.style="none";
		document.getElementById("default").display.style="none";
		document.getElementById("answers").display.style="inline";
	}
}
