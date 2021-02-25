# TODO - Add Refresh Button in Chat
# TODO - Fix Bug Where Chat Page Automatically sends Empty Messages When Opened
# TODO - Add Support For Downloading Individual Files
# TODO - Add Support For Downloading Versions
# TODO - Add An Option To Download A Project, Which will download All files in the Latest Version of the Project

import datetime
import os
import json
import smtplib
import urllib
import pyrebase
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineListItem
from kivymd.uix.textfield import MDTextField

Window.clearcolor = (1, 1, 1, 1)
Window.maximize()

with open("firebase_config.json", "r") as read_file:
    firebaseConfig = json.load(read_file)

CodeX_Base = pyrebase.initialize_app(firebaseConfig)

database = CodeX_Base.database()
auth = CodeX_Base.auth()
storage = CodeX_Base.storage()


# Time = datetime.datetime.now().strftime("%H:%M:%S")


class FileDialogContent(BoxLayout):
    def __init__(self):
        super(FileDialogContent, self).__init__()
        global file_text_field

        file_text_field = MDTextField()
        file_text_field.hint_text = "File Name"

        self.add_widget(file_text_field)


class VersionDialogContent(BoxLayout):
    def __init__(self):
        super(VersionDialogContent, self).__init__()
        global version_text_field, version_file_field, sm, screen1, screen2, screen2

        sm = ScreenManager()
        screen1 = MDScreen(name="Screen 1")
        screen2 = MDScreen(name="Screen 2")
        screen3 = MDScreen(name="Screen 3")

        version_text_field = MDTextField()
        version_text_field.hint_text = "Version Number"
        version_file_field = MDTextField()
        version_file_field.hint_text = "File Name"

        label = MDLabel(text="Please Wait For A minute After you Press The 'Next' Button")

        screen1.add_widget(version_text_field)
        screen2.add_widget(version_file_field)
        screen3.add_widget(label)

        sm.add_widget(screen1)
        sm.add_widget(screen2)
        sm.add_widget(screen3)

        self.add_widget(sm)

        sm.current = "Screen 1"


