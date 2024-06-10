#!/usr/bin/env python
# coding: utf-8

# # **Парсер для LMS Moodle**

# # Библиотеки

# In[1]:


import xml.etree.ElementTree as ET
import psycopg2

import os
from os import _exit
import shutil

import tarfile

from flask import Flask, request, redirect, url_for

import re

from pytube import YouTube
import datetime


# # Разархивация backup файла

# In[2]:


def unzipping_backup_file(path_to_backup_file):
    backup_file = None
    
    if not os.path.exists(path_to_backup_file):
            os.makedirs(path_to_backup_file)
    
    # находим файл со случайным названием, начинающимся на "backup" в папке "folder/"
    for file in os.listdir(path_to_backup_file):
        if file.startswith("backup") and file.endswith(".mbz"):
            backup_file = file
            #break
    
    if backup_file:
        # создаем директорию для разархивированных файлов, если ее нет
        if not os.path.exists("backup/"):
            os.makedirs("backup/")
    
        # разархивируем первый файл
        with tarfile.open(path_to_backup_file + backup_file, "r:gz") as tar:
            tar.extractall("backup/")
    
        # находим внутренний файл в разархивированной папке
        inner_file = None
        for file in os.listdir("backup/"):
            if file.endswith(".tar.gz"):
                inner_file = file
                break
    
        if inner_file:
            # разархивируем внутренний файл
            with tarfile.open("backup/" + inner_file, "r:gz") as tar:
                tar.extractall("backup/")

    return backup_file

if_unzipping_backup_file_exists = unzipping_backup_file("moodle_backup_file/")


# # Базовые функции для работы с XML файлами

# Указываем путь к папке backup

# In[3]:


def get_path_to_backup_file():
    file = r'C:/Users/Eugene/Parser-Moodle/backup/'

#get_path_to_backup_file()


# возврат путей xml файлов

# In[4]:


def activities_directories ():
    file = "backup/moodle_backup.xml"
    direct = []
    directory = find_by_tag(file,"directory")
    modulename = find_by_tag(file,"modulename")
    for i in range( len(modulename) ):
        text_dir = "backup/" + directory[i] + "/" + modulename[i] + ".xml"
        direct.insert(i, text_dir)
    return direct


# возварт текста по тегу

# In[5]:


def find_by_tag (file, tag):
    tree = ET.parse(file)
    root = tree.getroot()
    res = ""
    for text_in_root in root.iter(tag):
        res += str(text_in_root.text)
        res += "\n"
    listRes = list(res.split("\n"))
    listRes.pop( len(listRes)-1 )
    return listRes


# возварт текста по тегу из конкретного вложенного тега

# In[6]:


def find_by_tag_from_tag (file, where, tag):
    tree = ET.parse(file)
    root = tree.getroot()
    res = ""
    for text_in_root in tree.findall(".//" + where + "/" + tag):
        res += str(text_in_root.text)
        res += "\n"
    listRes = list(res.split("\n"))
    listRes.pop( len(listRes)-1 )
    return listRes


# возварт аррибута по тегу

# In[7]:


def find_ID_attrib_by_tag (file, tag):
    tree = ET.parse(file)
    root = tree.getroot()
    res = ""
    for text_in_root in root.iter(tag):
        symbols_to_remove = "{}id:' "
        res += remove_symbols(symbols_to_remove, str( text_in_root.attrib ))
        res += "\n"
    listRes = list(res.split("\n"))
    listRes.pop( len(listRes)-1 )
    return listRes


# возврат всего файла

# In[8]:


"""def read_all(file):
    tree = ET.parse(file)
    s = ET.dump(tree)
    return s"""

