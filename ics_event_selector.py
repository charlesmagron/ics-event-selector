#!/usr/bin/env python3
# coding: utf-8

# Script:       ics_event_selector.py

# Author:       Charles Magron / Zurich, Switzerland
# Created:      05.Jul.2016       v0.1
# Last update:  08.Oct.2016       v1.1

# Purpose       Read an ICS file, let the user select some calendar events
#               from it, and write the selected events into a new ICS file.

import tkinter as tk       # install this with "sudo [apt-get|dnf] install python3-tkinter"
from tkinter import Menu
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
from tkinter import ttk      # needed for the tabs
from os.path import splitext, basename
from ics import Calendar     # install this with "pip3 install ics"

### import pdb; pdb.set_trace()           # used to set a debugging breakpoint

class Checkbox(object):
    """
    Enhanced checkbutton/checkbox widget, used as an element of the MyTab widget
    """

    def __init__(self, parent_frame=None, label='', value=0, i_no=0, i_row=0):
        """
        Initialize new checkbutton/checkbox widget at creation/instantiation time
        """
        self.i_var = tk.BooleanVar()  # did not work as expected; left here for illustration
        self.i = tk.Checkbutton(parent_frame, text=label, variable = self.i_var,
                                command=self.valueChanged)
        self.i_no = i_no        # check-box sequence number
        self.i.select()         # set the check-mark
        self.checkmark_set = True  # we manage check-mark state ourselves, since 'i_var' did not work as expected
        self.i.grid(column=0, row=i_row, sticky='W')
        self.label = label

    def valueChanged(self):
        """
        Toggle the state of the check-button whenever the user sets/deletes the corresponding check-mark
        """
        if self.checkmark_set:
            self.checkmark_set = False
        else:
            self.checkmark_set = True

class MyTab(ttk.Frame):
    """
    Enhanced tab widget, used as an element of the notebook widget
    """

    def __init__ (self, parent=None, e_list=[], my_font="Helvetica 10 bold"):
        """
        Initialize the MyTab widget at creation time, including adding the
        check-buttons which are to populate the tab
        """

        def time_string(t):
            """
            Time string formatting function used only at object creation time,
            and therefore not kept as a method for later use with this object
            """
            return str(t)[:10] + " " + str(t)[11:16]

        super(MyTab, self).__init__(parent)   # invoke __init__ of parent class (that is ttk.Frame)
        self.my_tab = self
        self.parent = parent            # parent window (the notebook)
        self.event_list = e_list
        self.number_of_events = len(self.event_list)  # total amount of events in this tab
        self.my_font = my_font

        # Frame for tab-level buttons (Set and Clear)
        self.frame1 = tk.Frame(self)
        self.frame1.grid()
        self.set_button = tk.Button(self.frame1,text="Select All",
            bg='light blue', command=self.do_select_all)
        self.set_button.grid(column=0, row=0, sticky='W')
        self.clear_button = tk.Button(self.frame1,text="Clear All",
            bg='yellow', command=self.do_clear_all)
        self.clear_button.grid(column=1, row=0, sticky='W')

        # Frame for title and for event list elements
        self.frame2 = tk.Frame(self)
        self.frame2.grid()
        self.d_label_font = my_font
        self.d_label0 = tk.Label(self.frame2,text="Checkmarks  ", font=self.d_label_font)
        self.d_label0.grid(column=0, row=0, sticky='W')
        self.d_label1 = tk.Label(self.frame2, text="Begin", font=self.d_label_font)
        self.d_label1.grid(column=1, row=0, sticky='W')
        self.d_label2 = tk.Label(self.frame2, text="End", font=self.d_label_font)
        self.d_label2.grid(column=2, row=0, sticky='W')
        self.d_label3 = tk.Label(self.frame2, text="(Created)", font=self.d_label_font)
        self.d_label3.grid(column=3, row=0, sticky='W')
        self.d_label4 = tk.Label(self.frame2, text="Description", font=self.d_label_font)
        self.d_label4.grid(column=4, row=0, sticky='W')

        # column text descriptions for the corresponding rows
        self.e_label1 = []; self.e_label2 = []; self.e_label3 = []; self.e_label4 = [];

        self.buttons = []      # list of buttons/checkboxes for this tab

        for i in range(self.number_of_events):
            current_row     = i + 1
            self.buttons.append(Checkbox(self.frame2, label=str(current_row), value=1, i_no=i, i_row=current_row))
            self.e_label1.append(tk.Label(self.frame2, text=time_string(e_list[i].begin)+"  "))
            self.e_label1[i].grid(column=1, row=current_row, sticky='W')
            self.e_label2.append(tk.Label(self.frame2, text=time_string(e_list[i].end)+"  "))
            self.e_label2[i].grid(column=2, row=current_row, sticky='W')
            self.e_label3.append(tk.Label(self.frame2, text="("+time_string(e_list[i].created)+")   "))
            self.e_label3[i].grid(column=3, row=current_row, sticky='W')
            self.e_label4.append(tk.Label(self.frame2, text=str(e_list[i].name)))
            self.e_label4[i].grid(column=4, row=current_row, sticky='W')

    def do_select_all(self):
        """
        Set check-marks of all check-buttons of current tab
        """
        for n in range(self.number_of_events):
            self.buttons[n].i.select()
            self.buttons[n].checkmark_set = True

    def do_clear_all(self):
        """
        Clear check-marks of all check-buttons of current tab
        """
        for n in range(self.number_of_events):
            self.buttons[n].i.deselect()
            self.buttons[n].checkmark_set = False

