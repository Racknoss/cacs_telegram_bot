import telebot
import CACS_parser as parser
import time
import sqlite3
import re

bot = telebot.TeleBot('')
admin = telebot.TeleBot("")
admin_id = ""
list_p = ""

keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard1.row('На Сегодня', 'На Завтра')

#Вывод Расписания
def get_current_schedule(message, time_dif):
    conn = sqlite3.connect("Cacs_bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE id=?", [str(message.from_user.id)])
    who = cursor.fetchone()
    if who:
        try: bot.send_message(message.from_user.id, parser.get_timetable(who[1],int(time.time() + time_dif)), reply_markup=keyboard1)
        except: bot.send_message(message.from_user.id, "У вас нет занятий", reply_markup=keyboard1)
    else:
        bot.send_message(message.from_user.id, "Кажется, Вы не зарегистрированы. Напишите /reg")
    conn.close()


@bot.message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect("Cacs_bot.db")
    cursor = conn.cursor()
    sql = "SELECT * FROM Users WHERE id=?; "
    cursor.execute(sql, [message.from_user.id])
    if not cursor.fetchall():
        bot.send_message(message.from_user.id,"Добро Пожаловать в Cacs-bot. Что бы начать регистрацию напишите /reg")
    else:
        cursor.execute(sql, [message.from_user.id])
        what = cursor.fetchone()
        bot.send_message(message.from_user.id, "Бот Вас помнит. Проверьте" +
                         ". Что бы заново зарегистрироваться напишите /reg", reply_markup=keyboard1)
        
        
@bot.message_handler(commands=['reg'])
def start_reg(message):
    conn = sqlite3.connect("Cacs_bot.db")
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Users WHERE id=?;", [str(message.from_user.id)])
    except:
        print("Запись не была удалена")
    conn.commit()
    bot.send_message(message.from_user.id, "Напишите свою Фамилию и Имя (опционально)")
    bot.register_next_step_handler(message, find_part)
    
def find_part(message):
    global list_p
    try: names = parser.find_person_s(*message.text.split())
    except: names = parser.find_person_n(*message.text.split())
    leng = len(names)
    if (leng > 1):
        list_p = list(map(lambda x: [message.text + " " + x[1], x[0]] , names))
        lis = ""
        for t in range(leng):
            lis = lis + str(t) + ". " + list_p[t][0] + "\n"
        lis += "Выберете соответствующий номер"
        keyboard2 = telebot.types.ReplyKeyboardMarkup(True, True)
        keyboard2.row(*map(str,[i for i in range(len(names))]) )
        bot.send_message(message.from_user.id, lis, reply_markup = keyboard2)
        bot.register_next_step_handler(message, which_pers)
    else:
        get_name(message.from_user.id, *(message.text + " " + names[0][1]).split(), names[0][0])
        
def which_pers(message):
    global list_p
    print(list_p)
    try: item = int(message.text)
    except:
        bot.send_message(message.from_user.id, "Введите цифру, пожалуйста")
        bot.register_next_step_handler(message, which_pers)
        return
    try: tag = list_p[item]
    except:
        bot.send_message(message.from_user.id, "Цифра не попала в диапазон. Попробуйте еще раз")
        bot.register_next_step_handler(message, which_pers)
        return
    get_name(message.from_user.id, *(tag[0]).split(), tag[1])
        
    
    
    
def get_name(id_m,surname, f_name, s_name, id_p):
    conn = sqlite3.connect("Cacs_bot.db")
    cursor = conn.cursor()
       
    
    cursor.execute("""INSERT INTO Users ('id', 'cacs_id') VALUES (?,?);""",
                   [id_m, id_p])
    conn.commit()
    cursor.execute("""SELECT * FROM Cacs_p WHERE Cacs_id = ?;""",
                   [str(id_p)])
    who = cursor.fetchone()
    if not who:
        cursor.execute("""INSERT INTO Cacs_p ('Cacs_id', 'surname', 'f_name', 's_name') VALUES (?,?,?,?);""",
                   [id_p, surname, f_name, s_name])
        conn.commit() 
        
    bot.send_message(id_m, "Вы были успешно зарегистрированы. Ваш id на Cacs: " +
                     str(id_p), reply_markup=keyboard1)
    
#Сегодняшнее расписание    
@bot.message_handler(content_types=['text'], func=lambda message: message.text == "На Сегодня" )
def c_s(message, time = 0):
    get_current_schedule(message, time)
 
#Завтрашнее расписание 
@bot.message_handler(content_types=['text'], func=lambda message: message.text == "На Завтра")
def t_s(message, time = 86400):
    get_current_schedule(message,time)

#Сегодняшнее расписание с командой
@bot.message_handler(commands=['t'])
def c_s(message, time = 0):
    get_current_schedule(message, time)
    
#Завтрашнее расписание с командой
@bot.message_handler(commands=['n'])
def c_s(message, time = 86400):
    get_current_schedule(message, time)
    
    
#Вывод информации о боте    
@bot.message_handler(commands=['help'])
def hell(message):
    file_to_send = open('Help.txt', 'rb')
    bot.send_document(message.from_user.id, data = file_to_send)
 
 
#Отправить сообщение администратору 
@bot.message_handler(commands=['admin'])
def message_to_admin(message):
    mes = re.sub(r"/admin", "", message.text)
    admin.send_message(admin_id, str(message.from_user.id) + mes)
    
#Расписание произвольного студента
#@bot.message_handler(commands=['ts'])
#def part_stud(message):
    
     
    
bot.polling()
admin.polling(5)
                                        
