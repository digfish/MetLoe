# -*- coding: utf-8 -*-
from bcbio import isatab
import urllib, urllib2
import json
import traceback
import re
import datetime
import zipfile
import os.path
import os
import glob
import subprocess
import sys
import shutil
import hashlib
import timeit
from ftplib import FTP
#from SPARQLWrapper import SPARQLWrapper, JSON
from os.path import join
import random
from json2html import *
 
global verbose
verbose = True
global pathMTBLS
pathMTBLS = 'OUTPUT/_dataMTBLS/'
global pathISAPARSER
pathISAPARSER = 'OUTPUT/_isatabPARSER/'
global pathppISAPARSER
pathppISAPARSER = 'OUTPUT/_ppisatabPARSER/'
global pathppISAPARSERsummary
pathppISAPARSERsummary = 'OUTPUT/_ppisatabPARSER/aSummary/'

##BEGIN: METHODS TO OBTAIN MTBLS METADATA, CLEAN PATHS, MOVE FILE, ...
def extract_MTBLSentry_from_EBI(study_id):
#Get and check the URL provide and download the DATA    
    try:
        url = urllib.URLopener()        
    except urllib.URLError as e:
        print 'URLError = ' + str(e.reason)
    except urllib.IOError as e:
        print 'URLError = ' + str(e.reason)

    try:
        url.retrieve('http://www.ebi.ac.uk/metabolights/'+ study_id + '/files/metadata', study_id+'.zip')   
        url.cleanup()
    except :
        pass
    
def unzip_file(namefile):
#Unzip file *.zip in the current path
    for nameF in namefile.split():
        #print "Extracting: " + nameF
        try:
            zfile = zipfile.ZipFile(nameF)
            zfile.extractall('OUTPUT/'+os.path.splitext(nameF)[0])
        except :
            pass

def erase_specificFormatFiles(path, extension):
    for fp in glob.glob('*' + extension):
        os.remove(fp)
    
    
def erase_file(namefile):
#Remove files *.zip in the current path
    for nameF in namefile.split():
        os.remove(namefile)
    
def clean_path():
#Unzip and Erase all zips that start with MTBLS    
    for fzip in glob.glob('MTBLS*.zip'):
        unzip_file(fzip)
        erase_file(fzip)
            

def get_MTBLS_ID():
#Obtain MetaboLight entry(ies) inserted by user and return the IDs
    os.system('clear')
    print '======= GET METABOLIGHT ENTRIES ======='
    print "\nSearch for a range of values. INPUT: low-high!! Don't include MTBLS!!!"
    print 'Extract all metabolights entries from FTP server!!!. INPUT: all'
    print 'Search for a specific Metabolight entry. INPUT: MTBLS123'
    
    
    ID_entry = raw_input('Enter MetaboLight entry(leave empty to use examples): ')
    
    if not ID_entry: #check if string is empty
        PorG = raw_input('Examples: Moodle(m) or Poor(p) or Good(g) quality: ')
        if PorG.lower() == 'p':
            print 'MetagoLight entry: MTBLS72 - low quality in terms of metadata annotations'
            MTBLSid = 'MTBLS72'
            #get_Met_Entry('MTBLS72')
        elif PorG.lower() == 'g':
            print 'MetagoLight entry: MTBLS137 - good quality in terms of metadata annotations'
            MTBLSid = 'MTBLS137'
            #get_Met_Entry('MTBLS137')
        else:
            MTBLSid = 'MTBLS72 MTBLS137 MTBLS79'
            #for entry in ID_entry.split():         
                #get_Met_Entry(entry.upper())
    else:#USER defined a MTBLS entry
        if 'all' in ID_entry.lower(): #DOWNLOAD MTBLS entries from FTP public server
            
            print 'Accessing to ftp server: ftp.ebi.ac.uk'
            ftp = FTP('ftp.ebi.ac.uk')   # connect to host, default port (some example server, i'll use other one)
            ftp.login()               # user anonymous, passwd anonymous@
            file_list = []
            ftp.cwd('/pub/databases/metabolights/studies/public/')
            ftp.retrlines('NLST',file_list.append)    # list directory contents
            ftp.quit() 
            print str(len(file_list)) + " MTBLS ids extracted from ftp.ebi.ac.uk/pub/databases/metabolights/studies/public/"
            MTBLSid = file_list 
            #print 'Obtaining MTBLS entries'
            #for n in file_list:
                #get_Met_Entry(n.upper())
        elif type(ID_entry.split()) is list :#User specified more than one MTBLS entry
            
            mtbls_list = []
            for entry in ID_entry.split(): 
                mtbls_list.append(entry.upper())
            MTBLSid = mtbls_list
        elif "-" in ID_entry : #Search for a range of values
            ID_entry_low  = int(ID_entry.split('-')[0])
            ID_entry_high = int(ID_entry.split('-')[1])
            mtbls_list = []
            for i in range(ID_entry_low, ID_entry_high):
                mtbls_list.append('MTBLS'+str(i))
            MTBLSid = mtbls_list 
        
            
    return MTBLSid
    
def get_MTBLS_metadata(MTBLSid):
#Obtain metadata of MTBLSid and put it in folder: _dataMTBLS
    if verbose :
        print '> Obtaining metadata of MTBLS entries'
        
    if type(MTBLSid) is list:
        for MTBLSentry in MTBLSid:
            extract_MTBLSentry_from_EBI(MTBLSentry) 
    else:
        extract_MTBLSentry_from_EBI(MTBLSid)
               
    #ORGANIZE STUFF!              
    #Unzip and Remove *.zip files
    clean_path()
    
    for entry in glob.glob('OUTPUT/' + MTBLSid) :
        if os.path.isdir(entry):
            print "==== " + entry
            print "**** " + pathMTBLS + entry.split('/')[1]
            if not os.path.exists(pathMTBLS + entry.split('/')[1]) or (not ComputeHashBetweenFolders(entry, pathMTBLS + entry.split('/')[1])) :
                shutil.move(entry, pathMTBLS + entry.split('/')[1])
              
                
def ComputeHashBetweenFolders( folder1, folder2) :
#Compute hash of two folders: zip -> compute hash -> compare ? TRUE : FALSE

    shutil.make_archive(folder1, "zip" , folder1)
    shutil.make_archive(folder2, "zip" , folder2)
    
    print hashlib.sha256(folder1 + ".zip").hexdigest()
    print hashlib.sha256(folder2 + ".zip").hexdigest()
    erase_specificFormatFiles('.', ".zip") 
    
    
                          