class Main(MDApp):
    title = "CodeX Base"
    icon = "codex.png"

    project_name = StringProperty()
    version_name = StringProperty()
    file_name = StringProperty()
    file_content = []
    content = ""

    version_dialog = None
    file_dialog = None

    def build(self, **kwargs):
        self.theme_cls.primary_palette = "Indigo"

        return Builder.load_string(KV)

    def change_screen(self, *args):
        self.root.current = "MainPanel"
        self.update_main_panel()

    def login(self, *args):
        global username
        username = self.root.ids.username.text
        user_password = self.root.ids.password.text
        user_email = self.root.ids.email.text
        MainPanel = self.root.ids.MainPanel
        try:
            auth.sign_in_with_email_and_password(user_email, user_password)
            time = datetime.datetime.now().strftime("%H:%M:%S")
            database.child("Users").child(username).update({'Login Time': time})
            toast("Login successful")
            self.change_screen()
        except:
            toast("Incorrect username or password")

    def create(self, *args):
        new_name = self.root.ids.Reg_username.text
        new_email = self.root.ids.Reg_email.text
        new_password = self.root.ids.Reg_password.text

        try:
            auth.create_user_with_email_and_password(new_email, new_password)
            time = datetime.datetime.now().strftime("%H:%M:%S")
            add_data = {'Email': new_email, 'Username': new_name, 'Login Time': time, 'Type': 'User',
                        'Password': new_password}
            database.child("Users").child(new_name).set(add_data)
            toast("Account created successfully!")
        except:
            toast("This Email Isn't available")

    def forgot_details(self, *args):
        try:
            forgot_username = self.root.ids.forgot_username.text

            # Getting The Details
            users = database.child("Users").get()
            for search in users.each():
                every_user = database.child("Users").child(forgot_username).get()
                registered_email = (every_user.val()['Email'])
                login_username = (every_user.val()['Username'])
                login_password = (every_user.val()['Password'])

            # Sending mail
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login("teamcodexbase@gmail.com", "#codex_teamSQL455")
            server.sendmail(
                "teamcodexbase@gmail.com",
                registered_email,
                "The Login Details For your Codex Account are " + "\n" + str(login_username) + "\n" + str(
                    login_password))
            server.quit()
            toast("Your Login Details have been sent To your registered Email ID")

        except:
            toast("An error occurred.Please try again")

    def new_project(self):
        project_names = []

        try:
            project_name = self.root.ids.project_name.text
            starter_file = self.root.ids.starter_file.text
            projects = database.child("Projects").get()

            for every_project in projects.each():
                project = every_project.key()
                print(project)
                project_names.append(project)

            if project_name in project_names:
                toast("This Project Already Exists")

            elif (project_name != "") and (starter_file != ""):
                # Temp File
                open(starter_file, "a").close()

                storage.child("Projects").child(project_name).child("Versions").child("Version1.0").child(
                    starter_file).put(starter_file)

                os.remove(starter_file)

                add_data = {"Project Name": str(project_name)}
                database.child("Projects").child(project_name).set(add_data)

                toast(f"New project created by the name '{project_name}'")
            else:
                toast("Incorrect Project Name")
        except:
            toast("An Error Occurred.Please Try Again")

        # project_name = self.root.ids.project_name.text
        #
        # add_data = {"Project Name": str(project_name)}
        # add_data45 = {"Version1": {"File": f"Projects/{project_name}/Versions/Version1"}}
        # database.child("Projects").child(project_name).set(add_data)
        # database.child("Projects").child(project_name).child("Versions").set(add_data45)
        # database.child("Projects").child(project_name).child("Latest Version").set("1")
        #
        # toast(f"New project created by the name '{project_name}'")

    def new_version_dialog(self):
        project_name = self.project_name

        self.version_dialog = MDDialog(title="New Version",
                                       type="custom",
                                       content_cls=VersionDialogContent(),
                                       auto_dismiss=False,
                                       buttons=[
                                           MDFlatButton(text="Cancel", on_release=self.close_version_dialog),
                                           MDRaisedButton(text="Next",
                                                          on_release=lambda x: self.new_version(
                                                              version_text_field.text, version_file_field.text))
                                       ])
        self.version_dialog.open()

    def close_version_dialog(self, *args):
        self.version_dialog.dismiss()

    def new_version(self, version, starter_file):
        if sm.current == "Screen 1":
            sm.current = "Screen 2"
            self.version_dialog.title = "Create A Starter File For Your New Version"

        elif sm.current == "Screen 2":
            sm.current = "Screen 3"

        elif sm.current == "Screen 3":
            if type(version) == str:
                try:
                    version = float(version)
                except ValueError:
                    pass

            if type(version) == int:
                version = float(version)

            if type(version) == float:
                version_exists = database.child("Sorting").child("Versions").child("Exists").get().val()
                unsorted_versions = storage.list_files()

                for each_value in unsorted_versions:
                    if f"Projects/{self.project_name}/Versions/Version{version}/" in str(each_value.name):
                        database.child("Sorting").child("Versions").child("Exists").set("True")

                if version_exists == "False":
                    # Temp File
                    open(starter_file, "a").close()

                    storage.child("Projects").child(self.project_name).child("Versions").child(
                        f"Version{version}").child(starter_file).put(starter_file)
                    os.remove(starter_file)

                    self.update_version_panel()
                    self.close_version_dialog()

                    toast(f"Made A New Version 'Version {version}' of Project '{self.project_name}'")
                else:
                    toast("This Version Already Exists.")

            else:
                toast("Please Enter A Proper Version Number")

    def close_file_dialog(self, *args):
        self.file_dialog.dismiss()

    def new_file_dialog(self, *args):
        self.file_dialog = MDDialog(title="New File",
                                    type="custom",
                                    auto_dismiss=False,
                                    content_cls=FileDialogContent(),
                                    buttons=[
                                        MDFlatButton(text="Cancel", on_release=self.close_file_dialog),
                                        MDRaisedButton(text="Make New File",
                                                       on_release=lambda x: self.new_file(file_text_field.text))
                                    ])

        self.file_dialog.open()

    def new_file(self, name_of_file, create_new_file=True):
        project = self.project_name
        version = self.version_name
        print(name_of_file)

        if name_of_file != "":
            unsorted_files = storage.list_files()
            file_exists = database.child("Sorting").child("Files").child("Exists").get().val()
            print(str(file_exists))

            if create_new_file:
                for each_value in unsorted_files:
                    if f"Projects/{self.project_name}/Versions/Version{version}/{name_of_file}" in str(each_value.name):
                        database.child("Sorting").child("Files").child("Exists").set("True")

            if file_exists == "False":
                # temp file
                open(os.path.join("temp", name_of_file), 'a').close()

                storage.child("Projects").child(project).child("Versions").child(version).child(
                    name_of_file).put(os.path.join("temp", name_of_file))

                os.remove(os.path.join("temp", name_of_file))

                try:
                    self.update_file_panel()
                    self.close_file_dialog()
                except AttributeError:
                    pass

                if create_new_file:
                    toast(f"New File created for {version} of Project '{project}'")
                else:
                    toast("Saved File")

            elif file_exists == "True":
                toast("This File Already Exists")

        else:
            toast("Please Enter A File Name")

    def update_main_panel(self):
        self.root.ids.projects_panel.clear_widgets()

        try:
            unsorted_projects = storage.list_files()
            projects = []
            for each_value in unsorted_projects:
                print(each_value.name)
                if each_value.name == f"Projects/":
                    pass
                elif f"Projects/" in each_value.name:
                    print(f"After Processing: {each_value.name}")
                    each_value.name = each_value.name.replace(
                        f"Projects/", "")
                    splited_files = each_value.name.split("/")
                    print(f"Splited Files: {splited_files}")
                    each_value.name = splited_files[0]
                    print(f"Each Value.name: {each_value.name}")
                    projects.append(each_value.name)

            # Remove Duplicates
            projects = list(dict.fromkeys(projects))

            for every_project in projects:
                if every_project != "":
                    self.root.ids.projects_panel.add_widget(
                        OneLineListItem(text=every_project,
                                        on_release=lambda x: self.project_clicked(x.text)
                                        ))
        except:
            pass

        # projects = database.child("Projects").get()
        # self.root.ids.projects_panel.clear_widgets()
        # try:
        #     for every_project in projects.each():
        #         each_project = every_project.val()
        #         each_project_name = each_project["Project Name"]
        #
        #         self.root.ids.projects_panel.add_widget(
        #             OneLineListItem(text=each_project_name,
        #                             on_release=lambda x: self.project_clicked(x.text)))
        # except:
        #     pass

    def update_version_panel(self):
        self.root.ids.version_panel.clear_widgets()

        try:
            unsorted_versions = storage.list_files()
            versions = []
            for each_value in unsorted_versions:
                print(each_value.name)
                if each_value.name == f"Projects/{self.project_name}/Versions/":
                    pass
                elif f"Projects/{self.project_name}/Versions/" in each_value.name:
                    print(f"After Processing: {each_value.name}")
                    each_value.name = each_value.name.replace(
                        f"Projects/{self.project_name}/Versions/", "")
                    splited_files = each_value.name.split("/")
                    print(f"Splited Files: {splited_files}")
                    each_value.name = splited_files[0]
                    print(f"Each Value.name: {each_value.name}")
                    versions.append(each_value.name)

            # Remove Duplicates
            versions = list(dict.fromkeys(versions))

            for every_version in versions:
                if every_version != "":
                    # print(every_file)
                    self.root.ids.version_panel.add_widget(
                        OneLineListItem(text=every_version,
                                        on_release=lambda x: self.version_clicked(x.text)
                                        ))
        except:
            pass

        # versions = database.child("Projects").child(self.project_name).child("Versions").get()
        # self.root.ids.version_panel.clear_widgets()
        #
        # try:
        #     for every_version in versions.each():
        #         version = every_version.key()
        #         print(version)
        #
        #         self.root.ids.version_panel.add_widget(
        #             OneLineListItem(text=version,
        #                             on_release=lambda x: self.version_clicked(x.text)
        #                             ))
        # except:
        #     pass

    def update_file_panel(self):
        self.root.ids.file_panel.clear_widgets()

        try:
            unsorted_files = storage.list_files()
            files = []
            for each_value in unsorted_files:
                print(each_value.name)
                if each_value.name == f"Projects/{self.project_name}/Versions/{self.version_name}/":
                    pass
                elif f"Projects/{self.project_name}/Versions/{self.version_name}/" in each_value.name:
                    print(f"After Processing: {each_value.name}")
                    each_value.name = each_value.name.replace(
                        f"Projects/{self.project_name}/Versions/{self.version_name}/", "")
                    files.append(each_value.name)

            # Remove Duplicates
            files = list(dict.fromkeys(files))

            for every_file in files:
                if every_file != "":
                    # print(every_file)
                    self.root.ids.file_panel.add_widget(
                        OneLineListItem(text=every_file,
                                        on_release=lambda x: self.file_clicked(x.text)
                                        ))
        except:
            pass

    def project_clicked(self, project_name):
        self.project_name = project_name
        self.root.current = "Version Screen"

        self.update_version_panel()

    def version_clicked(self, version_name):
        self.version_name = version_name
        self.root.current = "File Screen"

        self.update_file_panel()

    def file_clicked(self, file_name):
        self.file_name = file_name
        print(file_name)
        print(self.file_name)

        if self.file_name != file_name:
            self.file_name = file_name

        self.root.current = "Every File Screen"

        self.update_file(file_name)

    def update_file(self, filename):
        url = storage.child(f"Projects/{self.project_name}/Versions/{self.version_name}/{filename}").get_url(None)
        print(url)

        file = urllib.request.urlopen(url)
        self.file_content = []

        for line in file:
            decoded_line = line.decode("utf-8")
            decoded_line = decoded_line.rstrip("\r\n")
            self.file_content.append(decoded_line)

        number_of_lines = len(self.file_content)
        print(number_of_lines)
        file_text = ""

        for i in range(number_of_lines):
            file_text += f"{self.file_content[i]}\n"

        self.root.ids.file_text.text = file_text

    def save_file(self, *args):
        # Temp File

        if not (os.path.exists("temp")):
            os.mkdir("temp")

        file = open(os.path.join("temp", self.file_name), "w")
        file.write(str(self.root.ids.file_text.text))

        location = f"Projects/{self.project_name}/Versions/{self.version_name}/{self.file_name}"
        print(location)
        storage.delete(location)
        file.close()

        self.new_file(self.file_name, create_new_file=False)
        # storage.child("Projects").child(self.project_name).child("Versions").child(self.version_name).child(
        #     self.file_name).put(f"temp/{self.file_name}")

        # os.remove(os.path.join("temp", self.file_name))

        # toast("Saved File.")

    """
    Chat Functions Here
    """

    def update_chats(self, *args):
        """
        Called When The Refresh Button is clicked,
        Or The User sends a Message

        Function:
            Refresh The Chats
        """
        chats = database.child("Chat").child("Messages").get()
        self.root.ids.chat_list.clear_widgets()

        for each_chat in chats.each():
            chat = each_chat.val()

            for user_name, message in chat.items():
                self.root.ids.chat_list.add_widget(OneLineListItem(text=user_name + ": " + message))

    def send_msg(self, message):
        """
        Called When User Presses The 'Send' Button on the Chat Screen,
        Or Presses Enter Key While The Cursor is on The Message Box of the Chat Screen

        Function:
            Add Messages To Database,
            And Call Update Function to Actually Convert The Database Values To Messages
        """
        time = datetime.datetime.now().strftime("%H:%M:%S")
        message = str(message)
        user = str(self.root.ids.username.text)
        add_message = {user: f"{message}   {time}"}
        database.child("Chat").child("Messages").push(add_message)
        self.root.ids.message_box.text = ""
        toast("Message Sent")

        self.update_chats()


