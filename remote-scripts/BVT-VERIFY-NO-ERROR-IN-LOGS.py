#!/usr/bin/python

from azuremodules import *


import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('-wl', '--whitelist', help='specify the xml file which contains the ignorable errors')

args = parser.parse_args()
white_list_xml = args.whitelist

def RunTest():
    UpdateState("TestRunning")
    RunLog.info("Checking for ERROR messages in waagent.log...")
    errors = Run("grep -i error /var/log/waagent.log")
    if (not errors) :
        RunLog.info('There is no errors in the logs waagent.log')
        ResultLog.info('PASS')
        UpdateState("TestCompleted")
    else :
        if white_list_xml and os.path.isfile(white_list_xml):
            try:
                import xml.etree.cElementTree as ET
            except ImportError:
                import xml.etree.ElementTree as ET

            white_list_file = ET.parse(white_list_xml)
            xml_root = white_list_file.getroot()
            RunLog.info('Checking ignorable walalog ERROR messages...')
            for node in xml_root:
                if (errors and node.tag == "errors"):
                    for keywords in node:
                        if(errors):
                            errors = RemoveIgnorableMessages(''.join(errors), keywords.text)
        if (errors):
            RunLog.info('ERROR are  present in wala log.')
            RunLog.info('Errors: ' + ''.join(errors))
            ResultLog.error('FAIL')
        else:
            ResultLog.info('PASS')
        UpdateState("TestCompleted")
		
def RemoveIgnorableMessages(messages, keywords):
    matchstring = re.findall(keywords,messages,re.M)
    matchcount = 0
    index = 0
    if(matchstring):			
        for msg in matchstring:
            RunLog.info('Ignorable ERROR message:\n' + msg)
            matchcount +=1
            
        while matchcount > 0:
            matchcount -=1
            str = re.split(matchstring[index],messages)
            index+=1
            messages=str[1]
   
        valid_list = []
        for substr in str:
            if re.search('error', substr, re.IGNORECASE):
                valid_list.append(substr)
            else:
                continue
        if len(valid_list) > 0:
            return valid_list
        else:
            return None             
    else:
        return messages

RunTest()
