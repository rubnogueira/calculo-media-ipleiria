# -*- coding: latin-1 -*-

import re
from random import randint

try:
    import requests
except ImportError:
    print("Instale o modulo requests.\nUsage: python -m pip install requests")
    exit(1)
    
s = requests.Session()
USERAGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'
USERNAME = input("Introduza o seu numero de utilizador: ")
PASSWORD = input("Introduza a sua password: ")

def login():
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Host': 'estudantes.ipleiria.pt',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': USERAGENT}

    info = s.get('http://estudantes.ipleiria.pt/AreaPessoal',headers=headers).text
    if check_login(info):
        endpoint = re.compile('action="(.+?)"').findall(info)[0]

        data = {'__EVENTTARGET': '', 
        '__EVENTARGUMENT': '',
        '__VIEWSTATE': re.compile('<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="(.+?)" />').findall(info)[0],
        '__EVENTVALIDATION': re.compile('<input type="hidden" name="__EVENTVALIDATION" id="__EVENTVALIDATION" value="(.+?)" />').findall(info)[0],
        'ctl00$AuthenticationFormPlaceHolder$LoginForm$Username': USERNAME,
        'ctl00$AuthenticationFormPlaceHolder$LoginForm$Password': PASSWORD,
        'ctl00$AuthenticationFormPlaceHolder$LoginForm$ButtonLogin.x': randint(0,10),
        'ctl00$AuthenticationFormPlaceHolder$LoginForm$ButtonLogin.y': randint(0,10)}

        info = s.post('http://estudantes.ipleiria.pt/_layouts/Usi.IPLeiria.CustomPages/' + endpoint,headers=headers,data=data).text
        if check_login(info):
            print("Login falhou")
            exit(1)
            return False
        else:
            print("Login OK")
            return True
    else:
        return True


def check_login(content):
    if "login-panel" in content:
        return True
    else:
        return False

def start_capture():
    mygrades = []
    allcourse = []
    
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Host': 'estudantes.ipleiria.pt',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': USERAGENT}

    info = s.get('http://estudantes.ipleiria.pt/AreaPessoal/Pages/historicoavaliacoes.aspx',headers=headers).text

    if check_login(info):
        login()
        info = s.get('http://estudantes.ipleiria.pt/AreaPessoal/Pages/historicoavaliacoes.aspx',headers=headers).text

    try:
        course = re.compile('"_text":"(.+?)"').findall(info)[0]
        course = course.split(' - ')
        courseid = course[0]
        course.pop(0)
        course = ' - '.join(course)
    except:
        course = ''
        courseid = ''

    temp = re.compile('<tbody>(.+?)</tbody>').findall(info.replace('\n','').replace('\r','').replace('\t',''))[0]

    for x in re.compile('<tr.+?>(.+?)</tr>').findall(temp):
        item = {}
        raw = re.compile('<td title="(.+?)"').findall(x)
        item['name'] = raw[0]
        item['year'] = raw[1]
        #item['period'] = raw[2]
        item['grade'] = raw[3]
        #item['done'] = raw[4]
        mygrades.append(item)
        

    course_link = all_courses(course,courseid)
    if course_link:
        uclink = s.get(course_link,headers=headers).text
        temp = re.compile('<h3>Plano curricular</h3>(.+?)</article>').findall(uclink.replace('\n','').replace('\r','').replace('\t',''))[0]

        for x in re.compile('<tr>(.+?)</tr>').findall(temp):
            item = {}
            
            for y,z in re.compile('<td(.+?)>(.+?)</td>').findall(x):
                if 'curricular_plan_cu_code' in y: item['number'] = z
                elif 'curricular_plan_cu_title' in y: item['name'] = z
                elif 'curricular_plan_cu_ects' in y: item['ects'] = z
                elif 'curricular_plan_cu_duration' in y: item['duration'] = z

            if item:
                item['grade'] = 0
                item['year'] = 0

                for i in mygrades:
                    if i['name'].lower() == item['name'].lower():
                        item['grade'] = i['grade']
                        item['year'] = i['year']
                        
                allcourse.append(item)

        #### verificacao das notas para media

        ects = {}
        for i in allcourse:
            if int(i['grade']) >= 10:
                print("%s ano - %s: %s valores" % (i['year'],i['name'],i['grade']))

                if i['year'] not in ects:
                    ects[i['year']] = {}
                    ects[i['year']]['totalects'] = 0
                    ects[i['year']]['totalvalue'] = 0

                ects[i['year']]['totalects'] += int(i['ects'])
                ects[i['year']]['totalvalue'] += float(int(i['grade']) * int(i['ects']))

        print("\n")

        totalmedia = 0
        totalyears = 0
        
        for i in ects.keys():
            media = float(ects[i]['totalvalue'] / ects[i]['totalects'])
            print("Media %s ano: %.2f valores" % (str(i),media))

            totalmedia += media
            totalyears += 1

        print("Média Global: %.2f valores" % (float(totalmedia/totalyears)))
        
    else:
        print("Lista de UCs não encontrada :(")
    

def all_courses(course,courseid):
    print("A procurar código de curso...")
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Host': 'estudantes.ipleiria.pt',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': USERAGENT}

    info = s.get('https://www.ipleiria.pt/cursos/course/type/licenciatura/',headers=headers).text

    regex = '<a class="link block noicon" title="(.+?)" href="(.+?)">'

    #Caso o nome coincida
    for x,y in re.compile(regex).findall(info):
        if course == x:
            return y

    #Tentar encontrar o codigo do curso
    for x,y in re.compile(regex).findall(info):
        temp = s.get(y,headers=headers).text

        pattern = re.compile('<h3>Código curso</h3><div >(.+?)</div>').findall(temp)[0]
        if courseid in pattern:
            return y
        
    return None
    
if __name__ == "__main__":
    start_capture()