def Rnd_MTBLSid():
#Go to ftp.ebi.ac.uk -> pub/databases and obtain a random MTBLS id (just the ID, not the content)
    ftp = FTP('ftp.ebi.ac.uk')   # connect to host, default port (some example server, i'll use other one)
    ftp.login()               # user anonymous, passwd anonymous@
    file_list = []
    ftp.cwd('/pub/databases/metabolights/studies/public/')
    ftp.retrlines('NLST',file_list.append)    # list directory contents
    ftp.quit() 
    
    return random.choice(file_list)
    
    
def opt_RandomStudy() :
#Obtain a random MTBLSid > parse it > getScore

    print "\tOtbaining random MTBLS entry"
    rnd_MTBLSid = Rnd_MTBLSid() # get random MTBLSid
    print "\t\t-> " + rnd_MTBLSid
    
    print "Obtaining " + rnd_MTBLSid + " metadata"
    get_MTBLS_metadata(rnd_MTBLSid) # get metadata of MTBLSid
    
    print "Running isatab parser"
    isatab_parser(rnd_MTBLSid) # do isatab_parser
    
    print "Running isatab parser (Pretty Printed)"
    pp_isatab_parser(rnd_MTBLSid) # do pp_isatab_parser
    
    print "Calculating score"
    get_EvaluationScore(rnd_MTBLSid)
          
    
    
##END:
            
##BEGIN: METHODS FOR EXTRACTION AND PARSING INFORMATION FROM MTBLS ENTRIES FOLDERS                                   
#Now serious...Extract information from file * 
#              in a pretty print way. Primary step
#              to get relevant information to 
#              search ontologies!!!
#WARNING: need to run first isatab_parser().
#       Because this function use the file 
#       created by ISATAB_parser (*)
def pp_isatab_parser(id_MTBLS=None):
#Extract information from file * in a pretty print way. Primary step to get relevant information to search ontologies!!!
    
    if not id_MTBLS:#id_MTBLS is None -> do PP for every MTBLS entry in folder _ppisatabPARSER
        #os.system('clear')
        #print '======= Pretty Print ISATab Information Extractor ======='
        if not os.path.exists(pathppISAPARSER):
            os.makedirs(pathppISAPARSER)
    
        if not os.listdir(pathISAPARSER) : #CASE: folder with isatab_parsed files is empty! 
            opt = raw_input('No files to process. Run ISATAB_parser to obtain these files?(Y/N): ')
            if ('y' in opt.lower()) or ('yes' in opt.lower()) : #Lets do some work. Run ISATAB_parser!
                isatab_parser()
            else:#CASE: Exit!
                return
       
        for name in os.listdir(pathISAPARSER) : #Find files already parsed by ISATAB parser
            if name.endswith("_parsed") :
                parse_text(pathISAPARSER + name)##Very sensible, don't change output * format
        ext_Information_from_file(2, 'MTBLS144')#Extract Ontologies
    else:#CASE: function called with one input parameter. USER should provide a good and existing MTBLS entry!!!!
        #Check if file parsed already exists
        if not os.path.isfile(pathISAPARSER + id_MTBLS + "_parsed") :
            isatab_parser(id_MTBLS)
        return parse_text(pathISAPARSER + id_MTBLS + '_parsed')
        

def parse_text(nameFile) : 
#READ a file *_parsed and extract relevant information:
    output = ''
    i = 0
    itemsOrg = []
    itemsOrgPart = []
    itemsAsFollows = []
    
    with open(nameFile) as fp :
        for line in fp :
            tmp_StudyAssays = []
            if ('   nodes:' not in line) :
                output += line ####IMPROVE += to another function
            elif line.find('   nodes:') == 0 : ##FOUND node: now another approach is used!! ##NOT OPTIMIZED!!!
                nameFile = nameFile.replace('OUTPUT/_isatabPARSER/','')
                for next_lines in fp :
                    if next_lines.find('Organism=') != -1 : 
                        ##DUMMY WAY!! NEED TO IMPROVE THIS...USE LEXER, PARSER INSTEAD!!!I WILL THINK ABOUT IT.
                        itemsOrg.extend(extractInfoDummy(next_lines, itemsOrg))
                        itemsAsFollows.extend(extractInfoDummy(next_lines, itemsAsFollows))
                    if next_lines.find('Organism_part=') != -1 :
                        ##DUMMY WAY!! NEED TO IMPROVE THIS...USE LEXER, PARSER INSTEAD!!!I WILL THINK ABOUT IT.
                        itemsOrgPart.extend(extractInfoDummy(next_lines, itemsOrgPart))
                        itemsAsFollows.extend(extractInfoDummy(next_lines, itemsAsFollows))
                    if next_lines.find("'Study Assay Measurement Type':") != -1 :
                        #itemsOrgPart.extend(extractInfoAssayDummy(next_lines, itemsOrgPart))
                        tmp_StudyAssays.extend(extractInfoAssayDummy(next_lines))
                    if next_lines.find("'Study Assay Measurement Type Term Accession Number':") != -1 :   
                        tmp_StudyAssays.extend(extractInfoAssayDummy(next_lines))
                    if next_lines.find("'Study Assay Measurement Type Term Source REF':") != -1 :   
                        tmp_StudyAssays.extend(extractInfoAssayDummy(next_lines))
                        
                        if len(set(tmp_StudyAssays).intersection(set(itemsOrg))) != 3:
                            itemsOrg.extend(tmp_StudyAssays)
                        if len(set(tmp_StudyAssays).intersection(set(itemsAsFollows))) != 3:
                            itemsAsFollows.extend(tmp_StudyAssays)
                        
                        
                        
                    #if next_lines.find('    * Assay') != -1 :
                    #    break;
                ##Format information to summary files
                output = output + '  * STRUCTURE : \n'
                for i in xrange(0,len(itemsOrg),3) :
                #for it in itemsOrg : 
                    output = output + '\t\t' + itemsOrg[i] + '\n'
                for i in xrange(0,len(itemsOrgPart),3) :
                    output = output + '\t\t\t' + itemsOrgPart[i] + '\n'
                        
                write_to_File(pathppISAPARSERsummary + 'pp_' + nameFile.replace('_parsed','_summary.inf'), output, 'w')
                write_to_File(pathppISAPARSER + 'pp_' + nameFile.replace('_parsed','.parsed'), ', '.join(itemsAsFollows), 'w')
                                
                break #Exit the external for loop
                                            

