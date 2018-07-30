# -- coding: utf8 --

import os
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import *
import subprocess
import threading

# вывод текста в форму
def printer(string): 
	info_window.config(state=NORMAL)
	info_window.insert(END, string+'\n')
	info_window.config(state=DISABLED)
	info_window.see(END)


root_dir = os.getcwd()
source_dir = root_dir
finish_dir = root_dir
files_mazatrol = []  # список мазаковских файлов
files_fanuc = []  # список фануковских файлов
err = []  # список ошибок
times = 0  # счетчик
result = ''
result2 = ''


# диалоговое окно с каталогом сканирования
def scan_folder_dialog():
	global form_scan_folder
	global finish_dir
	global source_dir
	source_dir = askdirectory()
	if source_dir == '':
		source_dir = root_dir
		finish_dir = source_dir
	source_dir = source_dir.replace('/', '\\')
	finish_dir = source_dir
	# вставка пути в 1 форму
	form_save_folder.delete(0, END)
	form_save_folder.insert(0, finish_dir)
	# вставка пути во 2 форму
	form_scan_folder.delete(0, END)
	form_scan_folder.insert(0, source_dir)


# диалоговое окно с каталогом сохранения
def save_folder_dialog():
	global form_save_folder
	global finish_dir
	finish_dir = askdirectory()
	if finish_dir == '':
		finish_dir = root_dir
	finish_dir = finish_dir.replace('/', '\\')
	# вставка пути во 2 форму
	form_save_folder.delete(0, END)
	form_save_folder.insert(0, finish_dir)


# окно со справкой
def help_window():
	messagebox.showinfo('Справка', '''При запуске автоматически сканируется папка с программой на наличие управяляющих программ для стоек FANUC и MAZATROL SMART.
Так же можно выбрать и отсканировать любую другую папку, после смены папки автоматического сканирования не происходит, т.к. при большом объеме данных это 
занимает время, поэтому сканирование выполняется кнопкой.
Файлы копируются с новым названием в папки ouput_fanuc и output_mazatrol, так же при выборе режима с созданием подпапок создается отдельная папка FOLDERS
для исключения ошибок при одинаковых названиях папок и файлов. Файлы с одинаковыми названиями заменяются. 
Все старые файлы остаются без каких либо изменений на случай проверки, или неправильной работы программы (вероятность крайне мала).''')


# открыть конечную папку
def open_finish():
	subprocess.run('explorer "'+finish_dir+'"')


# создание потоков для функций
def thread(my_func):
    def wrapper(*args, **kwargs):
        my_thread = threading.Thread(target=my_func, args=args, kwargs=kwargs)
        my_thread.start()
    return wrapper

