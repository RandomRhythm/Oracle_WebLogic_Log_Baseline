import os
import re

dictDateFirstSeen = dict()
dictCount = dict()
strInputFolderPath = "D:\\Processing\\logs\\"
strOutputFile = "D:\\Processed\\baseline.txt"

def GetData(contents, endOfStringChar, matchString):
    matchStringLen = len(contents)
    x = contents.find(matchString)
    if x > -1:
        y = contents.find(endOfStringChar,x)
        if y > 0:
            return contents[x+ len(matchString):y]
        else:
            return contents[x:]


def processOracleLogs(strInputFile):
  f1 = open(strInputFile, 'r', encoding="cp1252") #cp-1252 utf-8
  for line in f1:
    replaceDate = "####<"

    if "<Starting session...>" in line:
        with open(strOutputFile + ".session", 'a+', encoding="utf-8") as f4:
            f4.write(line )
    strNear = GetData(line, "....}", "[Near : {...")
    if strNear != None:
        with open(strOutputFile + ".near", 'a+', encoding="utf-8") as f3:
            f3.write(strNear +"\n")
    strDateTime = GetData(line, ">", replaceDate)
    if strDateTime == None:
        strDateTime = GetData(line, ">", "<")
        replaceDate = "<"
    if strDateTime is None:
        linedata = line
        strDateTime = ""
    else:
        linedata = line.replace(replaceDate + strDateTime + "> ", "")
    p = re.compile('[\da-z]+\.burpcollaborator.net')#Web application testing
    sResult = re.findall('[\\da-z]+\\.burpcollaborator\\.net',linedata)
    if len(sResult) > 0:
        print(sResult)
    p = re.compile('(reached|Retired) \\d+(,|)\\d* (times for the last |records in )\\d+(,|)\\d* ')#count and seconds
    linedata = p.sub('<Count_Seconds_Replaced>', linedata)

    p = re.compile('<Self-tuning thread pool contains \\d+ running threads, \\d+ idle threads, and \\d+ standby threads>')#threads
    linedata = p.sub('<Self-tuning thread pool contains # running threads, # idle threads, and # standby threads>', linedata)

    p = re.compile('<\\d+% of the total memory in the server is free')#threads
    linedata = p.sub('<#% of the total memory in the server is free', linedata)
    
    p = re.compile('<[\\dabcdef-]*>')#int and guid replacement
    linedata = p.sub('<Baseline_GUID_INT_Replaced>', linedata)
    p = re.compile('((25[0-5]|(2[0-4]|1[0-9]|[1-9]|)[0-9])(\\.(?!$)|:\\d{1,3},\\d{1,3})){4}') #replace ipv4:port,int
    linedata = p.sub('<Baseline_ipv4:port,int_Replaced>', linedata)
    p = re.compile('ExecuteThread: \'\d{1,2}\'')#int replacement: ExecuteThread: '10'
    linedata = p.sub('ExecuteThread: \'#\'', linedata)
    p = re.compile('<java.lang.ProcessImpl@[\\dabcdef]{8}>')#hex replacement: <java.lang.ProcessImpl@49751b10>
    linedata = p.sub('<java.lang.ProcessImpl@hex_replaced>', linedata)
    if linedata not in dictDateFirstSeen:
      dictDateFirstSeen[linedata] = strDateTime
    if linedata not in dictCount:
      dictCount[linedata] = 1
    else:
      dictCount[linedata] += 1
      
      
#enum log files
for file in os.listdir(strInputFolderPath):
  inputpath = os.path.join(strInputFolderPath, file)
  if os.path.isfile(inputpath):
      processOracleLogs(inputpath)

with open(strOutputFile, 'a+', encoding="utf-8") as f2:
    for logEvent in dictDateFirstSeen: #output consolidated log events
      #print(logEvent)
      f2.write('"' + dictDateFirstSeen[logEvent] +'","' + str(dictCount[logEvent]) +'","' + logEvent.replace("\n","") + '"' + "\n")
print("done")
