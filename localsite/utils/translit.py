#!/usr/bin/python
# -*- coding: utf-8 -*-

from os import walk, rename, unlink, mkdir
from os.path import isdir, exists
from sys import argv, exit, getfilesystemencoding
from shutil import copyfile
import shutil

conversion = {
	u' ' : ' ',
	u'0' : '0',
	u'1' : '1',
	u'2' : '2',
	u'3' : '3',
	u'4' : '4',
	u'5' : '5',
	u'6' : '6',
	u'7' : '7',
	u'8' : '8',
	u'9' : '9',
        u'а' : 'a',
        u'б' : 'b',
        u'в' : 'v',
        u'г' : 'g',
        u'д' : 'd',
        u'е' : 'e',
        u'ё' : 'e',
        u'ж' : 'zh',
        u'з' : 'z',
        u'и' : 'i',
        u'й' : 'j',
	u'й' : '',
        u'к' : 'k',
        u'л' : 'l',
        u'м' : 'm',
        u'н' : 'n',
        u'о' : 'o',
        u'п' : 'p',
        u'р' : 'r',
        u'с' : 's',
        u'т' : 't',
        u'у' : 'u',
        u'ф' : 'f',
        u'х' : 'h',
        u'ц' : 'c',
        u'ч' : 'ch',
        u'ш' : 'sh',
        u'щ' : 'sch',
        u'ь' : 'q',
        u'ы' : 'y',
        u'ь' : 'q',
        u'э' : 'e',
        u'ю' : 'ju',
        u'я' : 'ja',
        u'А' : 'A',
        u'Б' : 'B',
        u'В' : 'V',
        u'Г' : 'G',
        u'Д' : 'D',
        u'Е' : 'E',
        u'Ё' : 'E',
        u'Ж' : 'ZH',
        u'З' : 'Z',
        u'И' : 'I',
        u'Й' : 'J',
        u'К' : 'K',
        u'Л' : 'L',
        u'М' : 'M',
        u'Н' : 'N',
        u'О' : 'O',
        u'П' : 'P',
        u'Р' : 'R',
        u'С' : 'S',
        u'Т' : 'T',
        u'У' : 'U',
        u'Ф' : 'F',
        u'Х' : 'H',
        u'Ц' : 'C',
        u'Ч' : 'CH',
        u'Ш' : 'SH',
        u'Щ' : 'SCH',
        u'Ъ' : 'q',
        u'Ы' : 'Y',
        u'Ь' : 'q',
        u'Э' : 'E',
        u'Ю' : 'JU',
        u'Я' : 'JA',
        u',' : '-',
        }

def cyr2lat(s):
    retval = ""
    d = ''
    for c in s:
	if ord(c) > 128:
            try:
                c = conversion[c]
            except KeyError:
                c=''
        retval += c
    return retval