# сканер в отдельном потоке
@thread
def scaner():
	progressbar.config(mode='indeterminate', maximum=50)
	os.chdir(source_dir)
	global files_mazatrol
	global files_fanuc
	global result
	global result2
	progressbar.start() # гоняем пустой прогресс бар во время сканирования
	print(threading.currentThread().getName() + '\n')

	# генератор списка мазаковских программ
	files_mazatrol = [f for f in os.listdir() if f.endswith('.PBG') or f.endswith('.pbg')]
	files_mazatrol = list(files_mazatrol)
	if files_mazatrol == []:
		result = 'Файлов Mazatrol не найдено.'
	else:
		result = 'Найдено файлов Mazatrol: ' + str(len(files_mazatrol))


	# список того, что пропустит фануковский сканер
	badfiles = ('.PBG', 'PYC', '.PY', '.PYW',
		'.MP3', '.FLAC', '.WAV', '.OGG',
		'.JPG', '.JPEG', '.BMP', '.ICO', '.TIFF', '.JPE', '.OXPS', '.PSD', '.PNG', '.GIF',
		'.MPEG', '.MP4', '.WEBM', '.WMA', '.FLV', '.MOV', '3GP', '.AVI', '.VOB', 
		'.EXE', '.RAR', '.ZIP', '.7Z', '.MSI', '.INSTALL', '.APK'
		'.XLS', '.XLSX', '.WPS', '.FRW',
		'.INI', '.CFG', '.DB', '.DAT', '.TMP'
		'.DOC', '.DOCX', '.PDF', '.DJVU', '.FB2', '.EPUB' 
		'.DB', '.LNK', '.URL', '.HTML', 
		'.GP3', '.GP4', '.GP5', '.GPX',
		'.CDW', '.FRW', '.M3D', '.KDW', '.SPW', '.A3D') 
	badfiles2 = []
	# оно же в нижнем регистре
	for i in badfiles: 
		i = i.lower()
		badfiles2.append(i) 
	badfiles2 = tuple(badfiles2)

	# генератор списка фануковских программ (видит все кроме списка выше, потому что фануковские программы могут быть с любым расширением или вообще без него)
	files_fanuc = [f for f in os.listdir() if not f.endswith(badfiles) and not f.endswith(badfiles2)]

	# удаляем точно лишнее
	if 'Thumbs.db' in files_fanuc:
		files_fanuc.remove('Thumbs.db')
	if 'output_mazatrol' in files_fanuc:
		files_fanuc.remove('output_mazatrol')
	if 'output_fanuc' in files_fanuc:
		files_fanuc.remove('output_fanuc')

	# ебанутая реализация удаления папок и лишних тхт из фануковского сканера
	for i in range(10):
		info_window.update()
		root.update()
		for i in files_fanuc:
			try:
				with open(i, 'r') as e:
					e = e.read(1)
					if e not in ('%', 'O'):
						files_fanuc.remove(i)
						print('Файл', i, 'не является управляющей программой Fanuc.')
			except(PermissionError):
				print('Из обработки исключена папка: ' + i)
				files_fanuc.remove(i)
			except:
				print('ВНИМАНИЕ: Не удалось удалить ' + i + ' из списка обработки.')
	if files_fanuc == []:
		result2 = 'Файлов Fanuc не найдено.'
	else:
		result2 = 'Найдено файлов Fanuc: ' + str(len(files_fanuc))
	
	printer(result+'\n' + result2)

	result_var_mazatrol.set(result)
	result_var_fanuc.set(result2)
	fanuc_list_label.update()
	mazatrol_list_label.update()
	mazatrol_list.delete(0, END)
	for i in files_mazatrol:
		mazatrol_list.insert(END, i)
	fanuc_list.delete(0, END)
	for i in files_fanuc:
		fanuc_list.insert(END, i)
	progressbar.config(mode='determinate')	
	progressbar.stop()



# кнопка сканирования
def scaner_button():
	progressbar.config(mode='indeterminate', maximum=50)
	info_window.config(state=NORMAL)
	info_window.delete(1.0, END)
	info_window.config(state=DISABLED)
	printer('Сканирование директории: "'+source_dir+'"')
	mazatrol_list.delete(0, END)
	fanuc_list.delete(0, END)
	result_var_mazatrol.set('Сканирование...')
	result_var_fanuc.set('Сканирование...')
	scaner()


# обработчик мазаковских программ
def mazak_renamer(i):
	info_window.update()
	root.update()
	global source_dir
	global finish_dir
	progressbar.step()
	try:
		os.chdir(source_dir)
		with open(i, 'rb') as f:
			text = f.read()
			f.seek(80)
			fileold = f.read(32)
			fileold = fileold.rstrip(b'\x00').decode()
			fileold_folder = fileold.replace('\\', '-').replace('*', '-').replace('/', '-').strip(' ')
			fileold = fileold_folder + '.PBG'
		symbols = str(108 - len(fileold))
		finish_dir_new = finish_dir+'\output_mazatrol\\'
		finish_dir_checkboxed = finish_dir_new+'FOLDERS\\'+fileold_folder
		try:
			os.mkdir(finish_dir_new)
			os.chdir(finish_dir_new)
		except:
				os.chdir(finish_dir_new)
		if checkbox_var.get() == 1:
			try:
				os.makedirs(finish_dir_checkboxed)
				os.chdir(finish_dir_checkboxed)
			except:
				os.chdir(finish_dir_checkboxed)	
		try:
			with open(fileold, 'wb') as filenew:
					filenew.write(text)
			os.chdir(source_dir)
			printer(fileold + (' {:.>'+symbols+'}').format('скопирован!'))
			global times
			times += 1
		except:
			os.chdir(source_dir)
			printer(fileold + (' {:.>'+symbols+'}').format('не скопирован!'))
			err.append(i)
	except:
		os.chdir(source_dir)
		printer(fileold + (' {:.>'+symbols+'}').format('не скопирован!'))
		err.append(i)


