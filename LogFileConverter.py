#!/usr/bin/python
import gzip
import re
import sys
import os.path

class InfileType:
    LOG = 0
    LOG_GZ = 1
    ASC = 2

if len(sys.argv) != 2:
    print("usage: ./LogFileConverter.py [filename.{log|log.gz|asc}]")
    sys.exit(0)

infile_name = sys.argv[1]

print("opening infile: " + infile_name)

if infile_name.endswith(".log.gz"):
    infile = gzip.open(infile_name, 'r')
    outfile_name = infile_name[0:-7] + '_new.log.gz'
    infile_type = InfileType.LOG_GZ
elif infile_name.endswith(".log"):
    infile = open(infile_name, 'r')
    outfile_name = infile_name[0:-4] + '_new.log.gz'
    infile_type = InfileType.LOG
elif infile_name.endswith('.asc'):
    infile = open(infile_name, 'r')
    outfile_name = infile_name[0:-4] + '_new.log.gz'
    infile_type = InfileType.ASC

print("opening outfile: " + outfile_name)

#check if outfile exists and prompt for overwrite
if os.path.exists(outfile_name):
    print("!file already exists")
    res = input("overwrite [Y|n]?")
    if not (res == 'y' or res == 'Y') and not res == '':
        infile.close()
        sys.exit(0)
try:
    outfile = gzip.open(outfile_name, 'w')
except:
    print("!could not open outfile")
    sys.exit(0)

# first run: collect header information
description_string = ''
description_found = 0
platform_string = ''
platform_found = False
device_aliases = []
content = []

# .log or .log.gz file format
if infile_type == InfileType.LOG or infile_type == InfileType.LOG_GZ:
    for line in infile:
        if infile_type == InfileType.LOG_GZ:
            line = line.decode('UTF-8')

        line = line[0:-1]
        if re.match('\([0-9]+\.[0-9]{6}\) [a-zA-Z0-9]{1,16} [A-Za-z0-9]{3,8}#[A-Fa-f0-9rR]+', line):
            content.append(line)

            #check if bus has a device alias
            bus_name = line.split(' ')[1]
            found = False
            for device_alias in device_aliases:
                if device_alias[1] == bus_name:
                    found = True
                    break

            if not found:
                device_aliases.append((bus_name, bus_name))
                print('adding alias for: ' + bus_name)

            continue
        elif re.match('DESCRIPTION "[a-zA-Z0-9\?\+\-\.\*\\/\(\)\[\]\s]+"', line):
            if description_found == 0:
                description_string = line[13:-1]
                print('single line description: ' + description_string)
                description_found = 2
            else:
                print('! multiple description definition!')
            continue
        elif re.match('DESCRIPTION "[a-zA-Z0-9\?\+\-\.\*\\/\(\)\[\]\s]+\Z', line):
            if description_found == 0:
                description_string = line[13:]
                description_found = 1
            else:
                print('! multiple description definition!')
            continue
        elif re.match('DESCRIPTION [a-zA-Z0-9\?\+\-\.\*\\/\(\)\[\]\s]+"', line):
            if description_found == 1:
                description_string += ' ' + line[12:-1]
                print('multi line description: ' + description_string)
                description_found = 2
            else:
                print('! multiple description definition!')
            continue
        elif re.match('DESCRIPTION [a-zA-Z0-9\?\+\-\.\*\\/\(\)\[\]\s]+', line):
            if description_found == 1:
                description_string += ' ' + line[12:]
            else:
                print('! multiple description definition!')
            continue
        elif re.match('PLATFORM [A-Z0-9_]+', line):
            if not platform_found:
                platform_string = line[9:]
                print('found platform: ' + platform_string)
            else:
                print('! duplicate platform definition. ignoring!')
            continue
        elif re.match('DEVICE_ALIAS [A-Za-z0-9]+ [a-z0-9]{1,16}', line):
            elements = line.split(' ')
            print('found device alias: ' + elements[1] + ' ' + elements[2])
            device_aliases.append((elements[1], elements[2]))
            continue
        elif re.match('EVENT \([0-9]+\.[0-9]{6}\) [a-z0-9]{1,16} "[:alnum::punct:]+"', line):
            content.append(line)
            continue
        else:
            print('! invalid line: ' + line)

#.asc infile format
elif infile_type == InfileType.ASC:
    for line in infile:
        line = line[0:-1]

        if re.match('\s+[0-9]+.[0-9]+\s+[0-9]\s+[a-fA-F0-9]+\s+[TxR]+\s+[d]\s+[0-8]\s+[0-9A-Fa-f\s]+' , line):
            elements = line.split()
            bus_name = 'can' + elements[1]
            newline = '(' + elements[0] +  ') ' + bus_name + ' ' + elements[2] + '#'
            for i in range(6, len(elements)):
                newline += elements[i]

            content.append(newline)

            found = False
            for device_alias in device_aliases:
                if device_alias[1] == bus_name:
                    found = True
                    break

            if not found:
                device_aliases.append((bus_name, bus_name))
                print('adding alias for: ' + bus_name)

infile.close()

#write header
if description_string != '':
    outfile.write(('DESCRIPTION "' + description_string + '"\n').encode("utf-8"))
else:
    outfile.write(('DESCRIPTION "' + 'converted log file' + '"\n').encode("utf-8"))

if platform_string != '':
    outfile.write(('PLATFORM ' + platform_string + '\n').encode("utf-8"))
else:
    outfile.write(('PLATFORM ' + 'NO_PLATFORM' + '\n').encode("utf-8"))


for device_alias in device_aliases:
    outfile.write(('DEVICE_ALIAS ' + device_alias[0] + ' ' + device_alias[1] + '\n').encode("utf-8"))

#copy content
for contentline in content:
    outfile.write((contentline + '\n').encode("utf-8"))

outfile.close()
