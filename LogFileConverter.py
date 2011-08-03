#!/usr/bin/python
import gzip
import re
import sys
import os.path

infile_name = sys.argv[1]

print("opening infile: " + infile_name)

if infile_name.endswith(".log.gz"):
    infile = gzip.open(infile_name, 'r')
    outfile_name = infile_name[0:-7] + '_new.log.gz'
    infile_type = '.log.gz'
elif infile_name.endswith(".log"):
    infile = open(infile_name, 'r')
    outfile_name = infile_name[0:-4] + '_new.log.gz'
    infile_type = '.log'

print("opening outfile: " + outfile_name)

#check if outfile exists and prompt for overwrite
if os.path.exists(outfile_name):
    print("!file already exists")
    res = input("overwrite [Y|n]?")
    if not (res == 'y' or res == 'Y') and not res == '':
        infile.close()
        sys.exit(0)

outfile = gzip.open(outfile_name, 'w')

# first run: collect header information
description_string = ''
description_found = 0
platform_string = ''
platform_found = False
device_aliases = []
content = []

for line in infile:
    if infile_type == '.log.gz':
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

infile.close()

#write header
outfile.write(bytes('DESCRIPTION "' + description_string + '"\n', 'UTF-8'))
outfile.write(bytes('PLATFORM ' + platform_string + '\n', 'UTF-8'))

for device_alias in device_aliases:
    outfile.write(bytes('DEVICE_ALIAS ' + device_alias[0] + ' ' + device_alias[1] + '\n', 'UTF-8'))

#copy content
for contentline in content:
    outfile.write(bytes(contentline + '\n', 'UTF-8'))

outfile.close()
