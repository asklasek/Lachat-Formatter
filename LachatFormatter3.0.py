# Converts CSV file from Prep Data into a usable file for Lachat

# Output text file's format:
# Sample Number,Sample Name,Cup Number,Replicates,MDF,Sample Weight,Weight Units,Requested Autodilution check box <y/n>,Requested Autodilution Factor

import time
import sys

def main():
    fileName=input("Enter the workgroup number: ") # User inputs the workgroup number to be formatted.
    fileNameIn, fileNameOut=formatName(fileName)   # Create infile and outfile names
    wgNum=fileNameIn[0:8]                          # Workgroup number.
    try: # Open files for reading and writing, respectively.
        inFile=open(fileNameIn, 'r')
        outFile=open(fileNameOut, 'w')
    except IOError: # Ensure user's file is in the folder.
        print(fileNameIn + ' was not a valid file in the folder.')
        time.sleep(5)
        sys.exit(1)
    runList=createList(inFile, wgNum) # Create the sorted list of samples.
    writeRun(outFile, runList)        # Write the samples to the formatted file.
    inFile.close()                    # Close the files
    outFile.close()
    time.sleep(3)

# writeRun() takes a list and writes it to an outFile.
def writeRun(outFile, runList):
    for item in runList:  # Write the list of samples to the outfile.
        outFile.write(item+'\n')
    print('File created successfully.')

# createList() creates a list of the L-numbers from the input file, sorts the list, then adds any duplicates or spikes.
# The list of the formatted workgroup is returned.
def createList(inFile, wgNum): 
    numList=[]    # List of numbers to be sorted.
    sampleList=[] # Sorted L-numbers with spikes and duplicates.
    file=inFile.readlines()
    for item in file:
        if item[0]=='L' and item[1]!='C':              # Ensure that LCS/LCSD are not appended to the list.
            num=int(item[1:8])+(float(item[9:11])/100) # Convert the L number into a decimal for sorting.
            numList.append(num)
    numList.sort()        # Put the L numbers in numerical order.
    for item in numList:  # Revert numbers back to L-numbers and append to list.
        strNum=str(item).split('.')
        if len(strNum[1])==1:  # Add the zero back to mulitples of ten since the float division does not keep trailing zeros.
            LNum='L'+strNum[0]+'-'+strNum[1]+'0 '+wgNum
        else:
            LNum='L'+strNum[0]+'-'+strNum[1]+' '+wgNum
        sampleList.append(LNum)
        for item in file: # Add any Duplicates or Spikes to the list after the parent sample.
            if item[4:24]==LNum or item[3:23]==LNum:
                sampleList.append(item.rstrip('\n'))
    runList, bracket=addQC(wgNum) # List of formatted/sorted workgroup to be returned, bracketing information
    sampNum=len(runList) # Initialize sample number, cup number, and number of injections.
    if bracket==1:
        cupNum=sampNum-1
    else:
        cupNum=sampNum+6
    injections=sampNum-2
    for item in sampleList: # Format samples for the Omnion import csv format.
        sampNum+=1          # increase sample number, cup number, and injection for each sample.
        strSN=str(sampNum)  
        cupNum+=1
        strCN=str(cupNum)
        injections+=1
        if injections>10: # Insert a CCV/CCB bracketing pair every 10 injections.
            injections=1  # Reset injections to 1
            if bracket==1:
                runList.append(strSN+',CCV,2,1,,,,n,')
                sampNum+=1
                strSN=str(sampNum)
                runList.append(strSN+',CCB,1,1,,,,n,')
                sampNum+=1
                strSN=str(sampNum)
            else:
                runList.append(strSN+',CCV,9,1,,,,n,')
                sampNum+=1
                strSN=str(sampNum)
                runList.append(strSN+',CCB,8,1,,,,n,')
                sampNum+=1
                strSN=str(sampNum)
        line=strSN+','+item+','+strCN+',1,,,,n,' # Line format for Omnion csv format.
        runList.append(line)
    sampNum+=1  # Add a closing bracket of CCV/CCB
    strSN=str(sampNum)
    if bracket==1:
        runList.append(strSN+',CCV,2,1,,,,n,')
        sampNum+=1
        strSN=str(sampNum)
        runList.append(strSN+',CCB,1,1,,,,n,')
    else:
        runList.append(strSN+',CCV,9,1,,,,n,')
        sampNum+=1
        strSN=str(sampNum)
        runList.append(strSN+',CCB,8,1,,,,n,')
    return runList # Return the completed run information.