def extractInfoAssayDummy(abc) : 
    new_items = []
    abc = abc.replace("        'Study Assay Measurement Type':","")
    abc = abc.replace("        'Study Assay Measurement Type Term Accession Number':","")
    abc = abc.replace("        'Study Assay Measurement Type Term Source REF':","")  
    abc = abc.replace(",","")
    abc = abc.replace("'","")
    abc = abc.strip()  
    
    new_items.append(abc)
    
    
    return new_items

#Extract information from 2 lines below in form: [Organism;TSREF; TANUMBER; Org_part; TSREF; TANUMBER]
# metadata: {'Organism': [Attrs(Organism='Homo sapiens (Human)', Term_Source_REF='NEWT', Term_Accession_Number='9606')],
#   'Organism part': [Attrs(Organism_part='blood plasma', Term_Source_REF='BTO', Term_Accession_Number='BTO:0000131')],
def extractInfoDummy(abc, items) : 
#Extract Organism, REF, ACCNUM
    new_items = []   
    abc = abc.replace("  metadata: {'Organism': [Attrs(Organism='", "")
    abc = abc.replace("   'Organism part': [Attrs(Organism_part='", "")
    abc = abc.replace("', Term_Source_REF='",";")
    abc = abc.replace("', Term_Accession_Number='",";")
    abc = abc.replace(")],\n","")
    abc = abc.replace("'","")
    abc = abc.strip()     
    
    #abc = abc.replace("  ","")
    it = abc.split(";") #FORMAT: <NAME> <REF> <ONTOLOGY>
   
    if it[0] == '': 
        it[0] = 'NONE'
       
    if it[1] == '': 
        it[1] = 'NONE'
          
    if it[2] == '': 
        it[2] = 'NONE'
        
    if not ((it[0] in items) and (it[1] in items) and (it[2] in items)) :

        if it[0] == '': 
            new_items.append('NONE')
        else:
            new_items.append(it[0])
        
        if it[1] == '': 
            new_items.append('NONE')
        else:
            new_items.append(it[1])
        
        if it[2] == '': 
            new_items.append('NONE')
        else:
            new_items.append(it[2])
    
    
    return new_items
                         
                                                                                                                           

def isatab_parser(id_MTBLS=None):
                
    if not id_MTBLS :
        #os.system('clear')
        #print '======= ISATAB parser ======='
        #
        MTBLSentries = get_MTBLS_ID()
        for name in MTBLSentries:
            #print name
            #if os.path.isdir('OUTPUT/_dataMTBLS/' + name) and name.startswith("MTBLS") :
            rec = isatab.parse(pathMTBLS + name)
            fp = open(pathISAPARSER + name + '_parsed', 'w')
            print >> fp, rec
            fp.close()
    else:#CASE: function called with one input parameter. USER should provide a good and existing MTBLS entry!!!!
        if not os.path.exists(pathMTBLS + id_MTBLS) :
            get_MTBLS_metadata(id_MTBLS)
            
        rec = isatab.parse(pathMTBLS + id_MTBLS)
        fp = open(pathISAPARSER + id_MTBLS + '_parsed', 'w')
        print >> fp, rec
        fp.close()

#Extract only ontologies from a file
#posiStart :
#    > 0 : get Names
#    > 1 : get REF
#    > 2 : get Ontology
def ext_Information_from_file(posiStart, id_MTBLS=None):
    #Choose appropriate filename
    if posiStart == 0 : #Extract Org
            pathFile = pathppISAPARSER + 'Ontologies/org_'
    elif posiStart == 1 : #Extract Ref <- maybe never used!
            pathFile = pathppISAPARSER + 'Ontologies/ref_' 
    else : #Extract Term_Acc_Num
            pathFile = pathppISAPARSER + 'Ontologies/ont_'
    
    if not id_MTBLS : 
        #print '======= GET ONTOLOGIES ======='
        tmp = ''
        #url = urllib.URLopener()  
        #url.retrieve('http://rest.bioontology.org/bioportal/ontologies/metrics/40644?apikey=f92b9d92-6284-47c2-9c3a-68e66917e7c7', tmp)   
        #url.cleanup()    
    
        justone = False #check if only has to search for 1 entry
        opt = raw_input('What MTBLS entries do you want to get ontologies?(all,MTBLS[id]): ')
        opt2 = 'n' #default value
        if 'all' in opt.lower() : #PARSER all files
            opt = [ f for f in os.listdir(pathppISAPARSER) if os.path.isfile(join(pathppISAPARSER,f)) ]
            opt2 = raw_input('Are you sure you want to process  ' + str(len(opt)) + ' entries. Are you sure?(Y/N): ')
            #os.system('clear')   
            if 'yes' not in str(opt2.lower()) and 'y' not in str(opt2.lower()) : 
                return
        elif 'MTBLS' not in opt and opt[0].isdigit() : #PARSER a specific file(s)
            opt = 'pp_MTBLS' + str(opt) + '.parsed'
        elif opt.upper().startswith('MTBLS') :
            justone = True
            opt = 'pp_' + str(opt).upper() + '.parsed'
        else:
            print 'Not a valid input'
            return
            
        
        only_Ont = []
        if justone : #CASE: just asked 1 entry to process
            fp = open(pathppISAPARSER + opt,'r')        
            for fpcontent in fp :
                for posiOnt in xrange(posiStart,len(fpcontent.split(',')),3) :
                    print posiOnt
                    only_Ont.append(fpcontent.split(',')[posiOnt].strip())
            write_to_File(pathFile + opt, only_Ont, 'w')      
        else : #lets do it for each entry
            for entry in opt:
                fp = open(pathppISAPARSER + entry,'r')
                for fpcontent in fp :
                    for posiOnt in xrange(posiStart,len(fpcontent.split(',')),3) : #Just search for multiple 3 position
                        tmp = ''
                        if not fpcontent.split(',')[posiOnt].strip() :# CASE: empty cell no information there!!
                            tmp = 'NONE'
                        else:
                            tmp = fpcontent.split(',')[posiOnt].strip()
                        only_Ont.append(tmp) #Split file to a list only with Ontologies
                write_to_File(pathFile + entry, ';'.join(only_Ont), 'w')
                only_Ont[:] = [] 
    
    else:#CASE: function called with one input parameter. USER should provide a good and existing MTBLS entry!!!!
        only_Ont = []
        with open(pathppISAPARSER + 'pp_' + id_MTBLS + '.parsed','r') as fp : 
            for fpcontent in fp :
                for posiOnt in xrange(posiStart,len(fpcontent.split(',')),3) :
                    only_Ont.append(fpcontent.split(',')[posiOnt].strip())
            write_to_File(pathFile + id_MTBLS + '.parsed', ';'.join(only_Ont), 'w')      
        return only_Ont
            
    return #Not applied when used with a list of MTBLS entries as input