# обработчик фануковских программ
def fanuc_renamer(i):
	info_window.update()
	root.update()
	progressbar.step()
	try:
		os.chdir(source_dir)
		global finish_dir
		with open(i, 'rb') as f:
			text = f.read()
			f.seek(2)
			fileold = f.read(55)
			if b')' not in fileold:
				try:
					fileold.decode()
					printer('Файл ' + str(i) +' не содержит названия внутри!')
				except(UnicodeDecodeError):
					printer('Файл '+ str(i) + ' не поддерживается!')
			else:
				fileold = fileold.split(b'(')
				fileold = fileold[1].split(b')')
				try:
					fileold = fileold[0].decode()
					fileold = fileold.replace('\\', '-').replace('*', '-').replace('/', '-').strip(' ')
				except:
					printer('Файл '+ str(i) + ' не поддерживается!')
		symbols = str(108 - len(fileold))
		symbols2 = str(108 - len(i))

		finish_dir_new = finish_dir+'\output_fanuc\\'
		finish_dir_checkboxed = finish_dir_new+'FOLDERS\\'+fileold
		try:
			os.mkdir(finish_dir_new)
			os.chdir(finish_dir_new)
		except:
			os.chdir(finish_dir_new)
		if checkbox_var.get() == 1:
			try:
				os.makedirs(finish_dir_checkboxed)
				os.chdir(finish_dir_checkboxed)
			except:
				os.chdir(finish_dir_checkboxed)				
		try:
			with open(fileold, 'wb') as filenew:
				filenew.write(text)
			os.chdir(source_dir)
			printer(fileold + (' {:.>'+symbols+'}').format('скопирован!'))
			global times
			times += 1
		except:
			os.chdir(source_dir)
			printer(i + (' {:.>'+symbols2+'}').format('не скопирован!'))
			err.append(i)
	except(PermissionError):
		symbols2 = str(108 - len(i))
		printer('В обработку попала папка: '+'"'+str(i)+'"')
		printer(i + (' {:.>'+symbols2+'}').format('пропуск папки!'))
		err.append(i)
	except:
		symbols2 = str(108 - len(i))
		printer('Неизвестная ошибка при обработке: '+'"'+str(i)+'"')
		printer(i + (' {:.>'+symbols2+'}').format('пропуск файла!'))
		err.append(i)


# кнопка вызывающая мазаковский обработчик
def mazatrol_button():
	global err
	global files_mazatrol
	global times
	times = 0
	info_window.config(state=NORMAL)
	info_window.delete(1.0, END)
	info_window.config(state=DISABLED)
	if files_mazatrol == []:
		messagebox.showerror('Хрен!', 'Нечего переименовывать!')
	else:
		progressbar.stop()
		progressbar.config(mode='determinate', maximum=len(files_mazatrol))
		mode_mazatrol = 'Выбран режим Mazatrol с созданием папок' if checkbox_var.get() == 1 else 'Выбран режим Mazatrol'
		printer('{: ^109}'.format(mode_mazatrol))
		for i in files_mazatrol:
			mazak_renamer(i)
		errors = '\n'.join(err)
		printer('_'*110)
		printer('{: >109}'.format('Принято файлов: ' + str(len(files_mazatrol))))
		printer('{: >109}'.format('Обработано файлов: ' + str(times)))
		if errors == '':
			printer('{: >109}'.format('Ошибок нет!'))
		else:
			printer('Ошибки:\n' + str(errors))
		err = []
		errors = ''
		messagebox.showinfo('Готово!', 'Принято файлов: ' + str(len(files_mazatrol)) + '.' + '\nОбработано файлов: ' + str(times) + '.' + '\nПодробности в окне информации.')


