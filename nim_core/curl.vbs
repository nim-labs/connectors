' CURL implementation for Windows
' From: https://forums.adobe.com/message/5680364#5680364

set namedArgs = WScript.Arguments.Named
set objFSO = CreateObject("Scripting.FileSystemObject")

sMethod = namedArgs.Item("Method")
sUrl = namedArgs.Item("URL")
sRequest = namedArgs.Item("Query")
tempFilePath = namedArgs.Item("TempFilePath")
username = namedArgs.Item("Username")
apiKey = namedArgs.Item("ApiKey")

' scriptPath = WScript.ScriptFullName
' set objFSO = CreateObject("Scripting.FileSystemObject")
' set objFile = objFSO.GetFile(scriptPath)
' scriptFolder = objFSO.GetParentFolderName(objFile)

HTTPPost sMethod, sUrl, sRequest, tempFilePath, username, apiKey

Function HTTPPost(sMethod, sUrl, sRequest, tempFilePath, username, apiKey)

    set oHTTP = CreateObject("MSXML2.ServerXMLHTTP.6.0")

    oHTTP.SetOption 2, oHTTP.GetOption(2) - SXH_SERVER_CERT_IGNORE_UNKNOWN_CA

    If sMethod = "POST" Then
        oHTTP.open "POST", sUrl,false
    ElseIf sMethod = "GET" Then
        oHTTP.open "GET", sUrl & "?" & sRequest,false
    End If

    oHTTP.setRequestHeader "Content-Type", "text/plain"
    oHTTP.setRequestHeader "Content-Length", Len(sRequest)

    If VarType(username) = 8 Then
        oHTTP.setRequestHeader "X-NIM-API-USER", username
    End If

    If VarType(apiKey) = 8 Then
        oHTTP.setRequestHeader "X-NIM-API-KEY", apiKey
    End If

    If sMethod = "POST" Then
        oHTTP.send sRequest
    ElseIf sMethod = "GET" Then
        oHTTP.send
    End If

    HTTPPost = oHTTP.responseText

    outputFile = tempFilePath
    set objFileOut = objFSO.CreateTextFile(outputFile,True)
    objFileOut.Write HTTPPost
    objFileOut.Close

    WScript.Echo HTTPPost

End Function