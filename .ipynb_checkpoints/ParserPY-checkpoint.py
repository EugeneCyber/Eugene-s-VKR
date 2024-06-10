{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {
    "id": "eTHVrO-XDbv6",
    "jp-MarkdownHeadingCollapsed": true
   },
   "source": [
    "# **Парсер для LMS Moodle**"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "id": "Q3rpZws1QJBf",
    "jp-MarkdownHeadingCollapsed": true
   },
   "source": [
    "# Библиотеки"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {
    "id": "B1inMDi7QvMp"
   },
   "outputs": [],
   "source": [
    "import xml.etree.ElementTree as ET\n",
    "import psycopg2\n",
    "\n",
    "import os\n",
    "from os import _exit\n",
    "import shutil\n",
    "\n",
    "import tarfile\n",
    "\n",
    "from flask import Flask, request, redirect, url_for\n",
    "\n",
    "import re\n",
    "\n",
    "from pytube import YouTube\n",
    "import datetime"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "jp-MarkdownHeadingCollapsed": true
   },
   "source": [
    "# Разархивация backup файла"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [],
   "source": [
    "def unzipping_backup_file(path_to_backup_file):\n",
    "    backup_file = None\n",
    "    \n",
    "    if not os.path.exists(path_to_backup_file):\n",
    "            os.makedirs(path_to_backup_file)\n",
    "    \n",
    "    # находим файл со случайным названием, начинающимся на \"backup\" в папке \"folder/\"\n",
    "    for file in os.listdir(path_to_backup_file):\n",
    "        if file.startswith(\"backup\") and file.endswith(\".mbz\"):\n",
    "            backup_file = file\n",
    "            #break\n",
    "    \n",
    "    if backup_file:\n",
    "        # создаем директорию для разархивированных файлов, если ее нет\n",
    "        if not os.path.exists(\"backup/\"):\n",
    "            os.makedirs(\"backup/\")\n",
    "    \n",
    "        # разархивируем первый файл\n",
    "        with tarfile.open(path_to_backup_file + backup_file, \"r:gz\") as tar:\n",
    "            tar.extractall(\"backup/\")\n",
    "    \n",
    "        # находим внутренний файл в разархивированной папке\n",
    "        inner_file = None\n",
    "        for file in os.listdir(\"backup/\"):\n",
    "            if file.endswith(\".tar.gz\"):\n",
    "                inner_file = file\n",
    "                break\n",
    "    \n",
    "        if inner_file:\n",
    "            # разархивируем внутренний файл\n",
    "            with tarfile.open(\"backup/\" + inner_file, \"r:gz\") as tar:\n",
    "                tar.extractall(\"backup/\")\n",
    "\n",
    "unzipping_backup_file(\"moodle_backup_file/\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "jp-MarkdownHeadingCollapsed": true
   },
   "source": [
    "# Базовые функции для работы с XML файлами"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Указываем путь к папке backup"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [],
   "source": [
    "def get_path_to_backup_file():\n",
    "    file = r'C:/Users/Eugene/Parser-Moodle/backup/'\n",
    "\n",
    "#get_path_to_backup_file()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "возврат путей xml файлов"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {
    "id": "pVdFzS18DCvo"
   },
   "outputs": [],
   "source": [
    "def activities_directories ():\n",
    "    file = \"backup/moodle_backup.xml\"\n",
    "    direct = []\n",
    "    directory = find_by_tag(file,\"directory\")\n",
    "    modulename = find_by_tag(file,\"modulename\")\n",
    "    for i in range( len(modulename) ):\n",
    "        text_dir = \"backup/\" + directory[i] + \"/\" + modulename[i] + \".xml\"\n",
    "        direct.insert(i, text_dir)\n",
    "    return direct"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "возварт текста по тегу"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {},
   "outputs": [],
   "source": [
    "def find_by_tag (file, tag):\n",
    "    tree = ET.parse(file)\n",
    "    root = tree.getroot()\n",
    "    res = \"\"\n",
    "    for text_in_root in root.iter(tag):\n",
    "        res += str(text_in_root.text)\n",
    "        res += \"\\n\"\n",
    "    listRes = list(res.split(\"\\n\"))\n",
    "    listRes.pop( len(listRes)-1 )\n",
    "    return listRes"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "возварт текста по тегу из конкретного вложенного тега"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "metadata": {},
   "outputs": [],
   "source": [
    "def find_by_tag_from_tag (file, where, tag):\n",
    "    tree = ET.parse(file)\n",
    "    root = tree.getroot()\n",
    "    res = \"\"\n",
    "    for text_in_root in tree.findall(\".//\" + where + \"/\" + tag):\n",
    "        res += str(text_in_root.text)\n",
    "        res += \"\\n\"\n",
    "    listRes = list(res.split(\"\\n\"))\n",
    "    listRes.pop( len(listRes)-1 )\n",
    "    return listRes"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "возварт аррибута по тегу"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "metadata": {},
   "outputs": [],
   "source": [
    "def find_ID_attrib_by_tag (file, tag):\n",
    "    tree = ET.parse(file)\n",
    "    root = tree.getroot()\n",
    "    res = \"\"\n",
    "    for text_in_root in root.iter(tag):\n",
    "        symbols_to_remove = \"{}id:' \"\n",
    "        res += remove_symbols(symbols_to_remove, str( text_in_root.attrib ))\n",
    "        res += \"\\n\"\n",
    "    listRes = list(res.split(\"\\n\"))\n",
    "    listRes.pop( len(listRes)-1 )\n",
    "    return listRes"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "возврат всего файла"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "metadata": {},
   "outputs": [],
   "source": [
    "\"\"\"def read_all(file):\n",
    "    tree = ET.parse(file)\n",
    "    s = ET.dump(tree)\n",
    "    return s\"\"\"\n",
    "\n",
    "def read_all(file_path):\n",
    "    try:\n",
    "        with open(file_path, 'r', encoding='utf-8') as file:\n",
    "            data = file.read()\n",
    "            data = remove_symbols('\\n', data)\n",
    "        return data\n",
    "    except FileNotFoundError:\n",
    "        return \"File not found\""
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "замена конкретной последовательности символов"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "metadata": {},
   "outputs": [],
   "source": [
    "def replace_symbols(text, old_word, new_word):\n",
    "    new_s = text.replace(old_word, new_word)\n",
    "    return new_s"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "удаление конкретных символов"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "metadata": {},
   "outputs": [],
   "source": [
    "def remove_symbols(symbols_to_remove, text):\n",
    "    for symbol in symbols_to_remove:\n",
    "        text = text.replace(symbol, \"\")\n",
    "    return text"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "удаление последнего символа"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "metadata": {},
   "outputs": [],
   "source": [
    "def remove_last_symbol(text):\n",
    "    result_string = \"\"\n",
    "    index = len(text)\n",
    "    for i in range(index-1):\n",
    "        result_string += text[i]\n",
    "    return result_string"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "удаление символов sql"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 12,
   "metadata": {},
   "outputs": [],
   "source": [
    "def remove_sql_symbol(text_):\n",
    "    text = str(text_)\n",
    "    symbols_to_remove = \"(, )[]\"\n",
    "    for symbol in symbols_to_remove:\n",
    "        text = text.replace(symbol, \"\")\n",
    "    return text"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "возврат contextid из xml фалов"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 13,
   "metadata": {},
   "outputs": [],
   "source": [
    "def find_contextid_in_activity(xml_file):\n",
    "    tree = ET.parse(xml_file)\n",
    "    root = tree.getroot()\n",
    "    \n",
    "    contextids = []\n",
    "    \n",
    "    for activity in root.iter('activity'):\n",
    "        contextid = activity.get('contextid')\n",
    "        if contextid is not None:\n",
    "            contextids.append(contextid)\n",
    "    \n",
    "    return contextids\n",
    "\n",
    "#find_contextid_in_activity('backup/activities/resource_6/resource.xml')"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "функция help"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 14,
   "metadata": {},
   "outputs": [],
   "source": [
    "def help():\n",
    "    stars = \"||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||\\n\"\n",
    "    res = stars\n",
    "    res += \"Функция all_files_read() считывает все данные файлов, помещенных в папку backup\\n\"\n",
    "    res += \"Общий массив имеет следующую структуру:\\n\"\n",
    "    \n",
    "    res += \"[\\n\"\n",
    "    res += \"  ['названия ресурсов'] в виде строк,\\n\"\n",
    "    res += \"  ['типы ресурсов'] в виде строк,\\n\"\n",
    "    res += \"  ['ссылки на ресурсы'] в виде строк,\\n\"\n",
    "    res += \"    [\\n\"\n",
    "    res += \"      [массив ресурса 1], [массив ресурса 2], [массив ресурса 3]... \\n\"\n",
    "    res += \"    ]\\n\"\n",
    "    res += \"]\\n\"\n",
    "\n",
    "    #res = \"\"\n",
    "    res += stars\n",
    "    res += \"Ресурс PAGE имеет следующую структуру массива:\\n\"\n",
    "    res += \"[\\n\"\n",
    "    res += \"  'название ресурса',\\n\"\n",
    "    res += \"  ['строка 1', 'строка 2', 'строка 3', 'строка 4'...]\\n\"\n",
    "    res += \"]\\n\"\n",
    "\n",
    "    #res = \"\"\n",
    "    res += stars\n",
    "    res += \"Ресурс CHOICE имеет следующую структуру массива:\\n\"\n",
    "    res += \"[\\n\"\n",
    "    res += \"  'название ресурса',\\n\"\n",
    "    res += \"  ['вопрос (строка) 1', 'вопрос 2', 'вопрос 3', 'вопрос 4'...],\\n\"\n",
    "    res += \"  ['ответ (число в виде строки) 1', 'ответ 2', 'ответ 3', 'ответ 4'...]\\n\"\n",
    "    res += \"]\\n\"\n",
    "\n",
    "    #res = \"\"\n",
    "    res += stars\n",
    "    res += \"Ресурс BOOK имеет следующую структуру массива:\\n\"\n",
    "    res += \"[\\n\"\n",
    "    res += \"  'название ресурса',\\n\"\n",
    "    res += \"  ['глава (строка) 1', 'глава 2', 'глава 3'...],\\n\"\n",
    "    res += \"  [\\n\"\n",
    "    res += \"    ['строка главы 1', 'строка главы 1', 'строка главы 1'...], \\n\"\n",
    "    res += \"    ['строка главы 2', 'строка главы 2', 'строка главы 2'...], \\n\"\n",
    "    res += \"    ['строка главы 3', 'строка главы 3', 'строка главы 3'...] \\n\"\n",
    "    res += \"  ]\\n\"\n",
    "    res += \"]\\n\"\n",
    "\n",
    "    #res = \"\"\n",
    "    res += stars\n",
    "    res += \"Ресурс FEEDBACK имеет следующую структуру массива:\\n\"\n",
    "    res += \"[\\n\"\n",
    "    res += \"  'название ресурса',\\n\"\n",
    "    res += \"  ['вопрос 1', 'вопрос 2', 'вопрос 3'...],\\n\"\n",
    "    res += \"  ['вариат ответа на ворос 1', 'вариат ответа на ворос 1', 'вариат ответа на ворос 1'...], \\n\"\n",
    "    res += \"  ['вариат ответа на ворос 2', 'вариат ответа на ворос 2', 'вариат ответа на ворос 2'...], \\n\"\n",
    "    res += \"  ['вариат ответа на ворос 3', 'вариат ответа на ворос 3', 'вариат ответа на ворос 3'...] \\n\"\n",
    "    res += \"]\\n\"\n",
    "\n",
    "    #res = \"\"\n",
    "    res += stars\n",
    "    res += \"Ресурс SURVEY имеет следующую структуру массива:\\n\"\n",
    "    res += \"[\\n\"\n",
    "    res += \"  'название ресурса',\\n\"\n",
    "    res += \"  ['номер вороса из банка вопросов', 'номер вороса из банка вопросов'...]\\n\"\n",
    "    res += \"]\\n\"\n",
    "\n",
    "    #res = \"\"\n",
    "    res += stars\n",
    "    res += \"Ресурс FORUM имеет следующую структуру массива:\\n\"\n",
    "    res += \"[\\n\"\n",
    "    res += \"  'название ресурса',\\n\"\n",
    "    res += \"  ['id комментария', 'id комментария, на который идет ответ', 'id пользователя, оставившего комментарий', 'текст комментария'],\\n\"\n",
    "    res += \"  ['id комментария', 'id комментария, на который идет ответ', 'id пользователя, оставившего комментарий', 'текст комментария']\\n\"\n",
    "    res += \"]\\n\"\n",
    "\n",
    "    #res = \"\"\n",
    "    res += stars\n",
    "    res += \"Ресурс SCHEDULER имеет следующую структуру массива:\\n\"\n",
    "    res += \"[\\n\"\n",
    "    res += \"  'название ресурса',\\n\"\n",
    "    res += \"  ['id записи', 'id учителя', 'время начала в Unixtime', 'продолжительность в минутах', 'заметки'],\\n\"\n",
    "    res += \"  ['id записи', 'id учителя', 'время начала в Unixtime', 'продолжительность в минутах', 'заметки']\\n\"\n",
    "    res += \"]\\n\"\n",
    "\n",
    "    #res = \"\"\n",
    "    res += stars\n",
    "    res += \"Ресурс QUIZ имеет следующую структуру массива:\\n\"\n",
    "    res += \"[\\n\"\n",
    "    res += \"  'название ресурса',\\n\"\n",
    "    res += \"  ['номер вороса в квизе', 'id вопроса из банка вопросов', 'баллы за правильный ответ'],\\n\"\n",
    "    res += \"  ['номер вороса в квизе', 'id вопроса из банка вопросов', 'баллы за правильный ответ']\\n\"\n",
    "    res += \"]\\n\"\n",
    "\n",
    "    res += stars\n",
    "    return res \n",
    "#print( help() )"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "jp-MarkdownHeadingCollapsed": true
   },
   "source": [
    "# Функции чтения отдельных XML файлов ресурсов"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "чтение page"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 15,
   "metadata": {},
   "outputs": [],
   "source": [
    "def page_read (file):\n",
    "    all_content = []\n",
    "    \n",
    "    title = remove_symbols(\"[]'\", str(find_by_tag_from_tag(file, \"page\", \"name\")))\n",
    "    strings_arr = find_by_tag(file, \"content\")\n",
    "\n",
    "    #all_content.append( title )\n",
    "    all_content.append( strings_arr )\n",
    "\n",
    "    new_page = replace_symbols(remove_symbols(\"[]'\", str(all_content)), '>, <', '> <' )\n",
    "    \n",
    "    return new_page\n",
    "\n",
    "#page_read(\"backup/activities/page_3/page.xml\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "чтение choice"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 16,
   "metadata": {},
   "outputs": [],
   "source": [
    "def choice_read (file):\n",
    "    all_content = []\n",
    "    \n",
    "    title = remove_symbols(\"[]'\", str(find_by_tag_from_tag(file, \"choice\", \"name\")))\n",
    "    text = find_by_tag(file, \"text\")\n",
    "    count = find_by_tag(file, \"maxanswers\")\n",
    "\n",
    "    #all_content.append( title )\n",
    "    #all_content.append( text )\n",
    "    #all_content.append( count )\n",
    "    new_choice = remove_symbols(\"[]'\", str(text))\n",
    "    return new_choice\n",
    "\n",
    "#choice_read(\"backup/activities/choice_4/choice.xml\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "чтение book"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 17,
   "metadata": {},
   "outputs": [],
   "source": [
    "def book_read (file):\n",
    "    all_content = []\n",
    "    book_content = []\n",
    "    name = remove_symbols(\"'[]\", str( find_by_tag(file, \"name\") ) )\n",
    "    title = find_by_tag(file, \"title\")\n",
    "\n",
    "    for i in range( len(title) ):\n",
    "        chap = \"chapter[\" + str(i+1) + \"]\"\n",
    "        content = find_by_tag_from_tag(file, chap, \"content\")\n",
    "        book_content.append(content)\n",
    "    \n",
    "    #all_content.append(name)\n",
    "    all_content.append(title)\n",
    "    all_content.append(book_content)\n",
    "\n",
    "    new_content = \"\"\n",
    "    for index in range( len(title) ):\n",
    "        new_content += \"<h1>\"\n",
    "        new_content += str(all_content[0][index])\n",
    "        new_content += \"</h1>\"\n",
    "        new_content += remove_symbols(\"[]'\", str(all_content[1][index]))\n",
    "        \n",
    "    new_content = replace_symbols(new_content, '>, <', '> <' )\n",
    "    new_content = replace_symbols(new_content, '><', '> <' )\n",
    "    \n",
    "    return new_content\n",
    "    \n",
    "#book_read(\"backup/activities/book_9/book.xml\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "чтение feedback"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 18,
   "metadata": {},
   "outputs": [],
   "source": [
    "def feedback_read (file):\n",
    "    all_content = []\n",
    "    new_parts = []\n",
    "    questions = find_by_tag_from_tag(file, \"item\", \"name\")\n",
    "    answers = []\n",
    "    title = remove_symbols(\"[]'\", str(find_by_tag_from_tag(file, \"feedback\", \"name\")))\n",
    "\n",
    "    arr_content = find_by_tag(file, \"presentation\")\n",
    "    str_content = ''.join(arr_content)\n",
    "    parts = str_content.rsplit('>>>>>')\n",
    "    parts.pop(0)\n",
    "\n",
    "    #all_content.append( title )\n",
    "\n",
    "    #убираем последний символ\n",
    "    for i in range ( len(parts) ):\n",
    "        if i != len(parts)-1:\n",
    "            new_parts.append( remove_last_symbol(parts[i]) )\n",
    "        else:\n",
    "            new_parts.append( parts[i] )\n",
    "\n",
    "    questions = replace_symbols(remove_symbols(\"[]'\", str(questions)), '>, <', '> <' )\n",
    "    all_content.append(questions)\n",
    "    \n",
    "    #разделяем строки по разделителям\n",
    "    for i in range ( len(parts) ):\n",
    "        new = new_parts[i].rsplit('|')\n",
    "\n",
    "        new = replace_symbols(remove_symbols(\"'\", str(new)), '>, <', '> <' )\n",
    "        \n",
    "        answers.append(new)\n",
    "\n",
    "    answers = replace_symbols(remove_symbols(\"'\", str(answers)), '>, <', '> <' )\n",
    "    answers = replace_symbols(answers, '[[', '[' )\n",
    "    answers = replace_symbols(answers, ']]', ']' )\n",
    "    all_content.append(answers)\n",
    "    \n",
    "    return all_content\n",
    "    \n",
    "#feedback_read(\"backup/activities/feedback_7/feedback.xml\")[1]"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "чтение survey"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 19,
   "metadata": {},
   "outputs": [],
   "source": [
    "def survey_read (file):\n",
    "    all_content = []\n",
    "    \n",
    "    questions = find_by_tag(file, \"questions\")\n",
    "    str_content = ''.join(questions)\n",
    "    parts = str_content.rsplit(',')\n",
    "    name = remove_symbols(\"[]'\", str(find_by_tag_from_tag(file, \"survey\", \"name\")))\n",
    "\n",
    "    #all_content.append(name)\n",
    "    all_content.append(parts)\n",
    "\n",
    "    new_survey = remove_symbols(\"[]'\", str(all_content))\n",
    "    \n",
    "    return new_survey\n",
    "#survey_read(\"backup/activities/survey_8/survey.xml\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "чтение forum"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 20,
   "metadata": {},
   "outputs": [],
   "source": [
    "def forum_read (file):\n",
    "    all_content = []\n",
    "    comment = []\n",
    "\n",
    "    forum_title = remove_symbols(\"[]'\", str(find_by_tag_from_tag(file, \"discussion\", \"name\")))\n",
    "\n",
    "    comment_id = find_ID_attrib_by_tag(file, \"post\")\n",
    "    parent = find_by_tag(file, \"parent\")\n",
    "    userid = find_by_tag(file, \"userid\")\n",
    "    message = find_by_tag(file, \"message\")\n",
    "\n",
    "    #all_content.append( forum_title )\n",
    "    \n",
    "    for i in range ( len(find_by_tag(file, \"parent\")) ):\n",
    "        #id комментария // id комментария, на который идет ответ // id пользователя, оставившего комментарий // текст комментария\n",
    "        comment = []\n",
    "        comment.append( comment_id[i] )\n",
    "        comment.append( parent[i] )\n",
    "        comment.append( userid[i] )\n",
    "        comment.append( message[i] )\n",
    "        all_content.append( comment )\n",
    "    \n",
    "    return all_content\n",
    "#forum_read(\"backup/activities/forum_1/forum.xml\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "чтение scheduler"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 21,
   "metadata": {},
   "outputs": [],
   "source": [
    "def scheduler_read (file):\n",
    "    all_content = []\n",
    "    slot = []\n",
    "\n",
    "    name = remove_symbols(\"[]'\", str(find_by_tag_from_tag(file, \"scheduler\", \"name\")))\n",
    "    slot_id = find_ID_attrib_by_tag(file, \"slot\")\n",
    "    teacherid = find_by_tag(file, \"teacherid\")\n",
    "    start_time = find_by_tag(file, \"starttime\")\n",
    "    duration = find_by_tag(file, \"duration\")\n",
    "    notes = find_by_tag(file, \"notes\")\n",
    "\n",
    "    #all_content.append( name )\n",
    "\n",
    "    for i in range( len(slot_id) ):\n",
    "        #id записи // id учителя // время начала в Unixtime  // продолжительность в минутах // заметки\n",
    "        slot = []\n",
    "        slot.append( slot_id[i] )\n",
    "        slot.append( teacherid[i] )\n",
    "        slot.append( start_time[i] )\n",
    "        slot.append( duration[i] )\n",
    "        slot.append( notes[i] )\n",
    "\n",
    "        all_content.append( slot )\n",
    "\n",
    "    #new_scheduler = replace_symbols(remove_symbols(\"[]'\", str(all_content)), '>, <', '> <' )\n",
    "    \n",
    "    return all_content\n",
    "#scheduler_read(\"backup/activities/scheduler_5/scheduler.xml\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "чтение quiz"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 22,
   "metadata": {},
   "outputs": [],
   "source": [
    "def quiz_read (file):\n",
    "    all_content = []\n",
    "    slot = []\n",
    "\n",
    "    name = remove_symbols(\"[]'\", str(find_by_tag_from_tag(file, \"quiz\", \"name\")))\n",
    "    question_instance = find_ID_attrib_by_tag(file, \"question_instance\")\n",
    "    questionbankentryid = find_by_tag(file, \"questionbankentryid\")\n",
    "    maxmark = find_by_tag(file, \"maxmark\")\n",
    "\n",
    "    #all_content.append( name )\n",
    "    \n",
    "    for i in range( len(question_instance) ):\n",
    "        #номер вороса в квизе // id вопроса из банка вопросов // баллы за правильный ответ\n",
    "        slot = []\n",
    "        #slot.append( question_instance[i] )\n",
    "        slot.append( questionbankentryid[i] )\n",
    "        #slot.append( maxmark[i] )\n",
    "\n",
    "        all_content.append( slot )\n",
    "\n",
    "        new_quiz = remove_symbols(\"[]'\", str(all_content))\n",
    "    \n",
    "    return new_quiz\n",
    "#quiz_read(\"backup/activities/quiz_12/quiz.xml\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "чтение glossary"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 23,
   "metadata": {},
   "outputs": [],
   "source": [
    "def glossary_read (file):\n",
    "    all_content = []\n",
    "    slot = []\n",
    "    \n",
    "    concept = find_by_tag_from_tag(file, \"entry\", \"concept\")\n",
    "    definition = []\n",
    "    #definition = find_by_tag_from_tag(file, \"entry\", \"definition\")\n",
    "\n",
    "    tree = ET.parse(file)\n",
    "    root = tree.getroot()\n",
    "    \n",
    "    for elem in root.iter('definition'):\n",
    "        text = elem.text\n",
    "        text = text.replace('\\n', ' ')  # заменяем символ переноса строки на пробел\n",
    "        definition.append( text )\n",
    "\n",
    "    for index in range( len(concept) ):\n",
    "        slot = []\n",
    "        slot.append( concept[index] )\n",
    "        slot.append( definition[index] )\n",
    "        all_content.append( slot )\n",
    "\n",
    "    return all_content\n",
    "\n",
    "#glossary_read(\"backup/activities/glossary_26/glossary.xml\")[2]"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "чтение банка воросов"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 24,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "'\\n# чтение банка воросов\\ndef bank_questions_read (file):\\n    all_conntant = []\\n    name = find_by_tag_from_tag(file, \"question\", \"name\")\\n    questiontext = find_by_tag_from_tag(file, \"question\", \"questiontext\")\\n    question_id = find_ID_attrib_by_tag(file, \"question\")\\n\\n    for i in range( len(name) ):\\n        content = []\\n        content.append(question_id[i])\\n        content.append(name[i])\\n        content.append(questiontext[i])\\n        all_conntant.append(content)\\n    \\n    return all_conntant\\n\\n#bank_questions_read(\"backup/questions.xml\\n'"
      ]
     },
     "execution_count": 24,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "\"\"\"\n",
    "# чтение банка воросов\n",
    "def bank_questions_read (file):\n",
    "    all_conntant = []\n",
    "    name = find_by_tag_from_tag(file, \"question\", \"name\")\n",
    "    questiontext = find_by_tag_from_tag(file, \"question\", \"questiontext\")\n",
    "    question_id = find_ID_attrib_by_tag(file, \"question\")\n",
    "\n",
    "    for i in range( len(name) ):\n",
    "        content = []\n",
    "        content.append(question_id[i])\n",
    "        content.append(name[i])\n",
    "        content.append(questiontext[i])\n",
    "        all_conntant.append(content)\n",
    "    \n",
    "    return all_conntant\n",
    "\n",
    "#bank_questions_read(\"backup/questions.xml\n",
    "\"\"\""
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "jp-MarkdownHeadingCollapsed": true
   },
   "source": [
    "# Функции чтения всех файлов"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "чтение всех видов файлов"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 25,
   "metadata": {},
   "outputs": [],
   "source": [
    "def read_file (file):\n",
    "    s = file\n",
    "    parts = s.rsplit('/')\n",
    "    res = parts[3]\n",
    "    \n",
    "    if res == \"page.xml\" :\n",
    "        return page_read (file)\n",
    "    elif res == \"choice.xml\" :\n",
    "        return choice_read (file)\n",
    "    elif res == \"book.xml\" :\n",
    "        return book_read (file)\n",
    "    elif res == \"feedback.xml\" :\n",
    "        return feedback_read (file)\n",
    "    elif res == \"survey.xml\" :\n",
    "        return survey_read (file)\n",
    "    elif res == \"forum.xml\" :\n",
    "        return forum_read (file)\n",
    "    elif res == \"scheduler.xml\" :\n",
    "        return scheduler_read (file)\n",
    "    elif res == \"quiz.xml\" :\n",
    "        return quiz_read (file)\n",
    "    elif res == \"glossary.xml\" :\n",
    "        return glossary_read (file)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "чтение всего backup файла"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 26,
   "metadata": {},
   "outputs": [],
   "source": [
    "def all_files_read ():\n",
    "    all_content = []\n",
    "    titles = find_by_tag_from_tag(\"backup/moodle_backup.xml\", \"activity\", \"title\")\n",
    "    types = find_by_tag(\"backup/moodle_backup.xml\", \"modulename\")\n",
    "    ids = find_by_tag(\"backup/moodle_backup.xml\", \"moduleid\")\n",
    "    #urls = []\n",
    "    #contents = []\n",
    "    dirs = activities_directories()\n",
    "    \n",
    "    for i in range ( len(dirs) ):\n",
    "        file = []\n",
    "        urls = \"\"\n",
    "        \n",
    "        contents = read_file(dirs[i])\n",
    "        orig_url = str( find_by_tag(\"backup/moodle_backup.xml\", \"original_wwwroot\") )\n",
    "\n",
    "        #формирование ссылки\n",
    "        symbols_to_remove = \" '[] \"\n",
    "        orig_url = remove_symbols(symbols_to_remove, orig_url)\n",
    "        urls = orig_url + \"/mod/\" + types[i] + \"/view.php\" +  \"?id=\" + ids[i]\n",
    "\n",
    "        file.append( urls )\n",
    "        file.append( dirs[i] )\n",
    "        file.append( types[i] )\n",
    "        file.append( titles[i] )\n",
    "        file.append( contents )\n",
    "        contextid = find_contextid_in_activity(dirs[i])[0]\n",
    "        file.append( contextid )\n",
    "        file.append( i+1 )\n",
    "        all_content.append( file )\n",
    "\n",
    "    #all_content.append(titles)\n",
    "    #all_content.append(types)\n",
    "    #all_content.append(urls)\n",
    "    #all_content.append(contents)\n",
    "    return all_content\n",
    "\n",
    "#all_files_read()[5]"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "jp-MarkdownHeadingCollapsed": true
   },
   "source": [
    "# Работа с файлами"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "чтение информации о файлах"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 27,
   "metadata": {},
   "outputs": [],
   "source": [
    "def files_read (file):\n",
    "    all_content = []\n",
    "    slot = []\n",
    "\n",
    "    contenthash = find_by_tag(file, \"contenthash\")\n",
    "    filename = find_by_tag(file, \"filename\")\n",
    "    contextid = find_by_tag(file, \"contextid\")\n",
    "\n",
    "    for i in range( len(contenthash) ):\n",
    "        if filename[i] != '.':\n",
    "            resource_id = ''\n",
    "            for j in range ( len(all_files_read()) ):\n",
    "                if contextid[i] == all_files_read()[j][5]:\n",
    "                    resource_id = j+1\n",
    "                \n",
    "            slot = []\n",
    "            slot.append( contenthash[i] )\n",
    "            slot.append( filename[i] )\n",
    "            #slot.append( contextid[i] )\n",
    "            slot.append( resource_id )\n",
    "    \n",
    "            all_content.append( slot )\n",
    "    \n",
    "    return all_content\n",
    "    \n",
    "#files_read(\"backup/files.xml\")\n",
    "#all_files_read()[5]"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "вывод информации о файлах"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 28,
   "metadata": {},
   "outputs": [],
   "source": [
    "def files_creation_and_information():\n",
    "    # Функция для переименования и копирования файлов\n",
    "    def rename_and_copy_files(file_info):\n",
    "        new_files_info = []\n",
    "        for info in file_info:\n",
    "            initial_name = info[0]\n",
    "            new_name = info[1]\n",
    "            additional_info = info[2]\n",
    "    \n",
    "            for root, dirs, files in os.walk('backup/files'):\n",
    "                for file in files:\n",
    "                    if file == initial_name:\n",
    "                        source_path = os.path.join(root, file)\n",
    "                        destination_path = os.path.join('backup/new_files', new_name)\n",
    "    \n",
    "                        shutil.copy2(source_path, destination_path)\n",
    "                        new_files_info.append([destination_path, additional_info])\n",
    "    \n",
    "        return new_files_info\n",
    "    \n",
    "    # Массив со структурой [начальное название файла, новое название файла, дополнительная информация о файле]\n",
    "    file_info = files_read(\"backup/files.xml\")\n",
    "    \n",
    "    # Проверяем, что папка new_files существует, если нет - создаем\n",
    "    if not os.path.exists('backup/new_files'):\n",
    "        os.makedirs('backup/new_files')\n",
    "    \n",
    "    # Вызываем функцию и сохраняем результат\n",
    "    new_files_info = rename_and_copy_files(file_info)\n",
    "    \n",
    "    # Выводим результат\n",
    "    return new_files_info\n",
    "\n",
    "#files_creation_and_information()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "jp-MarkdownHeadingCollapsed": true
   },
   "source": [
    "# Базовые функции для работы с БД"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "данные для авторизации в БД"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 29,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "'\\nhost = \"127.0.0.1\"\\nuser = \"postgres\"\\npassword = \"qwerty\"\\ndb_name = \"test\"\\n'"
      ]
     },
     "execution_count": 29,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "#from config import host, user, password, db_name\n",
    "\"\"\"\n",
    "host = \"127.0.0.1\"\n",
    "user = \"postgres\"\n",
    "password = \"qwerty\"\n",
    "db_name = \"test\"\n",
    "\"\"\""
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "функция для SQL запросов"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 30,
   "metadata": {},
   "outputs": [],
   "source": [
    "#функция для SQL запросов\n",
    "def sql(SQL_text):\n",
    "    try:\n",
    "        # connect to exist database\n",
    "        connection = psycopg2.connect(\n",
    "            host=host,\n",
    "            user=user,\n",
    "            password=password,\n",
    "            database=db_name    \n",
    "        )\n",
    "        connection.autocommit = True\n",
    "        \n",
    "        # the cursor for perfoming database operations\n",
    "        # cursor = connection.cursor()\n",
    "        \n",
    "        with connection.cursor() as cursor:\n",
    "            cursor.execute(\n",
    "                \"SELECT version();\"\n",
    "            )\n",
    "            #print(f\"Server version: {cursor.fetchone()}\")\n",
    "            res = cursor.fetchall()\n",
    "            \n",
    "        # create a new table\n",
    "        with connection.cursor() as cursor:\n",
    "             cursor.execute( SQL_text )\n",
    "             res = cursor.fetchall()\n",
    "            \n",
    "             #connection.commit()\n",
    "             #print(\"[INFO] Successfully\")\n",
    "        \n",
    "    except Exception as _ex:\n",
    "        #Error while working with PostgreSQL\n",
    "        print(\"[INFO] \", _ex)\n",
    "    finally:\n",
    "        if connection:\n",
    "            # cursor.close()\n",
    "            connection.close()\n",
    "            #print(\"[INFO] PostgreSQL connection closed\")\n",
    "    return res\n",
    "\n",
    "#sql(\"SELECT version();\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 31,
   "metadata": {},
   "outputs": [],
   "source": [
    "def get_schema_name():\n",
    "    schema_name = \"edu.\"\n",
    "    return schema_name\n",
    "\n",
    "SN = get_schema_name()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "функция для просмотра содержимого таблиц"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 32,
   "metadata": {},
   "outputs": [],
   "source": [
    "def show_tables(host, user, password, db_name, table):\n",
    "    all_ = \"\"\n",
    "    \n",
    "    conn = psycopg2.connect(\n",
    "        host=host,\n",
    "        user=user,\n",
    "        password=password,\n",
    "        dbname=db_name\n",
    "    )\n",
    "    cur = conn.cursor()\n",
    "\n",
    "    cur.execute(f\"SELECT table_name FROM information_schema.tables WHERE table_schema='{remove_last_symbol(SN)}';\")\n",
    "    tables = cur.fetchall()\n",
    "\n",
    "    \"\"\"\n",
    "    for table in tables:\n",
    "        table_name = table[0]\n",
    "        all_ += f\"Table: {table_name}\"\n",
    "        all_ += '<br>'\n",
    "        cur.execute(f\"SELECT * FROM {SN}{table_name};\")\n",
    "        rows = cur.fetchall()\n",
    "        for row in rows:\n",
    "            all_ += str(row)\n",
    "            all_ += '<br>'\n",
    "\n",
    "        all_ += '<br>'\n",
    "    \"\"\"\n",
    "    all_ += f\"Table: {table}\"\n",
    "    all_ += '<br>'\n",
    "    cur.execute(f\"SELECT * FROM {SN}{table};\")\n",
    "    rows = cur.fetchall()\n",
    "    for row in rows:\n",
    "        all_ += remove_symbols( \"'\", str(row) )\n",
    "        all_ += '<br>'\n",
    "\n",
    "    all_ += '<br>'\n",
    "\n",
    "    conn.close()\n",
    "    return all_\n",
    "    \n",
    "#show_tables(host, user, password, db_name)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "функция удаления всех таблиц"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 33,
   "metadata": {},
   "outputs": [],
   "source": [
    "def delete_all_tables():\n",
    "    # Устанавливаем соединение с базой данных\n",
    "    conn = psycopg2.connect(\n",
    "        host=host,\n",
    "        user=user,\n",
    "        password=password,\n",
    "        database=db_name\n",
    "    )\n",
    "    cur = conn.cursor()\n",
    "\n",
    "    # Получаем список всех таблиц в базе данных\n",
    "    cur.execute(\"SELECT table_name FROM information_schema.tables WHERE table_schema='public'\")\n",
    "    tables = [table[0] for table in cur.fetchall()]\n",
    "\n",
    "    # Удаляем каждую таблицу из списка\n",
    "    for table in tables:\n",
    "        cur.execute(f\"DROP TABLE IF EXISTS {table} CASCADE\")\n",
    "\n",
    "    conn.commit()\n",
    "    conn.close()\n",
    "\n",
    "\n",
    "#delete_all_tables()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "jp-MarkdownHeadingCollapsed": true
   },
   "source": [
    "# Создание таблиц"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 34,
   "metadata": {},
   "outputs": [],
   "source": [
    "def creation_main_tables( create_or_drop ):\n",
    "    \n",
    "    create = \"\"\"\n",
    "    -- edu.file_type определение\n",
    "    \n",
    "    -- Drop table\n",
    "    \n",
    "    -- DROP TABLE edu.file_type;\n",
    "    \n",
    "    CREATE TABLE edu.file_type (\n",
    "    \tid serial4 NOT NULL,\n",
    "    \t\"name\" varchar NULL,\n",
    "    \t\"extension\" varchar NULL,\n",
    "    \tCONSTRAINT file_type_pk PRIMARY KEY (id)\n",
    "    );\n",
    "    \n",
    "    \n",
    "    -- edu.lms определение\n",
    "    \n",
    "    -- Drop table\n",
    "    \n",
    "    -- DROP TABLE edu.lms;\n",
    "    \n",
    "    CREATE TABLE edu.lms (\n",
    "    \tid serial4 NOT NULL,\n",
    "    \t\"name\" varchar NOT NULL,\n",
    "    \tCONSTRAINT lms_pk PRIMARY KEY (id)\n",
    "    );\n",
    "    \n",
    "    \n",
    "    -- edu.lms_resource_type определение\n",
    "    \n",
    "    -- Drop table\n",
    "    \n",
    "    -- DROP TABLE edu.lms_resource_type;\n",
    "    \n",
    "    CREATE TABLE edu.lms_resource_type (\n",
    "    \tid serial4 NOT NULL,\n",
    "    \t\"name\" varchar NOT NULL,\n",
    "    \tCONSTRAINT lms_resource_type_pk PRIMARY KEY (id)\n",
    "    );\n",
    "    \n",
    "    \n",
    "    -- edu.resource определение\n",
    "    \n",
    "    -- Drop table\n",
    "    \n",
    "    -- DROP TABLE edu.resource;\n",
    "    \n",
    "    CREATE TABLE edu.resource (\n",
    "    \tid bigserial NOT NULL,\n",
    "    \turl varchar NULL,\n",
    "    \t\"name\" varchar NULL,\n",
    "    \tdescription text NULL,\n",
    "    \ttags json NULL,\n",
    "    \tCONSTRAINT edu_resource_pk PRIMARY KEY (id)\n",
    "    );\n",
    "    \n",
    "    \n",
    "    -- edu.comment_resource определение\n",
    "    \n",
    "    -- Drop table\n",
    "    \n",
    "    -- DROP TABLE edu.comment_resource;\n",
    "    \n",
    "    CREATE TABLE edu.comment_resource (\n",
    "    \tid bigserial NOT NULL,\n",
    "    \treplied_comment_id int8 NULL,\n",
    "    \tuser_id int8 NOT NULL,\n",
    "    \t\"text\" text NULL,\n",
    "    \tresource_id int8 NOT NULL,\n",
    "    \tCONSTRAINT comment_resource_pk PRIMARY KEY (id),\n",
    "    \tCONSTRAINT comment_resource_resource_fk FOREIGN KEY (resource_id) REFERENCES edu.resource(id) ON DELETE RESTRICT ON UPDATE CASCADE\n",
    "    );\n",
    "    \n",
    "    \n",
    "    -- edu.edu_announcment определение\n",
    "    \n",
    "    -- Drop table\n",
    "    \n",
    "    -- DROP TABLE edu.edu_announcment;\n",
    "    \n",
    "    CREATE TABLE edu.edu_announcment (\n",
    "    \tid bigserial NOT NULL,\n",
    "    \t\"name\" varchar NULL,\n",
    "    \tresource_id int8 NOT NULL,\n",
    "    \tCONSTRAINT edu_announcment_pk PRIMARY KEY (id),\n",
    "    \tCONSTRAINT edu_announcment_fk FOREIGN KEY (resource_id) REFERENCES edu.resource(id) ON DELETE CASCADE ON UPDATE CASCADE\n",
    "    );\n",
    "    \n",
    "    \n",
    "    -- edu.edu_discussion определение\n",
    "    \n",
    "    -- Drop table\n",
    "    \n",
    "    -- DROP TABLE edu.edu_discussion;\n",
    "    \n",
    "    CREATE TABLE edu.edu_discussion (\n",
    "    \tid bigserial NOT NULL,\n",
    "    \t\"name\" varchar NULL,\n",
    "    \tresource_id int8 NOT NULL,\n",
    "    \tCONSTRAINT edu_discussion_pk PRIMARY KEY (id),\n",
    "    \tCONSTRAINT edu_discussion_resource_fk FOREIGN KEY (resource_id) REFERENCES edu.resource(id) ON DELETE RESTRICT ON UPDATE CASCADE\n",
    "    );\n",
    "    \n",
    "    \n",
    "    -- edu.edu_lab_report определение\n",
    "    \n",
    "    -- Drop table\n",
    "    \n",
    "    -- DROP TABLE edu.edu_lab_report;\n",
    "    \n",
    "    CREATE TABLE edu.edu_lab_report (\n",
    "    \tid bigserial NOT NULL,\n",
    "    \tresource_id int8 NOT NULL,\n",
    "    \tCONSTRAINT edu_lab_report_pk PRIMARY KEY (id),\n",
    "    \tCONSTRAINT edu_lab_report_fk FOREIGN KEY (resource_id) REFERENCES edu.resource(id) ON DELETE CASCADE ON UPDATE CASCADE\n",
    "    );\n",
    "    \n",
    "    \n",
    "    -- edu.edu_resource_lecture определение\n",
    "    \n",
    "    -- Drop table\n",
    "    \n",
    "    -- DROP TABLE edu.edu_resource_lecture;\n",
    "    \n",
    "    CREATE TABLE edu.edu_resource_lecture (\n",
    "    \tid bigserial NOT NULL,\n",
    "    \t\"name\" text NULL,\n",
    "    \tresource_id int8 NOT NULL,\n",
    "    \tsummary text NULL,\n",
    "    \tCONSTRAINT edu_resource_lecture_pk PRIMARY KEY (id),\n",
    "    \tCONSTRAINT edu_resource_lecture_fk FOREIGN KEY (resource_id) REFERENCES edu.resource(id) ON DELETE CASCADE ON UPDATE CASCADE\n",
    "    );\n",
    "    \n",
    "    \n",
    "    -- edu.edu_survey определение\n",
    "    \n",
    "    -- Drop table\n",
    "    \n",
    "    -- DROP TABLE edu.edu_survey;\n",
    "    \n",
    "    CREATE TABLE edu.edu_survey (\n",
    "    \tid bigserial NOT NULL,\n",
    "    \t\"name\" varchar NULL,\n",
    "    \tresource_id int8 NOT NULL,\n",
    "    \tCONSTRAINT edu_survey_pk PRIMARY KEY (id),\n",
    "    \tCONSTRAINT edu_survey_resource_fk FOREIGN KEY (resource_id) REFERENCES edu.resource(id) ON DELETE RESTRICT ON UPDATE CASCADE\n",
    "    );\n",
    "    \n",
    "    \n",
    "    -- edu.edu_term определение\n",
    "    \n",
    "    -- Drop table\n",
    "    \n",
    "    -- DROP TABLE edu.edu_term;\n",
    "    \n",
    "    CREATE TABLE edu.edu_term (\n",
    "    \tid bigserial NOT NULL,\n",
    "    \t\"name\" varchar NULL,\n",
    "    \t\"text\" text NULL,\n",
    "    \tresource_id int8 NOT NULL,\n",
    "    \tCONSTRAINT edu_term_pk PRIMARY KEY (id),\n",
    "    \tCONSTRAINT edu_term_fk FOREIGN KEY (resource_id) REFERENCES edu.resource(id) ON DELETE CASCADE ON UPDATE CASCADE\n",
    "    );\n",
    "    \n",
    "    \n",
    "    -- edu.edu_test определение\n",
    "    \n",
    "    -- Drop table\n",
    "    \n",
    "    -- DROP TABLE edu.edu_test;\n",
    "    \n",
    "    CREATE TABLE edu.edu_test (\n",
    "    \tid bigserial NOT NULL,\n",
    "    \t\"name\" varchar NULL,\n",
    "    \tresource_id int8 NOT NULL,\n",
    "    \tCONSTRAINT edu_text_pk PRIMARY KEY (id),\n",
    "    \tCONSTRAINT edu_text_resource_fk FOREIGN KEY (resource_id) REFERENCES edu.resource(id) ON DELETE RESTRICT ON UPDATE CASCADE\n",
    "    );\n",
    "    \n",
    "    \n",
    "    -- edu.edu_theme определение\n",
    "    \n",
    "    -- Drop table\n",
    "    \n",
    "    -- DROP TABLE edu.edu_theme;\n",
    "    \n",
    "    CREATE TABLE edu.edu_theme (\n",
    "    \tid bigserial NOT NULL,\n",
    "    \tresource_id int8 NOT NULL,\n",
    "    \t\"name\" text NULL,\n",
    "    \tCONSTRAINT edu_theme_pk PRIMARY KEY (id),\n",
    "    \tCONSTRAINT edu_theme_fk FOREIGN KEY (resource_id) REFERENCES edu.resource(id) ON DELETE CASCADE ON UPDATE CASCADE\n",
    "    );\n",
    "    \n",
    "    \n",
    "    -- edu.file_resource_description определение\n",
    "    \n",
    "    -- Drop table\n",
    "    \n",
    "    -- DROP TABLE edu.file_resource_description;\n",
    "    \n",
    "    CREATE TABLE edu.file_resource_description (\n",
    "    \tid bigserial NOT NULL,\n",
    "    \ttype_id int4 NULL,\n",
    "    \t\"name\" varchar NOT NULL,\n",
    "    \tresource_id int8 NULL,\n",
    "    \t\"path\" varchar NOT NULL,\n",
    "    \tCONSTRAINT file_resource_description_pk PRIMARY KEY (id),\n",
    "    \tCONSTRAINT file_resource_description_fk FOREIGN KEY (type_id) REFERENCES edu.file_type(id) ON DELETE RESTRICT ON UPDATE CASCADE,\n",
    "    \tCONSTRAINT file_resource_description_fk_2 FOREIGN KEY (resource_id) REFERENCES edu.resource(id) ON DELETE CASCADE ON UPDATE CASCADE\n",
    "    );\n",
    "    \n",
    "    \n",
    "    -- edu.html_resource определение\n",
    "    \n",
    "    -- Drop table\n",
    "    \n",
    "    -- DROP TABLE edu.html_resource;\n",
    "    \n",
    "    CREATE TABLE edu.html_resource (\n",
    "    \tid bigserial NOT NULL,\n",
    "    \thtml text NULL,\n",
    "    \tresource_id int8 NOT NULL,\n",
    "    \tCONSTRAINT html_resource1_pk PRIMARY KEY (id),\n",
    "    \tCONSTRAINT html_resource_resource_fk FOREIGN KEY (resource_id) REFERENCES edu.resource(id) ON DELETE RESTRICT ON UPDATE RESTRICT\n",
    "    );\n",
    "    \n",
    "    \n",
    "    -- edu.lms_resource определение\n",
    "    \n",
    "    -- Drop table\n",
    "    \n",
    "    -- DROP TABLE edu.lms_resource;\n",
    "    \n",
    "    CREATE TABLE edu.lms_resource (\n",
    "    \tid bigserial NOT NULL,\n",
    "    \taccess_rights xml NULL,\n",
    "    \tmodule_config xml NULL,\n",
    "    \tview_config xml NULL,\n",
    "    \tresource_id int8 NOT NULL,\n",
    "    \tCONSTRAINT lms_resource_pk PRIMARY KEY (id),\n",
    "    \tCONSTRAINT lms_resource_fk FOREIGN KEY (resource_id) REFERENCES edu.resource(id) ON DELETE CASCADE ON UPDATE CASCADE\n",
    "    );\n",
    "    \n",
    "    \n",
    "    -- edu.original_lms_resource определение\n",
    "    \n",
    "    -- Drop table\n",
    "    \n",
    "    -- DROP TABLE edu.original_lms_resource;\n",
    "    \n",
    "    CREATE TABLE edu.original_lms_resource (\n",
    "    \tid bigserial NOT NULL,\n",
    "    \ttype_id int8 NULL,\n",
    "    \tplatform_id int8 NULL,\n",
    "    \t\"content\" text NULL,\n",
    "    \tresource_id int8 NULL,\n",
    "    \tCONSTRAINT original_lms_resource_pk PRIMARY KEY (id),\n",
    "    \tCONSTRAINT original_lms_resource_lms_fk FOREIGN KEY (platform_id) REFERENCES edu.lms(id) ON DELETE RESTRICT ON UPDATE CASCADE,\n",
    "    \tCONSTRAINT original_lms_resource_lms_resource_type_fk FOREIGN KEY (type_id) REFERENCES edu.lms_resource_type(id) ON DELETE RESTRICT ON UPDATE CASCADE,\n",
    "    \tCONSTRAINT original_lms_resource_resource_fk FOREIGN KEY (resource_id) REFERENCES edu.resource(id) ON DELETE RESTRICT ON UPDATE CASCADE\n",
    "    );\n",
    "    \n",
    "    \n",
    "    -- edu.questions_resource определение\n",
    "    \n",
    "    -- Drop table\n",
    "    \n",
    "    -- DROP TABLE edu.questions_resource;\n",
    "    \n",
    "    CREATE TABLE edu.questions_resource (\n",
    "    \tid bigserial NOT NULL,\n",
    "    \tquestions text NULL,\n",
    "    \tanswers text NULL,\n",
    "    \tresource_id int8 NOT NULL,\n",
    "    \tCONSTRAINT questions_resource_pk PRIMARY KEY (id),\n",
    "    \tCONSTRAINT questions_resource_resource_fk FOREIGN KEY (resource_id) REFERENCES edu.resource(id) ON DELETE RESTRICT ON UPDATE CASCADE\n",
    "    );\n",
    "    \n",
    "    \n",
    "    -- edu.resource_relations определение\n",
    "    \n",
    "    -- Drop table\n",
    "    \n",
    "    -- DROP TABLE edu.resource_relations;\n",
    "    \n",
    "    CREATE TABLE edu.resource_relations (\n",
    "    \tid bigserial NOT NULL,\n",
    "    \tresource_one_id int8 NOT NULL,\n",
    "    \tresource_two_id int8 NOT NULL,\n",
    "    \tCONSTRAINT resource_relations_pk PRIMARY KEY (id),\n",
    "    \tCONSTRAINT resource_relations_fk FOREIGN KEY (resource_one_id) REFERENCES edu.resource(id) ON DELETE RESTRICT ON UPDATE CASCADE,\n",
    "    \tCONSTRAINT resource_relations_fk_1 FOREIGN KEY (resource_two_id) REFERENCES edu.resource(id) ON DELETE RESTRICT ON UPDATE CASCADE\n",
    "    );\n",
    "    \n",
    "    \n",
    "    -- edu.schedule_resource определение\n",
    "    \n",
    "    -- Drop table\n",
    "    \n",
    "    -- DROP TABLE edu.schedule_resource;\n",
    "    \n",
    "    CREATE TABLE edu.schedule_resource (\n",
    "    \tid bigserial NOT NULL,\n",
    "    \tteacher_id int8 NOT NULL,\n",
    "    \tstart_time int8 NOT NULL,\n",
    "    \tduration int8 NULL,\n",
    "    \tnotes text NULL,\n",
    "    \tresource_id int8 NOT NULL,\n",
    "    \tCONSTRAINT schedule_resource_pk PRIMARY KEY (id),\n",
    "    \tCONSTRAINT schedule_resource_resource_fk FOREIGN KEY (resource_id) REFERENCES edu.resource(id) ON DELETE RESTRICT ON UPDATE CASCADE\n",
    "    );\n",
    "    \n",
    "    \n",
    "    -- edu.video_resource_description определение\n",
    "    \n",
    "    -- Drop table\n",
    "    \n",
    "    -- DROP TABLE edu.video_resource_description;\n",
    "    \n",
    "    CREATE TABLE edu.video_resource_description (\n",
    "    \tid bigserial NOT NULL,\n",
    "    \t\"name\" varchar NULL,\n",
    "    \turl varchar NULL,\n",
    "    \tduration int8 NULL,\n",
    "    \tresource_id int8 NULL,\n",
    "    \tauthor varchar NULL,\n",
    "    \tCONSTRAINT video_resource_description_pk PRIMARY KEY (id),\n",
    "    \tCONSTRAINT video_resource_description_resource_fk FOREIGN KEY (resource_id) REFERENCES edu.resource(id) ON DELETE RESTRICT ON UPDATE CASCADE\n",
    "    );\n",
    "    \"\"\"\n",
    "    \n",
    "    drop = \"\"\"\n",
    "    DROP TABLE IF EXISTS edu.file_type CASCADE;\n",
    "    DROP TABLE IF EXISTS edu.lms CASCADE;\n",
    "    DROP TABLE IF EXISTS edu.lms_resource_type CASCADE;\n",
    "    DROP TABLE IF EXISTS edu.resource CASCADE;\n",
    "    DROP TABLE IF EXISTS edu.edu_announcment CASCADE;\n",
    "    DROP TABLE IF EXISTS edu.edu_lab_report CASCADE;\n",
    "    DROP TABLE IF EXISTS edu.edu_resource_lecture CASCADE;\n",
    "    DROP TABLE IF EXISTS edu.edu_term CASCADE;\n",
    "    DROP TABLE IF EXISTS edu.edu_theme CASCADE;\n",
    "    DROP TABLE IF EXISTS edu.file_resource_description CASCADE;\n",
    "    DROP TABLE IF EXISTS edu.html_resource CASCADE;\n",
    "    DROP TABLE IF EXISTS edu.lms_resource CASCADE;\n",
    "    DROP TABLE IF EXISTS edu.original_lms_resource CASCADE;\n",
    "    DROP TABLE IF EXISTS edu.resource_relations CASCADE;\n",
    "    DROP TABLE IF EXISTS edu.video_resource_description CASCADE;\n",
    "\n",
    "    DROP TABLE IF EXISTS edu.edu_discussion CASCADE;\n",
    "    DROP TABLE IF EXISTS edu.comment_resource CASCADE;\n",
    "    DROP TABLE IF EXISTS edu.edu_test CASCADE;\n",
    "    DROP TABLE IF EXISTS edu.edu_survey CASCADE;\n",
    "    DROP TABLE IF EXISTS edu.questions_resource CASCADE;\n",
    "    DROP TABLE IF EXISTS edu.schedule_resource CASCADE;\n",
    "    \"\"\"\n",
    "    if create_or_drop == \"create\":\n",
    "        return create\n",
    "    elif create_or_drop == \"drop\":\n",
    "        return drop\n",
    "\n",
    "\n",
    "#sql( creation_main_tables(\"drop\") )\n",
    "#sql( creation_main_tables(\"create\") )"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Перезагрузка БД"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 35,
   "metadata": {},
   "outputs": [],
   "source": [
    "################################################################################################################################\n",
    "#### Перезагрузка БД\n",
    "\n",
    "def tables_reload():\n",
    "    sql( creation_main_tables(\"drop\") )\n",
    "    sql( creation_main_tables(\"create\") )\n",
    "    return \"Таблицы успешно очищены\"\n",
    "\n",
    "#tables_reload()\n",
    "################################################################################################################################"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "jp-MarkdownHeadingCollapsed": true
   },
   "source": [
    "# Добавление в БД original_lms_resource SELECT"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "select ID recource by URL"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 36,
   "metadata": {},
   "outputs": [],
   "source": [
    "def select_resource_BY_URL(url):\n",
    "    return remove_sql_symbol( sql( f\"SELECT id FROM {SN}resource WHERE url = '{url}' \" ) )\n",
    "\n",
    "#select_resource_BY_URL('http://51.250.4.123/moodle/my/courses.php')"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "select ID original_lms_resource by RESOURCE_URL"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 37,
   "metadata": {},
   "outputs": [],
   "source": [
    "def select_original_lms_resource_BY_RESOURCE_URL(resource_url):\n",
    "    resource_id = select_resource_BY_URL(resource_url)\n",
    "    if resource_id != \"\":\n",
    "        return remove_sql_symbol( sql( f\"SELECT id FROM {SN}original_lms_resource WHERE resource_id = {resource_id} \" ) )\n",
    "\n",
    "#select_original_lms_resource_BY_RESOURCE_URL('http://51.250.4.123/moodle/my/courses.php')\n",
    "#sql( f\"SELECT id FROM original_lms_resource WHERE resource_id = '2' \" )"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "select ID lms by NAME"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 38,
   "metadata": {},
   "outputs": [],
   "source": [
    "def select_lms_BY_NAME(name):\n",
    "    return remove_sql_symbol( sql( f\"SELECT id FROM {SN}lms WHERE name = '{name}' \" ) )\n",
    "\n",
    "#select_lms_BY_NAME('lms')"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "select ID lms_resource_type by NAME"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 39,
   "metadata": {},
   "outputs": [],
   "source": [
    "def select_lms_resource_type_BY_NAME(name):\n",
    "    return remove_sql_symbol( sql( f\"SELECT id FROM {SN}lms_resource_type WHERE name = '{name}' \" ) )\n",
    "\n",
    "#select_lms_resource_type_BY_NAME('url')"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "jp-MarkdownHeadingCollapsed": true
   },
   "source": [
    "# Добавление в БД original_lms_resource INSERT"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "insert resource"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 40,
   "metadata": {},
   "outputs": [],
   "source": [
    "def insert_resource(url, name, description):\n",
    "    if select_resource_BY_URL(url) == '':\n",
    "        sql( f\"INSERT INTO {SN}resource(url, name, description) VALUES('{url}', '{name}', '{description}')\" )\n",
    "        return \"Элемент добавлен (insert_resource)\"\n",
    "    else:\n",
    "        return \"Такой элемент уже cуществует (insert_resource)\"\n",
    "\n",
    "#insert_resource('url', 'name', 'description')"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "insert original_lms_resource"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 41,
   "metadata": {},
   "outputs": [],
   "source": [
    "def insert_original_lms_resource(resource_type, platform, content, resource_url):\n",
    "    resource_type_id = select_lms_resource_type_BY_NAME (resource_type)\n",
    "    platform_id = select_lms_BY_NAME (platform)\n",
    "    resource_id = select_resource_BY_URL (resource_url)\n",
    "    is_elem_exist = select_original_lms_resource_BY_RESOURCE_URL (resource_url)\n",
    "    \n",
    "    if (is_elem_exist == \"\") or (is_elem_exist == None):\n",
    "        \n",
    "        if (resource_type_id != \"\") and (platform_id != \"\") and (resource_id != \"\"):\n",
    "            sql( f\"INSERT INTO {SN}original_lms_resource(type_id, platform_id, content, resource_id) VALUES({resource_type_id}, {platform_id}, '{content}', {resource_id})\" )\n",
    "            return \"Успешно добавлено (insert_original_lms_resource)\"\n",
    "        elif (resource_type_id == ''):\n",
    "            return \"Ошибка resource_type_id == '' (insert_original_lms_resource)\"\n",
    "        elif (platform_id == ''):\n",
    "            return \"Ошибка platform_id == '' (insert_original_lms_resource)\"\n",
    "        elif (resource_id == ''):\n",
    "            return \"Ошибка resource_id =='' (insert_original_lms_resource)\"\n",
    "        \n",
    "        else:\n",
    "            return \"Ошибка добавления (insert_original_lms_resource)\"\n",
    "    else:\n",
    "        return \"Такой элемент уже существует (insert_original_lms_resource)\"\n",
    "    \n",
    "#insert_original_lms_resource('page', 'Moodle', 'content', 'http://51.250.4.123/moodle/my/courses.php')\n",
    "#print( select_original_lms_resource_BY_RESOURCE_URL ('http://51.250.4.123/moodle/my/courses.php') )"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "insert lms"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 42,
   "metadata": {},
   "outputs": [],
   "source": [
    "def insert_lms(name):\n",
    "    if select_lms_BY_NAME(name) == '':\n",
    "        sql( f\"INSERT INTO {SN}lms(name) VALUES('{name}')\" )\n",
    "        return \"Элемент добавлен (insert_lms)\"\n",
    "    else:\n",
    "        return \"Такой элемент уже cуществует (insert_lms)\"\n",
    "\n",
    "#insert_lms(\"lms\")"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "insert lms_resource_type"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 43,
   "metadata": {},
   "outputs": [],
   "source": [
    "def insert_lms_resource_type(name):\n",
    "    if select_lms_resource_type_BY_NAME(name) == '':\n",
    "        sql( f\"INSERT INTO {SN}lms_resource_type(name) VALUES('{name}')\" )\n",
    "        return \"Элемент добавлен (insert_lms_resource_type)\"\n",
    "    else:\n",
    "        return \"Такой элемент уже cуществует (insert_lms_resource_type)\"\n",
    "\n",
    "#insert_lms_resource_type('page')"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "insert FULL_original_resource"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 44,
   "metadata": {},
   "outputs": [],
   "source": [
    "def insert_FULL_original_resource(resource_name, resource_url, resource_description, lms_resource_type_name, lms_name, content):\n",
    "    res_1 = insert_resource(resource_url, resource_name, resource_description)\n",
    "    res_2 = insert_lms(lms_name)\n",
    "    res_3 = insert_lms_resource_type(lms_resource_type_name)\n",
    "    res_4 = insert_original_lms_resource(lms_resource_type_name, lms_name, content, resource_url)\n",
    "\n",
    "    return f\"{res_1} || {res_2} || {res_3} || {res_4}\"\n",
    "\n",
    "#insert_FULL_original_resource('Ресурс 1', 'http://51.250.4.123/moodle/my/courses.php', 'Описание', 'page', 'Moodle', 'content')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 45,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Остатки от работы\n",
    "\n",
    "#insert_resource('http://51.250.4.123/moodle/my/courses.php', 'Ресурс 1', 'Описание')\n",
    "#insert_lms('Moodle')\n",
    "#insert_lms_resource_type('page')\n",
    "#insert_original_lms_resource('page', 'Moodle', 'content', 'http://51.250.4.123/moodle/my/courses.php')\n",
    "\n",
    "#insert_resource(resource_url, resource_name, resource_description)\n",
    "#insert_lms(lms_name)\n",
    "#insert_lms_resource_type(lms_resource_type_name)\n",
    "#insert_original_lms_resource(lms_resource_type_name, lms_name, content, resource_url)\n",
    "\n",
    "#resource_name = 'Ресурс 1'\n",
    "#resource_url = 'http://51.250.4.123/moodle/my/courses.php'\n",
    "#resource_description = 'Описание'\n",
    "#lms_resource_type_name = 'page'\n",
    "#lms_name = 'Moodle'\n",
    "#content = 'content'\n",
    "#insert_FULL_original_resource(resource_name, resource_url, resource_description, lms_resource_type_name, lms_name, content)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "jp-MarkdownHeadingCollapsed": true
   },
   "source": [
    "# Добавление в БД edu SELECT"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "select_edu_theme_BY_RESOURCE_ID"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 46,
   "metadata": {},
   "outputs": [],
   "source": [
    "def select_edu_theme_BY_RESOURCE_ID(resource_id):\n",
    "    return remove_sql_symbol( sql( f\"SELECT id FROM {SN}edu_theme WHERE resource_id = {resource_id} \" ) )\n",
    "\n",
    "#select_edu_theme_BY_RESOURCE_ID(1)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "select_edu_announcment_BY_RESOURCE_ID"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 47,
   "metadata": {},
   "outputs": [],
   "source": [
    "def select_edu_announcment_BY_RESOURCE_ID(resource_id):\n",
    "    return remove_sql_symbol( sql( f\"SELECT name FROM {SN}edu_announcment WHERE resource_id = {resource_id} \" ) )\n",
    "\n",
    "#select_edu_announcment_BY_RESOURCE_ID(1)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "select_edu_announcment_BY_RESOURCE_ID"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 48,
   "metadata": {},
   "outputs": [],
   "source": [
    "def select_edu_lab_report_BY_RESOURCE_ID(resource_id):\n",
    "    return remove_sql_symbol( sql( f\"SELECT id FROM {SN}edu_lab_report WHERE resource_id = {resource_id} \" ) )\n",
    "\n",
    "#select_edu_lab_report_BY_RESOURCE_ID(1)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "select_edu_resource_lecture_BY_RESOURCE_ID"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 49,
   "metadata": {},
   "outputs": [],
   "source": [
    "def select_edu_resource_lecture_BY_RESOURCE_ID(resource_id):\n",
    "    return remove_sql_symbol( sql( f\"SELECT name FROM {SN}edu_resource_lecture WHERE resource_id = {resource_id} \" ) )\n",
    "\n",
    "#select_edu_resource_lecture_BY_RESOURCE_ID(1)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "select_edu_term_BY_RESOURCE_ID"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 50,
   "metadata": {},
   "outputs": [],
   "source": [
    "def select_edu_term_BY_RESOURCE_ID(resource_id):\n",
    "    return remove_sql_symbol( sql( f\"SELECT name FROM {SN}edu_term WHERE resource_id = {resource_id} \" ) )\n",
    "\n",
    "#select_edu_term_BY_RESOURCE_ID(1)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "select_edu_survey_BY_RESOURCE_ID"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 51,
   "metadata": {},
   "outputs": [],
   "source": [
    "def select_edu_survey_BY_RESOURCE_ID(resource_id):\n",
    "    return remove_sql_symbol( sql( f\"SELECT id FROM {SN}edu_survey WHERE resource_id = {resource_id} \" ) )\n",
    "\n",
    "#select_edu_survey_BY_RESOURCE_ID(1)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "select_edu_test_BY_RESOURCE_ID"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 52,
   "metadata": {},
   "outputs": [],
   "source": [
    "def select_edu_test_BY_RESOURCE_ID(resource_id):\n",
    "    return remove_sql_symbol( sql( f\"SELECT id FROM {SN}edu_test WHERE resource_id = {resource_id} \" ) )\n",
    "\n",
    "#select_edu_test_BY_RESOURCE_ID(1)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "select_edu_discussion_BY_RESOURCE_ID"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 53,
   "metadata": {},
   "outputs": [],
   "source": [
    "def select_edu_discussion_BY_RESOURCE_ID(resource_id):\n",
    "    return remove_sql_symbol( sql( f\"SELECT id FROM {SN}edu_discussion WHERE resource_id = {resource_id} \" ) )\n",
    "\n",
    "#select_edu_discussion_BY_RESOURCE_ID(1)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "jp-MarkdownHeadingCollapsed": true
   },
   "source": [
    "# Добавление в БД edu INSERT"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "insert_edu_theme"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 54,
   "metadata": {},
   "outputs": [],
   "source": [
    "def insert_edu_theme(name, resource_id):\n",
    "    if select_edu_theme_BY_RESOURCE_ID(resource_id) == '':\n",
    "        sql( f\"INSERT INTO {SN}edu_theme(name, resource_id) VALUES('{name}', {resource_id})\" )\n",
    "        return \"Элемент добавлен (insert_edu_theme)\"\n",
    "    else:\n",
    "        return \"Такой элемент уже cуществует (insert_edu_theme)\"\n",
    "\n",
    "#insert_edu_theme('Название темы', 1)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "insert_edu_announcment"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 55,
   "metadata": {},
   "outputs": [],
   "source": [
    "def insert_edu_announcment(name, resource_id):\n",
    "    if select_edu_announcment_BY_RESOURCE_ID(resource_id) == '':\n",
    "        sql( f\"INSERT INTO {SN}edu_announcment(name, resource_id) VALUES('{name}', {resource_id})\" )\n",
    "        return \"Элемент добавлен (insert_edu_announcment)\"\n",
    "    else:\n",
    "        return \"Такой элемент уже cуществует (insert_edu_announcment)\"\n",
    "\n",
    "#insert_edu_announcment('Название опроса', 1)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "insert_edu_lab_report"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 56,
   "metadata": {},
   "outputs": [],
   "source": [
    "def insert_edu_lab_report(resource_id):\n",
    "    if select_edu_lab_report_BY_RESOURCE_ID(resource_id) == '':\n",
    "        sql( f\"INSERT INTO {SN}edu_lab_report(resource_id) VALUES({resource_id})\" )\n",
    "        return \"Элемент добавлен (insert_edu_lab_report)\"\n",
    "    else:\n",
    "        return \"Такой элемент уже cуществует (insert_edu_lab_report)\"\n",
    "\n",
    "#insert_edu_lab_report(1)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "insert_edu_resource_lecture"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 57,
   "metadata": {},
   "outputs": [],
   "source": [
    "def insert_edu_resource_lecture(name, resource_id, summary):\n",
    "    if select_edu_resource_lecture_BY_RESOURCE_ID(resource_id) == '':\n",
    "        sql( f\"INSERT INTO {SN}edu_resource_lecture(name, resource_id, summary) VALUES('{name}', {resource_id}, '{summary}')\" )\n",
    "        return \"Элемент добавлен (insert_edu_resource_lecture)\"\n",
    "    else:\n",
    "        return \"Такой элемент уже cуществует (insert_edu_resource_lecture)\"\n",
    "\n",
    "#insert_edu_resource_lecture('Название лекции', 1, 'Краткое описание')"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "insert_edu_term"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 58,
   "metadata": {},
   "outputs": [],
   "source": [
    "def insert_edu_term(name, resource_id, text):\n",
    "    #if select_edu_term_BY_RESOURCE_ID(resource_id) == '':\n",
    "        sql( f\"INSERT INTO {SN}edu_term(name, resource_id, text) VALUES('{name}', {resource_id}, '{text}')\" )\n",
    "        return \"Элемент добавлен (insert_edu_term)\"\n",
    "    #else:\n",
    "        #return \"Такой элемент уже cуществует (insert_edu_term)\"\n",
    "\n",
    "#insert_edu_term('Название термина', 1, 'Текст термина')"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "insert_edu_survey"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 59,
   "metadata": {},
   "outputs": [],
   "source": [
    "def insert_edu_survey(name, resource_id):\n",
    "    if select_edu_survey_BY_RESOURCE_ID(resource_id) == '':\n",
    "        sql( f\"INSERT INTO {SN}edu_survey(name, resource_id) VALUES('{name}', {resource_id})\" )\n",
    "        return \"Элемент добавлен (insert_edu_survey)\"\n",
    "    else:\n",
    "        return \"Такой элемент уже cуществует (insert_edu_survey)\"\n",
    "\n",
    "#insert_edu_survey('Название термина', 1)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "insert_edu_test"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 60,
   "metadata": {},
   "outputs": [],
   "source": [
    "def insert_edu_test(name, resource_id):\n",
    "    if select_edu_test_BY_RESOURCE_ID(resource_id) == '':\n",
    "        sql( f\"INSERT INTO {SN}edu_test(name, resource_id) VALUES('{name}', {resource_id})\" )\n",
    "        return \"Элемент добавлен (insert_edu_test)\"\n",
    "    else:\n",
    "        return \"Такой элемент уже cуществует (insert_edu_test)\"\n",
    "\n",
    "#insert_edu_test('Название термина', 1)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "insert_edu_discussion"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 61,
   "metadata": {},
   "outputs": [],
   "source": [
    "def insert_edu_discussion(name, resource_id):\n",
    "    if select_edu_discussion_BY_RESOURCE_ID(resource_id) == '':\n",
    "        sql( f\"INSERT INTO {SN}edu_discussion(name, resource_id) VALUES('{name}', {resource_id})\" )\n",
    "        return \"Элемент добавлен (insert_edu_discussion)\"\n",
    "    else:\n",
    "        return \"Такой элемент уже cуществует (insert_edu_discussion)\"\n",
    "\n",
    "#insert_edu_discussion('Название термина', 1)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "jp-MarkdownHeadingCollapsed": true
   },
   "source": [
    "# Добавление в БД resource SELECT"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "select_html_resource_BY_RESOURCE_ID"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 62,
   "metadata": {},
   "outputs": [],
   "source": [
    "def select_html_resource_BY_RESOURCE_ID(resource_id):\n",
    "    return remove_sql_symbol( sql( f\"SELECT id FROM {SN}html_resource WHERE resource_id = {resource_id} \" ) )\n",
    "\n",
    "#select_html_resource_BY_RESOURCE_ID(1)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "select_video_resource_description_BY_URL"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 63,
   "metadata": {},
   "outputs": [],
   "source": [
    "def select_video_resource_description_BY_URL(url):\n",
    "    return remove_sql_symbol( sql( f\"SELECT id FROM {SN}video_resource_description WHERE url = '{url}' \" ) )\n",
    "\n",
    "#select_video_resource_description_BY_URL('https://www.youtube.com/watch?v=jfKfPfyJRdk&ab_channel=LofiGirl')"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "select_file_type_BY_EXTENSION"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 64,
   "metadata": {},
   "outputs": [],
   "source": [
    "def select_file_type_BY_EXTENSION(extention):\n",
    "    return remove_sql_symbol( sql( f\"SELECT id FROM {SN}file_type WHERE extension = '{extention}' \" ) )\n",
    "\n",
    "#select_file_type_BY_EXTENSION('docx')"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "select_file_resource_description_BY_RESOURCE_ID"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 65,
   "metadata": {},
   "outputs": [],
   "source": [
    "def select_file_resource_description_BY_RESOURCE_ID(resource_id):\n",
    "    return remove_sql_symbol( sql( f\"SELECT id FROM {SN}file_resource_description WHERE resource_id = {resource_id} \" ) )\n",
    "\n",
    "#select_file_resource_description_BY_RESOURCE_ID(1)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "select_questions_resource_BY_RESOURCE_ID"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 66,
   "metadata": {},
   "outputs": [],
   "source": [
    "def select_questions_resource_BY_RESOURCE_ID(resource_id):\n",
    "    all_content = sql( f\"SELECT id FROM {SN}questions_resource WHERE resource_id = {resource_id} \" )\n",
    "    new_ = replace_symbols(remove_symbols(\"[]'()\", str(all_content)), ',,', ',' )\n",
    "    return new_\n",
    "\n",
    "#select_questions_resource_BY_RESOURCE_ID(1)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "select_comment_resource_BY_RESOURCE_ID"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 67,
   "metadata": {},
   "outputs": [],
   "source": [
    "def select_comment_resource_BY_RESOURCE_ID(resource_id):\n",
    "    return remove_sql_symbol( sql( f\"SELECT id FROM {SN}comment_resource WHERE resource_id = {resource_id} \" ) )\n",
    "\n",
    "#select_comment_resource_BY_RESOURCE_ID(1)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "jp-MarkdownHeadingCollapsed": true
   },
   "source": [
    "# Добавление в БД resource INSERT"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "insert_html_resource"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 68,
   "metadata": {},
   "outputs": [],
   "source": [
    "def insert_html_resource(html, resource_id):\n",
    "    if select_html_resource_BY_RESOURCE_ID(resource_id) == '':\n",
    "        sql( f\"INSERT INTO {SN}html_resource(html, resource_id) VALUES('{html}', {resource_id})\" )\n",
    "        return \"Элемент добавлен (insert_html_resource)\"\n",
    "    else:\n",
    "        return \"Такой элемент уже cуществует (insert_html_resource)\"\n",
    "\n",
    "#insert_html_resource('Тело html ресурса', 1)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "insert_video_resource_description"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 69,
   "metadata": {},
   "outputs": [],
   "source": [
    "def insert_video_resource_description(name, url, duration, resource_id, author):\n",
    "    if select_video_resource_description_BY_URL(url) == '':\n",
    "        sql( f\"INSERT INTO {SN}video_resource_description(name, url, duration, resource_id, author) VALUES('{name}', '{url}', {duration}, {resource_id}, '{author}')\" )\n",
    "        return \"Элемент добавлен (insert_video_resource_description)\"\n",
    "    else:\n",
    "        return \"Такой элемент уже cуществует (insert_video_resource_description)\"\n",
    "\n",
    "#insert_video_resource_description('Название видео ресурса', 'https://www.youtube.com/watch?v=jfKfPfyJRdk&ab_channel=LofiGirl', 120, 1, 1)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "insert_file_type"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 70,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "\"\\ninsert_file_type('Ворд', 'docx')\\ninsert_file_type('ПДФ', 'pdf')\\ninsert_file_type('Гифка', 'gif')\\ninsert_file_type('Джипег', 'jpeg')\\ninsert_file_type('ПэЭнГэ', 'png')\\n\""
      ]
     },
     "execution_count": 70,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "def insert_file_type(name, extension):\n",
    "    if select_file_type_BY_EXTENSION(extension) == '':\n",
    "        sql( f\"INSERT INTO {SN}file_type(name, extension) VALUES('{name}', '{extension}')\" )\n",
    "        return \"Элемент добавлен (insert_file_type)\"\n",
    "    else:\n",
    "        return \"Такой элемент уже cуществует (insert_file_type)\"\n",
    "\"\"\"\n",
    "insert_file_type('Ворд', 'docx')\n",
    "insert_file_type('ПДФ', 'pdf')\n",
    "insert_file_type('Гифка', 'gif')\n",
    "insert_file_type('Джипег', 'jpeg')\n",
    "insert_file_type('ПэЭнГэ', 'png')\n",
    "\"\"\""
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "insert_file_resource_description"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 71,
   "metadata": {},
   "outputs": [],
   "source": [
    "def insert_file_resource_description(name, extension, resource_id, path):\n",
    "    if select_file_resource_description_BY_RESOURCE_ID(resource_id) == '':\n",
    "        type_id = select_file_type_BY_EXTENSION(extension)\n",
    "        if type_id == '':\n",
    "            return \"Такого расширения файла нет\"\n",
    "        else:\n",
    "            sql( f\"INSERT INTO {SN}file_resource_description(name, type_id, resource_id, path) VALUES('{name}', '{type_id}', {resource_id}, '{path}')\" )\n",
    "            return \"Элемент добавлен (insert_file_resource_description)\"\n",
    "    else:\n",
    "        return \"Такой элемент уже cуществует (insert_file_resource_description)\"\n",
    "\n",
    "#insert_file_resource_description('Название ресурса-файла', 'docx', 1, 'крутой путь к файлу')"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "insert_questions_resource"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 72,
   "metadata": {},
   "outputs": [],
   "source": [
    "def insert_questions_resource(questions, answers, resource_id):\n",
    "    if select_questions_resource_BY_RESOURCE_ID(resource_id) == '':\n",
    "        sql( f\"INSERT INTO {SN}questions_resource(questions, answers, resource_id) VALUES('{questions}', '{answers}', {resource_id})\" )\n",
    "        return \"Элемент добавлен (insert_questions_resource)\"\n",
    "    else:\n",
    "        return \"Такой элемент уже cуществует (insert_questions_resource)\"\n",
    "\n",
    "#insert_questions_resource('Название видео ресурса', 'https://www.youtube.com/watch?v=jfKfPfyJRdk&ab_channel=LofiGirl', 1)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "insert_comment_resource"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 73,
   "metadata": {},
   "outputs": [],
   "source": [
    "def insert_comment_resource(replied_comment_id, user_id, text, resource_id):\n",
    "    #if select_questions_resource_BY_RESOURCE_ID(resource_id) == '':\n",
    "        sql( f\"INSERT INTO {SN}comment_resource(replied_comment_id, user_id, text, resource_id) VALUES({replied_comment_id}, {user_id}, '{text}', {resource_id})\" )\n",
    "        return \"Элемент добавлен (insert_comment_resource)\"\n",
    "    #else:\n",
    "        #return \"Такой элемент уже cуществует (insert_questions_resource)\"\n",
    "\n",
    "#insert_comment_resource(1, 1, 'https://www.youtube.com/watch?v=jfKfPfyJRdk&ab_channel=LofiGirl', 1)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "insert_schedule_resource"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 74,
   "metadata": {},
   "outputs": [],
   "source": [
    "def insert_schedule_resource(teacher_id, start_time, duration, notes, resource_id):\n",
    "    #if select_questions_resource_BY_RESOURCE_ID(resource_id) == '':\n",
    "        sql( f\"INSERT INTO {SN}schedule_resource(teacher_id, start_time, duration, notes, resource_id) VALUES({teacher_id}, {start_time}, {duration}, '{notes}', {resource_id})\" )\n",
    "        return \"Элемент добавлен (insert_schedule_resource)\"\n",
    "    #else:\n",
    "        #return \"Такой элемент уже cуществует (insert_questions_resource)\"\n",
    "\n",
    "#insert_schedule_resource(1, 1, 1, 'https://www.youtube.com/watch?v=jfKfPfyJRdk&ab_channel=LofiGirl', 1)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "jp-MarkdownHeadingCollapsed": true
   },
   "source": [
    "# Поиск ссылок на YouTube"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 75,
   "metadata": {},
   "outputs": [],
   "source": [
    "def convert_time_to_number(time):\n",
    "    hours, minutes, seconds = map(int, time.split(':'))\n",
    "    total_seconds = hours * 3600 + minutes * 60 + seconds\n",
    "    return total_seconds\n",
    "\n",
    "def get_video_info(url):\n",
    "    yt = YouTube(url)\n",
    "    video_title = yt.title\n",
    "    video_author = yt.author\n",
    "    video_duration = str(datetime.timedelta(seconds=yt.length))\n",
    "    video_duration = convert_time_to_number(video_duration)\n",
    "    \n",
    "    return [url, video_title, video_author, video_duration]\n",
    "\n",
    "def find_youtube_links(text):\n",
    "    youtube_regex = r'(https?://)?(www\\.)?(youtube|youtu|youtube-nocookie)\\.(com|be)/(watch\\?v=|embed/|v/|watch\\?.*v=)?([^&=%\\?]{11})'\n",
    "    youtube_links = re.findall(youtube_regex, text)\n",
    "    \n",
    "    youtube_urls = []\n",
    "    for link in youtube_links:\n",
    "        youtube_url = 'https://www.youtube.com/watch?v=' + link[5]\n",
    "        youtube_urls.append( get_video_info(youtube_url) )\n",
    "    \n",
    "    return youtube_urls\n",
    "\n",
    "\n",
    "#smth = str( all_files_read() )\n",
    "#video_url = \"https://www.youtube.com/watch?v=dQw4w9WgXcQ\" # ссылка на видео Rick Astley - Never Gonna Give You Up\n",
    "#find_youtube_links(smth)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "jp-MarkdownHeadingCollapsed": true
   },
   "source": [
    "# Импорт всех файлов"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 76,
   "metadata": {},
   "outputs": [],
   "source": [
    "def all_files_import():\n",
    "    all_ = all_files_read()\n",
    "    for index in range(len(all_)):\n",
    "        resource_url = all_[index][0]\n",
    "        directory = all_[index][1]\n",
    "        lms_resource_type_name = all_[index][2]\n",
    "        resource_name = all_[index][3]\n",
    "        all_file_content = read_all( all_[index][1] )\n",
    "        lms_name = 'Moodle'\n",
    "        resource_description = f\"Ресурс типа {lms_resource_type_name}, загруженный из системы {lms_name}\"\n",
    "        insert_FULL_original_resource(resource_name, resource_url, resource_description, lms_resource_type_name, lms_name, all_file_content)\n",
    "        resource_id = select_resource_BY_URL(resource_url)\n",
    "\n",
    "        links = find_youtube_links( str(all_[index]) )\n",
    "        if ( links ) != []:\n",
    "            for link in links:\n",
    "                name = link[1]\n",
    "                url = link[0]\n",
    "                duration = link[3]\n",
    "                author = link[2]\n",
    "                insert_video_resource_description(name, url, duration, resource_id, author)\n",
    "        \n",
    "        if lms_resource_type_name == \"page\" : add_page_resource_to_DB(all_, index, resource_name, resource_id)\n",
    "        elif lms_resource_type_name == \"choice\" : add_choice_resource_to_DB(all_, index, resource_name, resource_id)\n",
    "        elif lms_resource_type_name == \"book\" : add_book_resource_to_DB(all_, index, resource_name, resource_id)\n",
    "        elif lms_resource_type_name == \"feedback\" : add_feedback_resource_to_DB(all_, index, resource_name, resource_id)\n",
    "        elif lms_resource_type_name == \"survey\" : add_survey_resource_to_DB(all_, index, resource_name, resource_id)\n",
    "        elif lms_resource_type_name == \"forum\" : add_forum_resource_to_DB(all_, index, resource_name, resource_id)\n",
    "        elif lms_resource_type_name == \"scheduler\" : add_scheduler_resource_to_DB(all_, index, resource_name, resource_id)\n",
    "        elif lms_resource_type_name == \"quiz\" : add_quiz_resource_to_DB(all_, index, resource_name, resource_id)\n",
    "        elif lms_resource_type_name == \"glossary\" : add_glossary_resource_to_DB(all_, index, resource_name, resource_id)\n",
    "\n",
    "    add_in_DB_files_description()\n",
    "            \n",
    "    return 'Ресурсы были успешно импортированы в базу данных!'\n",
    "              \n",
    "#all_files_import()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Выносим функции добавления ресурсов в базу данных"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 77,
   "metadata": {},
   "outputs": [],
   "source": [
    "def add_page_resource_to_DB(all_, index, resource_name, resource_id):\n",
    "    insert_edu_resource_lecture(resource_name, resource_id, '')\n",
    "    insert_html_resource(all_[index][4], resource_id)\n",
    "    \n",
    "def add_choice_resource_to_DB(all_, index, resource_name, resource_id):\n",
    "    insert_edu_survey(resource_name, resource_id)\n",
    "    questions = all_[index][4]\n",
    "    answers = ''\n",
    "    insert_questions_resource(questions, answers, resource_id)\n",
    "    \n",
    "def add_book_resource_to_DB(all_, index, resource_name, resource_id):\n",
    "    insert_edu_resource_lecture(resource_name, resource_id, '')\n",
    "    insert_html_resource(all_[index][4], resource_id)\n",
    "    \n",
    "def add_feedback_resource_to_DB(all_, index, resource_name, resource_id):\n",
    "    insert_edu_survey(resource_name, resource_id)\n",
    "    questions = all_[index][4][0]\n",
    "    answers = all_[index][4][1]\n",
    "    insert_questions_resource(questions, answers, resource_id)\n",
    "    \n",
    "def add_survey_resource_to_DB(all_, index, resource_name, resource_id):\n",
    "    insert_edu_survey(resource_name, resource_id)\n",
    "    questions = all_[index][4]\n",
    "    answers = ''\n",
    "    insert_questions_resource(questions, answers, resource_id)\n",
    "\n",
    "def add_forum_resource_to_DB(all_, index, resource_name, resource_id):\n",
    "    insert_edu_discussion(resource_name, resource_id)\n",
    "    # replied_comment_id, user_id, text, resource_id\n",
    "    # ['id комментария', 'id комментария, на который идет ответ', 'id пользователя, оставившего комментарий', 'текст комментария'],\\n\"\n",
    "    len_ = len( all_[index][4] )\n",
    "    for j in range( len_ ):\n",
    "        #id = all_[index][4][j][0]\n",
    "        replied_comment_id = all_[index][4][j][1]\n",
    "        user_id = all_[index][4][j][2]\n",
    "        text = all_[index][4][j][3]\n",
    "        insert_comment_resource(replied_comment_id, user_id, text, resource_id)\n",
    "    \n",
    "def add_scheduler_resource_to_DB(all_, index, resource_name, resource_id):\n",
    "    # ['id записи', 'id учителя', 'время начала в Unixtime', 'продолжительность в минутах', 'заметки']\n",
    "    insert_edu_announcment(resource_name, resource_id)\n",
    "    #insert_html_resource(all_[index][4], resource_id)\n",
    "    len_ = len( all_[index][4] )\n",
    "    for j in range( len_ ):\n",
    "        teacher_id = all_[index][4][j][1]\n",
    "        start_time = all_[index][4][j][2]\n",
    "        duration = all_[index][4][j][3]\n",
    "        notes = all_[index][4][j][4]\n",
    "        insert_schedule_resource(teacher_id, start_time, duration, notes, resource_id)\n",
    "        \n",
    "def add_quiz_resource_to_DB(all_, index, resource_name, resource_id):\n",
    "    insert_edu_test(resource_name, resource_id)\n",
    "    questions = all_[index][4]\n",
    "    answers = ''\n",
    "    insert_questions_resource(questions, answers, resource_id)\n",
    "\n",
    "def add_glossary_resource_to_DB(all_, index, resource_name, resource_id):\n",
    "    len_ = len( all_[index][4] )\n",
    "    for j in range(len_):\n",
    "        name = all_[index][4][j][0]\n",
    "        #html = all_[index][4][j][1]\n",
    "        text = all_[index][4][j][1]\n",
    "        \n",
    "        #return insert_edu_term(name, resource_id, text), insert_html_resource(html, resource_id)\n",
    "        insert_edu_term(name, resource_id, text)\n",
    "        #insert_html_resource(html, resource_id)\n",
    "#len( all_files_read()[12][4] )\n",
    "#all_files_read()[12][4][2][0]\n",
    "#add_glossary_resource_to_DB(all_files_read(), 12, 'Терминологический словарь', 13)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Создаем новые файлы и добавляем к соответствующим ресурсам"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 78,
   "metadata": {},
   "outputs": [],
   "source": [
    "def add_in_DB_files_description():\n",
    "    new_files = files_creation_and_information()\n",
    "    for index in range( len(new_files) ):\n",
    "        if new_files[index][1] != '':\n",
    "            path = new_files[index][0]\n",
    "            name, extension = os.path.splitext(path)\n",
    "            name, extension = [os.path.basename(name), extension[1:]]\n",
    "            resource_id = new_files[index][1]\n",
    "            \n",
    "            insert_file_resource_description(name, extension, resource_id, path)\n",
    "\n",
    "#add_in_DB_files_description()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {
    "jp-MarkdownHeadingCollapsed": true
   },
   "source": [
    "# Веб-интерфейс"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 79,
   "metadata": {},
   "outputs": [],
   "source": [
    "host = \"127.0.0.1\"\n",
    "user = \"postgres\"\n",
    "password = \"qwerty\"\n",
    "db_name = \"test\"\n",
    "\n",
    "def web_interface():\n",
    "    app = Flask(__name__)\n",
    "    \n",
    "    # Значения по умолчанию для полей ввода\n",
    "\n",
    "    \n",
    "    # Функция для проверки подключения к базе данных\n",
    "    def check_db_connection():\n",
    "        try:\n",
    "            conn = psycopg2.connect(\n",
    "                host=host,\n",
    "                user=user,\n",
    "                password=password,\n",
    "                dbname=db_name\n",
    "            )\n",
    "            conn.close()\n",
    "            return True\n",
    "        except psycopg2.Error as e:\n",
    "            return False\n",
    "    \n",
    "    # Страница входа\n",
    "    @app.route('/')\n",
    "    def login():\n",
    "        return f'''\n",
    "            <form method=\"post\">\n",
    "                <label for=\"host\">Хост:</label>\n",
    "                <input type=\"text\" id=\"host\" name=\"host\" value=\"127.0.0.1\"><br><br>\n",
    "                <label for=\"user\">Пользователь:</label>\n",
    "                <input type=\"text\" id=\"user\" name=\"user\" value=\"postgres\"><br><br>\n",
    "                <label for=\"password\">Пароль:</label>\n",
    "                <input type=\"text\" id=\"password\" name=\"password\" value=\"qwerty\"><br><br>\n",
    "                <label for=\"db_name\">Имя БД:</label>\n",
    "                <input type=\"text\" id=\"db_name\" name=\"db_name\" value=\"test\"><br><br>\n",
    "                <input type=\"submit\" value=\"Вход\">\n",
    "            </form>\n",
    "            <button onclick=\"window.location.href='/exit'\">Завершить программу</button><br>\n",
    "        '''\n",
    "    \n",
    "    \n",
    "    @app.route('/', methods=['POST'])\n",
    "    def login_post():\n",
    "        global host, user, password, db_name\n",
    "        host = request.form['host']\n",
    "        user = request.form['user']\n",
    "        password = request.form['password']\n",
    "        db_name = request.form['db_name']\n",
    "    \n",
    "        if check_db_connection():\n",
    "            return redirect(url_for('import_page'))\n",
    "        else:\n",
    "            return \"Failed to connect to the database\"\n",
    "    \n",
    "    # Новая страница для отображения данных переменной all_files_read\n",
    "    @app.route('/show_resources_from_files')\n",
    "    def show_resources_from_files():\n",
    "        return all_files_read()\n",
    "    \n",
    "    @app.route('/show_resources_from_db')\n",
    "    def show_resources_from_db():\n",
    "        res = \"\"\"<a href=\"/import\">Назад</a><br>\"\"\"\n",
    "        res += show_tables(host, user, password, db_name, \"resource\")\n",
    "        return res\n",
    "\n",
    "    @app.route('/show_tables_video')\n",
    "    def show_tables_video():\n",
    "        res = \"\"\"<a href=\"/import\">Назад</a><br>\"\"\"\n",
    "        res += show_tables(host, user, password, db_name, \"video_resource_description\")\n",
    "        return res\n",
    "    \n",
    "    @app.route('/import_resources')\n",
    "    def import_resources():\n",
    "        res = all_files_import()\n",
    "        res += \"\"\"<br><a href=\"/import\">Назад</a>\"\"\"\n",
    "        return res\n",
    "    \n",
    "    @app.route('/delete_resources')\n",
    "    def delete_resources():\n",
    "        res = tables_reload()\n",
    "        res += \"\"\"<br><a href=\"/import\">Назад</a>\"\"\"\n",
    "        return res\n",
    "    \n",
    "    @app.route('/exit')\n",
    "    def exit_program():\n",
    "        _exit(0)\n",
    "    \n",
    "    @app.route('/import')\n",
    "    def import_page():\n",
    "        return f'''\n",
    "            <button onclick=\"window.location.href='/show_resources_from_files'\">Показать ресурсы из экспортируемого файла</button><br>\n",
    "            <button onclick=\"window.location.href='/show_resources_from_db'\">Показать ресурсы из базы данных</button><br>\n",
    "            <button onclick=\"window.location.href='/show_tables_video'\">Показать видео-ресурсы</button><br>\n",
    "            <button onclick=\"window.location.href='/import_resources'\">Импортировать ресурсы</button><br>\n",
    "            <button onclick=\"window.location.href='/delete_resources'\">Очистить таблицы</button><br>\n",
    "            <a href=\"/\">Назад</a>\n",
    "        '''\n",
    "    \n",
    "    if __name__ == '__main__':\n",
    "        app.run()\n",
    "\n",
    "#web_interface()"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Основной код"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 80,
   "metadata": {
    "colab": {
     "base_uri": "https://localhost:8080/"
    },
    "id": "RGc4YPtekbx9",
    "outputId": "b8e5adcc-8022-40d1-b79b-c0ced6229189",
    "scrolled": true
   },
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      " * Serving Flask app '__main__'\n",
      " * Debug mode: off\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.\n",
      " * Running on http://127.0.0.1:5000\n",
      "Press CTRL+C to quit\n",
      "127.0.0.1 - - [11/Jun/2024 04:29:38] \"GET / HTTP/1.1\" 200 -\n",
      "127.0.0.1 - - [11/Jun/2024 04:29:40] \"GET / HTTP/1.1\" 200 -\n",
      "127.0.0.1 - - [11/Jun/2024 04:29:41] \"GET / HTTP/1.1\" 200 -\n",
      "127.0.0.1 - - [11/Jun/2024 04:29:41] \"POST / HTTP/1.1\" 302 -\n",
      "127.0.0.1 - - [11/Jun/2024 04:29:41] \"GET /import HTTP/1.1\" 200 -\n",
      "127.0.0.1 - - [11/Jun/2024 04:29:42] \"GET / HTTP/1.1\" 200 -\n",
      "127.0.0.1 - - [11/Jun/2024 04:29:43] \"POST / HTTP/1.1\" 302 -\n",
      "127.0.0.1 - - [11/Jun/2024 04:29:43] \"GET /import HTTP/1.1\" 200 -\n",
      "127.0.0.1 - - [11/Jun/2024 04:29:44] \"GET / HTTP/1.1\" 200 -\n",
      "[2024-06-11 04:29:46,203] ERROR in app: Exception on / [POST]\n",
      "Traceback (most recent call last):\n",
      "  File \"C:\\Users\\Eugene\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\flask\\app.py\", line 1473, in wsgi_app\n",
      "    response = self.full_dispatch_request()\n",
      "               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n",
      "  File \"C:\\Users\\Eugene\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\flask\\app.py\", line 882, in full_dispatch_request\n",
      "    rv = self.handle_user_exception(e)\n",
      "         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n",
      "  File \"C:\\Users\\Eugene\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\flask\\app.py\", line 880, in full_dispatch_request\n",
      "    rv = self.dispatch_request()\n",
      "         ^^^^^^^^^^^^^^^^^^^^^^^\n",
      "  File \"C:\\Users\\Eugene\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\flask\\app.py\", line 865, in dispatch_request\n",
      "    return self.ensure_sync(self.view_functions[rule.endpoint])(**view_args)  # type: ignore[no-any-return]\n",
      "           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n",
      "  File \"C:\\Users\\Eugene\\AppData\\Local\\Temp\\ipykernel_3660\\2885774350.py\", line 54, in login_post\n",
      "    if check_db_connection():\n",
      "       ^^^^^^^^^^^^^^^^^^^^^\n",
      "  File \"C:\\Users\\Eugene\\AppData\\Local\\Temp\\ipykernel_3660\\2885774350.py\", line 16, in check_db_connection\n",
      "    conn = psycopg2.connect(\n",
      "           ^^^^^^^^^^^^^^^^^\n",
      "  File \"C:\\Users\\Eugene\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\psycopg2\\__init__.py\", line 122, in connect\n",
      "    conn = _connect(dsn, connection_factory=connection_factory, **kwasync)\n",
      "           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n",
      "UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc2 in position 55: invalid continuation byte\n",
      "127.0.0.1 - - [11/Jun/2024 04:29:46] \"POST / HTTP/1.1\" 500 -\n",
      "[2024-06-11 04:29:49,528] ERROR in app: Exception on / [POST]\n",
      "Traceback (most recent call last):\n",
      "  File \"C:\\Users\\Eugene\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\flask\\app.py\", line 1473, in wsgi_app\n",
      "    response = self.full_dispatch_request()\n",
      "               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n",
      "  File \"C:\\Users\\Eugene\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\flask\\app.py\", line 882, in full_dispatch_request\n",
      "    rv = self.handle_user_exception(e)\n",
      "         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n",
      "  File \"C:\\Users\\Eugene\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\flask\\app.py\", line 880, in full_dispatch_request\n",
      "    rv = self.dispatch_request()\n",
      "         ^^^^^^^^^^^^^^^^^^^^^^^\n",
      "  File \"C:\\Users\\Eugene\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\flask\\app.py\", line 865, in dispatch_request\n",
      "    return self.ensure_sync(self.view_functions[rule.endpoint])(**view_args)  # type: ignore[no-any-return]\n",
      "           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n",
      "  File \"C:\\Users\\Eugene\\AppData\\Local\\Temp\\ipykernel_3660\\2885774350.py\", line 54, in login_post\n",
      "    if check_db_connection():\n",
      "       ^^^^^^^^^^^^^^^^^^^^^\n",
      "  File \"C:\\Users\\Eugene\\AppData\\Local\\Temp\\ipykernel_3660\\2885774350.py\", line 16, in check_db_connection\n",
      "    conn = psycopg2.connect(\n",
      "           ^^^^^^^^^^^^^^^^^\n",
      "  File \"C:\\Users\\Eugene\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\psycopg2\\__init__.py\", line 122, in connect\n",
      "    conn = _connect(dsn, connection_factory=connection_factory, **kwasync)\n",
      "           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n",
      "UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc2 in position 55: invalid continuation byte\n",
      "127.0.0.1 - - [11/Jun/2024 04:29:49] \"POST / HTTP/1.1\" 500 -\n",
      "[2024-06-11 04:29:52,762] ERROR in app: Exception on / [POST]\n",
      "Traceback (most recent call last):\n",
      "  File \"C:\\Users\\Eugene\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\flask\\app.py\", line 1473, in wsgi_app\n",
      "    response = self.full_dispatch_request()\n",
      "               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n",
      "  File \"C:\\Users\\Eugene\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\flask\\app.py\", line 882, in full_dispatch_request\n",
      "    rv = self.handle_user_exception(e)\n",
      "         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n",
      "  File \"C:\\Users\\Eugene\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\flask\\app.py\", line 880, in full_dispatch_request\n",
      "    rv = self.dispatch_request()\n",
      "         ^^^^^^^^^^^^^^^^^^^^^^^\n",
      "  File \"C:\\Users\\Eugene\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\flask\\app.py\", line 865, in dispatch_request\n",
      "    return self.ensure_sync(self.view_functions[rule.endpoint])(**view_args)  # type: ignore[no-any-return]\n",
      "           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n",
      "  File \"C:\\Users\\Eugene\\AppData\\Local\\Temp\\ipykernel_3660\\2885774350.py\", line 54, in login_post\n",
      "    if check_db_connection():\n",
      "       ^^^^^^^^^^^^^^^^^^^^^\n",
      "  File \"C:\\Users\\Eugene\\AppData\\Local\\Temp\\ipykernel_3660\\2885774350.py\", line 16, in check_db_connection\n",
      "    conn = psycopg2.connect(\n",
      "           ^^^^^^^^^^^^^^^^^\n",
      "  File \"C:\\Users\\Eugene\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\psycopg2\\__init__.py\", line 122, in connect\n",
      "    conn = _connect(dsn, connection_factory=connection_factory, **kwasync)\n",
      "           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n",
      "UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc2 in position 56: invalid continuation byte\n",
      "127.0.0.1 - - [11/Jun/2024 04:29:52] \"POST / HTTP/1.1\" 500 -\n",
      "127.0.0.1 - - [11/Jun/2024 04:29:57] \"POST / HTTP/1.1\" 302 -\n",
      "127.0.0.1 - - [11/Jun/2024 04:29:57] \"GET /import HTTP/1.1\" 200 -\n",
      "127.0.0.1 - - [11/Jun/2024 04:29:58] \"GET / HTTP/1.1\" 200 -\n",
      "127.0.0.1 - - [11/Jun/2024 04:30:01] \"POST / HTTP/1.1\" 302 -\n",
      "127.0.0.1 - - [11/Jun/2024 04:30:01] \"GET /import HTTP/1.1\" 200 -\n",
      "127.0.0.1 - - [11/Jun/2024 04:30:03] \"GET /show_tables_video HTTP/1.1\" 200 -\n",
      "127.0.0.1 - - [11/Jun/2024 04:30:04] \"GET /import HTTP/1.1\" 200 -\n",
      "127.0.0.1 - - [11/Jun/2024 04:30:07] \"GET /show_resources_from_db HTTP/1.1\" 200 -\n",
      "127.0.0.1 - - [11/Jun/2024 04:30:09] \"GET /import HTTP/1.1\" 200 -\n",
      "127.0.0.1 - - [11/Jun/2024 04:30:10] \"GET /show_tables_video HTTP/1.1\" 200 -\n",
      "127.0.0.1 - - [11/Jun/2024 04:30:12] \"GET /import HTTP/1.1\" 200 -\n",
      "127.0.0.1 - - [11/Jun/2024 04:30:14] \"GET /show_tables_video HTTP/1.1\" 200 -\n",
      "127.0.0.1 - - [11/Jun/2024 04:30:16] \"GET /import HTTP/1.1\" 200 -\n",
      "127.0.0.1 - - [11/Jun/2024 04:30:18] \"GET /show_resources_from_db HTTP/1.1\" 200 -\n",
      "127.0.0.1 - - [11/Jun/2024 04:30:23] \"GET /import HTTP/1.1\" 200 -\n",
      "127.0.0.1 - - [11/Jun/2024 04:30:24] \"GET / HTTP/1.1\" 200 -\n"
     ]
    }
   ],
   "source": [
    "#all_files_read()\n",
    "#tables_reload()\n",
    "#all_files_import()\n",
    "web_interface()"
   ]
  }
 ],
 "metadata": {
  "colab": {
   "collapsed_sections": [
    "qHNlpN74kd3b",
    "SliYKrKskoQu"
   ],
   "provenance": []
  },
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.12.3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
