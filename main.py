import psycopg2
from config import API_KEY,SECRET_KEY
from tinkoff_voicekit_client import ClientSTT
from time import strftime
from os import remove


client=ClientSTT(API_KEY, SECRET_KEY)

name_audio=input('Введите имя wav файла: ')
number=input('Введите номер телефона: ')
call_db=input('Хотите чтобы произошла запись в базу данных? 1-да 0-нет: ')

audio_config={
    "encoding": "LINEAR16",
    "sample_rate_hertz": 8000,
    "num_channels": 1
}

# идентификациоонный номер
with open('log.log','rt') as num:
    id_num=len(num.readlines())
#    print(id_num)

# recognise method call
response=client.recognize(name_audio+'.wav',audio_config)
#print(response)
d=dict(response[0])['alternatives'][0].get('transcript')
print('Текст из файла: '+d)
s='автоответчик'
negative_word=['нет','неудобно']
good_word=['говорите','да кончено']
l=[]
date=strftime('%Y%m%d')
time=strftime('%H%M%S')
l.append(date)
l.append(time)
l.append(str(id_num))
# если в аудио записи распознан автоответчик возвращает 0, если человек возвращает 1.
if set(s.split()) & set(d.split()):
    print('Распознан автоответчик 0')
    l.append('0')
else:
    print('Распознан человек 1')
    l.append('1')
# если в ответе есть отрицательные слова (“нет”, “неудобно” и т.п.), то возвращает 0, если положительные (“говорите”, “да конечно” и т.п.) то возвращает 1.
if set(negative_word) & set(d.split()):
    print('В ответе отрицательное слово 0')
    l.append('0')
else:
    print('В ответе пложительное слово 1')
    l.append('1')

l.append(number)
end_time=dict(response[len(response)-1])['end_time']
l.append(end_time)
print(end_time)
l.append(d)
f=open('log.log','at')
print(l,file=f)
f.close()
#print(l)
if call_db == '0':
    print('Не надо БД')
elif call_db == '1':
    print('Надо БД')
    conn=psycopg2.connect(dbname='database',user='postgres', password='password', host='localhost')
    cursor=conn.cursor()
    cursor.execute("INSERT into db (id,date,time,ao_human,plus_minus,number,end_time,text) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s')"%(l[2],l[0],l[1],l[3],l[4],l[5],l[6][0:-1],l[7]))
    conn.commit()
remove(name_audio+'.wav')
