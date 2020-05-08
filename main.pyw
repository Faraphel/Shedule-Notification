from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from tkinter import ttk
from tkinter import *
import webbrowser
import time
from tkinter import messagebox
from pystray import Icon, Menu, MenuItem
from PIL import Image
import threading
import json

class AppClass():
    def __init__(self):
        self.EU2FR_date = {
        "Monday": "Lundi",
        "Tuesday": "Mardi",
        "Wednesday": "Mercredi",
        "Thursday": "Jeudi",
        "Friday": "Vendredi",
        "Saturday": "Samedi",
        "Sunday": "Dimanche"
        }
        self.ButtonWidgetSchedule = []
        self.day_start = 8
        self.day_total = 10
        self.dayList = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]

        self.root = Tk()
        self.root.title("Emploie du temps")
        self.root.iconbitmap("icon.ico")


        self.LB_Schedule = LabelFrame(self.root, text = "Emploie du temps")
        self.LB_Schedule.grid(row = 1, column = 1, sticky = "NEWS", rowspan = 4)

        for hour in range(self.day_total * 2):
            if hour % 2: text = ""
            else: text = "%ih30" % ((hour // 2) + self.day_start)

            Label(self.LB_Schedule, text = text).grid(row = hour + 1, column = 0)

        for day, date in enumerate(self.dayList):
            Label(self.LB_Schedule, text = date).grid(row = 0, column = day + 1)

            for hour in range(0, self.day_total * 2, 2):
                Label(self.LB_Schedule,
                width = 20,
                height = 3,
                background = "lightgray",
                relief = RIDGE
                ).grid(row = hour + 1, column = day + 1, rowspan = 2)


        self.LB_GetActivityID = LabelFrame(self.root, text = "Obtenir l'ActivityID'")
        self.LB_GetActivityID.grid(row = 1, column = 2, sticky = "NEWS")

        Label(self.LB_GetActivityID, text = "écrivez ici le code venant après\n\"https://cvirtuelle.phm.education.gouv.fr/\"", font = ("tkDefaultFont", 7)).grid(row = 2, column = 1, columnspan = 2)

        self.Entry_Url = Entry(self.LB_GetActivityID)
        self.Entry_Url.grid(row = 3, column = 1, sticky = "NEWS")

        self.Button_Url = Button(self.LB_GetActivityID, text = "Rechercher", command = self.get_ActivityID, relief = RIDGE)
        self.Button_Url.grid(row = 4, column = 1, sticky = "NEWS")


        self.LB_GetUrlApp = LabelFrame(self.root, text = "Entrer l'ActivityID")
        self.LB_GetUrlApp.grid(row = 2, column = 2, sticky = "NEWS")

        Label(self.LB_GetUrlApp, text = "écrivez ici l'ActivityID (voir ci-dessus pour l'obtenir)", font = ("tkDefaultFont", 7)).grid(row = 2, column = 1, columnspan = 2)
        self.Entry_ActivityID = Entry(self.LB_GetUrlApp)
        self.Entry_ActivityID.grid(row = 3, column = 1, columnspan = 2, sticky = "NEWS")

        self.Button_ActivityID = Button(self.LB_GetUrlApp, text = "Générer", command = self.get_url, relief = RIDGE)
        self.Button_ActivityID.grid(row = 6, column = 1, columnspan = 2, sticky = "NEWS")

        Label(self.LB_GetUrlApp, text = "Prénom").grid(row = 4, column = 1)
        self.FirstName = Entry(self.LB_GetUrlApp)
        self.FirstName.grid(row = 5, column = 1, sticky = "NEWS")
        Label(self.LB_GetUrlApp, text = "Nom").grid(row = 4, column = 2)
        self.LastName = Entry(self.LB_GetUrlApp)
        self.LastName.grid(row = 5, column = 2, sticky = "NEWS")


        self.LB_GetUrlApp = LabelFrame(self.root, text = "URL")
        self.LB_GetUrlApp.grid(row = 3, column = 2, sticky = "NEWS")

        self.Text_UrlApp = Text(self.LB_GetUrlApp, width = 30, state = DISABLED, height = 8)
        self.Text_UrlApp.grid(row = 1, column = 1)

        Button(self.LB_GetUrlApp,
        text = "Ouvrir",
        command = self.goto_lesson,
        relief = RIDGE
        ).grid(row = 2, column = 1, sticky = "NEWS")

        self.LB_Other = LabelFrame(self.root, text = "Autre")
        self.LB_Other.grid(row = 4, column = 2, sticky = "NEWS")

        Button(self.LB_Other, text = "Fermer l'application", command = self.quit, relief = RIDGE).grid(row = 1, column = 1)


        self.SysStrayThread = threading.Thread(target = self.SystemStray)
        self.SysStrayThread.daemon = True
        self.SysStrayThread.start()
        self.root.protocol('WM_DELETE_WINDOW', self.show)

        self.notification_set()


    def notification_set(self):
        self.refresh()


        if self.closest_lesson["hour"] != 1000:
            actual_time = (int(time.strftime("%H")) * 60) + int(time.strftime("%M")) # temps en minute actuel
            lesson_time = self.closest_lesson["hour"] * 30 # On converti l'heure du cours en minute

            sleep_time_1h =     lesson_time - actual_time - 60 # Temps a attendre pour signaler 1h avant le cours
            sleep_time_30m =    lesson_time - actual_time - 30 # Temps a attendre pour signaler 30min avant le cours
            sleep_time_10m =    lesson_time - actual_time - 10 # Temps a attendre pour signaler 10min avant le cours
            sleep_time = lesson_time - actual_time

            self.root.after(sleep_time_1h * 60000,    lambda: self.notification_lesson(time_lesson = "1 heure"))
            self.root.after(sleep_time_30m * 60000,   lambda: self.notification_lesson(time_lesson = "30 minutes"))
            self.root.after(sleep_time_10m * 60000,   lambda: self.notification_lesson(time_lesson = "10 minutes"))
        else:
            sleep_time = 0

        print("[%s] : %i (Tps Attente : %i)" % (time.strftime("%H:%M:%S"), sleep_time, (sleep_time + 1) * 60000))

        self.root.after((sleep_time + 1) * 60000,       self.notification_set)


    def show(self, icon = None, item = None):
        if self.isHide: self.root.deiconify()
        else: self.root.withdraw()

        self.isHide = not(self.isHide)


    def quit(self, icon = None, item = None):
        self.root.quit()


    def SystemStray(self):
        self.isHide = False

        Icon('EDT num.', Image.open("icon.ico"), menu=Menu(
            MenuItem('Afficher', self.show, checked = lambda item: None, default = True),
            MenuItem('Quitter', self.quit, checked = lambda item: None)
            )).run()


    def notification_lesson(self, time_lesson):
        self.duration_toast = 60
        w, h = self.root.winfo_screenwidth(), self.root.winfo_screenheight()

        self.notification_tl = Toplevel(bg = "#306F9F")
        self.notification_tl.geometry("%ix%i+%i+%i" % (w // 4, h // 7, w - w // 3.8, h - h // 5))
        self.notification_tl.overrideredirect(True)

        self.notification_tl.rowconfigure(0, weight = 1)
        self.notification_tl.rowconfigure(10, weight = 1)
        self.notification_tl.columnconfigure(0, weight = 1)
        self.notification_tl.columnconfigure(10, weight = 1)

        Label(self.notification_tl,
        text = "Vous avez cours (%s) dans %s" % (self.closest_lesson["lesson"], time_lesson),
        fg = "white",
        bg = "#306F9F",
        font = ("Segoe UI", 12, "bold")
        ).grid(row = 1, column = 1)

        Button(self.notification_tl,
        text = "Cliquez-ici pour le rejoindre",
        fg = "white",
        bg = "#205F8F",
        font = ("Segoe UI", 12),
        borderwidth = 0,
        command = self.goto_lesson,
        ).grid(row = 2, column = 1, pady = 10, sticky = "NEWS")

        self.notification_tl.after(20000, self.notification_tl.destroy)
        self.notification_tl.attributes('-topmost', True)


    def goto_lesson(self):
        self.get_url()
        webbrowser.open_new(self.Text_UrlApp.get("0.0", END))


    def set_lesson(self, lesson):
        if "Link" in self.choices[lesson].keys():
            self.Text_UrlApp.config(state = NORMAL)
            self.Text_UrlApp.delete("0.0", END)
            self.Text_UrlApp.insert("0.0", self.choices[lesson]["Link"])
            self.Text_UrlApp.config(state = DISABLED)
        else:
            self.Text_UrlApp.config(state = NORMAL)
            self.Text_UrlApp.delete("0.0", END)
            self.Text_UrlApp.config(state = DISABLED)

        if "ActivityID" in self.choices[lesson].keys():
            self.Entry_ActivityID.delete(0, END)
            self.Entry_ActivityID.insert(0, self.choices[lesson]["ActivityID"])
            self.get_url()
        else: self.Entry_ActivityID.delete(0, END)

        if "LinkID" in self.choices[lesson].keys(): # Si le cours utilise Via
            self.Entry_Url.delete(0, END)
            self.Entry_Url.insert(0, self.choices[lesson]["LinkID"])
        else: self.Entry_Url.delete(0, END)


    def refresh(self):
        self.closest_lesson = {"lesson": None, "hour": 1000}

        with open("lesson.json", "rb") as File:
            self.choices = json.load(File)


        for widget in self.ButtonWidgetSchedule: widget.destroy()
        self.ButtonWidgetSchedule = []

        for lesson in self.choices:
            date, schedule = self.choices[lesson]["Start"].split(" ")
            hour, minute = schedule.split("h")

            hour = int(hour)
            hour *= 2
            if minute == "30": hour += 1

            if self.EU2FR_date[time.strftime("%A")] == date:
                if (int(time.strftime("%H")) * 60) + int(time.strftime("%M")) < hour * 30:
                    if self.closest_lesson["hour"] > hour:
                        self.closest_lesson["lesson"] = lesson
                        self.closest_lesson["hour"] = hour

            duration_hour, duration_min = self.choices[lesson]["Duration"].split("h")

            duration_hour = int(duration_hour)
            duration_hour *= 2
            if duration_min == "30": duration_hour += 1

            self.ButtonWidgetSchedule.append(
            Button(self.LB_Schedule,
            text = lesson,
            background = "lightgray",
            borderwidth = 2,
            bg = self.choices[lesson]["Color"],
            relief = GROOVE,
            command = lambda lesson = lesson: self.set_lesson(lesson),
            ))

            self.ButtonWidgetSchedule[-1].grid(
            row = hour - (self.day_start * 2),
            column = self.dayList.index(date) + 1,
            rowspan = duration_hour,
            sticky = "NEWS")

            self.root.update()


    def get_url(self, title = None, PresenterName = None, PresenterPictureID = None):
        options = webdriver.ChromeOptions()
        options.headless = True
        options.add_argument('--no-sandbox') # Conseiller par les forums

        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options = options)


        Url =  "viaapp:https://cvirtuelle.phm.education.gouv.fr/guestActivity?"
        Url += "activityID=" + self.Entry_ActivityID.get()
        if title != None:               Url += "&title=" + title
        if PresenterName != None:       Url += "&presenterName=" + PresenterName
        if PresenterPictureID != None:  Url += "&presenterPictureID=" + PresenterPictureID
        if self.FirstName.get() != "":  Url += "&firstName=" + self.FirstName.get()
        if self.LastName.get() != "":   Url += "&lastName=" + self.LastName.get()

        self.Text_UrlApp.config(state = NORMAL)
        self.Text_UrlApp.delete("0.0", END)
        self.Text_UrlApp.insert("0.0", Url)
        self.Text_UrlApp.config(state = DISABLED)


    def get_ActivityID(self):
        hyperlink = self.Entry_Url.get()
        if hyperlink == "Pas d'ID":
            return 0

        self.driver.get("https://cvirtuelle.phm.education.gouv.fr/LoginP?hyperlink=" + hyperlink)

        CS = self.driver.page_source.split("\n")
        try: CS_button = next(i for i in CS if "activityAccessPopUp.openAccess" in i)
        except StopIteration:
            messagebox.showerror("Erreur",
            "Une erreur est survenue dans la récupération de l'ActivityID.\
            \nIl se peut que :\n\n\
            \t- Ce cours soit déjà terminé.\n\n\
            \t- Ce cours ne soit disponible que 30 minutes avant qu'il débute."
            )
            return -1


        i_start = CS_button.index("[")
        i_end = CS_button.index("]") + 1

        false = False
        true = True

        list_arg_button = eval(CS_button[i_start:i_end])

        self.Entry_ActivityID.delete(0, END)
        self.Entry_ActivityID.insert(0, str(list_arg_button[2]))

        App.driver.quit()


App = AppClass()
mainloop()

# Enregistrer automatiquement les noms / prénoms
# Mettre automatiquement à jour les cours
# Cliquer sur le boutton du rappel créer le lien avant de l'utiliser
# Lancer l'application alors que le cours aurait du être rappeller il y a 1h, il indique directement le temps restant
