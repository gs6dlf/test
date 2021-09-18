import shutil
import argparse
import re
import os


def var_index_find(var, var_name):
    k = 0
    for i in range(len(var)):
        if var[i]['var_name'] == var_name:
            return i
        k = k+1
    if k == len(var):
        print('error: %s not find' %var_name)
        return -1


parser = argparse.ArgumentParser(description="auto declare wire and reg")
parser.add_argument('--file_name','-f')
args = parser.parse_args()

file_name = args.file_name
shutil.copy(file_name,file_name+'.dec_bak')

var=[]
with open(file_name, "r", encoding="utf-8") as f1, open(file_name+'.tmp', "w", encoding="utf-8") as f2:
    for line in f1:
        var_type=''
        if re.match(r'[\s]*//.*',line) is None and re.search(r'//\s*<\w+.*>',line):
            s1 = re.search(r'//\s*<(.*)>',line)
            var_width = s1.group(1).split(',')
            if re.search(r'[\s]*\..*//.*',line):
                s2 = re.search(r'.*\((.*)\).*//.*',line)
                s2_sub = re.sub(r'[\s{}]','',s2.group(1))
                s2_sub = re.sub(r'\[.*?]','',s2_sub)
                var_type = 'wire'
            elif re.search(r'\s*assign.*',line):
                line_sub = re.sub(r'assign','',line)
                s2 = re.search(r'\s*(.*?)<?=.*//.*',line_sub)
                s2_sub = re.sub(r'[\s{}]','',s2.group(1))
                s2_sub = re.sub(r'\[.*?]','',s2_sub)
                var_type = 'wire'
            else:
                s2 = re.search(r'(\s+|:\s*)([a-z].*?)<?=.*//.*',line)
                s2_sub = re.sub(r'[\s{}]','',s2.group(2))
                s2_sub = re.sub(r'\[.*?]','',s2_sub)
                var_type = 'reg '
            var_name = s2_sub.split(',')
            if len(var_name) > 1 and len(var_width) != len(var_name) :
                print('error: %s, var num != <num>' % (s2_sub))
            elif len(var_name) == 1 and len(var_width) > 3 :
                print('error: %s, var num = 1, but <num> larger than 2' % (s2_sub))

            for i in range(len(var_name)):
                if len(var_name) == 1 and len(var_width) == 1:
                    var.append({'var_type':var_type, 'var_name':var_name[0], 'var_width':var_width[0]})
                elif len(var_name) == 1 and len(var_width) > 1:
                    var.append({'var_type': var_type, 'var_name': var_name[0], 'var_width': var_width})
                else:
                    var.append({'var_type':var_type, 'var_name':var_name[i], 'var_width':var_width[i]})

with open(file_name, "r", encoding="utf-8") as f1, open(file_name + '.tmp', "w", encoding="utf-8") as f2:
    flag = 0
    for line in f1:
        if flag == 1:
            if re.match(r'\s*//',line):
                flag = 0
                var_tmp = []
                for i in range(len(var)):
                    if var[i]['var_type'] == 'wire':
                        var_tmp.append(var[i])
                for i in range(len(var)):
                    if var[i]['var_type'] == 'reg ':
                        var_tmp.append(var[i])
                for i in range(len(var_tmp)):
                    if isinstance(var_tmp[i]['var_width'], list):
                        if var_tmp[i]['var_width'][0].isdigit():
                            index0 = '%d' % (int(var_tmp[i]['var_width'][0]) - 1)
                        else:
                            index0 = var_tmp[i]['var_width'][0] + '-1'
                        if var_tmp[i]['var_width'][1].isdigit():
                            index1 = '%d' % (int(var_tmp[i]['var_width'][1]) - 1)
                        else:
                            index1 = var_tmp[i]['var_width'][1] + '-1'
                        tmp = '%s [%s:0]' %(var_tmp[i]['var_type'], index1)
                        line_tmp = '{:<30}    {}[{}:0];\n'.format(tmp, var_tmp[i]['var_name'], index0)
                    else:
                        if var_tmp[i]['var_width'].isdigit():
                            index0 = '%d' % (int(var_tmp[i]['var_width']) - 1)
                        else:
                            index0 = var_tmp[i]['var_width'] + '-1'
                        tmp ='%s [%s:0]' %(var_tmp[i]['var_type'], index0)
                        line_tmp = '{:<30}    {};\n'.format(tmp, var_tmp[i]['var_name'])
                    f2.write(line_tmp)
                f2.write('////////////////\n')
            else:
                continue
        elif re.match(r'\s*input\s+', line):
            m=re.match(r'\s*input\s+(reg|wire)?\s*(\[.+])?\s*(\w+.*\n)',line)
            if m.group(2) is None:
                tmp = '    input wire'
            else:
                tmp = '    input wire %s' % m.group(2)
            line_tmp = '{:<30}    {}'.format(tmp, m.group(3))
            f2.write(line_tmp)
        elif re.match(r'\s*output\s+',line):
            m=re.match(r'\s*output\s+(reg|wire)?\s*(\[.+])?\s*(\w+)(.*\n)', line)
            index = var_index_find(var,m.group(3))
            if isinstance(var[index]['var_width'], list):
                if var[index]['var_width'][0].isdigit():
                    index0 = '%d' %(int(var[index]['var_width'][0]) - 1)
                else:
                    index0 = var[index]['var_width'][0]+'-1'
                if var[index]['var_width'][1].isdigit():
                    index1 = '%d' %(int(var[index]['var_width'][1]) - 1)
                else:
                    index1 = var[index]['var_width'][1] + '-1'
                tmp = '    output %s [%s:0]' %(var[index]['var_type'],index1)
                line_tmp = '{:<30}    {}[{}:0] {}'.format(tmp,var[index]['var_name'],index0,m.group(4))
            else:
                if var[index]['var_width'].isdigit():
                    index0 = '%d' %(int(var[index]['var_width']) - 1)
                else:
                    index0 = var[index]['var_width']+'-1'
                tmp ='    output %s [%s:0]' %(var[index]['var_type'],index0)
                line_tmp = '{:<30}    {} {}'.format(tmp,var[index]['var_name'],m.group(4))
            f2.write(line_tmp)
            var.pop(index)
        elif re.match(r'\s*//\s*auto_declare\s+',line):
            f2.write(line)
            flag = 1
        else:
            f2.write(line)

f1.close()
f2.close()
os.remove(file_name)
os.rename(file_name+'.tmp', file_name)
