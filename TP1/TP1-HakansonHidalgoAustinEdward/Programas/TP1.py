## IMPORTS
import re as regex
import unicodedata
from pathlib import Path
from bs4 import BeautifulSoup
from bs4.element import HTMLFormatter

## CONSTANTS
UNICODE_NORMAL_FORM_COMPATIBILITY_DECOMPOSITION = 'NFKD'    #Para la eliminacion de acentos y otras marcas
# Esta forma de normalización se esocogió porque permite descomponer los caracteres ya acentuados
# (i.e "á") en su forma normal "a" y la marca asociada "´". Para hacer esto existen las formas NFD y NFKD.
# La diferencia es que la NFKD ofrece más compatibilidad, por ejemplo en caso de que alguna fuente no tenga soporte
# para ciertos caracteres.
TEXT_MODE = 0   #Para cuando se tienen que extraer las etiquetas del archivo html como para crear los unigramas
TAG_MODE = 1    #Para cuando se tienen que mantener las etiquetas del archivo html como para extraer las referencias 

## GLOBAL VARIABLES 
HTML_File_Pattern = regex.compile(r'.*\.html?',regex.IGNORECASE)
Word_Pattern = regex.compile(r'[a-zñ]')
HTMLTextFiles = []
WordList = []
ReferenceSet = set()
WordLogicViewList = []
WordFrequencyDictionary = {}
UnigramLanguageModel = {}
Rank = {}
TotalWords = 0

## FUNCTIONS
def clearGlobalVariables():
    global HTMLTextFiles
    global WordList
    global ReferenceSet
    global WordLogicViewList
    global WordFrequencyDictionary
    global UnigramLanguageModel
    global Rank
    global TotalWords
    HTMLTextFiles.clear()
    WordList.clear()
    ReferenceSet.clear()
    WordLogicViewList.clear()
    WordFrequencyDictionary.clear()
    UnigramLanguageModel.clear()
    Rank.clear()
    TotalWords = 0

def traverseAllContentsFromPath(pPath):
    global HTMLTextFiles
    Entries = Path(pPath)
    text = ""
    for entry in Entries.iterdir():
        if entry.is_file():
            if HTML_File_Pattern.match(entry.name):
                with open(entry) as HtmlFile:
                    text = BeautifulSoup(HtmlFile,'lxml')
                    HTMLTextFiles.append(text.get_text())
        else:
            traverseAllContentsFromPath(entry)

def getTextFromFilesInPath(pPath, pMode):
    global HTMLTextFiles
    Entry = Path(pPath)
    if (Entry.is_file()):
        if HTML_File_Pattern.match(Entry.name):
                with open(Entry) as HtmlFile:
                    text = BeautifulSoup(HtmlFile,'lxml')
                    if pMode == TEXT_MODE:
                        HTMLTextFiles.append(text.get_text())
                    else:
                        HTMLTextFiles.append(text)
        else:
            print('El archivo',Entry.name,'no es de tipo html o html')
    else:
        traverseAllContentsFromPath(pPath)  

def createWordList():
    global HTMLTextFiles
    for text_file in HTMLTextFiles:
        for word in text_file.split():
            WordList.append(word.strip())

def stripAccentsAndSymbols(pWord):
    FormattedWord = ''
    CharacterDecomposition = ''
    for character in pWord:
        if Word_Pattern.match(character):
            FormattedWord += character
        else:
            CharacterDecomposition = unicodedata.normalize(UNICODE_NORMAL_FORM_COMPATIBILITY_DECOMPOSITION, character)
            for new_character in CharacterDecomposition:
                if Word_Pattern.match(new_character):
                    FormattedWord += new_character                       
    return FormattedWord

def createLogicView():
    global WordList
    global WordLogicViewList
    global TotalWords 
    for word in WordList:
        word = word.lower()
        word = stripAccentsAndSymbols(word)
        if word != '':
            WordLogicViewList.append(word)
    TotalWords = len(WordLogicViewList)

def createWordFrequencyDictionary():
    global WordLogicViewList
    global WordFrequencyDictionary
    for word in WordLogicViewList:
        if word in WordFrequencyDictionary:
            WordFrequencyDictionary[word] += 1
        else:
            WordFrequencyDictionary[word] = 1

def createUnigramLanguageModel():
    global WordFrequencyDictionary
    global UnigramLanguageModel
    global TotalWords
    for key, value in WordFrequencyDictionary.items():
        UnigramLanguageModel[key] = (value/TotalWords)

def writeUnigramLanguageModelToFile(pFileName):
    global UnigramLanguageModel
    with open(pFileName,'w') as LM_File:
        for key in sorted(UnigramLanguageModel.keys()):
            LM_File.write(key + ": " + str(UnigramLanguageModel[key]) + "\n")
             
def writeFileToUnigramLanguageModel(pPath):
    Dictionary = dict()
    with open(pPath, 'r') as LM_File:
        lines = LM_File.readlines()
        for line in lines:
            line_sections = line.split(': ')
            Dictionary[line_sections[0]] = line_sections[1].strip()
    return Dictionary

def genere_LM(pRuta, pArchivoLM):
    clearGlobalVariables()
    getTextFromFilesInPath(pRuta,TEXT_MODE)
    createWordList()
    createLogicView()
    createWordFrequencyDictionary()
    createUnigramLanguageModel()
    writeUnigramLanguageModelToFile(pArchivoLM)
    print("Se guardó con éxito en",pArchivoLM,"el Modelo de Lenguaje Unigrama para la ruta",pRuta)

def opr(LM_específico, LM_general, Escalafón):
    Specific_LM = writeFileToUnigramLanguageModel(LM_específico)
    General_LM = writeFileToUnigramLanguageModel(LM_general)
    for key, value in Specific_LM.items():
        if key in General_LM:
            Rank[key] = float(value)/float(General_LM[key])
    OrderedRank = {key: value for key, value in sorted(Rank.items(), key=lambda item: item[1], reverse=True)}
    pos = 1
    with open(Escalafón,'w') as RankFile:
        RankFile.write("Posición,   Palabra,    Peso\n")
        for key, value in OrderedRank.items():
            RankFile.write(str(pos) + "- " + key + ": " + str(value) +"\n")
            pos+=1
    print("Se guardo con éxito en",Escalafón, "el Modelo de Lenguaje Unigrama comparativo entre", LM_específico, "y", LM_general)

def extraer_refs(RutaArchivo, ArchivoRefs):
    clearGlobalVariables()
    global HTMLTextFiles
    global ReferenceSet
    getTextFromFilesInPath(RutaArchivo,TAG_MODE)
    with open(ArchivoRefs,'w') as ReferenceFile:
        for html_file in HTMLTextFiles:
            for element in html_file.find_all('a', href=True):
                ReferenceSet.add(element['href'])
        for ref in ReferenceSet:
            ReferenceFile.write(ref + "\n")
    print("Se guardo con éxito en",ArchivoRefs,"las referencias del archivo html en la ruta",RutaArchivo)

## EXAMPLE PROGRAM CALLS
genere_LM('Geografia/', 'lm_geo')
genere_LM('Geografia/América/Estados_Soberanos/Costa_Rica.htm', 'lm_cr')
opr('lm_cr','lm_geo','opr_cr')
extraer_refs('Geografia/América/Estados_Soberanos/Costa_Rica.htm','refs_CR')
