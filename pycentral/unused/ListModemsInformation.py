import win32com.client 
strComputer = "." 
objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator") 
objSWbemServices = objWMIService.ConnectServer(strComputer,"root\cimv2") 
colItems = objSWbemServices.ExecQuery("Select * from Win32_POTSModem") 
for objItem in colItems: 
    print "Answer Mode: ", objItem.AnswerMode 
    print "Attached To: ", objItem.AttachedTo 
    print "Availability: ", objItem.Availability 
    print "Blind Off: ", objItem.BlindOff 
    print "Blind On: ", objItem.BlindOn 
    print "Caption: ", objItem.Caption 
    print "Compatibility Flags: ", objItem.CompatibilityFlags 
    print "Compression Info: ", objItem.CompressionInfo 
    print "Compression Off: ", objItem.CompressionOff 
    print "Compression On: ", objItem.CompressionOn 
    print "Config Manager Error Code: ", objItem.ConfigManagerErrorCode 
    print "Config Manager User Config: ", objItem.ConfigManagerUserConfig 
    print "Configuration Dialog: ", objItem.ConfigurationDialog 
    z = objItem.CountriesSupported 
    if z is None: 
        a = 1 
    else: 
        for x in z: 
            print "Countries Supported: ", x 
    print "Country Selected: ", objItem.CountrySelected 
    print "Creation Class Name: ", objItem.CreationClassName 
    z = objItem.CurrentPasswords 
    if z is None: 
        a = 1 
    else: 
        for x in z: 
            print "Current Passwords: ", x 
    z = objItem.DCB 
    if z is None: 
        a = 1 
    else: 
        for x in z: 
            print "DCB: ", x 
    z = objItem.Default 
    if z is None: 
        a = 1 
    else: 
        for x in z: 
            print "Default: ", x 
    print "Description: ", objItem.Description 
    print "Device ID: ", objItem.DeviceID 
    print "Device Loader: ", objItem.DeviceLoader 
    print "Device Type: ", objItem.DeviceType 
    print "Dial Type: ", objItem.DialType 
    print "Driver Date: ", objItem.DriverDate 
    print "Error Cleared: ", objItem.ErrorCleared 
    print "Error Control Forced: ", objItem.ErrorControlForced 
    print "Error Control Info: ", objItem.ErrorControlInfo 
    print "Error Control Off: ", objItem.ErrorControlOff 
    print "Error Control On: ", objItem.ErrorControlOn 
    print "Error Description: ", objItem.ErrorDescription 
    print "Flow Control Hard: ", objItem.FlowControlHard 
    print "Flow Control Off: ", objItem.FlowControlOff 
    print "Flow Control Soft: ", objItem.FlowControlSoft 
    print "Inactivity Scale: ", objItem.InactivityScale 
    print "Inactivity Timeout: ", objItem.InactivityTimeout 
    print "Index: ", objItem.Index 
    print "Install Date: ", objItem.InstallDate 
    print "Last Error Code: ", objItem.LastErrorCode 
    print "Max Baud Rate To Phone: ", objItem.MaxBaudRateToPhone 
    print "Max Baud Rate To Serial Port: ", objItem.MaxBaudRateToSerialPort 
    print "Max Number Of Passwords: ", objItem.MaxNumberOfPasswords 
    print "Model: ", objItem.Model 
    print "Modem Inf Path: ", objItem.ModemInfPath 
    print "Modem Inf Section: ", objItem.ModemInfSection 
    print "Modulation Bell: ", objItem.ModulationBell 
    print "Modulation CCITT: ", objItem.ModulationCCITT 
    print "Modulation Scheme: ", objItem.ModulationScheme 
    print "Name: ", objItem.Name 
    print "PNP Device ID: ", objItem.PNPDeviceID 
    print "Port SubClass: ", objItem.PortSubClass 
    z = objItem.PowerManagementCapabilities 
    if z is None: 
        a = 1 
    else: 
        for x in z: 
            print "Power Management Capabilities: ", x 
    print "Power Management Supported: ", objItem.PowerManagementSupported 
    print "Prefix: ", objItem.Prefix 
    z = objItem.Properties 
    if z is None: 
        a = 1 
    else: 
        for x in z: 
            print "Properties: ", x 
    print "Provider Name: ", objItem.ProviderName 
    print "Pulse: ", objItem.Pulse 
    print "Reset: ", objItem.Reset 
    print "Responses KeyName: ", objItem.ResponsesKeyName 
    print "Rings Before Answer: ", objItem.RingsBeforeAnswer 
    print "Speaker Mode Dial: ", objItem.SpeakerModeDial 
    print "Speaker Mode Off: ", objItem.SpeakerModeOff 
    print "Speaker Mode On: ", objItem.SpeakerModeOn 
    print "Speaker ModeSetup: ", objItem.SpeakerModeSetup 
    print "Speaker Volume High: ", objItem.SpeakerVolumeHigh 
    print "Speaker Volume Info: ", objItem.SpeakerVolumeInfo 
    print "Speaker Volume Low: ", objItem.SpeakerVolumeLow 
    print "Speaker Volume Med: ", objItem.SpeakerVolumeMed 
    print "Status: ", objItem.Status 
    print "Status Info: ", objItem.StatusInfo 
    print "String Format: ", objItem.StringFormat 
    print "Supports Callback: ", objItem.SupportsCallback 
    print "Supports Synchronous Connect: ", objItem.SupportsSynchronousConnect 
    print "System Creation Class Name: ", objItem.SystemCreationClassName 
    print "System Name: ", objItem.SystemName 
    print "Terminator: ", objItem.Terminator 
    print "Time Of Last Reset: ", objItem.TimeOfLastReset 
    print "Tone: ", objItem.Tone 
    print "Voice Switch Feature: ", objItem.VoiceSwitchFeature 