class MyApp(object):
    """
    Application object for doing "the real work"
    """

    def __init__(self):
        """
        State initialization at application object creation time 
        """
        self.my_tab_list = []
        self.my_e_list = []
        self.o_fname = ""
        self.e_len = 0
        self.e_per_tab = 0
        self.no_of_tabs = 0
        self.root = None

    def do_give_help(self):
        """
        Help menu 
        """
        top = tk.Toplevel()
        top.title("Help")
        msg = tk.Message(top, text="Select All: marks all check-boxes\n" +
                                   "Clear All: clears all check-boxes\n" +
                                   "Save Selected: Saves all selected events into a new output file\n" +
                                   "Quit Now: terminates execution without saving anything (again)")
        msg.configure(width=500)
        msg.grid()
        button = tk.Button(top, text="Close", command=top.destroy)
        button.grid()

    def do_save_and_exit(self):
        """
        Save and Exit menu; it stores the selected data into a new file, and terminates the script 
        """
        new_calendar = Calendar()
        for tab in self.my_tab_list:
            for n in range(tab.number_of_events):
                if tab.buttons[n].checkmark_set:
                    new_calendar.events.append(tab.event_list[n])
        o_file = open(self.o_fname, 'w')
        o_file.writelines(new_calendar)
        o_file.close()
        self.root.destroy()
        messagebox.showinfo("Information", "Your selected events were stored in the following file:\n" +
                        "    %s" % self.o_fname)
        exit()

    def do_quit_now(self):
        """
        Quit menu; it terminates the script immediately without saving any data 
        """
        self.root.quit()
        self.root.destroy()
        exit()

    def start(self):
        """
        Main routine of the script; invoked by the main program just after start 
        """
        # get the input ICS filename via GUI dialog (Tkinter))
        i_fname = askopenfilename()

        # read the data from the ICS input file
        if i_fname:
            i_file = open(i_fname,'r')
            indata = i_file.read()
            i_file.close()
            self.o_fname = splitext(i_fname)[0] + "_selection.ics"

            # extract the list of events from the ICS input data
            try:
                self.app_caldata = Calendar(indata)
            except:
                messagebox.showinfo("Warning","Something seems to be wrong with " +
                "your input file %s" % basename(i_fname))
            else:
                # read the calendar events from the input file
                self.my_e_list = self.app_caldata.events   # list of events
                self.my_e_list.sort()             # sort them by ascending creation time
                self.e_len = len(self.my_e_list)  # total amount of events in list

                if self.e_len == 0:
                    messagebox.showinfo("Warning","Your input file is empty: %s\nThere is nothing to do."
                     % basename(i_fname))
                else:                    
                    # Let's start the GUI
                    self.root = tk.Tk()
                    self.root.title("ICS Event Selector ("+str(self.e_len)+" events in total)")

                    # Create a menu bar
                    self.menu_bar = Menu(self.root)
                    self.root.config(menu=self.menu_bar)

                    # Add a menu to the bar, and assign some menu items to the menu
                    self.file_menu = Menu(self.menu_bar, tearoff=0)  # tearoff = remove default dashed line at the top
                    self.file_menu.add_command(label="Save and Exit", command=self.do_save_and_exit)
                    self.file_menu.add_command(label="Quit without Saving", command=self.do_quit_now)
                    self.menu_bar.add_cascade(label="File", menu=self.file_menu)

                    # Add one more menu to the bar, and assign a menu item to the menu
                    self.help_menu = Menu(self.menu_bar, tearoff=0)
                    self.help_menu.add_command(label="About", command=self.do_give_help)
                    self.menu_bar.add_cascade(label="Help", menu=self.help_menu)

                    # Find out how many tabs we need in order to display all of our events
                    self.e_per_tab = 20                               # number of entries per tab
                    self.no_of_tabs = self.e_len // self.e_per_tab    # // = floor division
                    self.e_on_last_tab = self.e_len % self.e_per_tab  # entries in last tab (% = modulus)
                    if (self.e_on_last_tab > 0):
                        self.no_of_tabs += 1                 # total number of tabs
                    else:
                        self.e_on_last_tab = self.e_per_tab  # there is no tab with zero elements

                    # Create the needed tabs
                    self.tab_control = ttk.Notebook(self.root)
                    self.tab_control.grid()                # Make tabs visible
                    e_start = 0
                    for n in range(self.no_of_tabs):
                        if n == self.no_of_tabs-1:   # last tab
                            e_end = e_start + self.e_on_last_tab - 1
                        else:                           # up to penultimate tab
                            e_end = e_start + self.e_per_tab - 1
                        # Add a new tab
                        self.new_tab = MyTab(
                            parent=self.tab_control,
                            e_list=self.my_e_list[e_start:e_end+1]  # subset of overall event list
#                            e_list=self.my_e_list[e_start:e_end+1],  # subset of overall event list
#                            parent_app=self.my_app
                        )
                        self.tab_control.add(self.new_tab, text=" "+str(n+1)+" ")
                        self.my_tab_list.append(self.new_tab)
                        e_start = e_start + self.e_per_tab

                    self.tab_control.grid()                # Make tabs visible

                    self.root.mainloop()

def main():
    """
    Main program; which is actually only an envelope of the "working code" object 
    """
    my_app = MyApp()    # instantiate/create the application object, including state initialization
    my_app.start()      # invoke the 'start' method of the application object

if __name__ == '__main__':
    main()
