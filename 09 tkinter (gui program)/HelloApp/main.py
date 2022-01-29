import pickle
from tkinter import *
import os
from tkinter import messagebox
from zipfile import ZipFile


class User:
    def __init__(self, login, password):
        self.login = login
        self.password = password


root_window = Tk()
confirm_login_counter = 0
current_user_login = ''


# first define all functions (starting app description at the bottom)
def render_start_app_buttons():
    login_btn.grid(row=0, column=0, padx=50, pady=50)
    register_btn.grid(row=0, column=1, padx=50, pady=50)


def show_form_click(form_name):
    window = Toplevel()
    window.title(form_name)
    # label + field for login
    enter_login_label = Label(window, text='Login:')
    enter_login_label.grid(row=0, column=0, padx=(50, 5), pady=(50, 15))
    enter_login_field = Entry(window, width=50)
    enter_login_field.grid(row=0, column=1, padx=(0, 50), pady=(50, 15))

    # label + field for password
    enter_password_label = Label(window, text='Password:')
    enter_password_label.grid(row=1, column=0, padx=(50, 5), pady=15)
    enter_password_field = Entry(window, width=50)
    enter_password_field.grid(row=1, column=1, padx=(0, 50), pady=15)

    # run function for login or for registration, depending on which form name is this, by click on confirm button
    if form_name == 'Login':
        confirm_btn = Button(window, text='Confirm',
                             command=lambda: confirm_login(enter_login_field.get(), enter_password_field.get(), window),
                             padx=20, pady=10, fg='white', bg='#4d91ff')
    else:
        confirm_btn = Button(window, text='Confirm',
                             command=lambda: confirm_registration(enter_login_field.get(), enter_password_field.get(),
                                                                  window),
                             padx=20, pady=10, fg='white', bg='#4d91ff')

    confirm_btn.grid(row=2, column=0, columnspan=2, pady=15)


def confirm_registration(login, password, registration_window):
    # validation
    if len(login) < 4:
        error_login_label = Label(registration_window, text='login must be longer then 4 symbols, try again...',
                                  fg='red', pady=10)
        error_login_label.grid(row=3, column=0, columnspan=2)
        error_login_label.after(1000, lambda: error_login_label.destroy())  # remove label after 1 sec
    if len(password) < 4:
        error_password_label = Label(registration_window, text='password must be longer then 4 symbols, try again...',
                                     fg='red', pady=10)
        error_password_label.grid(row=4, column=0, columnspan=2)
        error_password_label.after(1000, lambda: error_password_label.destroy())
    else:
        # if login and password are valid
        users_list = []  # empty list for all users
        user = User(login, password)  # create new user
        if not os.path.exists("users.bin"):  # if there are no users yet
            # add new user to list and write list with one user to file
            users_list.append(user)
            new_file = open("users.bin", "wb")
            pickle.dump(users_list, new_file)
            new_file.close()
        else:
            # if there are already users -> read all users from file
            users_list = load_users()
            # then append new user to list
            users_list.append(user)
            users_file = open("users.bin", "wb")
            # and finally write the entire list to file again (rewrite)
            pickle.dump(users_list, users_file)

        messagebox.showinfo('Registration info', 'Registration completed!')
        registration_window.destroy()


def confirm_login(login, password, login_window):
    global confirm_login_counter
    global current_user_login

    if not os.path.exists("users.bin"):
        confirm_login_counter += 1
        messagebox.showerror('Login info', 'login or password is incorrect')
    else:
        users_list = load_users()
        login_result = ''
        for user in users_list:
            if user.login == login and user.password == password:
                login_result = 'ok'

        if login_result == 'ok':
            confirm_login_counter = 0

            # put login of a current user to global variable current_user_login
            current_user_login = login
            # make directory for current user file
            if not os.path.isdir(current_user_login):
                os.mkdir(current_user_login)

            start_user_profile()
            login_window.destroy()
        else:
            messagebox.showerror('Login info', 'login or password is incorrect')
            confirm_login_counter += 1

    # if user entered wrong login or password 3 times
    if confirm_login_counter == 3:
        root_window.quit()


def load_users():
    users_file = open('users.bin', 'rb')
    users_list = pickle.load(users_file)
    users_file.close()
    return users_list


def start_user_profile():
    # user profile will be in main window
    # so clear main window and add logout button
    login_btn.grid_forget()
    register_btn.grid_forget()

    # put on the main window user profile elements (we defined them at the beginning - below)
    logout_btn.grid(row=0, column=1, padx=0, pady=50)
    text_field.grid(row=2, column=0, columnspan=2, padx=50, pady=50)
    btn_open.grid(row=3, column=0, padx=50, pady=50)
    btn_save.grid(row=3, column=1, padx=50, pady=50)


def open_file():
    # current user login - user directory name and user file name
    if not os.path.exists(f'{current_user_login}/{current_user_login}.txt'):
        messagebox.showerror('Open file error', 'There is no file yet')
    else:
        file = open(f'{current_user_login}/{current_user_login}.txt', 'r')
        text_field.insert(END, file.read())
        file.close()


def save_to_file():
    file = open(f'{current_user_login}/{current_user_login}.txt', 'w')
    file.write(text_field.get("1.0", "end"))
    file.close()


def logout_click():
    # return main window to the initial state
    logout_btn.grid_forget()
    text_field.delete('1.0', END)  # clear text field
    text_field.grid_forget()
    btn_open.grid_forget()
    btn_save.grid_forget()

    # when user logging out we make reserve copy of date and put it to archive
    # if there is user's folder and user's file
    if os.path.exists(f'{current_user_login}/{current_user_login}.txt'):
        # create reserve directory
        if not os.path.isdir('reserve'):
            os.mkdir('reserve')
        # calling function to get all file paths in the directory
        file_paths = get_all_file_paths(current_user_login)
        # make zip file for current user in reserve directory
        with ZipFile(f'reserve/{current_user_login}.zip', 'w') as myzip:
            # writing each file one by one
            for file in file_paths:
                myzip.write(file)

    render_start_app_buttons()


def get_all_file_paths(directory):
    # no matter how many files or subdirectories are - this function will return all their paths
    # initializing empty file paths list
    file_paths = []

    # crawling through directory and subdirectories
    for root, directories, files in os.walk(directory):
        for filename in files:
            # join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)

    # returning all file paths
    return file_paths


# first define all main window elements (just define, but we will put them on the window later)
# define main window buttons (main window only has 2 buttons at the beginning - login_btn and register_btn)
login_btn = Button(root_window, command=lambda: show_form_click('Login'), text='Login',
                   padx=20, pady=20, fg='white', bg='#4d91ff')
register_btn = Button(root_window, command=lambda: show_form_click('Registration'), text='Registration',
                      padx=20, pady=20, fg='white', bg='#4d91ff')

# define user profile elements
logout_btn = Button(root_window, command=logout_click, text='Log out',
                    padx=20, pady=20, fg='white', bg='#4d91ff')
text_field = Text(root_window, height=20, width=100)
btn_open = Button(root_window, command=open_file, text='Open file',
                  padx=20, pady=20, fg='white', bg='#4d91ff')
btn_save = Button(root_window, command=save_to_file, text='Save to file',
                  padx=20, pady=20, fg='white', bg='#4d91ff')


# start app
render_start_app_buttons()


root_window.mainloop()






# igor 1111,  nina 2222