##END:                    

##BEGIN: METHODS FOR SECUNDARY STUFFS
def timeTotal(sec):
    print("Time elapsed: " +  str(datetime.timedelta(sec)))

def write_to_File(nameFile, content, mode_Open):
    #Create, Write, and Close a file. mode_Open: a, w, wb  
    
    fp = open(nameFile, mode_Open)
    #if mode_Open != 'a':
    #   print "Created file: " + nameFile    
    fp.write(content)    
    fp.close()# -*- coding: utf-8 -*-

def get_TimeRemaining(actEntry, totEntries, MTBLSentry):
    print('\tProcessing: ' + str(actEntry) + ' of ' + str(totEntries) + " --> " + MTBLSentry)

    
def PP_Documentation():
#Parse file do_magic.py and extract methods and more documentation
    fpout = open('OUTPUT/Documentation_do_magic.py','w')
    flag = False
    with open('do_magic.py') as fp:
        content = fp.readlines()
        for line in content:
            if line.startswith('##') :
                fpout.write(line)
            if line.startswith('def') :
                flag = True
                fpout.write('\t' + line)
            if flag and line.startswith('#') :
                fpout.write('\t\t' + line)
                flag = False
                    
        fpout.close()
    return
        
def json2xml(json_obj, line_padding=""):
    result_list = list()

    json_obj_type = type(json_obj)

    if json_obj_type is list:
        for sub_elem in json_obj:
            result_list.append(json2xml(sub_elem, line_padding))

        return "\n".join(result_list)

    if json_obj_type is dict:
        for tag_name in json_obj:
            sub_obj = json_obj[tag_name]
            result_list.append("%s<%s>" % (line_padding, tag_name))
            result_list.append(json2xml(sub_obj, "\t" + line_padding))
            result_list.append("%s</%s>" % (line_padding, tag_name))

        return "\n".join(result_list)

    return "%s%s" % (line_padding, json_obj)
            
def pprint_DateTime():
#PrettyPrint for date and time > YYYY-MM-DD HH:MM:SS
    idate = datetime.datetime.now()
    return str(idate.year) + '-' + str(idate.month) + '-' + str(idate.day) + ' ' + str(idate.hour) + ':' + str(idate.minute) + ':' +  str(idate.second)

def get_json(url):
    API_KEY = "f92b9d92-6284-47c2-9c3a-68e66917e7c7"
    opener = urllib2.build_opener()
    opener.addheaders = [('Authorization', 'apikey token=' + API_KEY)]
    return json.loads(opener.open(url).read())


def query(q,apikey,epr,f='application/json'):
    #Get ontologies where some results were returned
    try:
        params = {'query': q, 'apikey': apikey}
        params = urllib.urlencode(params)
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(epr+'?'+params)
        request.add_header('Accept', f)
        request.get_method = lambda: 'GET'
        url = opener.open(request)
        return url.read()
    except Exception, e:
        traceback.print_exc(file=sys.stdout)
        raise e  
        
def ext_OntNames(info):
    #extract Ontologies and Name of entry from a SPARQL query
    seeOnt = False
    seeName = False
    #hand = openname('OUTPUT/jsonOutput')
    outt = ''
    for line in info.split('\n'):
        line = line.strip()
        
        #Print Name value
        if re.search('"name":', line) :
            seeName = True
        if re.search('"value":', line) and seeName :
            #write_to_File('pp_Query.omg', line.replace('"',''), 'a')
            line  = line.replace('                   ','')
            line  = line.replace('value', 'name')
            outt += line.replace('"','')
            seeName = False
            
        #Print Ontology value
        if re.search('ont":', line) :
            seeOnt = True
        if re.search('"value":', line) and seeOnt :
            #write_to_File('pp_Query.omg', line.replace('"',''), 'a')
            line  = line.replace('                   ','   ')
            line  = line.replace('value', 'ontol')
            outt += line.replace('"','')
            outt += '\n'
            seeOnt = False

    write_to_File('./OUTPUT/pp_Query.omg', outt, 'wb') 
    
  
#END:

##BEGIN: EXTRACTION INFORMATION OF ONTOLOGIES, TERMS. CALCULATE FINAL SCORE!
    