# кнопка вызывающая фануковский обработчик
def fanuc_button():
	global err
	global files_fanuc
	global times
	times = 0
	info_window.config(state=NORMAL)
	info_window.delete(1.0, END)
	info_window.config(state=DISABLED)
	if files_fanuc == []:
		messagebox.showerror('Хрен!', 'Нечего переименовывать!')
	else:
		progressbar.stop()
		progressbar.config(mode='determinate', maximum=len(files_fanuc))
		mode_fanuc = 'Выбран режим Fanuc с созданием папок' if checkbox_var.get() == 1 else 'Выбран режим Fanuc'
		printer('{: ^109}'.format(mode_fanuc))
		for i in files_fanuc:
			fanuc_renamer(i)
		errors = '\n'.join(err)
		printer('_'*109)
		printer('{: >109}'.format('Принято файлов: ' + str(len(files_fanuc))))
		printer('{: >109}'.format('Обработано файлов: ' + str(times)))
		if errors == '':
			printer('{: >109}'.format('Ошибок нет!'))
		else:
			printer('Ошибки:\n' + str(errors))
		err = []
		errors = ''
		messagebox.showinfo('Готово!', 'Принято файлов: ' + str(len(files_fanuc)) + '.' + '\nОбработано файлов: ' + str(times) + '.' + '\nПодробности в окне информации.')


# создание элементов интерфейса
root = Tk()
root.title('Superzalupa v1.2')
root.resizable(False, False)
root['bg'] = '#ababab'
result_var_mazatrol = StringVar()
result_var_fanuc = StringVar()

result_var_mazatrol.set(result)
result_var_fanuc.set(result2)

window_label_name = Label(root, 
	text='    Переименовыватель-копир 3000', font=('Candara', 14, 'bold'), bg='#005578', fg='white', width=83, anchor=W, justify=LEFT)

root_frame = Frame(root, relief=FLAT, bg='#ababab', padx=20, pady=1)
frame_lisls = Frame(root_frame, relief=FLAT, bg='#ababab', pady=12)

label_scan_folder = Label(root_frame, text='Выбрать папку для сканирования:', font='Candara 12', bg='#ababab', anchor=W, justify=LEFT)
form_scan_folder = Entry(root_frame, width=54, font='Consolas 13', relief=RAISED)
form_scan_folder.insert(0, source_dir)
source_folder_button = Button(root_frame, text='Обзор...', command=scan_folder_dialog, padx=20, bg='#ababab')
help_button = Button(root_frame, text='Справка', command=help_window, padx=51.4, bg='#ababab', fg='black', font=('Arial', 9, 'bold'))

label_save_folder = Label(root_frame, text='Выбрать папку для сохранения:', font='Candara 12', anchor=W, justify=LEFT, bg='#ababab')
form_save_folder = Entry(root_frame, width=54, font='Consolas 13', relief=RAISED)
form_save_folder.insert(0, finish_dir)
finish_folder_button = Button(root_frame, text='Обзор...', command=save_folder_dialog, padx=20, bg='#ababab')
button_scaner = Button(root_frame, text='Сканировать снова', command=scaner_button, padx=20, bg='#005578', fg='white', font=('Arial', 9, 'bold'))

checkbox_var = IntVar()
checkbox = Checkbutton(frame_lisls, text='Создавать для каждой программы отдельную папку', variable=checkbox_var, bg='#ababab', activebackground='#ababab')

frame_of_mazatrol_list = Frame(frame_lisls, width=150, relief=RAISED, bg='white', bd=2)
frame_separator = Frame(frame_lisls, width=21, relief=RAISED, bd=0, bg='#ababab')
frame_of_fanuc_list = Frame(frame_lisls, width=150, relief=RAISED,	bg='white',	bd=2)

scrollbar_mazatrol = Scrollbar(frame_of_mazatrol_list)
scrollbar_fanuc = Scrollbar(frame_of_fanuc_list)

mazatrol_list_label = Label(frame_of_mazatrol_list, text=result, textvariable=result_var_mazatrol, font=('Candara', 12, 'italic'), anchor=W, justify=LEFT, bg='white')
fanuc_list_label = Label(frame_of_fanuc_list, text=result2, textvariable=result_var_fanuc, font=('Candara', 12, 'italic'), anchor=W, justify=LEFT, bg='white')

