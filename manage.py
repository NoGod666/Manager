#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sqlite3, os, subprocess, argparse, sys, getpass, signal
from cryptography.fernet import Fernet

os.system('clear')

if not os.path.exists('database.db'):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("create table Cuentas(id integer not null unique primary key autoincrement, nombre text unique, cuenta text, password text)")
    conn.commit()
    conn.close()
    print('\n[*] Se ha creado una base de datos.\n')

def menu():
    print("\n******* PASSWORD MANAGER *******\n")
    print("\t1. registrar cuenta")
    print("\t2. ver registros")
    print("\t3. Modificar cuenta")
    print("\t4. Eliminar cuenta")
    print("\t5. Salir\n")
    return input("Elija una opcion: ")

def Salir(sig, frame):
    print("\n [!] Canceling...\n")
    conn.commit()
    conn.close()
    sys.exit(1)

signal.signal(signal.SIGINT, Salir)

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('--insert', dest='insert', nargs='?', const='Skip')
parser.add_argument('--show', dest='show', nargs='?', const='ListAll')
parser.add_argument('complete', nargs='?')
args = parser.parse_args()

# Inicio de Programa
key = b'4qHtGTRA9r6Vb9Y43Vi8zAjP7BFWexr-Gpm7f8-8-PE='
f = Fernet(key)
salir = False

while salir == False:
    conn = sqlite3.connect('database.db') 
    cursor = conn.cursor()

# Modo Basico
    if args.insert != "Skip" and args.insert != None:
        name = args.insert
        passwd = getpass.getpass(" Type your password: ")
        passwd_test = getpass.getpass(" Type your password again: ")
        
        if passwd != passwd_test:
            print(" [!] Password do not match")
            sys.exit(1)

        try:
            enc_passwd = f.encrypt(passwd.encode())
            cursor.execute('insert into Cuentas (id,nombre,cuenta,password) values(null,\"{}\",\"{}\",\"{}\")'.format(name," ",enc_passwd.decode()))
            print(" [*] Password saved successful")
        except sqlite3.IntegrityError:
            print(" [!] The account '{}', is already registered.".format(name))
    elif args.show != None and args.show != "ListAll":
        name = args.show
        try:
            cursor.execute('select password from Cuentas where nombre=\"{}\"'.format(name))
            tmp = cursor.fetchall()
            d = tmp[0][0]
            dec_passwd = f.decrypt(d.encode())
            print("  └──➤➤ %s" % dec_passwd.decode())
            subprocess.call("echo '%s' | tr -d '\n' | xclip -sel clip >/dev/null 2>&1" % dec_passwd.decode(), shell=True)
        except (sqlite3.IntegrityError, IndexError):
            print(" [!] '%s' not found in the database" % name)
            print(" [*] List all password saved with argument '--show'")
            sys.exit(0)
    elif args.show == "ListAll":
        cursor.execute('select nombre from Cuentas')
        tmp = cursor.fetchall()
        for n, var in enumerate(tmp, 1):
            if n == 1 and len(tmp) > 1:
                print("  ├──➤ %s" % var[0])
            elif n == len(tmp):
                print("  └──➤ %s" % var[0])
            else:
                print("  ├──➤ %s" % var[0])

    elif args.complete != "complete" or args.insert == "Skip":
        print("\nUse: --insert '<account>'       Insert into dababase. ")
        print("     --show '<account>'         Show password.\n")

    if args.complete != "complete":
        conn.commit()
        conn.close()
        sys.exit(0)

# Modo Detallado
    op = menu()
    
    while op not in ('1','2','3','4','5','damemisclaves'):
        op = input("Elija una opcion: ")
    
    if op == '1':
        try:
            name = input('Nombre: ') 
            cta = input('Cuenta: ')
            passwd = input('Password: ')
            enc_passwd = f.encrypt(passwd.encode())
            cursor.execute('insert into Cuentas (id,nombre,cuenta,password) values(null,\"{}\",\"{}\",\"{}\")'.format(name, cta, enc_passwd.decode()))
            os.system('clear')
        
        except sqlite3.IntegrityError:
            os.system('clear')
            print('\n[!] La cuenta {}, ya se encuentra registrado.'.format(name))
     
    elif op == '2':

       os.system('clear')
       cursor.execute('select * from Cuentas')
       tmp_data = cursor.fetchall()
       column0 = 5
       column1 = 13
       column2 = 14

       for x in tmp_data:
           if len(x[1]) > column1:
               column1 = len(x[1])
           if len(x[2]) > column2:
               column2 = len(x[2])
       column1 += 6
       column2 += 6

       print(' +' + '-'*(column0) + '+' + '-'*(column1) + '+' + '-'*(column2) + '+')
       print(' |' + ' Id' + ' '*(column0-3) + '|' + '  Nombre' + ' '*(column1-8) + '|' + '  Cuenta' + ' '*(column2-8) + '|')
       print(' +' + '-'*(column0) + '+' + '-'*(column1) + '+' + '-'*(column2) + '+')
       
       for j in tmp_data:
           print(" | {:^3} | {:<}{}| {:<}{}|".format(j[0], j[1], " "*(column1-len(j[1])-1), j[2], " "*(column2-len(j[2])-1)))
    
       print(' +' + '-'*(column0) + '+' + '-'*(column1) + '+' + '-'*(column2) + '+')

    elif op == '3':
        try:
            Id = int(input('\nIngrese ID de cuenta a modificar: '))
            name = input('Ingrese nuevo nombre: ')
            cursor.execute('update Cuentas set nombre=\"{}\" where id={}'.format(name, Id))
            cta = input('Ingrese nueva cuenta: ')
            passwd = input('Ingrese nueva password: ')
            enc_passwd = f.encrypt(passwd.encode())
            cursor.execute('update Cuentas set cuenta=\"{}\" where id={}'.format(cta, Id))
            cursor.execute('update Cuentas set password=\"{}\" where id={}'.format(enc_passwd.decode(), Id))
            os.system('clear')
        except ValueError:
            os.system('clear')
            print('\n [!] El ID no es valido.')
        except sqlite3.IntegrityError:
            os.system('clear')
            print('\n [!] {}, ya se encuentra registrado'.format(name))

    elif op == '4':
        print('\n [!] La eliminacion es permanente...')

        try:
            Id = int(input('\nIngrese ID de la cuenta: '))
            cursor.execute('delete from Cuentas where id=\"{}\"'.format(Id))
            os.system('clear')
        except (ValueError, sqlite3.IntegrityError):
            os.system('clear')
            print('\n[!] ID de cuenta no existe o no es valido.')

    elif op == 'damemisclaves':
        try:
            Id = int(input('\nIngrese ID de cuenta: '))
            cursor.execute('select * from Cuentas where id={}'.format(Id))
            tmp = cursor.fetchall()
            d = tmp[0][3]
            dec_passwd = f.decrypt(d.encode())
            os.system('clear')
            print("\n  └──➤➤ {} - {} - {} - {}".format(tmp[0][0], tmp[0][1], tmp[0][2], dec_passwd.decode()))
            subprocess.call("echo '%s' | tr -d '\n' | xclip -sel clip >/dev/null 2>&1" % dec_passwd.decode(), shell=True)
        
        except (sqlite3.IntegrityError, IndexError, ValueError) :
            os.system('clear')
            print('\n[!] El ID de cuenta no es valido')

    elif op == '5':
        salir = True

    conn.commit()
    conn.close()