def get_EvaluationScore(id_MTBLS=None): 
#Method to calculate the quantitative score...IN PROGRESS!!
   # from html import HTML
    if not id_MTBLS :
        MTBLSentries = get_MTBLS_ID() 
    else:
        MTBLSentries = id_MTBLS
    
    os.system('clear')   
    print "Calculating the quantitative score..."
    counter = 0
    ontologies = [] #Store the ontologies extracted!!!
    organism = []
    print MTBLSentries
    db_onto = REST_getAllOntologiesBioportal()#get updated database with all ontologies available in bioportal
   
    for MTBLSentry in MTBLSentries :
        #clean files from previous studies
        if os.path.exists(pathppISAPARSERsummary + "pp_" + MTBLSentry + "_summary.inf") :
            os.remove(pathppISAPARSERsummary + "pp_" + MTBLSentry + "_summary.inf")
        if os.path.exists(pathppISAPARSERsummary + MTBLSentry + ".recommender") :
            os.remove(pathppISAPARSERsummary + MTBLSentry + ".recommender")
            
        ontologies = [] 
        organism = []
        #Check if file pp_parsed already exists    
        if not os.path.isfile(pathppISAPARSER + MTBLSentry) :
            pp_isatab_parser(MTBLSentry) 
            
        ontologies = ext_Information_from_file(2, MTBLSentry)#Each position is a file
        organism = ext_Information_from_file(0, MTBLSentry)#Each position is a file
        counter += 1
        get_TimeRemaining(counter, len(MTBLSentries), MTBLSentry)          
        
        #Need this because the file is read in mode append
        if os.path.isfile(pathppISAPARSERsummary + MTBLSentry + ".btw"):
            os.remove(pathppISAPARSERsummary + MTBLSentry + ".btw")
       
        #REST_API_FUNCTIONS ..HERE! 
        #EXTRACT METRICS OF ONTOLOGIES
        
        print '\t' + MTBLSentry
        #Search for empty fields = NONE
        print "\t\tTEST: PARSING"
        parsingScore, relScore = REST_SCOREparsing(MTBLSentry, db_onto)
        print "\t\t\tPARSE_SCORE: " + str(parsingScore) + " of 1(max_value)"
        print "\t\t\tPARSE_SCORE_relat: " + str(relScore) + " % ontologies were found!"
        
        print "\t\tTEST: LEXICAL"
        score = REST_SCOREOntoLexic(MTBLSentry)
        print "\t\t\tLEXIC_SCORE_efect: " + str(score)
        
        
        ##print '\tEXTRACT METRICS OF ONTOLOGIES'
        #for ontol in ontologies :
        #    print '\t\t' + str(ontol)
        #    REST_get_OntologyMetrics(ontol)
        
        #EXTRACT INFORMATION ABOUT ORGANISM -> USED AS TERMS!
        #print '\tEXTRACT INFORMATION ABOUT ORGANISM'
        #print '\t\tRECOMMENDER is working....'
        print "\t\tTEST: ANNOTATIONS"
        for org, ontol  in zip(organism, ontologies) :
            if org != 'NONE' and ontol != 'NONE':
                
                #print '\t\t\t' + str(org)
                print '\t\t\tTEST: Quality of MTBLS entries'
                #
                #Quality of MTBLS entries!!!
                SelfLinkOntolEq, SelfLinkOntolCont = REST_getNode_OntologyTerm(org, ontol)
                print "\t\t\t\tRESULTS:"
                print "\t\t\t\t\tEqual Ontology: " + str(len(SelfLinkOntolEq))
                #for elem in SelfLinkOntolEq:
                #    print "\t\t\t\t\t\t\t" + REST_recommender_OntoID(get_json(elem))
                print "\t\t\t\t\tContain Ontology: " + str(len(SelfLinkOntolCont))
                #for elem in SelfLinkOntolCont:
                #    print "\t\t\t\t\t\t\t" + REST_recommender_OntoID(get_json(elem))
                ##               
                print '\t\t\tTEST: Quality of Ontologies used in MTBLS entries'
                OntologiesByRecommender = REST_get_Recommender(MTBLSentry, org, ontol)
                print "\t\t\tSCORE: " + str(REST_SCOREDepthMTBLSentry(org, ontol, OntologiesByRecommender))
            else:
                print "\t\t\tEmpty Organism :: "+ontol if org == 'NONE' else "\t\t\t" + org + " :: Empty Ontology"
            #REST_get_Recommender(MTBLSentry, org)
            #REST_get_Annotations(MTBLSentry, org)
               
##END:           

def REST_getAllOntologiesBioportal():
#Return a list with a dictionary of all ontologies in bioportal ['acronym']['name']
    ontolJSON = get_json("http://data.bioontology.org/ontologies")
    db_onto = []
    
    for ont in ontolJSON:
        dic = {}
        dic['acr'] = ont['acronym']
        dic['name'] = ont['name']
        db_onto.append(dic)
        
    return db_onto
    
def print_annotations(MTBLSentry, annotations, get_class=True):
#Given a specific term, extract information to a file in 'OUTPUT/_ppisatabPARSER/[MTBLSID].btw
    fp = open(pathppISAPARSERsummary + MTBLSentry + ".annotation","w");
    
    for result in annotations:        
        
        print >> fp, json2xml(result,"")        
        
        class_details = get_json(result["annotatedClass"]["links"]["self"]) if get_class else result["annotatedClass"]
        
        print get_json(result["annotatedClass"]["links"]["self"])
       
        print >>fp,"Class details"
        print >>fp,"\tid: " + class_details["@id"]
        print >>fp,"\tprefLabel: " + class_details["prefLabel"]
        print >>fp,"\tontology: " + class_details["links"]["ontology"]

        print >>fp,"Annotation details"
        for annotation in result["annotations"]:
            print >>fp,"\tfrom: " + str(annotation["from"])
            print >>fp,"\tto: " + str(annotation["to"])
            print >>fp,"\tmatch type: " + annotation["matchType"]

        if result["hierarchy"]:
            print >>fp,"\n\tHierarchy annotations"
            for annotation in result["hierarchy"]:
                class_details = get_json(annotation["annotatedClass"]["links"]["self"])
                pref_label = class_details["prefLabel"] or "no label"
                print >>fp,"\t\tClass details"
                print >>fp,"\t\t\tid: " + class_details["@id"]
                print >>fp,"\t\t\tprefLabel: " + class_details["prefLabel"]
                print >>fp,"\t\t\tontology: " + class_details["links"]["ontology"]
                print >>fp,"\t\t\tdistance from originally annotated class: " + str(annotation["distance"])
       
        fp.close()
        return
        
def REST_recommender_HasChild(result): # return boolean
#check if a certain node has child
    child = get_json(result["links"]["descendants"])
   
    if not child:
        return "No"
    return "Yes"
    
def REST_recommender_GetPrefLabel(node):
#get the prefLabel field from self link

    return get_json(node["links"]["self"])["prefLabel"]    
    
def REST_recommender_HasParent(result): # return boolean
#check if a certain node has parent
    if not result:
        return "No"
    parent = get_json(result["links"]["ancestors"])
    if not parent:
        return "No"
    return "Yes"
    
def REST_recommender_GetParent(node):
#get parent of a given node
    return get_json(node["links"]["ancestors"])
        