mazatrol_list = Listbox(frame_of_mazatrol_list, relief=GROOVE, font='Consolas 8', width=60, yscrollcommand=scrollbar_mazatrol.set)
for i in files_mazatrol:
	mazatrol_list.insert(END, i)
scrollbar_mazatrol.config(command=mazatrol_list.yview)

fanuc_list = Listbox(frame_of_fanuc_list, relief=GROOVE, font='Consolas 8', width=60, yscrollcommand=scrollbar_fanuc.set)
for i in files_fanuc:
	fanuc_list.insert(END, i)
scrollbar_fanuc.config(command=fanuc_list.yview)

mazatrol_renamer_button = Button(frame_lisls, text='Переименовать файлы Mazatrol', command=mazatrol_button, padx=81, bg='#005578', fg='white', font=('Arial', 10, 'bold'))
fanuc_renamer_button = Button(frame_lisls, text='Переименовать файлы Fanuc', command=fanuc_button, padx=90, bg='#005578', fg='white', font=('Arial', 10, 'bold'))

info_window_frame = Frame(root_frame, bg='white', relief=RAISED, bd=2)
info_window_label = Label(info_window_frame, text='Информация:', font=('Candara', 12, 'italic'), bg='white')
scrollbar_info = Scrollbar(info_window_frame)
info_window = Text(info_window_frame, heigh=10, width=110, font='Consolas 9', yscrollcommand=scrollbar_info.set, state=DISABLED)
info_window.insert(1.0, '')
scrollbar_info.config(command=info_window.yview)

s = ttk.Style()
s.theme_use('clam')
s.configure('red.Horizontal.TProgressbar', foreground='#005578', background='#005578')
progressbar = ttk.Progressbar(style='red.Horizontal.TProgressbar', orient='horizontal', length=385)

copyright = Label(root_frame, text='© 2018 Dece1ver', bg='#ababab', fg='grey')
open_finish_button = Button(root_frame, text='Открыть расположение переименованных файлов', command=open_finish, padx=20, bg='#005578', fg='white', font=('Arial', 10, 'bold'))

scaner_button() # автоматическое первое сканирование

# расположение элементов интерфейса
window_label_name.grid(row=0, column=0, columnspan=4, sticky=W)
progressbar.grid(row=0, column=0, columnspan=4, sticky=E, padx=25)
root_frame.grid(row=1, column=0)
label_scan_folder.grid(row=2, column=0, columnspan=4, sticky=W)
form_scan_folder.grid(row=3, column=0)
source_folder_button.grid(row=3, column=1, sticky=W)
help_button.grid(row=3, column=3, columnspan=1, padx=20, sticky=E)

label_save_folder.grid(row=4, column=0, columnspan=4, sticky=W)
form_save_folder.grid(row=5, column=0)
finish_folder_button.grid(row=5, column=1, sticky=W)
button_scaner.grid(row=5, column=3, columnspan=2, padx=20, sticky=E)

frame_lisls.grid(row=6, column=0, rowspan=2, columnspan=4)

frame_of_mazatrol_list.grid(row=6, column=0)
mazatrol_list_label.grid(row=6, column=0)
mazatrol_list.grid(row=7, column=0)
scrollbar_mazatrol.grid(row=7, column=2, ipady=46)
frame_separator.grid(row=6, column=1, columnspan=2)
frame_of_fanuc_list.grid(row=6, column=3)
fanuc_list_label.grid(row=6, column=3)
scrollbar_fanuc.grid(row=7, column=4, ipady=46)
fanuc_list.grid(row=7, column=3)

checkbox.grid(row=8, column=0, columnspan=4)

mazatrol_renamer_button.grid(row=9, column=0, sticky=W)
fanuc_renamer_button.grid(row=9, column=3, sticky=E)

info_window_frame.grid(row=10, column=0, rowspan=2, columnspan=4)
info_window_label.grid(row=10, column=0, sticky=W)
info_window.grid(row=11, column=0, columnspan=4)
scrollbar_info.grid(row=11, column=4, ipady=46)

copyright.grid(row=12, column=0, columnspan=4, sticky=W)
open_finish_button.grid(row=12, column=0, columnspan=4, pady=10, sticky=E)

# запуск окна
if __name__ == '__main__':
	root.mainloop()