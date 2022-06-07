import sys
import re

p = re.compile(r"\\n")
p2 = re.compile(r"\"(.*?)\"")

p3 = re.compile(r"^\W+.*$")
p4 = re.compile(r'^.*[©*°[@~>+£:<>/_“®{}+!#$%^&*()_].*$')
p5 = re.compile(r'^.*\s[es|ee|ew|ees|jee].*$')
p6 = re.compile(r'^.*\s[Se|Ae|Ie|Ue|Gs]\s*.*$')
for line in sys.stdin:
    line = line.rstrip()
    line = p.sub(' ', line)
    line = p2.sub(r'\1', line)
    if p3.match(line):
        line = ''
    if p4.match(line):
        line = ''
    if p5.match(line):
        line = ''
    if p6.match(line):
        line = ''
    if re.search(r'(\w)\1{2,}', line):
        line = ''
    if re.search(r'\d', line):
        line = ''
    if re.search(r'^[a-z]', line):
        line = ''
    if re.search(r"['\"]$", line):
        line = ''

    if len(line) > 0:
        print(line)