# addQC will take the workgroup number and the test name as input from the user to create the run list
# with the begining Quality Control injections for the workgroup. The run list is returned and bracket type are returned.
# bracket=1 signifies cup numbers 2 and 1 for CCV/CCB. bracket=2 signifies cup numbers 9 and 8 for CCV/CCB.
def addQC(wgNum):
    runList=[]
    test=input('Enter the test name: ') # User enters the test to be analyzed.
    if test.lower()=='hard' or test.lower()=='hardness':            # HARDNESS
        runList.append('1,INSTBLK '+wgNum+',90,1,,,,n,')
        runList.append('2,ICV '+wgNum+',2,1,,,,n,')
        runList.append('3,BLANK '+wgNum+',1,1,,,,n,')
        runList.append('4,LCS '+wgNum+',3,1,,,,n,')
        runList.append('5,LCSD '+wgNum+',4,1,,,,n,')
        if rlvCheck()==True:
            runList.append('6,RL 30 '+wgNum+',30,1,,,,n,')
        bracket=1
    elif test.lower()=='alk' or test.lower()=='alkbio':             # ALKBIO
        runList.append('1,INSTBLK '+wgNum+',90,1,,,,n,')
        runList.append('2,ICV '+wgNum+',2,1,,,,n,')
        runList.append('3,BLANK '+wgNum+',1,1,,,,n,')
        runList.append('4,LCS '+wgNum+',3,1,,,,n,')
        runList.append('5,LCSD '+wgNum+',4,1,,,,n,')
        runList.append('6,ALT 50 '+wgNum+',5,1,,,,n,')
        if rlvCheck()==True:
            runList.append('7,RL 20 '+wgNum+',30,1,,,,n,')
        bracket=1
    elif test.lower()=='pt' or test.lower()=='tp':                  # PT
        runList.append('1,INSTBLK '+wgNum+',1,1,,,,n,')
        runList.append('2,ICV '+wgNum+',9,1,,,,n,')
        runList.append('3,BLANK '+wgNum+',8,1,,,,n,')
        runList.append('4,LCS '+wgNum+',10,1,,,,n,')
        runList.append('5,LCSD '+wgNum+',11,1,,,,n,')
        runList.append('6,ALT 4.0 '+wgNum+',12,1,,,,n,')
        bracket=2
    elif test.lower()=='nh3' or test.lower()=='ammonia':            # NH3
        runList.append('1,INSTBLK '+wgNum+',90,1,,,,n,')
        runList.append('2,ICV 10.0'+wgNum+',2,1,,,,n,')
        runList.append('3,BLANK '+wgNum+',1,1,,,,n,')
        runList.append('4,LCS '+wgNum+',3,1,,,,n,')
        runList.append('5,LCSD '+wgNum+',4,1,,,,n,')
        runList.append('6,ALT 5.0 '+wgNum+',5,1,,,,n,')
        bracket=1
    elif test.lower()=='tkn' or test.lower()=='total nitrogen':     # TKN
        runList.append('1,INSTBLK '+wgNum+',90,1,,,,n,')
        runList.append('2,ICV '+wgNum+',2,1,,,,n,')
        runList.append('3,BLANK '+wgNum+',1,1,,,,n,')
        runList.append('4,LCS '+wgNum+',3,1,,,,n,')
        runList.append('5,LCSD '+wgNum+',4,1,,,,n,')
        runList.append('6,ALT 5.0 '+wgNum+',5,1,,,,n,')
        bracket=1
    elif test.lower()=='pht' or test.lower()=='phenol':              # PHT
        runList.append('1,INSTBLK '+wgNum+',90,1,,,,n,')
        runList.append('2,ICV '+wgNum+',2,1,,,,n,')
        runList.append('3,BLANK '+wgNum+',1,1,,,,n,')
        runList.append('4,LCS '+wgNum+',3,1,,,,n,')
        runList.append('5,LCSD '+wgNum+',4,1,,,,n,')
        bracket=1
    elif test.lower()=='cn' or test.lower()=='cyanide':              # CN
        runList.append('1,INSTBLK '+wgNum+',1,1,,,,n,')
        runList.append('2,ICV '+wgNum+',9,1,,,,n,')
        runList.append('3,BLANK '+wgNum+',8,1,,,,n,')
        runList.append('4,LCS '+wgNum+',10,1,,,,n,')
        runList.append('5,LCSD '+wgNum+',11,1,,,,n,')
        runList.append('6,ALT 0.050 '+wgNum+',12,1,,,,n,')
        runList.append('7,ALT 0.200 '+wgNum+',13,1,,,,n,')
        if rlvCheck()==True:
            runList.append('8,RL 0.005 '+wgNum+',14,1,,,,n,')
        bracket=2
    else: # The program is exited if an invalid test is entered.
        print('That is not a valid test. Goodbye!')
        time.sleep(3)
        sys.exit(1)
    return runList, bracket

def rlvCheck():
    rlv=input('Is there an RLV to be analyzed (Y/N): ')
    if rlv.lower()=='y' or rlv.lower()=='yes':
        return True
    return False
    
# formatName() takes the user input and formats it to the name of the .csv file created from Prep Data
# and creates a name for the file made by the program.
def formatName(fileName):
    name=''
    for char in fileName:
        if char.isdigit()==True:  # Only takes the digits that the user entered.
            name+=char
    nameIn='WG'+name+'.csv'   # Input file's name
    nameOut='WG'+name+'.txt'  # Output file's name
    return nameIn, nameOut
    
main()