def read_all(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = file.read()
            data = remove_symbols('\n', data)
        return data
    except FileNotFoundError:
        return "File not found"


# замена конкретной последовательности символов

# In[9]:


def replace_symbols(text, old_word, new_word):
    new_s = text.replace(old_word, new_word)
    return new_s


# удаление конкретных символов

# In[10]:


def remove_symbols(symbols_to_remove, text):
    for symbol in symbols_to_remove:
        text = text.replace(symbol, "")
    return text


# удаление последнего символа

# In[11]:


def remove_last_symbol(text):
    result_string = ""
    index = len(text)
    for i in range(index-1):
        result_string += text[i]
    return result_string


# удаление символов sql

# In[12]:


def remove_sql_symbol(text_):
    text = str(text_)
    symbols_to_remove = "(, )[]"
    for symbol in symbols_to_remove:
        text = text.replace(symbol, "")
    return text


# возврат contextid из xml фалов

# In[13]:


def find_contextid_in_activity(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    contextids = []
    
    for activity in root.iter('activity'):
        contextid = activity.get('contextid')
        if contextid is not None:
            contextids.append(contextid)
    
    return contextids

#find_contextid_in_activity('backup/activities/resource_6/resource.xml')


# функция help

# In[14]:


def help():
    stars = "||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||\n"
    res = stars
    res += "Функция all_files_read() считывает все данные файлов, помещенных в папку backup\n"
    res += "Общий массив имеет следующую структуру:\n"
    
    res += "[\n"
    res += "  ['названия ресурсов'] в виде строк,\n"
    res += "  ['типы ресурсов'] в виде строк,\n"
    res += "  ['ссылки на ресурсы'] в виде строк,\n"
    res += "    [\n"
    res += "      [массив ресурса 1], [массив ресурса 2], [массив ресурса 3]... \n"
    res += "    ]\n"
    res += "]\n"

    #res = ""
    res += stars
    res += "Ресурс PAGE имеет следующую структуру массива:\n"
    res += "[\n"
    res += "  'название ресурса',\n"
    res += "  ['строка 1', 'строка 2', 'строка 3', 'строка 4'...]\n"
    res += "]\n"

    #res = ""
    res += stars
    res += "Ресурс CHOICE имеет следующую структуру массива:\n"
    res += "[\n"
    res += "  'название ресурса',\n"
    res += "  ['вопрос (строка) 1', 'вопрос 2', 'вопрос 3', 'вопрос 4'...],\n"
    res += "  ['ответ (число в виде строки) 1', 'ответ 2', 'ответ 3', 'ответ 4'...]\n"
    res += "]\n"

    #res = ""
    res += stars
    res += "Ресурс BOOK имеет следующую структуру массива:\n"
    res += "[\n"
    res += "  'название ресурса',\n"
    res += "  ['глава (строка) 1', 'глава 2', 'глава 3'...],\n"
    res += "  [\n"
    res += "    ['строка главы 1', 'строка главы 1', 'строка главы 1'...], \n"
    res += "    ['строка главы 2', 'строка главы 2', 'строка главы 2'...], \n"
    res += "    ['строка главы 3', 'строка главы 3', 'строка главы 3'...] \n"
    res += "  ]\n"
    res += "]\n"

    #res = ""
    res += stars
    res += "Ресурс FEEDBACK имеет следующую структуру массива:\n"
    res += "[\n"
    res += "  'название ресурса',\n"
    res += "  ['вопрос 1', 'вопрос 2', 'вопрос 3'...],\n"
    res += "  ['вариат ответа на ворос 1', 'вариат ответа на ворос 1', 'вариат ответа на ворос 1'...], \n"
    res += "  ['вариат ответа на ворос 2', 'вариат ответа на ворос 2', 'вариат ответа на ворос 2'...], \n"
    res += "  ['вариат ответа на ворос 3', 'вариат ответа на ворос 3', 'вариат ответа на ворос 3'...] \n"
    res += "]\n"

    #res = ""
    res += stars
    res += "Ресурс SURVEY имеет следующую структуру массива:\n"
    res += "[\n"
    res += "  'название ресурса',\n"
    res += "  ['номер вороса из банка вопросов', 'номер вороса из банка вопросов'...]\n"
    res += "]\n"

    #res = ""
    res += stars
    res += "Ресурс FORUM имеет следующую структуру массива:\n"
    res += "[\n"
    res += "  'название ресурса',\n"
    res += "  ['id комментария', 'id комментария, на который идет ответ', 'id пользователя, оставившего комментарий', 'текст комментария'],\n"
    res += "  ['id комментария', 'id комментария, на который идет ответ', 'id пользователя, оставившего комментарий', 'текст комментария']\n"
    res += "]\n"

    #res = ""
    res += stars
    res += "Ресурс SCHEDULER имеет следующую структуру массива:\n"
    res += "[\n"
    res += "  'название ресурса',\n"
    res += "  ['id записи', 'id учителя', 'время начала в Unixtime', 'продолжительность в минутах', 'заметки'],\n"
    res += "  ['id записи', 'id учителя', 'время начала в Unixtime', 'продолжительность в минутах', 'заметки']\n"
    res += "]\n"

    #res = ""
    res += stars
    res += "Ресурс QUIZ имеет следующую структуру массива:\n"
    res += "[\n"
    res += "  'название ресурса',\n"
    res += "  ['номер вороса в квизе', 'id вопроса из банка вопросов', 'баллы за правильный ответ'],\n"
    res += "  ['номер вороса в квизе', 'id вопроса из банка вопросов', 'баллы за правильный ответ']\n"
    res += "]\n"

    res += stars
    return res 
#print( help() )


# # Функции чтения отдельных XML файлов ресурсов

# чтение page

# In[15]:


def page_read (file):
    all_content = []
    
    title = remove_symbols("[]'", str(find_by_tag_from_tag(file, "page", "name")))
    strings_arr = find_by_tag(file, "content")

    #all_content.append( title )
    all_content.append( strings_arr )

    new_page = replace_symbols(remove_symbols("[]'", str(all_content)), '>, <', '> <' )
    
    return new_page

#page_read("backup/activities/page_3/page.xml")


# чтение choice

# In[16]:


def choice_read (file):
    all_content = []
    
    title = remove_symbols("[]'", str(find_by_tag_from_tag(file, "choice", "name")))
    text = find_by_tag(file, "text")
    count = find_by_tag(file, "maxanswers")

    #all_content.append( title )
    #all_content.append( text )
    #all_content.append( count )
    new_choice = remove_symbols("[]'", str(text))
    return new_choice

#choice_read("backup/activities/choice_4/choice.xml")


# чтение book

# In[17]:


def book_read (file):
    all_content = []
    book_content = []
    name = remove_symbols("'[]", str( find_by_tag(file, "name") ) )
    title = find_by_tag(file, "title")

    for i in range( len(title) ):
        chap = "chapter[" + str(i+1) + "]"
        content = find_by_tag_from_tag(file, chap, "content")
        book_content.append(content)
    
    #all_content.append(name)
    all_content.append(title)
    all_content.append(book_content)

    new_content = ""
    for index in range( len(title) ):
        new_content += "<h1>"
        new_content += str(all_content[0][index])
        new_content += "</h1>"
        new_content += remove_symbols("[]'", str(all_content[1][index]))
        
    new_content = replace_symbols(new_content, '>, <', '> <' )
    new_content = replace_symbols(new_content, '><', '> <' )
    
    return new_content
    
#book_read("backup/activities/book_9/book.xml")


# чтение feedback

# In[18]:


def feedback_read (file):
    all_content = []
    new_parts = []
    questions = find_by_tag_from_tag(file, "item", "name")
    answers = []
    title = remove_symbols("[]'", str(find_by_tag_from_tag(file, "feedback", "name")))

    arr_content = find_by_tag(file, "presentation")
    str_content = ''.join(arr_content)
    parts = str_content.rsplit('>>>>>')
    parts.pop(0)

    #all_content.append( title )

    #убираем последний символ
    for i in range ( len(parts) ):
        if i != len(parts)-1:
            new_parts.append( remove_last_symbol(parts[i]) )
        else:
            new_parts.append( parts[i] )

    questions = replace_symbols(remove_symbols("[]'", str(questions)), '>, <', '> <' )
    all_content.append(questions)
    
    #разделяем строки по разделителям
    for i in range ( len(parts) ):
        new = new_parts[i].rsplit('|')

        new = replace_symbols(remove_symbols("'", str(new)), '>, <', '> <' )
        
        answers.append(new)

    answers = replace_symbols(remove_symbols("'", str(answers)), '>, <', '> <' )
    answers = replace_symbols(answers, '[[', '[' )
    answers = replace_symbols(answers, ']]', ']' )
    all_content.append(answers)
    
    return all_content
    
#feedback_read("backup/activities/feedback_7/feedback.xml")[1]


# чтение survey

# In[19]:


def survey_read (file):
    all_content = []
    
    questions = find_by_tag(file, "questions")
    str_content = ''.join(questions)
    parts = str_content.rsplit(',')
    name = remove_symbols("[]'", str(find_by_tag_from_tag(file, "survey", "name")))

    #all_content.append(name)
    all_content.append(parts)

    new_survey = remove_symbols("[]'", str(all_content))
    
    return new_survey
#survey_read("backup/activities/survey_8/survey.xml")


# чтение forum

# In[20]:


def forum_read (file):
    all_content = []
    comment = []

    forum_title = remove_symbols("[]'", str(find_by_tag_from_tag(file, "discussion", "name")))

    comment_id = find_ID_attrib_by_tag(file, "post")
    parent = find_by_tag(file, "parent")
    userid = find_by_tag(file, "userid")
    message = find_by_tag(file, "message")

    #all_content.append( forum_title )
    
    for i in range ( len(find_by_tag(file, "parent")) ):
        #id комментария // id комментария, на который идет ответ // id пользователя, оставившего комментарий // текст комментария
        comment = []
        comment.append( comment_id[i] )
        comment.append( parent[i] )
        comment.append( userid[i] )
        comment.append( message[i] )
        all_content.append( comment )
    
    return all_content
#forum_read("backup/activities/forum_1/forum.xml")


# чтение scheduler

# In[21]:


def scheduler_read (file):
    all_content = []
    slot = []

    name = remove_symbols("[]'", str(find_by_tag_from_tag(file, "scheduler", "name")))
    slot_id = find_ID_attrib_by_tag(file, "slot")
    teacherid = find_by_tag(file, "teacherid")
    start_time = find_by_tag(file, "starttime")
    duration = find_by_tag(file, "duration")
    notes = find_by_tag(file, "notes")

    #all_content.append( name )

    for i in range( len(slot_id) ):
        #id записи // id учителя // время начала в Unixtime  // продолжительность в минутах // заметки
        slot = []
        slot.append( slot_id[i] )
        slot.append( teacherid[i] )
        slot.append( start_time[i] )
        slot.append( duration[i] )
        slot.append( notes[i] )

        all_content.append( slot )

    #new_scheduler = replace_symbols(remove_symbols("[]'", str(all_content)), '>, <', '> <' )
    
    return all_content
#scheduler_read("backup/activities/scheduler_5/scheduler.xml")


# чтение quiz

# In[22]:


def quiz_read (file):
    all_content = []
    slot = []

    name = remove_symbols("[]'", str(find_by_tag_from_tag(file, "quiz", "name")))
    question_instance = find_ID_attrib_by_tag(file, "question_instance")
    questionbankentryid = find_by_tag(file, "questionbankentryid")
    maxmark = find_by_tag(file, "maxmark")

    #all_content.append( name )
    
    for i in range( len(question_instance) ):
        #номер вороса в квизе // id вопроса из банка вопросов // баллы за правильный ответ
        slot = []
        #slot.append( question_instance[i] )
        slot.append( questionbankentryid[i] )
        #slot.append( maxmark[i] )

        all_content.append( slot )

        new_quiz = remove_symbols("[]'", str(all_content))
    
    return new_quiz
#quiz_read("backup/activities/quiz_12/quiz.xml")


# чтение glossary

# In[23]:


def glossary_read (file):
    all_content = []
    slot = []
    
    concept = find_by_tag_from_tag(file, "entry", "concept")
    definition = []
    #definition = find_by_tag_from_tag(file, "entry", "definition")

    tree = ET.parse(file)
    root = tree.getroot()
    
    for elem in root.iter('definition'):
        text = elem.text
        text = text.replace('\n', ' ')  # заменяем символ переноса строки на пробел
        definition.append( text )

    for index in range( len(concept) ):
        slot = []
        slot.append( concept[index] )
        slot.append( definition[index] )
        all_content.append( slot )

    return all_content

#glossary_read("backup/activities/glossary_26/glossary.xml")[2]


# чтение банка воросов

# In[24]:


"""
# чтение банка воросов
def bank_questions_read (file):
    all_conntant = []
    name = find_by_tag_from_tag(file, "question", "name")
    questiontext = find_by_tag_from_tag(file, "question", "questiontext")
    question_id = find_ID_attrib_by_tag(file, "question")

    for i in range( len(name) ):
        content = []
        content.append(question_id[i])
        content.append(name[i])
        content.append(questiontext[i])
        all_conntant.append(content)
    
    return all_conntant

#bank_questions_read("backup/questions.xml
"""


# # Функции чтения всех файлов

# чтение всех видов файлов

# In[25]:


def read_file (file):
    s = file
    parts = s.rsplit('/')
    res = parts[3]
    
    if res == "page.xml" :
        return page_read (file)
    elif res == "choice.xml" :
        return choice_read (file)
    elif res == "book.xml" :
        return book_read (file)
    elif res == "feedback.xml" :
        return feedback_read (file)
    elif res == "survey.xml" :
        return survey_read (file)
    elif res == "forum.xml" :
        return forum_read (file)
    elif res == "scheduler.xml" :
        return scheduler_read (file)
    elif res == "quiz.xml" :
        return quiz_read (file)
    elif res == "glossary.xml" :
        return glossary_read (file)


# чтение всего backup файла

# In[26]:


def all_files_read ():
    if if_unzipping_backup_file_exists != None:
        all_content = []
        titles = find_by_tag_from_tag("backup/moodle_backup.xml", "activity", "title")
        types = find_by_tag("backup/moodle_backup.xml", "modulename")
        ids = find_by_tag("backup/moodle_backup.xml", "moduleid")
        #urls = []
        #contents = []
        dirs = activities_directories()
        
        for i in range ( len(dirs) ):
            file = []
            urls = ""
            
            contents = read_file(dirs[i])
            orig_url = str( find_by_tag("backup/moodle_backup.xml", "original_wwwroot") )
    
            #формирование ссылки
            symbols_to_remove = " '[] "
            orig_url = remove_symbols(symbols_to_remove, orig_url)
            urls = orig_url + "/mod/" + types[i] + "/view.php" +  "?id=" + ids[i]
    
            file.append( urls )
            file.append( dirs[i] )
            file.append( types[i] )
            file.append( titles[i] )
            file.append( contents )
            contextid = find_contextid_in_activity(dirs[i])[0]
            file.append( contextid )
            file.append( i+1 )
            all_content.append( file )
    
        #all_content.append(titles)
        #all_content.append(types)
        #all_content.append(urls)
        #all_content.append(contents)
        return all_content
    else:
        return 'Поместите backup-файл в папку moodle_backup_file и перезапустите программу'

#all_files_read()[5]


# # Работа с файлами

# чтение информации о файлах

# In[27]:


def files_read (file):
    all_content = []
    slot = []

    contenthash = find_by_tag(file, "contenthash")
    filename = find_by_tag(file, "filename")
    contextid = find_by_tag(file, "contextid")

    for i in range( len(contenthash) ):
        if filename[i] != '.':
            resource_id = ''
            for j in range ( len(all_files_read()) ):
                if contextid[i] == all_files_read()[j][5]:
                    resource_id = j+1
                
            slot = []
            slot.append( contenthash[i] )
            slot.append( filename[i] )
            #slot.append( contextid[i] )
            slot.append( resource_id )
    
            all_content.append( slot )
    
    return all_content
    
#files_read("backup/files.xml")
#all_files_read()[5]


# вывод информации о файлах

# In[28]:


def files_creation_and_information():
    # Функция для переименования и копирования файлов
    def rename_and_copy_files(file_info):
        new_files_info = []
        for info in file_info:
            initial_name = info[0]
            new_name = info[1]
            additional_info = info[2]
    
            for root, dirs, files in os.walk('backup/files'):
                for file in files:
                    if file == initial_name:
                        source_path = os.path.join(root, file)
                        destination_path = os.path.join('backup/new_files', new_name)
    
                        shutil.copy2(source_path, destination_path)
                        new_files_info.append([destination_path, additional_info])
    
        return new_files_info
    
    # Массив со структурой [начальное название файла, новое название файла, дополнительная информация о файле]
    file_info = files_read("backup/files.xml")
    
    # Проверяем, что папка new_files существует, если нет - создаем
    if not os.path.exists('backup/new_files'):
        os.makedirs('backup/new_files')
    
    # Вызываем функцию и сохраняем результат
    new_files_info = rename_and_copy_files(file_info)
    
    # Выводим результат
    return new_files_info

#files_creation_and_information()


# # Базовые функции для работы с БД

# данные для авторизации в БД

# In[29]:


#from config import host, user, password, db_name
"""
host = "127.0.0.1"
user = "postgres"
password = "qwerty"
db_name = "test"
"""


# функция для SQL запросов

# In[30]:


#функция для SQL запросов
def sql(SQL_text):
    try:
        # connect to exist database
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name    
        )
        connection.autocommit = True
        
        # the cursor for perfoming database operations
        # cursor = connection.cursor()
        
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT version();"
            )
            #print(f"Server version: {cursor.fetchone()}")
            res = cursor.fetchall()
            
        # create a new table
        with connection.cursor() as cursor:
             cursor.execute( SQL_text )
             res = cursor.fetchall()
            
             #connection.commit()
             #print("[INFO] Successfully")
        
    except Exception as _ex:
        #Error while working with PostgreSQL
        print("[INFO] ", _ex)
    finally:
        if connection:
            # cursor.close()
            connection.close()
            #print("[INFO] PostgreSQL connection closed")
    return res