def REST_recommender_TreeDepth(node, beVerbose=False):
#get the tree depth based on a given node
    depth = 1
    
    print"\t\t\t\tCalculating Tree Depth",
     
    if beVerbose :
        print "\n\t\t\t\t\t 0  " + REST_recommender_GetPrefLabel(node)
    else:
        print ".",
    while(1):
        parent_node = REST_recommender_GetParent(node)
        node = parent_node[0]
        #print "\t\t\t\t" + node["synonym"][0] + "\t  " + str(depth)
        prefLabel = REST_recommender_GetPrefLabel(node)
        #if not( prefLabel == [] or (not prefLabel) or prefLabel == [ ]) :
        if beVerbose :
            print "\t\t\t\t\t " + str(depth) + "  " + prefLabel
        else:
            print ".",
        depth += 1
        
        #last iteration
        if REST_recommender_HasParent(get_json(node["links"]["ancestors"])[0]) == "No":
            if beVerbose :
                print "\t\t\t\t\t " + str(depth) + "  " + REST_recommender_GetPrefLabel(get_json(node["links"]["ancestors"])[0]) + " ..DONE!"
            else :
                print ". DONE!"
            return depth
         
        
    return -1
        
def REST_recommender_OntoID(result):
#get the ontology ID
    onto = get_json(result["links"]["ontology"])
    return onto["acronym"]

def REST_SCOREparsing(id_MTBLS, db_onto):
#Search if ontologies/REF have known values
    fp = open(pathppISAPARSER + "pp_" + id_MTBLS + ".parsed", 'r')
    line = fp.readlines()[0].split(",")
    
    #SCORES USED FOR DIFFERENT CASES
    score_fREF_fONT   = 1   # found_REF AND found_ONT
    score_nfREF_fONT  = 0.2 # not_found_REF AND found_ONT
    score_fREF_nfONT  = 0.7 # found_REF AND not_found_ONT
    score_nfREF_nfONT = 0   # not_found_REF AND not_found_ONT
    
    relFound = 0 #number of relations found!!
    score = 0
    for i in xrange(1,len(line),3) :
        #found_Ont = False
        found_ref = False
        found_ont = False
        
        for acr in db_onto:#Compare with all ontologies in bioportal
            if line[i].strip() == 'NONE' and line[i+1].strip() == 'NONE':
                continue
            if line[i].strip().upper() in acr['acr']:
                #found_Ont = True
                found_ref = True
            if line[i+1].strip().upper() in acr['acr']:
                #found_Ont = True
                found_ont = True        
            #calculate score: (ont OR ref) AND (ont == ref)
            if found_ont or found_ref : #OR    
                relFound += 1    
                if found_ont == found_ref : # both are 1 
                    score += score_fREF_fONT #MAX_SCORE
                if found_ont : #Found_ONT AND notFound_REF
                    score += score_nfREF_fONT
                else: #notFound_ONT AND Found_REF
                    score += score_fREF_nfONT
                break;
                
    return score, str(relFound/(2*len(line))*100)
        
def REST_SCOREOntoLexic(id_MTBLS):
#Compute syntactic analysis of an entry
    w_org = 0.5
    w_ref = 0.7
    w_ont = 0.9
        
    fp = open(pathppISAPARSER + "pp_" + id_MTBLS + ".parsed", 'r')
    e_org = 0
    e_ref = 0
    e_ont = 0
    
    line = fp.readlines()[0].split(",")
    
    
    for i in xrange(0,len(line),3) :
        if line[i].strip() == 'NONE':
            e_org += 1
        if line[i+1].strip() == 'NONE':
            e_ref += 1
        if line[i+2].strip() == 'NONE':
            e_ont += 1
            
    formula = 1-(e_org*w_org + e_ref*w_ref + e_ont*w_ont)/(len(line)/3)%1
    return formula        
        
def REST_getNode_OntologyTerm(term, ontology):
#Get self link based on term and ontology provided -> return NONE is link not found    

    #access to data.bioontology of given Term
    REST_URL = "http://data.bioontology.org"
    recom = get_json(REST_URL + "/recommender?input=" + urllib2.quote(term))
    SelfsLinkContains = [] #save the self links to ontologies found (with contains)
    SelfsLinkEqual = [] #save the self links to ontologies found (with equals)
    
    #ontology = ontology.replace(":","_")
    #run recommender
    #get all ontologies (for the term in study)
    for ontoID in recom: 
        #print get_json(ontoID["coverageResult"]["annotations"][0]["annotatedClass"]["links"]["ontology"])["@id"] + " VS " + ontology
        idOntology = str(ontoID["coverageResult"]["annotations"][0]["annotatedClass"]["@id"])
        #found the ontology asked
        if idOntology.find(ontology) != -1 or (ontology in idOntology) : #Found relation
            #obtain "self" link to the term in this ontology
            SelfsLinkContains.append(ontoID["coverageResult"]["annotations"][0]["annotatedClass"]["links"]["self"])
            
        if idOntology == ontology or str(get_json(ontoID["coverageResult"]["annotations"][0]["annotatedClass"]["links"]["ontology"])["acronym"]) == ontology:
            #obtain "self" link to the term in this ontology
            SelfsLinkEqual.append(ontoID["coverageResult"]["annotations"][0]["annotatedClass"]["links"]["self"])
            
    return SelfsLinkEqual, SelfsLinkContains

def REST_SCOREDepthMTBLSentry(term, ontology, OntologiesByRecommender):
#TEST: get the tree depth of the term used in MTBLSid, according with the ontology they specified!!!
    ontoEqual, ontoSimilar = REST_getNode_OntologyTerm(term, ontology)
   
    if len(ontoEqual) > 0:
        for elemEq in ontoEqual:
            elemEqjson = get_json(elemEq)
            treedepth = REST_recommender_TreeDepth(elemEqjson, False)
            haschildren = REST_recommender_HasChild(elemEqjson)
    else:
        if len(ontoSimilar) > 0:#Found an ontology equal to the one they specified!!Not take into account lexical analysis.
            for i,elemSim in enumerate(ontoSimilar): #treat special case of NCBITAXON
                if "NCBITAXON" in elemSim :        
                    elemSimjson = get_json(ontoSimilar[i])
                    treedepth = REST_recommender_TreeDepth(elemSimjson, False)
                    haschildren = REST_recommender_HasChild(elemSimjson)
            else:#work with first similar ontology found!!
                #for elemSim in ontoSimilar:
                elemSimjson = get_json(ontoSimilar[0])
                treedepth = REST_recommender_TreeDepth(elemSimjson, False)
                haschildren = REST_recommender_HasChild(elemSimjson)
                #break
        else:
            print "\t\t\t\tThe ontology " + ontology + " does not exists"
            score = 0
            return score
    
    #compute score!!
    score = 0
    w_Children = 0.4 #weight to penalize (OR NOT) a node with children
    score = w_Children  if haschildren == "Yes" else w_Children/treedepth + w_Children
    
    for i, onto in enumerate(OntologiesByRecommender):
            if onto == ontology or ontology in onto:#found ontology presented in metabolight study
                break
    #take into account the position in Recommender!!
    #FORMULA: (1 / (Position_TOP / TOP_Size) + 0.2 ) / 5 ---Equal to---> TOP_Size / ((5*Position_TOP) + 2 * TOP_Size)
    TOP_Size = len(OntologiesByRecommender)
    Position_TOP = i+1#because start at zero
    score += TOP_Size/((5*Position_TOP)+2*TOP_Size)
    #print TOP_Size
    #print TOP_Size/((5*Position_TOP)+2*TOP_Size)
    #print score
    #print treedepth
    #print haschildren  
    
    return score      
    
    
