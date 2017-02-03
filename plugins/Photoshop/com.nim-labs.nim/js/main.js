
// fileName is a String (with the .jsx extension included)
function loadJSX(fileName) {
	var csInterface = new CSInterface(),
		extensionRoot = csInterface.getSystemPath(SystemPath.EXTENSION) + "/jsx/";
	csInterface.evalScript('$.evalFile("' + extensionRoot + fileName + '")');
}

document.getElementById('nim_open').onclick = function() {
	loadJSX('nim_open.jsx');
};

document.getElementById('nim_saveAs').onclick = function() {
	loadJSX('nim_saveAs.jsx');
};

document.getElementById('nim_versionUp').onclick = function() {
	loadJSX('nim_versionUp.jsx');
};

document.getElementById('nim_publish').onclick = function() {
	loadJSX('nim_publish.jsx');
};

document.getElementById('nim_changeUser').onclick = function() {
	loadJSX('nim_changeUser.jsx');
};
