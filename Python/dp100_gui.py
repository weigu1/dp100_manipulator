from tkinter import *
from tkinter import ttk
import tkinter.font as tkFont
from time import strftime, localtime
import queue
from functools import partial # to pass argument from profile buttons

class GUI:
    def __init__(self, flags_2_main, queue_2_main, queue_2_gui, png_filename):
        self.standard_font = ["Helvetica", 12, "bold"]
        self.standard_font_big = ["Helvetica", 20, "bold"]
        self.textbox_font = ["Courier", 12, "bold"]
        self.welcome_txt = "Hello to DP100 manipulator V1.0 (2025)"
        self.active_profile = 0
        self.state = 0
        self.png_filename = png_filename
        self.flags_2_main = flags_2_main
        self.queue_2_main = queue_2_main
        self.queue_2_gui = queue_2_gui
         # Dictionary for widget texts (inside:message)
        self.widget_texts_dict = {"Title" : "Alientek DP100 Manipulator",
                                  "Connect" : "Connect",
                                  "Device Information" : "Getting device information",
                                  "Basic Information" : "Getting basic information",
                                  "Profiles" : "Getting all profiles",
                                  "Output": "Output Voltage and Current",
                                  "Set Voltage": "Set Voltage:",
                                  "Set Current": "Set Current:",
                                  "On" : "ON",
                                  "Off" : "OFF",
                                  "Profile Nr" : "Profile Nr:",
                                  "Change_Profile" : "Change Profile",
                                  "Clear PNG": "Reset Chart",
                                  "Clear Textwindow" : "Clear Textwindow",
                                  "Quit" : "Quit"
                                 }
        self.widget_texts_list = list(self.widget_texts_dict.keys())
        self.padx = 5
        self.pady = 5
        self.ipady = 7
        self.button_width_normal = 25
        self.button_width_small = 15
        self.combobox_width = 10
        self.VI_label_width = 10
        self.text_win_width = 106
        self.text_win_height = 6
        self.end = END

    def set_flag(self, flag, message):
        flag.set()
        if message != "":
            self.txt_win.insert(self.end, f"{message}\n")

    def check_queue_from_main(self):
        try:
            message = self.queue_2_gui.get_nowait()
            message = message.split('\n')
            if message[0] == "Error:":
                self.txt_win.insert(self.end, f"{message}\n")
                self.txt_win.see("end")
            elif message[0] == "Device_info:":
                text = message[1] + "\n" +  message[2] + "\n" + message[3] + "\n" + message[6] + "\n"
                print(text)
                self.device_info.set(text)
            elif message[0] == "Basic_info:":
                text = message[1] + "\n" +  message[2] + "\n" + message[3] + "\n" + message[5] + "\n"
                self.basic_info.set(text)
                self.voltage.set(message[2][5:])
                self.current.set(message[3][5:])
            elif message[0] == "Profiles_info:":
                for i in range(10):
                    print(message[i])
                for i in range(10):
                    self.profiles[i].set("")
                    text = self.profiles[i].get() + " "
                    text += message[i*3+2][10:] + " " + message[i*3+3][8:]
                    self.profiles[i].set(text)
            elif message[0] == "Active_profile:":
                self.active_profile = int(message[1][7:])
                self.state = int(message[2][7:])
                text = "Active profile: " + str(self.active_profile) + "\n"
                for i in range(10):
                    self.butt_profiles[i].configure(style="default.TButton")
                if self.state:
                    self.butt_on_off.configure(style="pressed.TButton", text=self.widget_texts_dict["On"])
                    self.butt_profiles[self.active_profile].configure(style="pressed.TButton")
                    text += "The Output is switched ON\n"
                else:
                    self.butt_on_off.configure(style="important.TButton", text=self.widget_texts_dict["Off"])
                    self.butt_profiles[self.active_profile].configure(style="important.TButton")
                    text += "The Output is switched OFF\n"
                print(text)
                self.txt_win.insert(self.end, f"{text}\n")
                self.txt_win.see("end")
            elif message[0] == "On_off:":
                if message[1][7:] == "True":
                    self.state = 1
                    self.butt_on_off.configure(style="pressed.TButton", text=self.widget_texts_dict["On"])
                    self.butt_profiles[self.active_profile].configure(style="pressed.TButton")
                else:
                    self.state = 0
                    self.butt_on_off.configure(style="important.TButton", text=self.widget_texts_dict["Off"])
                    self.butt_profiles[self.active_profile].configure(style="important.TButton")
                text = "The Output is switched ON" if self.state else "The Output is switched OFF"
                print(text)
                self.txt_win.insert(self.end, f"{text}\n")
            elif message[0] == "Off:":
                self.state = 0
                self.butt_on_off.configure(style="important.TButton", text=self.widget_texts_dict["Off"])
                self.butt_profiles[self.active_profile].configure(style="important.TButton")
                text = "The Output is switched OFF"
                print(text)
                self.txt_win.insert(self.end, f"{text}\n")
            elif message[0] == "PNG:":
                if message[1] == "plotted":
                    image = PhotoImage(file=self.png_filename)
                    self.label_PNG.configure(image = image)
                    self.label_PNG.image = image
        except queue.Empty:
            pass
        except TclError:
            print("Tcl Error: Cannot update elements.")
        except Exception as e:
            print(f"Unexpected error in check_queue_from_main: {e}")
        finally:
            # Schedule the next check only if the GUI is still running
            if self.mainWin.winfo_exists():
                self.mainWin.after(100, self.check_queue_from_main)

    def on_butt_connect(self):
        self.set_flag(self.flags_2_main["flag_connect"], self.widget_texts_dict["Device Information"])
        self.set_flag(self.flags_2_main["flag_get_basic_info"], self.widget_texts_dict["Basic Information"])
        self.txt_win.insert(self.end, f"{self.widget_texts_dict['Profiles']}\n")
        self.butt_connect.configure(style="pressed.TButton", text="Connected")
        self.butt_profiles[self.active_profile].configure(style="important.TButton")

    def on_butt_on_off(self):
        self.set_flag(self.flags_2_main["flag_on_off"], "")

    def on_butt_change_profile(self):
        p_nr = self.profile_set_nr.get()
        p_v = self.profile_set_v.get()
        p_i = self.profile_set_i.get()
        text = f"change_profile:\n{p_nr}\n{p_v}\n{p_i}"
        self.queue_2_main.put(text)  # Add the text to queue_2_main flag is set in main
        self.txt_win.insert(self.end, f"Setting profile {p_nr} to {p_v} V and {p_i} A\n")

    def on_butt_profile_pressed(self,nr):
        print("Profile Nr: ", nr)
        text = f"activate_profile:\n{nr}"
        self.queue_2_main.put(text)  # Add the text to queue_2_main flag is set in main
        self.txt_win.insert(self.end, f"Activating profile {nr}\n")

    def on_butt_reset_png(self):
        self.flags_2_main["flag_reset_png"].set()  # Set flag_reset_png

    def clear_textwindow(self):
        self.txt_win.delete(1.0, END)

    def on_close(self):
        """Handle GUI close event"""
        self.flags_2_main["flag_exit"].set()  # Set the exit flag
        self.mainWin.destroy()  # Close the GUI window

    def init_ttk_styles(self):
        self.s = ttk.Style()
        #frames
        self.s.configure("all.TFrame",
                         background="lightgrey")
        self.s.configure("test.TFrame",
                         background="grey")
        #widgets
        self.s.configure("default.TLabel",
                         background="lightgrey",
                         font=self.standard_font)
        self.s.configure("default_big.TLabel",
                         background="lightgrey",
                         foreground="red",
                         font=self.standard_font_big)
        self.s.configure("time.TLabel",
                         background="lightgrey",
                         font=self.standard_font)
        self.s.configure("default.TEntry",
                         background="lightgray",
                         font=self.standard_font)
        self.s.configure("default.TCombobox",
                         font=self.standard_font,
                         background="lightgrey",
                         fieldbackground="lightgrey",
                         arrowsize=20)
        self.s.configure("default.TSpinbox",
                         font=self.standard_font,
                         background="lightgrey",
                         fieldbackground="lightgrey",
                         arrowsize=20)
        self.s.configure("important.TButton",
                         background="orangered",
                         font=self.standard_font,
                         borderwidth=5)
        self.s.configure("default.TButton",
                         background="lightgrey",
                         font=self.standard_font,
                         borderwidth=5)
        self.s.configure("pressed.TButton",          # New style for pressed button
                         background="lawngreen",
                         font=self.standard_font,
                         borderwidth=5)
        self.s.map("important.TButton",
                   background = [("active", 'orangered')])
        self.s.map("pressed.TButton",
                   background = [("active", 'lawngreen')])

    def FontSizeUpdate(self):
        FSize = self.FSize.get()
        self.standard_font[1]=int(FSize)
        self.textbox_font[1]=int(FSize)
        print(self.standard_font)
        self.s.configure("default.TLabel", font=self.standard_font)
        self.s.configure("default_big.TLabel", font=self.standard_font_big)
        self.s.configure("time.TLabel", font=self.standard_font)
        self.s.configure("default.TEntry", font=self.standard_font)
        self.s.configure("default.TButton", font=self.standard_font)
        self.s.configure("important.TButton", font=self.standard_font)
        self.s.configure("pressed.TButton", font=self.standard_font)
        self.s.configure("default.TCombobox", font=self.standard_font)
        self.s.configure("default.TSpinbox",
                         font=self.standard_font,
                         background="lightgrey",
                         fieldbackground="lightgrey",
                         arrowsize=int(FSize)*1.5)
        self.txt_win.config(font=self.textbox_font)
        self.combobox_hpdir.config(font=self.standard_font)
        self.combobox_quick_links.config(font=self.standard_font)
        self.combobox_check_links.config(font=self.standard_font)
        self.spinb_fontsize.config(font=self.standard_font)

    def UpdateTime(self):
        ftime = strftime("%d.%m.%y %H:%M:%S", localtime())
        rtctime = strftime("%Y %m %d %H %M %S", localtime())
        intyear = str(int(rtctime[0:4])-1892)
        rtctimecorr = intyear[0:4]+rtctime[4:]
        self.label_time['text'] = ftime
        self.label_time.after(1000, self.UpdateTime)

    def run(self):
        self.mainWin = Tk()
        self.init_ttk_styles()
        self.FSize = StringVar()
        self.FSize.set("12")
        self.device_info = StringVar()
        self.device_info.set("\n\n\n\n")
        self.basic_info = StringVar()
        self.basic_info.set("\n\n\n\n")
        self.profiles = []
        for i in range(10):
            var = StringVar()
            var.set("P" + str(i) + ": ")
            self.profiles.append(var)
        self.voltage = StringVar()
        self.voltage.set("0.0 V")
        self.current = StringVar()
        self.current.set("0.0 A")
        self.profile_set_nr = IntVar()
        self.profile_set_nr.set(0)
        self.profile_set_v = DoubleVar()
        self.profile_set_nr.set(0)
        self.profile_set_i = DoubleVar()
        self.profile_set_nr.set(0)
        self.mainWin.protocol("WM_DELETE_WINDOW", self.on_close)
        self.mainWin.after(100, self.check_queue_from_main)  # Periodically check GUI queue
        self.mainWin.title(self.widget_texts_dict["Title"])
        self.mainWin.columnconfigure(0, weight=1)
        self.mainWin.rowconfigure(0, weight=1)
        # frame Main +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        self.frame_Main = ttk.Frame(self.mainWin, borderwidth=10, relief='ridge',
                                   padding="10 10 20 20", style = "all.TFrame")
        self.frame_Main.grid(column=0, row=0, sticky=(W, N, E, S))
        for column in range(1,3): # 2 columns
            self.frame_Main.columnconfigure(column, weight=1)
        for row in range(1,6):    # 5 rows
            self.frame_Main.rowconfigure(row, weight=1)

        # frame Header: Image with time and fontsize spinbox +++++++++++++++++++
        self.frame_Header = ttk.Frame(self.frame_Main, borderwidth=3, relief='groove',
                                      padding="10 10 20 20", style="all.TFrame")
        self.frame_Header.grid(column=1, row=1, columnspan=2, sticky=(N,W,E))
        for column in range(1,4): # 3 columns
            self.frame_Header.columnconfigure(column, weight=1)
        for row in range(1,4):    # 3 rows
            self.frame_Header.rowconfigure(row, weight=1)
        self.imageL1 = PhotoImage(file='dp100.png')
        self.label_png = ttk.Label(self.frame_Header, text="",
                                   image=self.imageL1,
                                   style="default.TLabel")
        self.label_png.grid(column=1, row=2, columnspan=3, sticky=N)
        self.label_time = ttk.Label(self.frame_Header, text="",
                                    justify='right',
                                    style="time.TLabel")
        self.label_time.grid(ipady=self.ipady, column=3, row=1, sticky=(N,E))
        self.frame_Fontsize = ttk.Frame(self.frame_Header, style="all.TFrame")
        self.frame_Fontsize.grid(column=3, row=3, sticky=(E,N))
        self.label_fontsize = ttk.Label(self.frame_Fontsize,
                                        text="Fontsize: ",
                                        style="default.TLabel")
        self.label_fontsize.grid(column=1, row=1,sticky=(E))
        self.spinb_fontsize = ttk.Spinbox(self.frame_Fontsize,from_=6, to=24,
                                          textvariable=self.FSize,
                                          command=self.FontSizeUpdate, width=4,
                                          justify='center',
                                          font=self.standard_font,
                                          style="default.TSpinbox")
        self.spinb_fontsize.grid(column=2, row=1, sticky=(E))

        # frame Connect +++++++++++++++++++++++++++++++++++++++++++++++++++++++
        self.frame_Connect = ttk.Frame(self.frame_Main,borderwidth=3, relief='groove',
                                      padding="10 10 20 20", style = "all.TFrame")
        self.frame_Connect.grid(column=1, row=2, sticky=(W,E))
        for column in range(1,7):
            self.frame_Connect.columnconfigure(column, weight=1)
        for row in range(1,7):
            self.frame_Connect.rowconfigure(row, weight=1)
        # 1 Button
        self.butt_connect = ttk.Button(self.frame_Connect,
                                       text=self.widget_texts_list[1],
                                       command=self.on_butt_connect,
                                       width=self.button_width_normal,
                                       style="important.TButton")
        self.butt_connect.grid(ipady=self.ipady, column=1,row=1, columnspan=2,sticky=(W))
        # 1 Frame with Device Infos
        self.frame_CD_info = ttk.Frame(self.frame_Connect, style="all.TFrame")
        self.frame_CD_info.grid(column=1, row=2, sticky=(W))
        self.label_CD_info = ttk.Label(self.frame_CD_info,
                                       text=self.widget_texts_list[2],
                                       padding="10 10 20 20",
                                       foreground="red",
                                       style="default.TLabel")
        self.label_CD_info.grid(column=1, row=1, sticky=(N,W,E))
        self.label_CD_info_2 = ttk.Label(self.frame_CD_info, relief='groove',
                                        padding="10 10 0 0",
                                        borderwidth = 5,
                                        width = 25,
                                        textvariable = self.device_info,
                                        style="default.TLabel")
        self.label_CD_info_2.grid(ipady=self.ipady, column=1, row=2, sticky=(S,W))
        # 2 Frame with Basic Infos
        self.frame_CB_info = ttk.Frame(self.frame_Connect, style="all.TFrame")
        self.frame_CB_info.grid(column=2, row=2, sticky=(W))
        self.label_CB_info = ttk.Label(self.frame_CB_info,
                                       text=self.widget_texts_list[3],
                                       padding="10 10 20 20",
                                       foreground="red",
                                       style="default.TLabel")
        self.label_CB_info.grid(column=1, row=1, sticky=(N,W))
        self.label_CB_info_2 = ttk.Label(self.frame_CB_info, relief='groove',
                                        padding="10 10 0 0",
                                        borderwidth = 5,
                                        width = 17,
                                        textvariable = self.basic_info,
                                        style="default.TLabel")
        self.label_CB_info_2.grid(ipady=self.ipady, column=1, row=2, sticky=(S,W))
        # On_Off4 button
        self.butt_on_off = ttk.Button(self.frame_Connect,
                                      text=self.widget_texts_dict["Off"],
                                      command=self.on_butt_on_off,
                                      width=self.button_width_normal,
                                      style="important.TButton")
        self.butt_on_off.grid(ipady=self.ipady, column=4, row=1, sticky=(W,E))
        # 3 Frame with voltage and current
        self.frame_VI = ttk.Frame(self.frame_Connect, style="all.TFrame")
        self.frame_VI.grid(column=4, row=2, sticky=(W))
        self.label_V = ttk.Label(self.frame_VI,
                                 text=self.widget_texts_dict["Output"],
                                 padding="10 10 20 20",
                                 foreground="red",
                                 style="default.TLabel")
        self.label_V.grid(column=1, row=1, sticky=(N,W))
        self.label_V_value = ttk.Label(self.frame_VI,
                                        relief='groove',
                                        padding="80 10 10 10",
                                        borderwidth = 5,
                                        width=self.VI_label_width,
                                        justify="center",
                                        textvariable = self.voltage,
                                        style="default_big.TLabel")
        self.label_V_value.grid(ipady=self.ipady, column=1, row=2, sticky=(S,W))
        self.label_I_value = ttk.Label(self.frame_VI,
                                        relief='groove',
                                        padding="80 10 10 10",
                                        borderwidth = 5,
                                        width=self.VI_label_width,
                                        textvariable = self.current,
                                        style="default_big.TLabel")
        self.label_I_value.grid(ipady=self.ipady, column=1, row=4, sticky=(S,W))

        # 4 frame Profile buttons ++++++++++++++++++++++++++++++++++++++++++++
        self.frame_P_buttons = ttk.Frame(self.frame_Connect, borderwidth=3,
                                         padding="10 0 10 0", style = "all.TFrame")
        self.frame_P_buttons.grid(column=5, row=1, rowspan=2, sticky=(E))
        self.butt_profiles = []
        for i in range(10):
            self.butt_profiles.append(ttk.Button(self.frame_P_buttons,
                                      textvariable=self.profiles[i],
                                      command=partial(self.on_butt_profile_pressed, i),
                                      width=self.button_width_small,
                                      style="default.TButton"))
        for i in range(5):
            self.butt_profiles[i].grid(ipady=self.ipady, column=1, row=i, sticky=(W,E))
            self.butt_profiles[i+5].grid(ipady=self.ipady, column=2, row=i, sticky=(W,E))

        # 5 frame change profile ++++++++++++++++++++++++++++++++++++++++++++++++++
        self.frame_C_Profile = ttk.Frame(self.frame_Connect, style="all.TFrame")
        self.frame_C_Profile.grid(column=6, row=1, rowspan = 2, sticky=(E))
        for column in range(1,3):
            self.frame_C_Profile.columnconfigure(column, weight=1)
        for row in range(1,3):
            self.frame_C_Profile.rowconfigure(row, weight=1)
        self.butt_change_profile = ttk.Button(self.frame_C_Profile,
                                              text=self.widget_texts_dict["Change_Profile"],
                                              command=self.on_butt_change_profile,
                                              width=self.button_width_normal,
                                              style="important.TButton")
        self.butt_change_profile.grid(ipady=self.ipady, column=1, columnspan = 2, row=1, sticky=(W,E))
        self.label_p_nr = ttk.Label(self.frame_C_Profile,
                                    text=self.widget_texts_dict["Profile Nr"],
                                    padding="10 20 10 20",
                                    foreground="red",
                                    style="default.TLabel")
        self.label_p_nr.grid(column=1, row=2, sticky=(W))
        self.combobox_p_nr = ttk.Combobox(self.frame_C_Profile,
                                          width = self.combobox_width,
                                          textvariable=self.profile_set_nr,
                                          font=self.standard_font,
                                          style="default.TCombobox")
        self.combobox_p_nr.grid(ipady=self.ipady, column=2, row=2, sticky=(E))
        self.combobox_p_nr['values'] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.combobox_p_nr.current()
        self.label_p_v = ttk.Label(self.frame_C_Profile,
                                   text=self.widget_texts_dict["Set Voltage"],
                                   padding="10 20 10 20",
                                   foreground="red",
                                   style="default.TLabel")
        self.label_p_v.grid(column=1, row=3, sticky=(W))
        self.combobox_p_v = ttk.Combobox(self.frame_C_Profile,
                                         width = self.combobox_width,
                                         textvariable=self.profile_set_v,
                                         font=self.standard_font,
                                         style="default.TCombobox")
        self.combobox_p_v.grid(ipady=self.ipady, column=2, row=3, sticky=(E))
        self.combobox_p_v['values'] = [2.0, 3.0, 4.5, 5.0, 6.0, 9.0, 10.0, 12.0]
        self.combobox_p_v.current()
        self.label_p_i = ttk.Label(self.frame_C_Profile,
                                   text=self.widget_texts_dict["Set Current"],
                                   padding="10 20 10 20",
                                   foreground="red",
                                   style="default.TLabel")
        self.label_p_i.grid(column=1, row=4, sticky=(W))
        self.combobox_p_i = ttk.Combobox(self.frame_C_Profile,
                                         width = self.combobox_width,
                                         textvariable=self.profile_set_i,
                                         font=self.standard_font,
                                         style="default.TCombobox")
        self.combobox_p_i.grid(ipady=self.ipady, column=2, row=4, sticky=(E))
        self.combobox_p_i['values'] = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.8, 1.0]
        self.combobox_p_i.current()

        # frame png image  ++++++++++++++++++++++++++++++++++++++++++++++++++++
        self.frame_PNG = ttk.Frame(self.frame_Main,  style="all.TFrame")
        self.frame_PNG.grid(column=1, row=3, columnspan=2,  sticky=(W,E))
        for column in range(1,3): # 2 columns
            self.frame_PNG.columnconfigure(column, weight=10)
        for row in range(1,3):    # 2 rows
            self.frame_PNG.rowconfigure(row, weight=10)
        #image = PhotoImage(file="idle.png")
        self.label_PNG = ttk.Label(self.frame_PNG,
                                   relief='groove',
                                   padding="10 10 10 10",
                                   borderwidth = 5,
                                   #image=image,
                                   style="default_big.TLabel")
        self.label_PNG.grid(ipady=self.ipady, column=1, row=1, sticky=(S,W))

        # frame Textbox +++++++++++++++++++++++++++++++++++++++++++++++++++++++
        self.frame_Textbox = ttk.Frame(self.frame_Main,  style="all.TFrame")
        self.frame_Textbox.grid(column=1, row=4, columnspan=2,  sticky=(W,E))
        for column in range(1,3): # 2 columns
            self.frame_Textbox.columnconfigure(column, weight=10)
        for row in range(1,3):    # 2 rows
            self.frame_Textbox.rowconfigure(row, weight=10)
        self.txt_win = Text(self.frame_Textbox,
                            font=self.textbox_font,
                            state='normal',
                            width = self.text_win_width,
                            height = self.text_win_height)
        self.txt_win.grid(column=1, row=1, sticky=(N,S,E))
        self.txt_win.insert(END, self.welcome_txt + "\n\n")
        self.scrollbar = ttk.Scrollbar(self.frame_Textbox, orient=VERTICAL,
                                       command=self.txt_win.yview)
        self.scrollbar.grid(column=2, row=1, sticky=(N,S,W))
        self.txt_win.configure(yscrollcommand=self.scrollbar.set)

        # frame Footer: Quit ++++++++++++++++++++++++++++++++++++++++++++++++++
        self.frame_Footer = ttk.Frame(self.frame_Main,  borderwidth=3,
                                      padding="10 10 10 10", relief='groove',
                                      style="all.TFrame")
        self.frame_Footer.grid(column=1, row=5, columnspan=2,  sticky=(S,W,E))
        for column in range(1,3): # 2 columns
            self.frame_Footer.columnconfigure(column, weight=1)
        for row in range(1,2):    # 1 rows
            self.frame_Footer.rowconfigure(row, weight=1)
        self.butt_clear_win = ttk.Button(self.frame_Footer,
                                         text=self.widget_texts_dict["Clear Textwindow"],
                                         command=self.clear_textwindow,
                                         width=self.button_width_normal,
                                         style="default.TButton")
        self.butt_clear_win.grid(ipady=self.ipady, column=1, row=1, sticky=(W,S))
        self.butt_reset_png = ttk.Button(self.frame_Footer,
                                         text=self.widget_texts_dict["Clear PNG"],
                                         command=self.on_butt_reset_png,
                                         width=self.button_width_normal,
                                         style="default.TButton")
        self.butt_reset_png.grid(ipady=self.ipady, column=2, row=1, sticky=(W,S))
        self.butt_quit = ttk.Button(self.frame_Footer,
                                    text=self.widget_texts_dict["Quit"],
                                    command=self.on_close,
                                    width=self.button_width_normal,
                                    style="default.TButton")
        self.butt_quit.grid(ipady=self.ipady, column=3, row=1,sticky=(S,E))

        self.UpdateTime()

        # Padding
        for child in self.frame_Main.winfo_children():
            child.grid_configure(padx=self.padx, pady=self.pady)
        for child in self.frame_Fontsize.winfo_children():
            child.grid_configure(padx=self.padx, pady=self.pady)
        for child in self.frame_Connect.winfo_children():
            child.grid_configure(padx=self.padx, pady=self.pady)
        for child in self.frame_PNG.winfo_children():
            child.grid_configure(padx=self.padx, pady=self.pady)
        for child in self.frame_Textbox.winfo_children():
            child.grid_configure(padx=self.padx, pady=self.pady)
        for child in self.frame_Footer.winfo_children():
            child.grid_configure(padx=self.padx, pady=self.pady)

        self.mainWin.mainloop()

def start_gui(flags_2_main, queue_2_main, queue_2_gui, png_filename):
    gui = GUI(flags_2_main, queue_2_main, queue_2_gui, png_filename)
    gui.run()
