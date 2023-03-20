import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import *
from tkcalendar import DateEntry
from EventTasks import Event_update_start, Event_Update_From, Event_delete, Event_Update_day



def get_date_toplevel():
    """
    Creates toplevel windows that gets start date and runs Event_Update_From.py file. This updates every day in
    google calendar with every event between the start date and the current date.
    :return:
    """
    def print_sel():
        date = cal.get_date()
        sdate = date.strftime('%Y%m%d')
        print("i have the date")
        Event_Update_From.appntmnts_info(sdate)


    top = tk.Toplevel(root, bg='white', height=15, width=40)
    print('gettoplevel function has started')

    cal = DateEntry(top, width=12, background='darkblue',
                    foreground='white', borderwidth=2)
    cal.grid(column=0, padx=4,pady=5)

    ttk.Button(top, text="ok", command=print_sel).grid(column=1, row=0, padx=5,pady=5)

# Unused -------------------------------------------
def day_toplevel():
    def print_sel():
        date = cal.get_date()
        sdate = date.strftime('%Y%m%d')
        print("i have the date")
        return sdate

    print('top level windows starting')

    top = tk.Toplevel(root, bg='white', height=15, width=40)

    cal = DateEntry(top, width=12, background='darkblue',
                    foreground='white', borderwidth=2)
    cal.grid(column=0, padx=4,pady=5)
    ttk.Button(top, text="ok", command=print_sel).grid(column=1, row=0, padx=5,pady=5)
#---------------------------------------------------

def update_day_toplevel():
    """
    create a toplevel windows that allows you to choose a user to update their appointments only and between a selected
    date.
    :return:
    """
    def print_sel2():

        day = cal.get_date()
        end = day + datetime.timedelta(days=1)
        associate = clicked.get()
        print(associate)
        print(day)
        print(end)

        string_date = day.strftime('%Y%m%d')
        string_end = end.strftime('%Y%m%d')
        print('Event_Update_day script beings')

        # runs the Event_Update_day.py file

        Event_Update_day.appntmnts_info(string_date, string_end, associate)


    top = tk.Toplevel(root, bg='white')
    top.geometry('200x75')
    top.resizable(False,False)
    top.iconphoto(True,ico)

    print('gettoplevel function has started')

    options = [
        'All',
        'Jackie',
        'Silvia',
        'Mayra',
        'Laura',
        'Monica',
        'Seyry',
        'Carlos',
        'Diego',
        'Elvin',
        'OPEN'
    ]

    # made a section to pick a starting date time
    cal = DateEntry(top, width=12, background='darkblue',
                    foreground='white', borderwidth=2)
    cal.grid(column=0, padx=5, pady=7)


    # Creates a drop down to select User.
    clicked = tk.StringVar(top)
    clicked.set('All')
    drop = tk.OptionMenu(top, clicked, *options)
    drop.grid(column=1,row=0, padx=8, pady=7)

    ttk.Button(top, text="Update", command=print_sel2).place(relx=0.5, rely=.7, anchor=CENTER)


# function below is still a work in progress no real use

def delete_events_entry():
    """
    creates toplevel windows that will be used to delete events if needed.
    :return:
    """
    def print_sel3():
        password = widget.get()
        if password == 'adminPassword':
            date = day_toplevel()
            Event_delete.event(date)



    top = tk.Toplevel(root, bg='white')
    top.geometry('150x75')
    top.resizable(False, False)
    top.iconphoto(True, ico)

    widget = Entry(top, show='*', width=15)
    widget.grid(column=0,padx=5, pady=7)

    ttk.Button(top, text='Enter', command=print_sel3).grid(column=1, row=0, padx=5,pady=5)


class App:
    def __init__(self,master) -> None:
        self.master = master

        menubar = Menu(root)
        root['menu'] = menubar

        menu_opt_file = Menu(menubar)
        menu_opt_edit = Menu(menubar)
        menu_opt_tools = Menu(menubar)
        menubar.add_cascade(menu=menu_opt_file, label='File')
        menubar.add_cascade(menu=menu_opt_edit, label='Edit')
        menubar.add_cascade(menu=menu_opt_tools, label="Tools")

        menu_opt_edit.add_command(label='Update From', command=lambda: get_date_toplevel())
        menu_opt_edit.add_command(label="Update Day...",command=lambda: update_day_toplevel())
        menu_opt_tools.add_command(label="Delete Events", command=lambda: delete_events_entry() )
        menu_opt_file.add_cascade(label='Exit', command=lambda: root.destroy())

        greeting = tk.Label(
            text='Click Button to\n Start Syncing Calendars',
            fg='Black',
            bg='white',
            font=('Arial',24),
            width=18,
            height=2)
        greeting.place(x=125
               ,y=150)

        button = tk.Button(
            text='Start Syncing Calendar',
            width=20,
            height=2,
            font=('Arial',10),
            fg='black',
            command= lambda: Event_update_start.appntmnts_info()
        )
        button.place(x=220,y=258)


if __name__ == '__main__':
    root = Tk()
    root.title('Calender Sync')
    ico = PhotoImage(file='Images/CalendarSyncICO.png')
    root.iconphoto(False, ico)
    root.geometry('612x408')

    img = PhotoImage(file='Images/CalendarBG.png')

    label = tk.Label(image=img)
    label.place(x=0, y=0)

    root.resizable(False,False)
    root.option_add('*tearOff', False)

    app = App(root)
    root.mainloop()