def print_recommendations(MTBLSentry, recom, printSummary=True):
#Given a specific term, extract information to a file in 'OUTPUT/_ppisatabPARSER/[MTBLSID].btw
    #
    top = 3; #define the number of ontologies to return
    turn = 1;
    beVerbose = True; #print output to file
    if beVerbose: 
        fp = open(pathppISAPARSERsummary + MTBLSentry + ".recommender","a");
    topOntologies = []
    for result in recom:
        
        class_details = get_json(result["coverageResult"]["annotations"][0]["annotatedClass"]["links"]["self"])
        name_Onto =  REST_recommender_OntoID(class_details)
        topOntologies.append(name_Onto)
        
        if turn == 1:
            has_child = REST_recommender_HasChild(class_details)# return boolean
            has_parent = REST_recommender_HasParent(class_details)# return boolean
            tree_depth =  REST_recommender_TreeDepth(class_details, False)            
            
            print "\t\t\t\tRecommended ontologies"        
            print  "\t\t\t\tDetails"
            print  "\t\t\t\t\tprefLabel: " + class_details["prefLabel"]
            print  "\t\t\t\t\tid: " + class_details["@id"]
            print  "\t\t\t\t\thas child: " + has_child
            print  "\t\t\t\t\thas parent: " + has_parent
            print  "\t\t\t\t\ttree depth: " + str(tree_depth)
      
            print "\t\t\t\t\tRecommended ontologies"
        
        if beVerbose :
            print >>fp, "\t\tontology: " + name_Onto
            print >>fp, "\t\t\tScore Values"
            print >>fp, "\t\t\t\tFinal Score         : " + str(result["evaluationScore"]*100)
            print >>fp, "\t\t\t\tCoverage Score      : " + str(result["coverageResult"]["normalizedScore"]*100)
            print >>fp, "\t\t\t\tAcceptance Score    : " + str(result["acceptanceResult"]["normalizedScore"]*100)
            print >>fp, "\t\t\t\tDetail Score        : " + str(result["detailResult"]["normalizedScore"]*100)
            print >>fp, "\t\t\t\tSpecialization Score: " + str(result["specializationResult"]["normalizedScore"]*100)
        
        if printSummary : #print to stdout
            print  "\t\t\t\t\tontology: " + name_Onto
            print  "\t\t\t\t\t\tScore Values"
            print  "\t\t\t\t\t\t\tFinal Score         : " + str(result["evaluationScore"]*100)
            print  "\t\t\t\t\t\t\tCoverage Score      : " + str(result["coverageResult"]["normalizedScore"]*100)
            print  "\t\t\t\t\t\t\tAcceptance Score    : " + str(result["acceptanceResult"]["normalizedScore"]*100)
            print  "\t\t\t\t\t\t\tDetail Score        : " + str(result["detailResult"]["normalizedScore"]*100)
            print  "\t\t\t\t\t\t\tSpecialization Score: " + str(result["specializationResult"]["normalizedScore"]*100)
                  
        if turn == top:
            if beVerbose :
                #print "close file"
                fp.close()
            break

        turn += 1;
    return topOntologies#name of ontologies, ordered by the recommender!!!
        
        
##BEGIN: METHODS TO EXTRACT INFORMATION ABOUT ONTOLOGIES, TERMS,.... -> data.bioontology.org

def REST_get_Recommender(MTBLSentry, organism, ontology):
#TEST: Navigate through data.bioontology.org, input the organism and obtain the recommended ontologies
    REST_URL = "http://data.bioontology.org"
    #text_to_annotate = "Melanoma is a malignant tumor of melanocytes which are found predominantly in skin but also in the bowel and the eye."
    #text_to_annotate = "blood plasma"
    # Annotate using the provided text
    #fp = open(pathppISAPARSERsummary + MTBLSentry + ".recommender","w");
    
    recom = get_json(REST_URL + "/recommender?input=" + urllib2.quote(organism))
    
    #recom = get_json("http://data.bioontology.org/ontologies/SNOMEDCT/classes/http%3A%2F%2Fpurl.bioontology.org%2Fontology%2FSNOMEDCT%2F337915000/tree")
    #REST_ownAPI_TreeDepth(recom, ontology)
    #print '\t\t\tRecommender is working....'
    # Print out annotation details
    topOntologies = print_recommendations(MTBLSentry, recom ,False)
    
    #print '\t\t\tAnnotate with hierarchy information'
    # Annotate with hierarchy information
    #recom = get_json(REST_URL + "/annotator?max_level=6&text=" + urllib2.quote(organism))
    #print_recommendations(MTBLSentry, recom)

    # Annotate with prefLabel, synonym, definition returned
    #annotations = get_json(REST_URL + "/annotator?include=prefLabel,synonym,definition&text=" + urllib2.quote(text_to_annotate))
    #print_annotations(MTBLSentry, annotations, False)               
    return topOntologies                      
                                                    
