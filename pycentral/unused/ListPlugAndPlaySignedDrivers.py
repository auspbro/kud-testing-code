import win32com.client 
strComputer = "." 
objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator") 
objSWbemServices = objWMIService.ConnectServer(strComputer,"root\cimv2") 
colItems = objSWbemServices.ExecQuery("Select * from Win32_PnPSignedDriver") 
for objItem in colItems: 
    print "Caption: ", objItem.Caption 
    print "Class Guid: ", objItem.ClassGuid 
    print "Compat ID: ", objItem.CompatID 
    print "Creation Class Name: ", objItem.CreationClassName 
    print "Description: ", objItem.Description 
    print "Device Class: ", objItem.DeviceClass 
    print "Device ID: ", objItem.DeviceID 
    print "Device Name: ", objItem.DeviceName 
    print "Dev Loader: ", objItem.DevLoader 
    print "Driver Date: ", objItem.DriverDate 
    print "Driver Name: ", objItem.DriverName 
    print "Driver Provider Name: ", objItem.DriverProviderName 
    print "Driver Version: ", objItem.DriverVersion 
    print "Friendly Name: ", objItem.FriendlyName 
    print "HardWare ID: ", objItem.HardWareID 
    print "Inf Name: ", objItem.InfName 
    print "Install Date: ", objItem.InstallDate 
    print "Is Signed: ", objItem.IsSigned 
    print "Location: ", objItem.Location 
    print "Manufacturer: ", objItem.Manufacturer 
    print "Name: ", objItem.Name 
    print "PDO: ", objItem.PDO 
    print "Signer: ", objItem.Signer 
    print "Started: ", objItem.Started 
    print "Start Mode: ", objItem.StartMode 
    print "Status: ", objItem.Status 
    print "System Creation Class Name: ", objItem.SystemCreationClassName 
    print "System Name: ", objItem.SystemName 