#sql("SELECT version();")


# In[31]:


def get_schema_name():
    schema_name = "edu."
    return schema_name

SN = get_schema_name()


# функция для просмотра содержимого таблиц

# In[32]:


def show_tables(host, user, password, db_name, table):
    all_ = ""
    
    conn = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        dbname=db_name
    )
    cur = conn.cursor()

    cur.execute(f"SELECT table_name FROM information_schema.tables WHERE table_schema='{remove_last_symbol(SN)}';")
    tables = cur.fetchall()

    """
    for table in tables:
        table_name = table[0]
        all_ += f"Table: {table_name}"
        all_ += '<br>'
        cur.execute(f"SELECT * FROM {SN}{table_name};")
        rows = cur.fetchall()
        for row in rows:
            all_ += str(row)
            all_ += '<br>'

        all_ += '<br>'
    """
    all_ += f"Table: {table}"
    all_ += '<br>'
    cur.execute(f"SELECT * FROM {SN}{table};")
    rows = cur.fetchall()
    for row in rows:
        all_ += remove_symbols( "'", str(row) )
        all_ += '<br>'

    all_ += '<br>'

    conn.close()
    return all_
    
#show_tables(host, user, password, db_name)


# функция удаления всех таблиц

# In[33]:


def delete_all_tables():
    # Устанавливаем соединение с базой данных
    conn = psycopg2.connect(
        host=host,
        user=user,
        password=password,
        database=db_name
    )
    cur = conn.cursor()

    # Получаем список всех таблиц в базе данных
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
    tables = [table[0] for table in cur.fetchall()]

    # Удаляем каждую таблицу из списка
    for table in tables:
        cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE")

    conn.commit()
    conn.close()


#delete_all_tables()


# # Создание таблиц

# In[34]:


def creation_main_tables( create_or_drop ):
    
    create = """
    -- edu.file_type определение
    
    -- Drop table
    
    -- DROP TABLE edu.file_type;
    
    CREATE TABLE edu.file_type (
    	id serial4 NOT NULL,
    	"name" varchar NULL,
    	"extension" varchar NULL,
    	CONSTRAINT file_type_pk PRIMARY KEY (id)
    );
    
    
    -- edu.lms определение
    
    -- Drop table
    
    -- DROP TABLE edu.lms;
    
    CREATE TABLE edu.lms (
    	id serial4 NOT NULL,
    	"name" varchar NOT NULL,
    	CONSTRAINT lms_pk PRIMARY KEY (id)
    );
    
    
    -- edu.lms_resource_type определение
    
    -- Drop table
    
    -- DROP TABLE edu.lms_resource_type;
    
    CREATE TABLE edu.lms_resource_type (
    	id serial4 NOT NULL,
    	"name" varchar NOT NULL,
    	CONSTRAINT lms_resource_type_pk PRIMARY KEY (id)
    );
    
    
    -- edu.resource определение
    
    -- Drop table
    
    -- DROP TABLE edu.resource;
    
    CREATE TABLE edu.resource (
    	id bigserial NOT NULL,
    	url varchar NULL,
    	"name" varchar NULL,
    	description text NULL,
    	tags json NULL,
    	CONSTRAINT edu_resource_pk PRIMARY KEY (id)
    );
    
    
    -- edu.comment_resource определение
    
    -- Drop table
    
    -- DROP TABLE edu.comment_resource;
    
    CREATE TABLE edu.comment_resource (
    	id bigserial NOT NULL,
    	replied_comment_id int8 NULL,
    	user_id int8 NOT NULL,
    	"text" text NULL,
    	resource_id int8 NOT NULL,
    	CONSTRAINT comment_resource_pk PRIMARY KEY (id),
    	CONSTRAINT comment_resource_resource_fk FOREIGN KEY (resource_id) REFERENCES edu.resource(id) ON DELETE RESTRICT ON UPDATE CASCADE
    );
    
    
    -- edu.edu_announcment определение
    
    -- Drop table
    
    -- DROP TABLE edu.edu_announcment;
    
    CREATE TABLE edu.edu_announcment (
    	id bigserial NOT NULL,
    	"name" varchar NULL,
    	resource_id int8 NOT NULL,
    	CONSTRAINT edu_announcment_pk PRIMARY KEY (id),
    	CONSTRAINT edu_announcment_fk FOREIGN KEY (resource_id) REFERENCES edu.resource(id) ON DELETE CASCADE ON UPDATE CASCADE
    );
    
    
    -- edu.edu_discussion определение
    
    -- Drop table
    
    -- DROP TABLE edu.edu_discussion;
    
    CREATE TABLE edu.edu_discussion (
    	id bigserial NOT NULL,
    	"name" varchar NULL,
    	resource_id int8 NOT NULL,
    	CONSTRAINT edu_discussion_pk PRIMARY KEY (id),
    	CONSTRAINT edu_discussion_resource_fk FOREIGN KEY (resource_id) REFERENCES edu.resource(id) ON DELETE RESTRICT ON UPDATE CASCADE
    );
    
    
    -- edu.edu_lab_report определение
    
    -- Drop table
    
    -- DROP TABLE edu.edu_lab_report;
    
    CREATE TABLE edu.edu_lab_report (
    	id bigserial NOT NULL,
    	resource_id int8 NOT NULL,
    	CONSTRAINT edu_lab_report_pk PRIMARY KEY (id),
    	CONSTRAINT edu_lab_report_fk FOREIGN KEY (resource_id) REFERENCES edu.resource(id) ON DELETE CASCADE ON UPDATE CASCADE
    );
    
    
    -- edu.edu_resource_lecture определение
    
    -- Drop table
    
    -- DROP TABLE edu.edu_resource_lecture;
    
    CREATE TABLE edu.edu_resource_lecture (
    	id bigserial NOT NULL,
    	"name" text NULL,
    	resource_id int8 NOT NULL,
    	summary text NULL,
    	CONSTRAINT edu_resource_lecture_pk PRIMARY KEY (id),
    	CONSTRAINT edu_resource_lecture_fk FOREIGN KEY (resource_id) REFERENCES edu.resource(id) ON DELETE CASCADE ON UPDATE CASCADE
    );
    
    
    -- edu.edu_survey определение
    
    -- Drop table
    
    -- DROP TABLE edu.edu_survey;
    
    CREATE TABLE edu.edu_survey (
    	id bigserial NOT NULL,
    	"name" varchar NULL,
    	resource_id int8 NOT NULL,
    	CONSTRAINT edu_survey_pk PRIMARY KEY (id),
    	CONSTRAINT edu_survey_resource_fk FOREIGN KEY (resource_id) REFERENCES edu.resource(id) ON DELETE RESTRICT ON UPDATE CASCADE
    );
    
    
    -- edu.edu_term определение
    
    -- Drop table
    
    -- DROP TABLE edu.edu_term;
    
    CREATE TABLE edu.edu_term (
    	id bigserial NOT NULL,
    	"name" varchar NULL,
    	"text" text NULL,
    	resource_id int8 NOT NULL,
    	CONSTRAINT edu_term_pk PRIMARY KEY (id),
    	CONSTRAINT edu_term_fk FOREIGN KEY (resource_id) REFERENCES edu.resource(id) ON DELETE CASCADE ON UPDATE CASCADE
    );
    
    
    -- edu.edu_test определение
    
    -- Drop table
    
    -- DROP TABLE edu.edu_test;
    
    CREATE TABLE edu.edu_test (
    	id bigserial NOT NULL,
    	"name" varchar NULL,
    	resource_id int8 NOT NULL,
    	CONSTRAINT edu_text_pk PRIMARY KEY (id),
    	CONSTRAINT edu_text_resource_fk FOREIGN KEY (resource_id) REFERENCES edu.resource(id) ON DELETE RESTRICT ON UPDATE CASCADE
    );
    
    
    -- edu.edu_theme определение
    
    -- Drop table
    
    -- DROP TABLE edu.edu_theme;
    
    CREATE TABLE edu.edu_theme (
    	id bigserial NOT NULL,
    	resource_id int8 NOT NULL,
    	"name" text NULL,
    	CONSTRAINT edu_theme_pk PRIMARY KEY (id),
    	CONSTRAINT edu_theme_fk FOREIGN KEY (resource_id) REFERENCES edu.resource(id) ON DELETE CASCADE ON UPDATE CASCADE
    );
    
    
    -- edu.file_resource_description определение
    
    -- Drop table
    
    -- DROP TABLE edu.file_resource_description;
    
    CREATE TABLE edu.file_resource_description (
    	id bigserial NOT NULL,
    	type_id int4 NULL,
    	"name" varchar NOT NULL,
    	resource_id int8 NULL,
    	"path" varchar NOT NULL,
    	CONSTRAINT file_resource_description_pk PRIMARY KEY (id),
    	CONSTRAINT file_resource_description_fk FOREIGN KEY (type_id) REFERENCES edu.file_type(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    	CONSTRAINT file_resource_description_fk_2 FOREIGN KEY (resource_id) REFERENCES edu.resource(id) ON DELETE CASCADE ON UPDATE CASCADE
    );
    
    
    -- edu.html_resource определение
    
    -- Drop table
    
    -- DROP TABLE edu.html_resource;
    
    CREATE TABLE edu.html_resource (
    	id bigserial NOT NULL,
    	html text NULL,
    	resource_id int8 NOT NULL,
    	CONSTRAINT html_resource1_pk PRIMARY KEY (id),
    	CONSTRAINT html_resource_resource_fk FOREIGN KEY (resource_id) REFERENCES edu.resource(id) ON DELETE RESTRICT ON UPDATE RESTRICT
    );
    
    
    -- edu.lms_resource определение
    
    -- Drop table
    
    -- DROP TABLE edu.lms_resource;
    
    CREATE TABLE edu.lms_resource (
    	id bigserial NOT NULL,
    	access_rights xml NULL,
    	module_config xml NULL,
    	view_config xml NULL,
    	resource_id int8 NOT NULL,
    	CONSTRAINT lms_resource_pk PRIMARY KEY (id),
    	CONSTRAINT lms_resource_fk FOREIGN KEY (resource_id) REFERENCES edu.resource(id) ON DELETE CASCADE ON UPDATE CASCADE
    );
    
    
    -- edu.original_lms_resource определение
    
    -- Drop table
    
    -- DROP TABLE edu.original_lms_resource;
    
    CREATE TABLE edu.original_lms_resource (
    	id bigserial NOT NULL,
    	type_id int8 NULL,
    	platform_id int8 NULL,
    	"content" text NULL,
    	resource_id int8 NULL,
    	CONSTRAINT original_lms_resource_pk PRIMARY KEY (id),
    	CONSTRAINT original_lms_resource_lms_fk FOREIGN KEY (platform_id) REFERENCES edu.lms(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    	CONSTRAINT original_lms_resource_lms_resource_type_fk FOREIGN KEY (type_id) REFERENCES edu.lms_resource_type(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    	CONSTRAINT original_lms_resource_resource_fk FOREIGN KEY (resource_id) REFERENCES edu.resource(id) ON DELETE RESTRICT ON UPDATE CASCADE
    );
    
    
    -- edu.questions_resource определение
    
    -- Drop table
    
    -- DROP TABLE edu.questions_resource;
    
    CREATE TABLE edu.questions_resource (
    	id bigserial NOT NULL,
    	questions text NULL,
    	answers text NULL,
    	resource_id int8 NOT NULL,
    	CONSTRAINT questions_resource_pk PRIMARY KEY (id),
    	CONSTRAINT questions_resource_resource_fk FOREIGN KEY (resource_id) REFERENCES edu.resource(id) ON DELETE RESTRICT ON UPDATE CASCADE
    );
    
    
    -- edu.resource_relations определение
    
    -- Drop table
    
    -- DROP TABLE edu.resource_relations;
    
    CREATE TABLE edu.resource_relations (
    	id bigserial NOT NULL,
    	resource_one_id int8 NOT NULL,
    	resource_two_id int8 NOT NULL,
    	CONSTRAINT resource_relations_pk PRIMARY KEY (id),
    	CONSTRAINT resource_relations_fk FOREIGN KEY (resource_one_id) REFERENCES edu.resource(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    	CONSTRAINT resource_relations_fk_1 FOREIGN KEY (resource_two_id) REFERENCES edu.resource(id) ON DELETE RESTRICT ON UPDATE CASCADE
    );
    
    
    -- edu.schedule_resource определение
    
    -- Drop table
    
    -- DROP TABLE edu.schedule_resource;
    
    CREATE TABLE edu.schedule_resource (
    	id bigserial NOT NULL,
    	teacher_id int8 NOT NULL,
    	start_time int8 NOT NULL,
    	duration int8 NULL,
    	notes text NULL,
    	resource_id int8 NOT NULL,
    	CONSTRAINT schedule_resource_pk PRIMARY KEY (id),
    	CONSTRAINT schedule_resource_resource_fk FOREIGN KEY (resource_id) REFERENCES edu.resource(id) ON DELETE RESTRICT ON UPDATE CASCADE
    );
    
    
    -- edu.video_resource_description определение
    
    -- Drop table
    
    -- DROP TABLE edu.video_resource_description;
    
    CREATE TABLE edu.video_resource_description (
    	id bigserial NOT NULL,
    	"name" varchar NULL,
    	url varchar NULL,
    	duration int8 NULL,
    	resource_id int8 NULL,
    	author varchar NULL,
    	CONSTRAINT video_resource_description_pk PRIMARY KEY (id),
    	CONSTRAINT video_resource_description_resource_fk FOREIGN KEY (resource_id) REFERENCES edu.resource(id) ON DELETE RESTRICT ON UPDATE CASCADE
    );
    """
    
    drop = """
    DROP TABLE IF EXISTS edu.file_type CASCADE;
    DROP TABLE IF EXISTS edu.lms CASCADE;
    DROP TABLE IF EXISTS edu.lms_resource_type CASCADE;
    DROP TABLE IF EXISTS edu.resource CASCADE;
    DROP TABLE IF EXISTS edu.edu_announcment CASCADE;
    DROP TABLE IF EXISTS edu.edu_lab_report CASCADE;
    DROP TABLE IF EXISTS edu.edu_resource_lecture CASCADE;
    DROP TABLE IF EXISTS edu.edu_term CASCADE;
    DROP TABLE IF EXISTS edu.edu_theme CASCADE;
    DROP TABLE IF EXISTS edu.file_resource_description CASCADE;
    DROP TABLE IF EXISTS edu.html_resource CASCADE;
    DROP TABLE IF EXISTS edu.lms_resource CASCADE;
    DROP TABLE IF EXISTS edu.original_lms_resource CASCADE;
    DROP TABLE IF EXISTS edu.resource_relations CASCADE;
    DROP TABLE IF EXISTS edu.video_resource_description CASCADE;

    DROP TABLE IF EXISTS edu.edu_discussion CASCADE;
    DROP TABLE IF EXISTS edu.comment_resource CASCADE;
    DROP TABLE IF EXISTS edu.edu_test CASCADE;
    DROP TABLE IF EXISTS edu.edu_survey CASCADE;
    DROP TABLE IF EXISTS edu.questions_resource CASCADE;
    DROP TABLE IF EXISTS edu.schedule_resource CASCADE;
    """
    if create_or_drop == "create":
        return create
    elif create_or_drop == "drop":
        return drop