def REST_get_Annotations(MTBLSentry, text_to_annotate):
#Navigate through data.bioontology.org and extract relevant information..NEED TO BE EXPLORED!!
    REST_URL = "http://data.bioontology.org"
    #text_to_annotate = "Melanoma is a malignant tumor of melanocytes which are found predominantly in skin but also in the bowel and the eye."
    #text_to_annotate = "blood plasma"
    # Annotate using the provided text
    annotations = get_json(REST_URL + "/annotator?text=" + urllib2.quote(text_to_annotate))
    
    
    print '\t\t\t\tPrint out annotation details'
    # Print out annotation details
    print_annotations(MTBLSentry, annotations)
    
    print '\t\t\t\tAnnotate with hierarchy information'
    # Annotate with hierarchy information
    annotations = get_json(REST_URL + "/annotator?max_level=6&text=" + urllib2.quote(text_to_annotate))
    print_annotations(MTBLSentry, annotations)

    # Annotate with prefLabel, synonym, definition returned
    #annotations = get_json(REST_URL + "/annotator?include=prefLabel,synonym,definition&text=" + urllib2.quote(text_to_annotate))
    #print_annotations(MTBLSentry, annotations, False)    
    
    
def REST_get_OntologyMetrics(ID_Ontology) : 
# Get the Ontology Metrics of a specific Ontology
    REST_URL = "http://data.bioontology.org"
    resources = get_json(REST_URL + "/")
    
    # Follow the ontologies link by looking for the media type in the list of links
    media_type = "http://data.bioontology.org/metadata/Ontology"
    #media_type = "http://data.bioontology.org/metadata/Metrics"
    #media_link_onto = "http://data.bioontology.org/ontologies/" + id_Ontology
    ontology_output = []
 
    fp = open(pathppISAPARSER + 'REST_OUTPUT/MTBLS72' , 'w');
    found_link = ""
    for link, link_type in resources["links"]["@context"].iteritems():
            #print link_type
        if media_type == link_type:
            found_link = link
            
    # Get the ontologies from the link we found
    ontologies = get_json(resources["links"][found_link])
    
    # Get the name and ontology id from the returned list
    for ontology in ontologies:
        if (str(ontology["@id"]) == ID_Ontology) or (str(ontology["acronym"]) == ID_Ontology) :
            print '\t\t\tObtaining maxDepth, Classes, ID of Ontology'
            #print ontology
            #ontology_output.append("name: " + str(ontology["name"]) + "\tacronym: " + str(ontology["acronym"]) + "\t" + ontology["@id"] + "\n\n")
            #ontology_output.append("acronym: " + str(ontology["acronym"]) + "\t ID: " + ontology["@id"] + "\n")
            ontology_output.append("maxDepth: " + str(ontology["maxDepth"]) + "\nClasses: " + str(ontology["classes"]) + "\n" + ontology["@id"] + "\n\n")
           # tt = "NAME: " + str(ontology["name"]) + "\tACRONYM: " + str(ontology["acronym"]) + "\tID: " + ontology["@id"] + "\n"
            tt = "maxDepth: " + str(ontology["maxDepth"]) + "\nClasses: " + str(ontology["classes"]) + "\n" + ontology["@id"] + "\n\n"
            print >> fp, tt
        
       
    fp.close()
    return
    
##END:    
        
##BEGIN: METHODS FOR USER OPTIONS
def main():
    os.system('clear')
    if (not os.path.exists('OUTPUT/')):
        os.makedirs('OUTPUT/')
    if not os.path.exists(pathMTBLS):
        os.makedirs(pathMTBLS)  
    if not os.path.exists(pathppISAPARSERsummary):
        os.makedirs(pathppISAPARSERsummary)
    if not os.path.exists(pathISAPARSER):
        os.makedirs(pathISAPARSER)
    if not os.path.exists(pathppISAPARSER + "Ontologies/"):
        os.makedirs(pathppISAPARSER + "Ontologies/")
  
    print ('==============================')
    print (' 0: Random Study')
    print (' 1: Quantitative Evaluation of MTBLS entry')
    print (' 2: Get documentation of do_magic.py <--- usem isto ajuda a perceber o que os métodos fazem')
    print (' 3: Other Functions')
    print (' 4: EXIT ')
    print ('==============================')
    
    #How to make something similar to SWITCH..CASE in Python
    options = {0 : rndStudy,
                    1 : opt_Evaluation,    
                    2 : opt_Documentation,  
                    3 : opt_OtherFunctions,     
                    4 : opt_Exit,
    }
    try:
        opt = raw_input(': ')
        options[int(opt)]()
        print 'Program has finished!'
    except KeyError :
        print 'Invalid option'
        process_default()
        
def opt_OtherFuns():
    
    os.system('clear')
    print ('Other Functions\n')
    print ('\t 1: Get data from MetaboLight')
    print ('\t 2: Use ISATab Parser')
    print ('\t 3: Use ISATab Validator')
    #print ('\t 4: Use THOR_infoExtractor') #Get the file created by opt 2 and format information
    print ('\t 5: Return to main menu')
    print ('\t 6: EXIT ')
    
    options = {1 : opt_DataMetaboLight,
                    2 : opt_IsatabParser,
                    3 : opt_IsatabValidator, 
                    4 : opt_ppInfoExtractor,
                    5 : opt_ReturnMain,
                    6 : opt_Exit,
    }
    try:
        opt = raw_input(': ')
        options[int(opt)]()
        print 'Program has finished!'
    except KeyError :
        print 'Invalid option'
        process_default()

def rndStudy():
    opt_RandomStudy()

def opt_OtherFunctions():
    opt_OtherFuns()
    
def opt_ReturnMain():
    main()
    
def opt_Documentation():
    PP_Documentation()
    
def process_default():
    main()
    
def opt_Exit() :
    os.system('clear')
    print 'Bye :)' 
    sys.exit()
            
def opt_ppInfoExtractor() :
    pp_isatab_parser()
    
    
def opt_Evaluation() :
    get_EvaluationScore()#Get ontology
    
      
def opt_DataMetaboLight() :
    get_MTBLS_metadata()# Get DATA from MetaboLight website    
    
#PrettyPrint records from each element, using isatab parser https://github.com/ISA-tools/biopy-isatab#readme
def opt_IsatabParser() :    
    if not os.path.exists(pathISAPARSER):
            os.makedirs(pathISAPARSER)
    isatab_parser()
 
def opt_IsatabValidator() :    
    subprocess.call(["java -jar isatools_deps.jar -Xms256m -Xmx1024m -XX:PermSize=64m -XX:MaxPermSize=128m"], shell=True)
    
##END:


#####STARTS HERE#####
#start_time = time.clock()
start = timeit.default_timer()
main()
stop = timeit.default_timer()
timeTotal(stop-start)



####LINK: https://github.com/ncbo/ncbo_rest_sample_code/tree/master/python