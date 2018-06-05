#include "PPro_API_Constants.jsx"

$._nim_PPP_={
	
	projectOpen : function(projToOpen) {
		if (projToOpen) {
			app.openDocument(	projToOpen,
								1,					// suppress 'Convert Project' dialogs
								1,					// suppress 'Locate Files' dialogs
								1);					// suppress warning dialogs
		}	
		else {
			alert("Project Not Found");
		}
	},

	projectSaveAs : function(projToSave) {
		if (projToSave) {
			app.project.saveAs(	projToSave );
		}	
		else {
			alert("Project Not Found");
		}
	},

};