#sql( creation_main_tables("drop") )
#sql( creation_main_tables("create") )


# Перезагрузка БД

# In[35]:


################################################################################################################################
#### Перезагрузка БД

def tables_reload():
    sql( creation_main_tables("drop") )
    sql( creation_main_tables("create") )
    return "Таблицы успешно очищены"

#tables_reload()
################################################################################################################################


# # Добавление в БД original_lms_resource SELECT

# select ID recource by URL

# In[36]:


def select_resource_BY_URL(url):
    return remove_sql_symbol( sql( f"SELECT id FROM {SN}resource WHERE url = '{url}' " ) )

#select_resource_BY_URL('http://51.250.4.123/moodle/my/courses.php')


# select ID original_lms_resource by RESOURCE_URL

# In[37]:


def select_original_lms_resource_BY_RESOURCE_URL(resource_url):
    resource_id = select_resource_BY_URL(resource_url)
    if resource_id != "":
        return remove_sql_symbol( sql( f"SELECT id FROM {SN}original_lms_resource WHERE resource_id = {resource_id} " ) )

#select_original_lms_resource_BY_RESOURCE_URL('http://51.250.4.123/moodle/my/courses.php')
#sql( f"SELECT id FROM original_lms_resource WHERE resource_id = '2' " )


# select ID lms by NAME

# In[38]:


def select_lms_BY_NAME(name):
    return remove_sql_symbol( sql( f"SELECT id FROM {SN}lms WHERE name = '{name}' " ) )

#select_lms_BY_NAME('lms')


# select ID lms_resource_type by NAME

# In[39]:


def select_lms_resource_type_BY_NAME(name):
    return remove_sql_symbol( sql( f"SELECT id FROM {SN}lms_resource_type WHERE name = '{name}' " ) )

#select_lms_resource_type_BY_NAME('url')


# # Добавление в БД original_lms_resource INSERT

# insert resource

# In[40]:


def insert_resource(url, name, description):
    if select_resource_BY_URL(url) == '':
        sql( f"INSERT INTO {SN}resource(url, name, description) VALUES('{url}', '{name}', '{description}')" )
        return "Элемент добавлен (insert_resource)"
    else:
        return "Такой элемент уже cуществует (insert_resource)"

#insert_resource('url', 'name', 'description')


# insert original_lms_resource

# In[41]:


def insert_original_lms_resource(resource_type, platform, content, resource_url):
    resource_type_id = select_lms_resource_type_BY_NAME (resource_type)
    platform_id = select_lms_BY_NAME (platform)
    resource_id = select_resource_BY_URL (resource_url)
    is_elem_exist = select_original_lms_resource_BY_RESOURCE_URL (resource_url)
    
    if (is_elem_exist == "") or (is_elem_exist == None):
        
        if (resource_type_id != "") and (platform_id != "") and (resource_id != ""):
            sql( f"INSERT INTO {SN}original_lms_resource(type_id, platform_id, content, resource_id) VALUES({resource_type_id}, {platform_id}, '{content}', {resource_id})" )
            return "Успешно добавлено (insert_original_lms_resource)"
        elif (resource_type_id == ''):
            return "Ошибка resource_type_id == '' (insert_original_lms_resource)"
        elif (platform_id == ''):
            return "Ошибка platform_id == '' (insert_original_lms_resource)"
        elif (resource_id == ''):
            return "Ошибка resource_id =='' (insert_original_lms_resource)"
        
        else:
            return "Ошибка добавления (insert_original_lms_resource)"
    else:
        return "Такой элемент уже существует (insert_original_lms_resource)"
    
#insert_original_lms_resource('page', 'Moodle', 'content', 'http://51.250.4.123/moodle/my/courses.php')
#print( select_original_lms_resource_BY_RESOURCE_URL ('http://51.250.4.123/moodle/my/courses.php') )


# insert lms

# In[42]:


def insert_lms(name):
    if select_lms_BY_NAME(name) == '':
        sql( f"INSERT INTO {SN}lms(name) VALUES('{name}')" )
        return "Элемент добавлен (insert_lms)"
    else:
        return "Такой элемент уже cуществует (insert_lms)"

#insert_lms("lms")


# insert lms_resource_type

# In[43]:


def insert_lms_resource_type(name):
    if select_lms_resource_type_BY_NAME(name) == '':
        sql( f"INSERT INTO {SN}lms_resource_type(name) VALUES('{name}')" )
        return "Элемент добавлен (insert_lms_resource_type)"
    else:
        return "Такой элемент уже cуществует (insert_lms_resource_type)"

#insert_lms_resource_type('page')


# insert FULL_original_resource

# In[44]:


def insert_FULL_original_resource(resource_name, resource_url, resource_description, lms_resource_type_name, lms_name, content):
    res_1 = insert_resource(resource_url, resource_name, resource_description)
    res_2 = insert_lms(lms_name)
    res_3 = insert_lms_resource_type(lms_resource_type_name)
    res_4 = insert_original_lms_resource(lms_resource_type_name, lms_name, content, resource_url)

    return f"{res_1} || {res_2} || {res_3} || {res_4}"

#insert_FULL_original_resource('Ресурс 1', 'http://51.250.4.123/moodle/my/courses.php', 'Описание', 'page', 'Moodle', 'content')


# In[45]:


# Остатки от работы

#insert_resource('http://51.250.4.123/moodle/my/courses.php', 'Ресурс 1', 'Описание')
#insert_lms('Moodle')
#insert_lms_resource_type('page')
#insert_original_lms_resource('page', 'Moodle', 'content', 'http://51.250.4.123/moodle/my/courses.php')

#insert_resource(resource_url, resource_name, resource_description)
#insert_lms(lms_name)
#insert_lms_resource_type(lms_resource_type_name)
#insert_original_lms_resource(lms_resource_type_name, lms_name, content, resource_url)

#resource_name = 'Ресурс 1'
#resource_url = 'http://51.250.4.123/moodle/my/courses.php'
#resource_description = 'Описание'
#lms_resource_type_name = 'page'
#lms_name = 'Moodle'
#content = 'content'
#insert_FULL_original_resource(resource_name, resource_url, resource_description, lms_resource_type_name, lms_name, content)


# # Добавление в БД edu SELECT

# select_edu_theme_BY_RESOURCE_ID

# In[46]:


def select_edu_theme_BY_RESOURCE_ID(resource_id):
    return remove_sql_symbol( sql( f"SELECT id FROM {SN}edu_theme WHERE resource_id = {resource_id} " ) )

#select_edu_theme_BY_RESOURCE_ID(1)


# select_edu_announcment_BY_RESOURCE_ID

# In[47]:


def select_edu_announcment_BY_RESOURCE_ID(resource_id):
    return remove_sql_symbol( sql( f"SELECT name FROM {SN}edu_announcment WHERE resource_id = {resource_id} " ) )

#select_edu_announcment_BY_RESOURCE_ID(1)


# select_edu_announcment_BY_RESOURCE_ID

# In[48]:


def select_edu_lab_report_BY_RESOURCE_ID(resource_id):
    return remove_sql_symbol( sql( f"SELECT id FROM {SN}edu_lab_report WHERE resource_id = {resource_id} " ) )

#select_edu_lab_report_BY_RESOURCE_ID(1)


# select_edu_resource_lecture_BY_RESOURCE_ID

# In[49]:


def select_edu_resource_lecture_BY_RESOURCE_ID(resource_id):
    return remove_sql_symbol( sql( f"SELECT name FROM {SN}edu_resource_lecture WHERE resource_id = {resource_id} " ) )

#select_edu_resource_lecture_BY_RESOURCE_ID(1)


# select_edu_term_BY_RESOURCE_ID

# In[50]:


def select_edu_term_BY_RESOURCE_ID(resource_id):
    return remove_sql_symbol( sql( f"SELECT name FROM {SN}edu_term WHERE resource_id = {resource_id} " ) )

#select_edu_term_BY_RESOURCE_ID(1)


# select_edu_survey_BY_RESOURCE_ID

# In[51]:


def select_edu_survey_BY_RESOURCE_ID(resource_id):
    return remove_sql_symbol( sql( f"SELECT id FROM {SN}edu_survey WHERE resource_id = {resource_id} " ) )

#select_edu_survey_BY_RESOURCE_ID(1)


# select_edu_test_BY_RESOURCE_ID

# In[52]:


def select_edu_test_BY_RESOURCE_ID(resource_id):
    return remove_sql_symbol( sql( f"SELECT id FROM {SN}edu_test WHERE resource_id = {resource_id} " ) )

#select_edu_test_BY_RESOURCE_ID(1)


# select_edu_discussion_BY_RESOURCE_ID

# In[53]:


def select_edu_discussion_BY_RESOURCE_ID(resource_id):
    return remove_sql_symbol( sql( f"SELECT id FROM {SN}edu_discussion WHERE resource_id = {resource_id} " ) )

#select_edu_discussion_BY_RESOURCE_ID(1)


# # Добавление в БД edu INSERT

# insert_edu_theme

# In[54]:


def insert_edu_theme(name, resource_id):
    if select_edu_theme_BY_RESOURCE_ID(resource_id) == '':
        sql( f"INSERT INTO {SN}edu_theme(name, resource_id) VALUES('{name}', {resource_id})" )
        return "Элемент добавлен (insert_edu_theme)"
    else:
        return "Такой элемент уже cуществует (insert_edu_theme)"

#insert_edu_theme('Название темы', 1)


# insert_edu_announcment

# In[55]:


def insert_edu_announcment(name, resource_id):
    if select_edu_announcment_BY_RESOURCE_ID(resource_id) == '':
        sql( f"INSERT INTO {SN}edu_announcment(name, resource_id) VALUES('{name}', {resource_id})" )
        return "Элемент добавлен (insert_edu_announcment)"
    else:
        return "Такой элемент уже cуществует (insert_edu_announcment)"

#insert_edu_announcment('Название опроса', 1)


# insert_edu_lab_report

# In[56]:


def insert_edu_lab_report(resource_id):
    if select_edu_lab_report_BY_RESOURCE_ID(resource_id) == '':
        sql( f"INSERT INTO {SN}edu_lab_report(resource_id) VALUES({resource_id})" )
        return "Элемент добавлен (insert_edu_lab_report)"
    else:
        return "Такой элемент уже cуществует (insert_edu_lab_report)"

#insert_edu_lab_report(1)


# insert_edu_resource_lecture

# In[57]:


def insert_edu_resource_lecture(name, resource_id, summary):
    if select_edu_resource_lecture_BY_RESOURCE_ID(resource_id) == '':
        sql( f"INSERT INTO {SN}edu_resource_lecture(name, resource_id, summary) VALUES('{name}', {resource_id}, '{summary}')" )
        return "Элемент добавлен (insert_edu_resource_lecture)"
    else:
        return "Такой элемент уже cуществует (insert_edu_resource_lecture)"

#insert_edu_resource_lecture('Название лекции', 1, 'Краткое описание')


# insert_edu_term

# In[58]:


def insert_edu_term(name, resource_id, text):
    #if select_edu_term_BY_RESOURCE_ID(resource_id) == '':
        sql( f"INSERT INTO {SN}edu_term(name, resource_id, text) VALUES('{name}', {resource_id}, '{text}')" )
        return "Элемент добавлен (insert_edu_term)"
    #else:
        #return "Такой элемент уже cуществует (insert_edu_term)"

#insert_edu_term('Название термина', 1, 'Текст термина')


# insert_edu_survey

# In[59]:


def insert_edu_survey(name, resource_id):
    if select_edu_survey_BY_RESOURCE_ID(resource_id) == '':
        sql( f"INSERT INTO {SN}edu_survey(name, resource_id) VALUES('{name}', {resource_id})" )
        return "Элемент добавлен (insert_edu_survey)"
    else:
        return "Такой элемент уже cуществует (insert_edu_survey)"

#insert_edu_survey('Название термина', 1)


# insert_edu_test

# In[60]:


def insert_edu_test(name, resource_id):
    if select_edu_test_BY_RESOURCE_ID(resource_id) == '':
        sql( f"INSERT INTO {SN}edu_test(name, resource_id) VALUES('{name}', {resource_id})" )
        return "Элемент добавлен (insert_edu_test)"
    else:
        return "Такой элемент уже cуществует (insert_edu_test)"

#insert_edu_test('Название термина', 1)


# insert_edu_discussion

# In[61]:


def insert_edu_discussion(name, resource_id):
    if select_edu_discussion_BY_RESOURCE_ID(resource_id) == '':
        sql( f"INSERT INTO {SN}edu_discussion(name, resource_id) VALUES('{name}', {resource_id})" )
        return "Элемент добавлен (insert_edu_discussion)"
    else:
        return "Такой элемент уже cуществует (insert_edu_discussion)"

#insert_edu_discussion('Название термина', 1)


# # Добавление в БД resource SELECT

# select_html_resource_BY_RESOURCE_ID

# In[62]:


def select_html_resource_BY_RESOURCE_ID(resource_id):
    return remove_sql_symbol( sql( f"SELECT id FROM {SN}html_resource WHERE resource_id = {resource_id} " ) )

#select_html_resource_BY_RESOURCE_ID(1)


# select_video_resource_description_BY_URL

# In[63]:


def select_video_resource_description_BY_URL(url):
    return remove_sql_symbol( sql( f"SELECT id FROM {SN}video_resource_description WHERE url = '{url}' " ) )

#select_video_resource_description_BY_URL('https://www.youtube.com/watch?v=jfKfPfyJRdk&ab_channel=LofiGirl')


# select_file_type_BY_EXTENSION

# In[64]:


def select_file_type_BY_EXTENSION(extention):
    return remove_sql_symbol( sql( f"SELECT id FROM {SN}file_type WHERE extension = '{extention}' " ) )

#select_file_type_BY_EXTENSION('docx')


# select_file_resource_description_BY_RESOURCE_ID

# In[65]:


def select_file_resource_description_BY_RESOURCE_ID(resource_id):
    return remove_sql_symbol( sql( f"SELECT id FROM {SN}file_resource_description WHERE resource_id = {resource_id} " ) )

#select_file_resource_description_BY_RESOURCE_ID(1)


# select_questions_resource_BY_RESOURCE_ID

# In[66]:


def select_questions_resource_BY_RESOURCE_ID(resource_id):
    all_content = sql( f"SELECT id FROM {SN}questions_resource WHERE resource_id = {resource_id} " )
    new_ = replace_symbols(remove_symbols("[]'()", str(all_content)), ',,', ',' )
    return new_

#select_questions_resource_BY_RESOURCE_ID(1)


# select_comment_resource_BY_RESOURCE_ID

# In[67]:


def select_comment_resource_BY_RESOURCE_ID(resource_id):
    return remove_sql_symbol( sql( f"SELECT id FROM {SN}comment_resource WHERE resource_id = {resource_id} " ) )

#select_comment_resource_BY_RESOURCE_ID(1)


# # Добавление в БД resource INSERT

# insert_html_resource

# In[68]:


def insert_html_resource(html, resource_id):
    if select_html_resource_BY_RESOURCE_ID(resource_id) == '':
        sql( f"INSERT INTO {SN}html_resource(html, resource_id) VALUES('{html}', {resource_id})" )
        return "Элемент добавлен (insert_html_resource)"
    else:
        return "Такой элемент уже cуществует (insert_html_resource)"

#insert_html_resource('Тело html ресурса', 1)


# insert_video_resource_description

# In[69]:


def insert_video_resource_description(name, url, duration, resource_id, author):
    if select_video_resource_description_BY_URL(url) == '':
        sql( f"INSERT INTO {SN}video_resource_description(name, url, duration, resource_id, author) VALUES('{name}', '{url}', {duration}, {resource_id}, '{author}')" )
        return "Элемент добавлен (insert_video_resource_description)"
    else:
        return "Такой элемент уже cуществует (insert_video_resource_description)"

#insert_video_resource_description('Название видео ресурса', 'https://www.youtube.com/watch?v=jfKfPfyJRdk&ab_channel=LofiGirl', 120, 1, 1)


# insert_file_type

# In[70]:


def insert_file_type(name, extension):
    if select_file_type_BY_EXTENSION(extension) == '':
        sql( f"INSERT INTO {SN}file_type(name, extension) VALUES('{name}', '{extension}')" )
        return "Элемент добавлен (insert_file_type)"
    else:
        return "Такой элемент уже cуществует (insert_file_type)"
"""
insert_file_type('Ворд', 'docx')
insert_file_type('ПДФ', 'pdf')
insert_file_type('Гифка', 'gif')
insert_file_type('Джипег', 'jpeg')
insert_file_type('ПэЭнГэ', 'png')
"""


# insert_file_resource_description

# In[71]:


def insert_file_resource_description(name, extension, resource_id, path):
    if select_file_resource_description_BY_RESOURCE_ID(resource_id) == '':
        type_id = select_file_type_BY_EXTENSION(extension)
        if type_id == '':
            return "Такого расширения файла нет"
        else:
            sql( f"INSERT INTO {SN}file_resource_description(name, type_id, resource_id, path) VALUES('{name}', '{type_id}', {resource_id}, '{path}')" )
            return "Элемент добавлен (insert_file_resource_description)"
    else:
        return "Такой элемент уже cуществует (insert_file_resource_description)"

#insert_file_resource_description('Название ресурса-файла', 'docx', 1, 'крутой путь к файлу')


# insert_questions_resource

# In[72]:


def insert_questions_resource(questions, answers, resource_id):
    if select_questions_resource_BY_RESOURCE_ID(resource_id) == '':
        sql( f"INSERT INTO {SN}questions_resource(questions, answers, resource_id) VALUES('{questions}', '{answers}', {resource_id})" )
        return "Элемент добавлен (insert_questions_resource)"
    else:
        return "Такой элемент уже cуществует (insert_questions_resource)"

#insert_questions_resource('Название видео ресурса', 'https://www.youtube.com/watch?v=jfKfPfyJRdk&ab_channel=LofiGirl', 1)


# insert_comment_resource

# In[73]:


def insert_comment_resource(replied_comment_id, user_id, text, resource_id):
    #if select_questions_resource_BY_RESOURCE_ID(resource_id) == '':
        sql( f"INSERT INTO {SN}comment_resource(replied_comment_id, user_id, text, resource_id) VALUES({replied_comment_id}, {user_id}, '{text}', {resource_id})" )
        return "Элемент добавлен (insert_comment_resource)"
    #else:
        #return "Такой элемент уже cуществует (insert_questions_resource)"

#insert_comment_resource(1, 1, 'https://www.youtube.com/watch?v=jfKfPfyJRdk&ab_channel=LofiGirl', 1)


# insert_schedule_resource

# In[74]:


def insert_schedule_resource(teacher_id, start_time, duration, notes, resource_id):
    #if select_questions_resource_BY_RESOURCE_ID(resource_id) == '':
        sql( f"INSERT INTO {SN}schedule_resource(teacher_id, start_time, duration, notes, resource_id) VALUES({teacher_id}, {start_time}, {duration}, '{notes}', {resource_id})" )
        return "Элемент добавлен (insert_schedule_resource)"
    #else:
        #return "Такой элемент уже cуществует (insert_questions_resource)"

#insert_schedule_resource(1, 1, 1, 'https://www.youtube.com/watch?v=jfKfPfyJRdk&ab_channel=LofiGirl', 1)


# # Поиск ссылок на YouTube

# In[75]:


def convert_time_to_number(time):
    hours, minutes, seconds = map(int, time.split(':'))
    total_seconds = hours * 3600 + minutes * 60 + seconds
    return total_seconds

def get_video_info(url):
    yt = YouTube(url)
    video_title = yt.title
    video_author = yt.author
    video_duration = str(datetime.timedelta(seconds=yt.length))
    video_duration = convert_time_to_number(video_duration)
    
    return [url, video_title, video_author, video_duration]

def find_youtube_links(text):
    youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|watch\?.*v=)?([^&=%\?]{11})'
    youtube_links = re.findall(youtube_regex, text)
    
    youtube_urls = []
    for link in youtube_links:
        youtube_url = 'https://www.youtube.com/watch?v=' + link[5]
        youtube_urls.append( get_video_info(youtube_url) )
    
    return youtube_urls


#smth = str( all_files_read() )
#video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # ссылка на видео Rick Astley - Never Gonna Give You Up
#find_youtube_links(smth)


# # Импорт всех файлов

# In[76]:


def all_files_import():
    if if_unzipping_backup_file_exists != None:
        all_ = all_files_read()
        for index in range(len(all_)):
            resource_url = all_[index][0]
            directory = all_[index][1]
            lms_resource_type_name = all_[index][2]
            resource_name = all_[index][3]
            all_file_content = read_all( all_[index][1] )
            lms_name = 'Moodle'
            resource_description = f"Ресурс типа {lms_resource_type_name}, загруженный из системы {lms_name}"
            insert_FULL_original_resource(resource_name, resource_url, resource_description, lms_resource_type_name, lms_name, all_file_content)
            resource_id = select_resource_BY_URL(resource_url)
    
            links = find_youtube_links( str(all_[index]) )
            if ( links ) != []:
                for link in links:
                    name = link[1]
                    url = link[0]
                    duration = link[3]
                    author = link[2]
                    insert_video_resource_description(name, url, duration, resource_id, author)
            
            if lms_resource_type_name == "page" : add_page_resource_to_DB(all_, index, resource_name, resource_id)
            elif lms_resource_type_name == "choice" : add_choice_resource_to_DB(all_, index, resource_name, resource_id)
            elif lms_resource_type_name == "book" : add_book_resource_to_DB(all_, index, resource_name, resource_id)
            elif lms_resource_type_name == "feedback" : add_feedback_resource_to_DB(all_, index, resource_name, resource_id)
            elif lms_resource_type_name == "survey" : add_survey_resource_to_DB(all_, index, resource_name, resource_id)
            elif lms_resource_type_name == "forum" : add_forum_resource_to_DB(all_, index, resource_name, resource_id)
            elif lms_resource_type_name == "scheduler" : add_scheduler_resource_to_DB(all_, index, resource_name, resource_id)
            elif lms_resource_type_name == "quiz" : add_quiz_resource_to_DB(all_, index, resource_name, resource_id)
            elif lms_resource_type_name == "glossary" : add_glossary_resource_to_DB(all_, index, resource_name, resource_id)
    
        add_in_DB_files_description()
                
        return 'Ресурсы были успешно импортированы в базу данных!'
    else:
        return 'Поместите backup-файл в папку moodle_backup_file и перезапустите программу'
              
#all_files_import()


# Выносим функции добавления ресурсов в базу данных

# In[77]:


def add_page_resource_to_DB(all_, index, resource_name, resource_id):
    insert_edu_resource_lecture(resource_name, resource_id, '')
    insert_html_resource(all_[index][4], resource_id)
    
def add_choice_resource_to_DB(all_, index, resource_name, resource_id):
    insert_edu_survey(resource_name, resource_id)
    questions = all_[index][4]
    answers = ''
    insert_questions_resource(questions, answers, resource_id)
    
def add_book_resource_to_DB(all_, index, resource_name, resource_id):
    insert_edu_resource_lecture(resource_name, resource_id, '')
    insert_html_resource(all_[index][4], resource_id)
    
def add_feedback_resource_to_DB(all_, index, resource_name, resource_id):
    insert_edu_survey(resource_name, resource_id)
    questions = all_[index][4][0]
    answers = all_[index][4][1]
    insert_questions_resource(questions, answers, resource_id)
    
def add_survey_resource_to_DB(all_, index, resource_name, resource_id):
    insert_edu_survey(resource_name, resource_id)
    questions = all_[index][4]
    answers = ''
    insert_questions_resource(questions, answers, resource_id)

def add_forum_resource_to_DB(all_, index, resource_name, resource_id):
    insert_edu_discussion(resource_name, resource_id)
    # replied_comment_id, user_id, text, resource_id
    # ['id комментария', 'id комментария, на который идет ответ', 'id пользователя, оставившего комментарий', 'текст комментария'],\n"
    len_ = len( all_[index][4] )
    for j in range( len_ ):
        #id = all_[index][4][j][0]
        replied_comment_id = all_[index][4][j][1]
        user_id = all_[index][4][j][2]
        text = all_[index][4][j][3]
        insert_comment_resource(replied_comment_id, user_id, text, resource_id)
    
def add_scheduler_resource_to_DB(all_, index, resource_name, resource_id):
    # ['id записи', 'id учителя', 'время начала в Unixtime', 'продолжительность в минутах', 'заметки']
    insert_edu_announcment(resource_name, resource_id)
    #insert_html_resource(all_[index][4], resource_id)
    len_ = len( all_[index][4] )
    for j in range( len_ ):
        teacher_id = all_[index][4][j][1]
        start_time = all_[index][4][j][2]
        duration = all_[index][4][j][3]
        notes = all_[index][4][j][4]
        insert_schedule_resource(teacher_id, start_time, duration, notes, resource_id)
        
def add_quiz_resource_to_DB(all_, index, resource_name, resource_id):
    insert_edu_test(resource_name, resource_id)
    questions = all_[index][4]
    answers = ''
    insert_questions_resource(questions, answers, resource_id)

def add_glossary_resource_to_DB(all_, index, resource_name, resource_id):
    len_ = len( all_[index][4] )
    for j in range(len_):
        name = all_[index][4][j][0]
        #html = all_[index][4][j][1]
        text = all_[index][4][j][1]
        
        #return insert_edu_term(name, resource_id, text), insert_html_resource(html, resource_id)
        insert_edu_term(name, resource_id, text)
        #insert_html_resource(html, resource_id)
#len( all_files_read()[12][4] )
#all_files_read()[12][4][2][0]
#add_glossary_resource_to_DB(all_files_read(), 12, 'Терминологический словарь', 13)


# Создаем новые файлы и добавляем к соответствующим ресурсам

# In[78]:


def add_in_DB_files_description():
    new_files = files_creation_and_information()
    for index in range( len(new_files) ):
        if new_files[index][1] != '':
            path = new_files[index][0]
            name, extension = os.path.splitext(path)
            name, extension = [os.path.basename(name), extension[1:]]
            resource_id = new_files[index][1]
            
            insert_file_resource_description(name, extension, resource_id, path)

#add_in_DB_files_description()


# # Веб-интерфейс

# In[79]:


host = "127.0.0.1"
user = "postgres"
password = "qwerty"
db_name = "test"

def web_interface():
    app = Flask(__name__)
    
    # Значения по умолчанию для полей ввода

    
    # Функция для проверки подключения к базе данных
    def check_db_connection():
        try:
            conn = psycopg2.connect(
                host=host,
                user=user,
                password=password,
                dbname=db_name
            )
            conn.close()
            return True
        except psycopg2.Error as e:
            return False
    
    # Страница входа
    @app.route('/')
    def login():
        return f'''
            <form method="post">
                <label for="host">Хост:</label>
                <input type="text" id="host" name="host" value="127.0.0.1"><br><br>
                <label for="user">Пользователь:</label>
                <input type="text" id="user" name="user" value="postgres"><br><br>
                <label for="password">Пароль:</label>
                <input type="text" id="password" name="password" value="qwerty"><br><br>
                <label for="db_name">Имя БД:</label>
                <input type="text" id="db_name" name="db_name" value="test"><br><br>
                <input type="submit" value="Вход">
            </form>
            <button onclick="window.location.href='/exit'">Завершить программу</button><br>
        '''
    
    
    @app.route('/', methods=['POST'])
    def login_post():
        global host, user, password, db_name
        host = request.form['host']
        user = request.form['user']
        password = request.form['password']
        db_name = request.form['db_name']
    
        if check_db_connection():
            return redirect(url_for('import_page'))
        else:
            return "Failed to connect to the database"
    
    # Новая страница для отображения данных переменной all_files_read
    @app.route('/show_resources_from_files')
    def show_resources_from_files():
        return all_files_read()
    
    @app.route('/show_resources_from_db')
    def show_resources_from_db():
        res = """<a href="/import">Назад</a><br>"""
        res += show_tables(host, user, password, db_name, "resource")
        return res

    @app.route('/show_tables_video')
    def show_tables_video():
        res = """<a href="/import">Назад</a><br>"""
        res += show_tables(host, user, password, db_name, "video_resource_description")
        return res
    
    @app.route('/import_resources')
    def import_resources():
        res = all_files_import()
        res += """<br><a href="/import">Назад</a>"""
        return res
    
    @app.route('/delete_resources')
    def delete_resources():
        res = tables_reload()
        res += """<br><a href="/import">Назад</a>"""
        return res
    
    @app.route('/exit')
    def exit_program():
        _exit(0)
    
    @app.route('/import')
    def import_page():
        return f'''
            <button onclick="window.location.href='/show_resources_from_files'">Показать ресурсы из экспортируемого файла</button><br>
            <button onclick="window.location.href='/show_resources_from_db'">Показать ресурсы из базы данных</button><br>
            <button onclick="window.location.href='/show_tables_video'">Показать видео-ресурсы</button><br>
            <button onclick="window.location.href='/import_resources'">Импортировать ресурсы</button><br>
            <button onclick="window.location.href='/delete_resources'">Очистить таблицы</button><br>
            <a href="/">Назад</a>
        '''
    
    if __name__ == '__main__':
        app.run()

#web_interface()


# # Основной код

# In[80]:


#all_files_read()
#tables_reload()
#all_files_import()
web_interface()

