import sys
import os
import subprocess
import time

#Configuration Setting
SkipDict = ['OdmLib']                                               # Skip dictionary list
SkipFile =  ['BuildInfo.h','Date5.bat','logo.bmp']                  # Skip File List
OutputFileName = 'FinalReport.txt'                                  # Use to store final result
PriorityDict = ['R8RomleyPkg','IbmRomleyPkg','TigerSharkPkg']       # Setting priority:TigerSharkPkg > IbmRomleyPkg > R8RomleyPkg
SpecifyPkg = 'TigerSharkPkg'                                        # Show off any change in this dictionary
TargetPkg = 'ValiPkg'
DiffResultName = "DiffResult.txt"

# Version 1.0 Beta
#Generate DiffResult.txt file
def GenDiffFile(Filename,OldFileName,NewFileName):
    # Create Compare Result list
    # Input <OldFileName> <NewFileName>
    # Output File  - DiffResult.txt
    cmd = "diff.exe " + OldFileName + " " + NewFileName +" -r -q -N > " + DiffResultName
    os.system(cmd)

class FileData(object):
    def __init__(self, SrcName, TarName):
        self.DiffList = []
        self.ModDict  = {}
        self.AddDict  = {}
        self.RmvDict  = {}
        self.ChkDict  = {}
        self.SrcDict  = SrcName
        self.TarDict  = TarName

    def _ChkPriority(self, FilePath, Priority):
        Index = 0
        for i in range(len(Priority)):
            if FilePath.find(Priority[i]) != -1:
                Index = i
        return Index

    def _ProcComp(self, FileSource, FileUpdate,FileTarget, CompTool, num):
        # Process Compare command
        if num == 2:
            arg = "\"" + CompTool + "\" " + FileSource + " " + FileUpdate
            CmpPopen1 = subprocess.Popen(arg, shell=True)
            time.sleep(0.4)

            arg = "\"" + CompTool + "\" " + FileTarget + " " + FileUpdate
            CmpPopen1 = subprocess.Popen(arg, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            time.sleep(0.2)
            
            arg = "\"" + CompTool + "\" " + FileTarget + " " + FileSource
            CmpPopen1 = subprocess.Popen(arg, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            time.sleep(0.2)
        elif num ==3:
            arg = "\"" + CompTool + "\" " + FileSource + " " +FileUpdate + " " + FileTarget
            CmpPopen1 = subprocess.Popen(arg, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)

    def Parser(self, Filename):
        # Read Compare Result file and create process list
        # Input : File DiffResult.txt
        DiffRes = open(Filename,'r')
        while(1):
            line = DiffRes.readline()
            if len(line) == 0:
                break
            line = line.replace("/","\\")
            halftmp = line.split(" and ")
            tmp1 = halftmp[0][6:]
            tmp2 = halftmp[1][0:-8]
            self.DiffList.append(tmp1 + "|" + tmp2)
        DiffRes.close()

    def DictFilter(self, SkipDictList):
        NewList=[]
        for i in SkipDictList:
            for j in self.DiffList:
                tmp = i + '\\'
                if (j.find(tmp)) == -1:
                    NewList.append(j)
                #else:
                #    print 'del',j
            self.DiffList = NewList
            NewList = []

    def FileFilter(self, SkipFileList):
        NewList=[]
        for i in SkipFileList:
            for j in self.DiffList:
                TmpFileName=j.split('\\')[-1]
                if TmpFileName != i:
                    NewList.append(j)
                #else:
                #    print 'remove', j
            self.DiffList = NewList
            NewList = []

    def GenFileDict(self, Priority, Package):
        # Create Old and New file Dictionary
        # Generate Form: <FileName>:[<Location1>,<Location2>,....]
        # Input List: Skip File List
        # New/Old Dict : {'FileName':['FullPath0',..]}
        OldList = []
        NewList = []
        ProList = []
        for i in self.DiffList:
            TmpStr = i.split("|")
            OldList.append(TmpStr[0])
            #OldFileName = os.path.basename(TmpStr[0])
            NewList.append(TmpStr[1])
            #NewFileName = os.path.basename(TmpStr[1])
            # Get Priority Index
            FileProirity = self._ChkPriority(TmpStr[0],Priority)
            ProList.append(FileProirity)

        #File = open('4.txt','w')
        #for j in range(len(OldList)):
        #    File.write(OldList[j]+' '+NewList[j]+' '+str(ProList[j])+'\n')
        #File.close()
        
        # Process File list by Proirity
        # Rule: 
        #   Case 1: Higher Proirity folder Create File
        #       Add it to add list and skip other same file name with lower proirity
        #   Case 2: Higher Proirity folder Modified File
        #       Add it to add list and skip other same file name with lower proirity
        #   Case 3: Higher Proirity folder Remove File
        #       Add it to Remove list and process lower proirity folder
        for i in range(len(Priority),-1,-1):
            for j in range(len(OldList)):
                if ProList[j] != i:
                    continue
                NewFileName = os.path.basename(NewList[j])
                if self.ModDict.has_key(NewFileName) or self.AddDict.has_key(NewFileName) or self.ChkDict.has_key(NewFileName):
                    continue
                if os.path.exists(NewList[j]):
                    if os.path.exists(OldList[j]):
                        self.ModDict[NewFileName] = OldList[j]+'|'+NewList[j]
                    else:
                        self.AddDict[NewFileName] = NewList[j]
                else:
                    if self.RmvDict.has_key(NewFileName):
                        self.ChkDict[NewFileName] = OldList[j]
                    else:
                        self.RmvDict[NewFileName] = OldList[j]
        File = open('MoreInfo.txt','w')
        for i in self.ModDict:
            File.write(self.ModDict[i]+'\n')
        File.write('Add List \n')
        for i in self.AddDict:
            File.write(self.AddDict[i]+'\n')
        File.write('Remove List \n')
        for i in self.RmvDict:
            File.write(self.RmvDict[i]+'\n')
        File.write('Check List \n')
        for i in self.ChkDict:
            File.write(self.ChkDict[i]+'\n')
        File.close()
   

    def GenReport(self,FileName, SpPkg, TgPkg, TgPath):
        # if any change filename exist targetpath
        # it should be check if need update
        File = open(FileName,'w')
        File.write('==== Modify List ====\n')
        for SearchFile in self.ModDict:
            # Process Special Pkg 
            if SearchFile.find(SpPkg) != -1:
                NewSearchFile = SearchFile.replace(SpPkg,TgPkg)
                arg = "dir /S /B " + TgPath + "\\" + TgPkg + "\\" + NewSearchFile
            else:
                arg = "dir /S /B " + TgPath + "\\" + TgPkg + "\\" + SearchFile
            SearchPopen = subprocess.Popen(arg, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            while(True):
                result = SearchPopen.stdout.readline()
                if result == '':
                    break
                else:
                    File.write(result.replace('\n','').replace('\r','')+" "+self.ModDict[SearchFile].split("|")[1]+"\n")

        File.write('==== Add List ====\n')
        for SearchFile in self.AddDict:
            # Process Special Pkg 
            if SearchFile.find(SpPkg) != -1:
                NewSearchFile = SearchFile.replace(SpPkg,TgPkg)
                arg = "dir /S /B " + TgPath + "\\" + TgPkg + "\\" + NewSearchFile
            else:
                arg = "dir /S /B " + TgPath + "\\" + TgPkg + "\\" + SearchFile
            SearchPopen = subprocess.Popen(arg, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            while(True):
                result = SearchPopen.stdout.readline()
                if result == '':
                    break
                else:
                    File.write(result.replace('\n',''))
            if self.AddDict[SearchFile].find(SpPkg+'\\') != -1:
                File.write(SearchFile.replace(SpPkg,TgPkg)+'\n')

        File.write('==== Check List ====\n')
        File.write('= It was removed in '+SpPkg+', you need to chekc if you need remove it too. =\n')
        for SearchFile in self.RmvDict:
            # Process Special Pkg 
            if SearchFile.find(SpPkg) != -1:
                NewSearchFile = SearchFile.replace(SpPkg,TgPkg)
                arg = "dir /S /B " + TgPath + "\\" + TgPkg + "\\" + NewSearchFile
            else:
                arg = "dir /S /B " + TgPath + "\\" + TgPkg + "\\" + SearchFile
            SearchPopen = subprocess.Popen(arg, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            while(True):
                result = SearchPopen.stdout.readline()
                if result == '':
                    break
                else:
                    File.write(result.replace('\n',''))

        for SearchFile in self.ChkDict:
            # Process Special Pkg 
            if SearchFile.find(SpPkg) != -1:
                NewSearchFile = SearchFile.replace(SpPkg,TgPkg)
                arg = "dir /S /B " + TgPath + "\\" + TgPkg + "\\" + NewSearchFile
            else:
                arg = "dir /S /B " + TgPath + "\\" + TgPkg + "\\" + SearchFile
            SearchPopen = subprocess.Popen(arg, shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            while(True):
                result = SearchPopen.stdout.readline()
                if result == '':
                    break
                else:
                    File.write(result.replace('\n',''))

        File.close()

    def Dbg_Dmp_DiffList(self, FileName):
        File = open(FileName,'w')
        for i in self.DiffList:
            File.write(i+'\n')
        File.close()

def Main(OldFileName, NewFileName, TargetName):
    print 'Generate update file list...',
    GenDiffFile(DiffResultName,OldFileName, NewFileName)
    print 'DiffResult.txt\n Done!!'

    #Creat Object    
    Diff = FileData(OldFileName,NewFileName)

    Diff.Parser(DiffResultName)
    # Input Skip Dictionary
    Diff.DictFilter(SkipDict)
    # Input Skip File List
    Diff.FileFilter(SkipFile)
    
    # Start Generate Update List and other Information
    Diff.GenFileDict(PriorityDict,SpecifyPkg)

    ## Input report file name and process special package
    Diff.GenReport(OutputFileName, SpecifyPkg, TargetPkg, TargetName)
   
if __name__ == '__main__':

    #Check Parameter
    if len(sys.argv) != 4:
        print "Parameter Error!!"
        print "Usage: Update.py [Old Reference Source Code Path] [New Reference Source Code Path] [Project Pkg Path]"
        print "Example: Update.py z:\\TKE_23A z:\\TKE_23B z:\\Vali_23A"
        sys.exit(0)

    #Check File Exist
    FileNotExistFlag = 0
    for i in range(1,4):
        if(not os.path.exists(sys.argv[i])):
           print sys.argv[i],'is not exist'
           FileNotExistFlag = 1
    if FileNotExistFlag == 1:
        sys.exit(0)

    #Start 
    r = Main(sys.argv[1],sys.argv[2],sys.argv[3])
    sys.exit(r)
