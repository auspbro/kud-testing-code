import win32com.client 
strComputer = "." 
objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator") 
objSWbemServices = objWMIService.ConnectServer(strComputer,"root\cimv2") 
colItems = objSWbemServices.ExecQuery("Select * from Win32_SoundDevice") 
for objItem in colItems: 
    print "Availability: ", objItem.Availability 
    print "Caption: ", objItem.Caption 
    print "Config Manager Error Code: ", objItem.ConfigManagerErrorCode 
    print "Config Manager User Config: ", objItem.ConfigManagerUserConfig 
    print "Creation Class Name: ", objItem.CreationClassName 
    print "Description: ", objItem.Description 
    print "Device ID: ", objItem.DeviceID 
    print "DMA Buffer Size: ", objItem.DMABufferSize 
    print "Error Cleared: ", objItem.ErrorCleared 
    print "Error Description: ", objItem.ErrorDescription 
    print "Install Date: ", objItem.InstallDate 
    print "Last Error Code: ", objItem.LastErrorCode 
    print "Manufacturer: ", objItem.Manufacturer 
    print "MPU401 Address: ", objItem.MPU401Address 
    print "Name: ", objItem.Name 
    print "PNP Device ID: ", objItem.PNPDeviceID 
    z = objItem.PowerManagementCapabilities 
    if z is None: 
        a = 1 
    else: 
        for x in z: 
            print "Power Management Capabilities: ", x 
    print "Product Name: ", objItem.ProductName 
    print "Status: ", objItem.Status 
    print "Status Info: ", objItem.StatusInfo 
    print "System Creation Class Name: ", objItem.SystemCreationClassName 
    print "System Name: ", objItem.SystemName 