KV = '''

#:import Window kivy.core.window.Window
#:import IconLeftWidget kivymd.uix.list.IconLeftWidget
#:import images_path kivymd.images_path

<FileDialogContent>
    orientation: "vertical"
    # pos_hint: {"center_y": 0.3, "center_x": 0.0}
    size_hint: (0.2, 0)

<VersionDialogContent>
    orientation: "vertical"
    # pos_hint: {"center_y": 0.3, "center_x": 0.0}
    size_hint: (0.2, 0)


ScreenManager:
    id: screen_manager
    Screen:
        name: "Intro"

        MDToolbar:
            title: "Codex Base"
            pos_hint: {"top":1}
            elevation:10

        MDIconButton:
            icon: "codex.png"
            pos_hint: {"center_x": 0.5, "center_y": 0.75}
            user_font_size: "120sp"

        MDLabel:
            text: "Welcome to CodeX Base."
            halign: "center"
            font_style: "H4"
            theme_text_color: "Custom"
            text_color: 51/255,51/255,153/255,1
            size_hint_y: 1.1
            height: self.texture_size[1]

        MDRectangleFlatIconButton:
            icon: "login"
            text: "Login"
            pos_hint: {"center_x": 0.5, "center_y": 0.425}
            font_size: "18sp" 
            text_color: 51/255,51/255,153/255,1
            on_release:
                screen_manager.current = "Login"

        MDRectangleFlatIconButton:
            icon: "plus"
            text: "Register"
            pos_hint: {"center_x": 0.5, "center_y": 0.325}
            font_size: "18sp" 
            text_color: 51/255,51/255,153/255,1
            on_release:
                screen_manager.current = "Register"

        MDLabel:
            text: "Developed by CodeX Community"
            halign: "center"
            theme_text_color: "Custom"
            text_color: 51/255,51/255,153/255,1
            font_style: "H6"
            size_hint_x: 1.7
            size_hint_y: 0.1
            height: self.texture_size[1]

    Screen:
        name: "Login"
        MDToolbar:
            title: "Codex Base"
            pos_hint: {"top":1}
            elevation:10

        MDIconButton:
            icon: "codex.png"
            pos_hint: {"center_x": 0.5, "center_y": 0.75}
            user_font_size: "120sp"

        MDTextField:
            id: email
            hint_text: "Enter email"
            pos_hint: {"center_y": 0.6, "center_x": 0.5}
            mode: "rectangle"
            icon_left: "login"
            size_hint: (0.3, 0.08)

        MDTextField:
            id: username
            hint_text: "Enter username"
            pos_hint: {"center_y": 0.5, "center_x": 0.5}
            mode: "rectangle"
            icon_left: "login"
            size_hint: (0.3, 0.08)

        MDTextField:
            id: password
            hint_text: "Enter password"
            pos_hint: {"center_y": 0.4, "center_x": 0.5}
            mode: "rectangle"
            icon_left: "login"
            size_hint: (0.3, 0.08)
            password: True

        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"center_x": 0.03, "center_y": 0.87}
            on_release:
                screen_manager.current = "Intro"

        MDRectangleFlatIconButton:
            text: "Login"
            pos_hint: {"center_x": 0.5, "center_y": 0.3}
            icon: "login"
            on_release: app.login()         


        MDLabel:
            text: "Developed by CodeX Community"
            halign: "center"
            theme_text_color: "Custom"
            text_color: 51/255,51/255,153/255,1
            font_style: "H6"
            size_hint_x: 1.7
            size_hint_y: 0.1
            height: self.texture_size[1]

        MDTextButton:
            text: "Forgot login details?"
            pos_hint: {"center_x": 0.5, "center_y": 0.2}
            on_release:
                screen_manager.current = "Forgot login"



    Screen:
        name: "Forgot login"
        MDTextField:
            id: forgot_username
            hint_text: "Enter your username"
            pos_hint: {"center_y": 0.5, "center_x": 0.5}
            mode: "rectangle"
            icon_right: "message"
            size_hint: (0.3, 0.08)


        MDRectangleFlatIconButton:
            text: "Send"
            pos_hint: {"center_x": 0.5, "center_y": 0.4}
            icon: "login"
            on_release: app.forgot_details(forgot_username)

        MDLabel:
            text: "Login Details will be sent to your email account."
            halign: "center"
            theme_text_color: "Custom"
            text_color: 51/255,51/255,153/255,1
            font_style: "H6"
            size_hint_x: 1.0
            size_hint_y: 1.3
            height: self.texture_size[1]

        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"center_x": 0.03, "center_y": 0.87}
            on_release:
                screen_manager.current = "Login"

        MDToolbar:
            title: "CodeX Base"
            pos_hint: {"top":1}
            elevation:10

        MDLabel:
            text: "Developed by CodeX Community"
            halign: "center"
            theme_text_color: "Custom"
            text_color: 51/255,51/255,153/255,1
            font_style: "H6"
            size_hint_x: 1.7
            size_hint_y: 0.1
            height: self.texture_size[1]

    Screen:
        name: "Register"

        MDToolbar:
            title: "Codex Base"
            pos_hint: {"top":1}
            elevation:10

        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"center_x": 0.03, "center_y": 0.87}
            on_release:
                screen_manager.current = "Intro"

        MDTextField:
            id: Reg_email
            hint_text: "Enter your e-mail id"
            pos_hint: {"center_y": 0.6, "center_x": 0.5}
            mode: "rectangle"
            icon_right: "email"
            size_hint: (0.3, 0.08)

        MDTextField:
            id: Reg_username
            hint_text: "Enter your username"
            pos_hint: {"center_y": 0.5, "center_x": 0.5}
            mode: "rectangle"
            icon_right: "message"
            size_hint: (0.3, 0.08)

        MDTextField:
            id: Reg_password
            hint_text: "Enter your password"
            pos_hint: {"center_y": 0.4, "center_x": 0.5}
            mode: "rectangle"
            icon_right: "key"
            size_hint: (0.3, 0.08)
            password: True

        MDRectangleFlatIconButton:
            text: "Register"
            pos_hint: {"center_x": 0.5, "center_y": 0.3}
            icon: "plus"
            on_release: app.create(Reg_email, Reg_username, Reg_password)

        MDLabel:
            text: "Developed by CodeX Community"
            halign: "center"
            theme_text_color: "Custom"
            text_color: 51/255,51/255,153/255,1
            font_style: "H6"
            size_hint_x: 1.7
            size_hint_y: 0.1
            height: self.texture_size[1]

    Screen:
        name: "MainPanel"
        id: MainPanel

        MDLabel:
            text: "PROJECTS"
            pos_hint: {"center_x": 0.9, "center_y": 0.85}
            font_style: "H3"
            height: self.texture_size[1]
            theme_text_color: "Custom"
            text_color: 51/255,51/255,153/255,1


        ScrollView:
            scroll_type: ['content', 'bars']
            bar_width: 15
            pos_hint: {"center_x": 0.5, "center_y": 0.4}
            size_hint: (1, 0.6)

            MDList:
                id: projects_panel  

        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"center_x": 0.03, "center_y": 0.87}
            on_release:
                screen_manager.current = "Login"

        MDFloatingActionButton:
            icon: "plus"       
            md_bg_color: app.theme_cls.primary_color
            pos_hint: {"center_x": 0.95, "center_y": 0.15}
            on_release:
                screen_manager.current = "New Project"


        NavigationLayout:
            ScreenManager:
                Screen:
                    BoxLayout:
                        orientation: 'vertical'

                        MDToolbar:
                            title: 'Codex Base'
                            pos_hint: {"top":1}
                            left_action_items: [['menu', lambda x: nav_drawer.toggle_nav_drawer()]]
                            elevation: 10

                        Widget:


        MDNavigationDrawer:
            id: nav_drawer
            BoxLayout:
                orientation: 'vertical'
                spacing: '8dp'
                padding: '8dp'

                Image: 
                    source: 'codex.png'
                    user_font_size: "120sp"

                MDLabel:
                    text: "   " + root.ids.username.text
                    font_style: 'Subtitle1'
                    size_hint_y: None
                    height: self.texture_size[1]

                MDLabel:
                    text: "    " + root.ids.email.text
                    font_style: 'Caption'
                    size_hint_y: None
                    height: self.texture_size[1]

                ScrollView:
                    MDList:
                        OneLineIconListItem:
                            text: 'Developers at CodeX Base'

                            IconLeftWidget:
                                icon: 'account'

                        OneLineIconListItem:
                            text: 'Logs'

                            IconLeftWidget:
                                icon: 'settings'


                        OneLineIconListItem:
                            text: 'Chat'
                            on_release: 
                                screen_manager.current = 'Chat'
                                app.update_chats()

                            IconLeftWidget:
                                icon: 'chat'



        MDLabel:
            text: "Developed by CodeX Community"
            halign: "center"
            theme_text_color: "Custom"
            text_color: 51/255,51/255,153/255,1
            font_style: "H6"
            size_hint_x: 1.7
            size_hint_y: 0.1
            height: self.texture_size[1]

    Screen:
        name: "Chat"
        id: "chat"

        ScrollView:    
            bar_width: 15
            scroll_type: ['content', 'bars']
            size_hint: (1, 0.65)
            pos_hint: {'center_x': 0.5, "center_y": 0.55}

            MDList:
                id: chat_list

        MDToolbar:
            title: "CodeX Base"
            pos_hint: {"top":1}
            elevation:10

        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"center_x": 0.03, "center_y": 0.87}
            on_release:
                screen_manager.current = "MainPanel"
                app.update_main_panel()

        MDTextField:
            id: message_box
            hint_text: "Enter your message"
            pos_hint: {"center_y": 0.1, "center_x": 0.475}
            mode: "rectangle"
            size_hint: (0.9, 0.08)
            on_text_validate: app.send_msg(root.ids.message_box.text)

        MDIconButton:
            id: send_btn
            pos_hint: {"center_x": 0.96, "center_y": 0.1}
            icon: "send"
            on_release:
                app.send_msg(root.ids.message_box.text)

        MDIconButton:
            icon: "refresh"
            pos_hint: {"center_x": 0.96, "center_y": 0.87}
            on_release:
                app.update_chats()

    Screen:
        name: "New Project"

        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"center_x": 0.03, "center_y": 0.87}
            on_release:
                screen_manager.current = "MainPanel"
                app.update_main_panel()

        MDIconButton:
            icon: "codex.png"
            # pos_hint: {"center_x": 0.5, "center_y": 0.6}
            pos_hint: {"center_y": 0.7, "center_x": 0.5}
            user_font_size: "140sp"

        MDToolbar:
            title: "New Project"
            pos_hint: {"top":1}
            elevation:10

        MDTextField:
            id: project_name
            hint_text: "Project Name"
            # pos_hint: {"center_y": 0.8, "center_x": 0.5}
            pos_hint: {"center_x": 0.5, "center_y": 0.5}
            mode: "rectangle"
            icon_right: "rename-box"
            size_hint: (0.3, 0.08)

        MDTextField:
            id: starter_file
            hint_text: "Starter File"
            # pos_hint: {"center_y": 0.8, "center_x": 0.5}
            pos_hint: {"center_x": 0.5, "center_y": 0.4}
            mode: "rectangle"
            icon_right: "rename-box"
            size_hint: (0.3, 0.08)

        MDRectangleFlatButton:
            text: "Make Project"
            pos_hint: {"center_x": 0.5, "center_y": 0.3}
            on_release:
                app.new_project()
                app.update_main_panel


    Screen:
        name: "Version Screen"
        id: version_screen

        ScrollView:
            scroll_type: ['content', 'bars']
            bar_width: 15
            pos_hint: {"center_x": 0.5, "center_y": 0.4}
            size_hint: (1, 0.6)

            MDList:
                id: version_panel            

        MDToolbar:
            title: app.project_name
            pos_hint: {"top":1}
            elevation:10

        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"center_x": 0.03, "center_y": 0.87}
            on_release:
                screen_manager.current = "MainPanel"
                # app.update_main_panel()

        MDRectangleFlatButton:
            text: "Make New Version"
            pos_hint: {"center_x": 0.1  , "center_y": 0.75}
            on_release:
                app.new_version_dialog()
                app.update_version_panel()


    Screen:
        name: "File Screen"
        id: file_screen

        ScrollView:
            scroll_type: ['content', 'bars']
            bar_width: 15
            pos_hint: {"center_x": 0.5, "center_y": 0.4}
            size_hint: (1, 0.6)

            MDList:
                id: file_panel         

        MDToolbar:
            title: app.project_name + " - " + app.version_name
            pos_hint: {"top":1}
            elevation:10

        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"center_x": 0.03, "center_y": 0.87}
            on_release:
                screen_manager.current = "Version Screen"

        MDRectangleFlatButton:
            text: "New File"
            pos_hint: {"center_x": 0.1  , "center_y": 0.75}
            on_release:
                app.new_file_dialog()
                app.update_file_panel()

    Screen:
        name: "Every File Screen"
        id: every_file_screen

        MDToolbar:
            title: app.file_name + ' - Project "' + app.project_name + '" ' + app.version_name
            pos_hint: {"top":1}
            elevation:10

        MDIconButton:
            icon: "arrow-left"
            pos_hint: {"center_x": 0.03, "center_y": 0.87}
            on_release:
                screen_manager.current = "File Screen"
                # app.update_main_panel()


        MDTextField:
            id: file_text
            text: app.content
            # pos_hint: {"center_y": 0.8, "center_x": 0.5}
            pos_hint: {"center_x": 0.5, "center_y": 0.47}
            mode: "rectangle"
            size_hint: (0.9, 0.7)

        MDRectangleFlatButton:
            text: "Save Changes"
            pos_hint: {"center_x": 0.4975, "center_y": 0.07}
            on_release:
                app.save_file()

'''

Main().run()
