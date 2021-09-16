import re
import argparse

parser = argparse.ArgumentParser(description="auto instantiate")
parser.add_argument('--file_name','-f')
args = parser.parse_args()

#file_name = 'C:/Users/Administrator/Desktop/new.v'
file_name = args.file_name
file_inst = file_name+'.inst'

para = []
port = []
module_name = ''
with open(file_name, "r", encoding="utf-8") as f1:
    for line in f1:
        m = re.match(r'\s*module\s+(\w+).*',line)
        if m is not None:
            module_name = m.group(1)
            continue
            #print(name)

        m = re.match(r'\s*parameter\s+(\w+)\s*(\[.*])?\s*=\s*([\w\']+)',line)
        if m is not None:
            para.append({'para_name': m.group(1), 'para_def': m.group(3)})
            continue

        m = re.match(r'\s*(input)\s+(wire)?\s*(\[.*])?\s*(\w+)',line)
        if m is not None:
            port.append({'port_name': m.group(4), 'dir': 'input', 'width': None})
            #print(m.groups())
            continue

        m = re.match(r'\s*(output)\s+(wire|reg)?\s*(\[.*])?\s*(\w+)',line)
        if m is not None:
            tmp = m.group(3)
            if tmp is None:
                width = '1'
            else:
                tmp = re.sub(r'[\[\]\s]','',tmp)
                tmp = tmp.split(':')
                tmp = tmp[0]
                if tmp.isdigit():
                    width = '%d' %(int(tmp)+1)
                elif re.match(r'(.*)-1',tmp):
                    m_tmp = re.match(r'(.*)-1',tmp)
                    width = m_tmp.group(1)
                else:
                    width = tmp+'+1'

            port.append({'port_name': m.group(4), 'dir': 'output', 'width': width})
            continue
            #print(m.groups())
f1.close()
with open(file_inst, "w", encoding="utf-8") as f2:
    if len(para) == 0:
        f2.write('%s %s_U0(\n' %(module_name, module_name))
    else:
        f2.write('%s %s_U0 #(\n' %(module_name, module_name))
        for i in range(len(para)):
            if i != len(para)-1:
                f2.write('\t.%s(%s),\n' %(para[i]['para_name'], para[i]['para_def']))
            else:
                f2.write('\t.%s(%s)\n' %(para[i]['para_name'], para[i]['para_def']))
        f2.write('\t)(\n')
    for i in range(len(port)):
        if i != len(port)-1:
            if port[i]['dir'] == 'output':
                f2.write('\t.%s(%s), //<%s>\n' %(port[i]['port_name'], port[i]['port_name'], port[i]['width']))
            else:
                f2.write('\t.%s(%s),\n' %(port[i]['port_name'], port[i]['port_name']))
        else:
            if port[i]['dir'] == 'output':
                f2.write('\t.%s(%s) //<%s>\n' %(port[i]['port_name'], port[i]['port_name'], port[i]['width']))
            else:
                f2.write('\t.%s(%s)\n' %(port[i]['port_name'], port[i]['port_name']))
    f2.write('\t);\n')
f2.close()