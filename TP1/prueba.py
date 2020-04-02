import unicodedata

Dictionary = dict()
with open('prueba.txt') as archivo:
    var = archivo.readlines()
    for line in var:
        line_sections = line.split(': ')
        # print("Seccion 1:",line_sections[0])
        # print("Seccion 2:",line_sections[1])
        Dictionary[line_sections[0]] = line_sections[1].strip()
print(Dictionary)