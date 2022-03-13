import aiohttp
import asyncio
import ctypes
import datetime
import json
import os
import platform
import playsound
import pypresence
import random
import re
import requests
import shutil
import sys
import time
import traceback
import winreg

import discord

from discord.ext import commands, tasks
from pystyle import Center, Colorate, Colors
from sys import exit
from typing import Any, Dict, List, Optional, Tuple, Union
from win10toast import ToastNotifier

class DataDirectory:
    DATA_FOLDER = "Data/"

class FileDirectories:
    CUSTOM_FOLDER         = f"{DataDirectory.DATA_FOLDER}/Custom/"
    IMAGE_FOLDER          = f"{DataDirectory.DATA_FOLDER}/Image/"
    LOGGING_FOLDER        = f"{DataDirectory.DATA_FOLDER}/Logging/"
    SETTINGS_FOLDER       = f"{DataDirectory.DATA_FOLDER}/Settings/"
    CONFIGS_FOLDER        = f"{DataDirectory.DATA_FOLDER}/Configs/"
    TERMINAL_LOGGING_FILE = f"{DataDirectory.DATA_FOLDER}/TerminalLogging.log"
    INI_FILE              = f"{DataDirectory.DATA_FOLDER}/desktop.ini"

class SubDirectories:
    LOGO_FILE             = f"{FileDirectories.IMAGE_FOLDER}/SolusSB_Logo_Notif.ico"
    FOLDER_LOGO_FILE      = f"{FileDirectories.IMAGE_FOLDER}/SolusSB_Folder_Logo.ico"
    CONFIG_FILE           = f"{FileDirectories.CONFIGS_FOLDER}/Config.json"
    RICH_PRESENCE_FILE    = f"{FileDirectories.CONFIGS_FOLDER}/Rich Presence.json"
    MISC_FILE             = f"{FileDirectories.CONFIGS_FOLDER}/Misc.json"
    COMMAND_THEMES_FOLDER = f"{FileDirectories.SETTINGS_FOLDER}/Custom Command Themes/"
    TRANSLATIONS_FOLDER   = f"{FileDirectories.SETTINGS_FOLDER}/Translations/"
    ALIASES_FILE          = f"{FileDirectories.SETTINGS_FOLDER}/Aliases.json"

class _Colors:
    def __init__(self) -> None:
        for i in range(256):
            setattr(_Colors.Fore, f"_{i}", f"\033[38;5;{i}m")
            setattr(_Colors.Back, f"_{i}", f"\033[48;5;{i}m")

    class Fore: pass

    class Back: pass

class SOLUS:
    START_TIME = time.time()

    class JSON:
        class CommandTheme:
            CUSTOM_TITLE_KEY      = ("Custom Title", "Solus Self-Bot")
            EMBED_AUTHOR_KEY      = ("Embed Author", "")
            EMBED_AUTHOR_URL_KEY  = ("Embed Author URL", "")
            EMBED_AUTHOR_ICON_KEY = ("Embed Author Icon", "")
            EMBED_THUMBNAIL_KEY   = ("Embed Thumbnail", "https://cdn.discordapp.com/attachments/825176286149476422/825183578114621480/SolusSB_Logo_Compressed.png")
            EMBED_IMAGE_KEY       = ("Embed Image", "")
            EMBED_COLOR_KEY       = ("Embed Color", "#E4BBF1")
            CUSTOM_FOOTER_KEY     = ("Custom Footer", "Solus-sb.com")
            EMBED_FOOTER_ICON_KEY = ("Embed Footer Icon", "")

        class Config:
            __PATH__                          = SubDirectories.CONFIG_FILE
            TOKEN_KEY                         = ("Token", "", __PATH__)
            PASSWORD_KEY                      = ("Password", "", __PATH__)
            CODEBLOCKS_KEY                    = ("Codeblocks", "", __PATH__)
            CODEBLOCK_MARKDOWN_KEY            = ("Codeblock Markdown", "brainfuck", __PATH__)
            PREFIX_KEY                        = ("Prefix", "", __PATH__)
            DELETE_COMMAND_INVOKE_MESSAGE_KEY = ("Delete Command Invoke Message", "", __PATH__)
            MESSAGE_DELETE_DELAY_KEY          = ("Message Delete Delay", 0, __PATH__)
            REPLY_DELETE_DELAY_KEY            = ("Reply Delete Delay", 30, __PATH__)
            COMMAND_THEME_KEY                 = ("Command Theme", "Default.json", __PATH__)
            LANGUAGE_KEY                      = ("Language", "English.json", __PATH__)
            MAX_CACHED_MESSAGES_KEY           = ("Max Cached Messages", 1000, __PATH__)
            ADVANCED_LOGGING_KEY              = ("Advanced Logging", False, __PATH__)

        class Misc:
            __PATH__                  = SubDirectories.MISC_FILE
            ON_READY_PRINT_FORMAT_KEY = ("On Ready Print Format", "advanced", __PATH__)
            LOAD_CUSTOM_SCRIPTS_KEY   = ("Load Custom Scripts", "", __PATH__)

        class RichPresence:
            __PATH__                  = SubDirectories.RICH_PRESENCE_FILE
            CUSTOM_RICH_PRESENCE_KEY  = ("Custom Rich Presence", False, __PATH__)
            APPLICATION_ID_KEY        = ("Application ID", "", __PATH__)
            RPC_STATE_KEY             = ("RPC State", "", __PATH__)
            RPC_DETAILS_KEY           = ("RPC Details", "", __PATH__)
            RPC_LARGE_IMAGE_ASSET_KEY = ("RPC Large Image Asset", "", __PATH__)
            RPC_LARGE_IMAGE_TEXT_KEY  = ("RPC Large Image Text", "", __PATH__)
            RPC_SMALL_IMAGE_ASSET_KEY = ("RPC Small Image Asset", "", __PATH__)
            RPC_SMALL_IMAGE_TEXT_KEY  = ("RPC Small Image Text", "", __PATH__)
            RPC_BUTTON_ONE_TEXT_KEY   = ("RPC Button One Text", "", __PATH__)
            RPC_BUTTON_ONE_URL_KEY    = ("RPC Button One URL", "", __PATH__)
            RPC_BUTTON_TWO_TEXT_KEY   = ("RPC Button Two Text", "", __PATH__)
            RPC_BUTTON_TWO_URL_KEY    = ("RPC Button Two URL", "", __PATH__)

        class Temp:
            _translation = {}
            _aliases = {}

            def update() -> None:
                if(SOLUS.JSON.Temp._translation):
                    SOLUS.FileHandler.write(f"{SubDirectories.TRANSLATIONS_FOLDER}/{SOLUS.Features.language}", SOLUS.JSON.Temp._translation, True)
                    SOLUS.FileHandler.write(SubDirectories.ALIASES_FILE, SOLUS.JSON.Temp._aliases, True, sort_keys=True)
                    del SOLUS.JSON.Temp
                elif(not SOLUS.JSON.Temp._translation):
                    SOLUS.FileHandler.create_if_not_exist(f"{SubDirectories.TRANSLATIONS_FOLDER}/{SOLUS.Features.language}", False, True)
                    SOLUS.JSON.Temp._translation = SOLUS.FileHandler.open(f"{SubDirectories.TRANSLATIONS_FOLDER}/{SOLUS.Features.language}")
                    SOLUS.JSON.Temp._aliases = SOLUS.FileHandler.open(SubDirectories.ALIASES_FILE)

    class Features:
        custom_title: str
        embed_author: str
        embed_author_url: str
        embed_author_icon: str
        embed_thumbnail: str
        embed_image: str
        embed_color: str
        custom_footer: str
        embed_footer_icon: str

        token: str
        password: str
        codeblocks: bool
        codeblock_markdown: str
        prefix: str
        delete_command_invoke_message: bool
        message_delete_delay: int
        reply_delete_delay: int
        command_theme: str
        language: str
        max_cached_messages: int
        advanced_logging: bool

        on_ready_print_format: str
        load_custom_scripts: bool

        custom_rich_presence: bool
        application_id: int
        rpc_state: str
        rpc_details: str
        rpc_large_image_asset: str
        rpc_large_image_text: str
        rpc_small_image_asset: str
        rpc_small_image_text: str
        button_one_text: str
        button_one_url: str
        button_two_text: str
        button_two_url: str

        def update() -> None:
            def assign(_class: object, filepath: str) -> None:
                try:
                    loaded_file = SOLUS.FileHandler.open(filepath, return_path=True)
                except FileNotFoundError:
                    return
                for key, value in vars(_class).items():
                    if not key.startswith("__"):
                        _value = SOLUS.FileHandler.value(value, file=loaded_file)
                        _value = value[1] if _value == "" else _value
                        _key = value[0].lower().replace(" ", "_")
                        setattr(SOLUS.Features, _key, _value)

            assign(SOLUS.JSON.Config, SubDirectories.CONFIG_FILE)
            assign(SOLUS.JSON.Misc, SubDirectories.MISC_FILE)
            assign(SOLUS.JSON.RichPresence, SubDirectories.RICH_PRESENCE_FILE)
            assign(SOLUS.JSON.CommandTheme, f"{SubDirectories.COMMAND_THEMES_FOLDER}/{SOLUS.Features.command_theme}")

    class Commands:
        cached = {}

        def update() -> None:
            for command in Solus.commands:
                class_name = command.callback.__qualname__.split(".")[0]
                if(class_name not in SOLUS.Commands.cached):
                    SOLUS.Commands.cached[class_name] = []
                SOLUS.Commands.cached[class_name].append({"Name": command.qualified_name.capitalize(), "Signature": SOLUS.Functions.signature(command), "Brief": command.brief})
            for key, value in SOLUS.Commands.cached.items():
                command_list = [f"**{{PREFIX}}{command['Name']} {command['Signature']}** » {command['Brief']}" for command in value]
                command_list.sort()
                command_list = "\n".join(command_list).replace("[]", "")
                SOLUS.Commands.cached[key] = command_list

    class System:
        NOTIFIER = ToastNotifier()
        OS = str(platform.system()).lower()
        KERNAL32 = ctypes.windll.kernel32
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Cryptography", 0, winreg.KEY_READ or winreg.KEY_WOW64_64KEY) as _key:
            _value = winreg.QueryValueEx(_key, "MachineGuid")
        UUID = _value[0]


        def sound(filepath: str) -> None:
            try:
                playsound.playsound(filepath, block=False)
            except playsound.PlaysoundException:
                pass

        def toast(title: str, description: str, *, icon_path: str = SubDirectories.LOGO_FILE, duration: int = 5, threaded: bool = True) -> None:
            SOLUS.System.NOTIFIER.show_toast(title, description, icon_path=icon_path, duration=duration, threaded=threaded)

    class Terminal:
        _last_event = ""

        class Colors:
            _c = _Colors()
            FORE  = _c.Fore
            BACK  = _c.Back
            RESET = "\033[0m"

        def _log_split(event: str, string: str, *, split_top: bool = False) -> str:
            if(SOLUS.Terminal._last_event != event):
                string = "\n" + string
            elif(SOLUS.Terminal._last_event == event and split_top == True):
                string = "\n" + string
            SOLUS.Terminal._last_event = event
            return string

        def print(event: str, contents: str, *, split_top: bool = False) -> None:
            event = event.lower()
            string = f"[{datetime.datetime.now().strftime('%X')}] "

            if(event == "event"): string += f"| [ EVENT ] | {contents}"
            elif(event == "command"): string += f"| [COMMAND] | {contents}"
            elif(event == "error"): string += f"| [ ERROR ] | {contents}"

            string = SOLUS.Terminal._log_split(event, string, split_top=split_top)

            if(event == "raw"):
                print(contents)
                SOLUS.Logger.push(contents)
                return

            print(Colorate.Horizontal(Colors.blue_to_purple, string))
            SOLUS.Logger.push(string)

        def input(contents: str, split_top: bool = False) -> str:
            string = SOLUS.Terminal._log_split("input", f"[{datetime.datetime.now().strftime('%X')}] | [ INPUT ] | {contents}", split_top=split_top)
            user_input = input(Colorate.Horizontal(Colors.blue_to_purple, string))
            string += user_input
            SOLUS.Logger.push(string)
            return user_input

        def title(header: str) -> None:
            SOLUS.System.KERNAL32.SetConsoleTitleW(header)

        def clear() -> None:
            os.system("cls")

        def prompt(question: str, key: str, true_false: bool = False, set_default: Any = None) -> None:
            pre_value = SOLUS.FileHandler.value(key)
            if(true_false):
                if(pre_value != True and pre_value != False):
                    while True:
                        user_input = str(SOLUS.Terminal.input(question))
                        if(user_input.isdigit()):
                            user_input = int(user_input)
                            if(user_input in (1, 2)):
                                to_write = True if user_input == 1 else False
                                SOLUS.FileHandler.value(key, to_write)
                                break
                        SOLUS.Terminal.print("error", "Answer must be 1 or 2")
                return
            elif(not true_false and not pre_value):
                user_input = SOLUS.Terminal.input(question)
                if(set_default is not None and user_input == ""):
                    user_input = set_default
                SOLUS.FileHandler.value(key, user_input)
                return
            if(SOLUS.Features.advanced_logging):
                SOLUS.Terminal.print("event", "Config Check Successful")

    class Logger:
        def push(contents: str) -> None:
            __e_s = re.sub('\\033(.*?)m', '', contents)
            SOLUS.FileHandler.write(FileDirectories.TERMINAL_LOGGING_FILE, f"{__e_s}\n", mode="a+")

        def clear() -> None:
            SOLUS.FileHandler.blank(FileDirectories.TERMINAL_LOGGING_FILE)

    class FileHandler:
        def open(filepath: str, *, return_path: bool = False) -> Union[Tuple[Union[Dict[Any, Any], str], str], Dict[Any, Any], str]:
            with open(filepath, "r", encoding="utf-8") as file:
                try:
                    content = json.load(file)
                except json.JSONDecodeError:
                    content = file.read()
            if(return_path):
                return (content, file.name)
            return content

        def write(filepath: str, text: Any, is_json: bool = False, *, sort_keys: bool = False, mode: str = "w", encoding: str = "utf-8") -> None:
            encoding = "utf-8" if mode not in ("wb", "rb") else None
            with open(filepath, mode, encoding=encoding) as file:
                if(is_json):
                    json.dump(text, file, indent=1, separators=(",", ": "), sort_keys=sort_keys)
                elif(not is_json):
                    file.write(text)

        def blank(filepath: str, is_json = False) -> None:
            with open(filepath, "w", encoding="utf-8") as file:
                if(is_json):
                    file.write("{}")
                elif(not is_json):
                    file.close()

        def create_if_not_exist(path: str, is_folder: bool = False, is_json: bool = False, default_value: Any = None, *, sort_keys: bool = False, image: bool = False, url: str = None, ini: bool = False, skip: bool = False) -> None:
            if(image and url is not None):
                response = requests.get(url).content
                SOLUS.FileHandler.write(path, response, mode="wb")
            elif(is_folder):
                if(not os.path.isdir(path)):
                    os.makedirs(path)
            elif(not is_folder):
                if(not os.path.isfile(path)):
                    if(is_json and default_value):
                        SOLUS.FileHandler.write(path, default_value, True, sort_keys=sort_keys)
                    elif(is_json and not default_value):
                        SOLUS.FileHandler.blank(path, True)
                    elif(not is_json and default_value):
                        SOLUS.FileHandler.write(path, default_value)
                    elif(not is_json and not default_value):
                        SOLUS.FileHandler.blank(path)
                    if(ini):
                        os.system(f"attrib +r {os.getcwd()}\\Data")
                        os.system(f"attrib +s +h {os.getcwd()}\\Data\\desktop.ini")
            if(not skip):
                if(SOLUS.Features.advanced_logging):
                    _type = "Folder" if is_folder else "File"
                    SOLUS.Terminal.print("event", f"{path} {_type} Found")

        def value(key: str, value: Any = "holder", *, file: Union[Dict[Any, Any], Tuple[Union[Dict[Any, Any], str], str]] = None) -> Any:
            if(file is None):
                path = key[2]
                loaded_file = SOLUS.FileHandler.open(path)
            else:
                path = file[1]
                loaded_file = file[0]
            if(value == "holder"):
                try:
                    loaded_file[key[0]]
                except KeyError:
                    loaded_file[key[0]] = key[1]
                    SOLUS.FileHandler.write(path, loaded_file, True)
                return loaded_file[key[0]]
            elif(value != "holder"):
                loaded_file[key[0]] = value
                SOLUS.FileHandler.write(path, loaded_file, True)
                return
            elif(value is None):
                loaded_file[key[0]] = key[1]
                SOLUS.FileHandler.write(path, loaded_file, True)
                return

    class Bool(commands.Converter):
        async def convert(self, ctx, argument: str) -> bool:
            __r_m_s = argument.lower()
            if(__r_m_s in ["on", "off"]):
                if(__r_m_s == "on"):
                    return True
                return False
            raise SOLUS.Errors.BoolError

    class Channel(commands.Converter):
        async def convert(self, ctx, argument: str) -> Union[discord.TextChannel, discord.VoiceChannel]:
            channel_id = re.sub("[<#!>]", "", argument)
            channel = Solus.get_channel(channel_id) or await Solus.fetch_channel(channel_id)
            return channel

    class Message(commands.Converter):
        async def convert(self, ctx, argument: str) -> Union[discord.Message, discord.PartialMessage]:
            try:
                return await commands.MessageConverter().convert(ctx, argument)
            except commands.BadArgument:
                return await commands.PartialMessageConverter().convert(ctx, argument)

    class Embed(discord.Embed):
        def __init__(self, **kwargs) -> None:
            super().__init__(**kwargs)

            self.colour = kwargs.pop("color", __customcolor__())
            self.title = kwargs.pop("title", __customtitle__())
            self.description = kwargs.get("description")

            __customauthor__(self)
            __customthumbnail__(self)
            __customimage__(self)
            __customfooter__(self)

    class Functions:
        class Webhook:
            def __init__(self, url: str) -> None:
                self.url = url
                self.session = None

            async def __aenter__(self):
                self.session = aiohttp.ClientSession()
                webhook = discord.Webhook.from_url(self.url, adapter=discord.AsyncWebhookAdapter(self.session))
                return webhook

            async def __aexit__(self, exc_type, exc_value, exc_traceback):
                await self.session.close()

        async def send(ctx, embed: discord.Embed) -> discord.Message:
            def clean_text(text) -> str:
                text = re.sub(r'\[(.*)\]\((?:.*)\)', r'\g<1>', text)
                return discord.utils.remove_markdown(text)

            text = f"```{SOLUS.Features.codeblock_markdown}\n\n"
            if(SOLUS.Features.codeblocks):
                if(embed.title is not None):
                    text += f"{clean_text(embed.title)}\n\n" 
                if(embed.description is not None):
                    text += f"{clean_text(embed.description)}\n\n"
                if(embed.fields):
                    fields = "\n\n".join([f"{clean_text(field.name)}\n{clean_text(field.value)}" for field in embed.fields])
                    text += f"{fields}\n\n"
                if(embed.footer):
                    text += clean_text(embed.footer.text)
                text += "```"
                message = await ctx.send(text, delete_after=SOLUS.Features.reply_delete_delay)
            else:
                message = await ctx.send(embed=embed, delete_after=SOLUS.Features.reply_delete_delay)
            return message

        async def paginator(ctx: commands.Context, _list: list, *, raw: bool = False) -> None:
            paginator = commands.Paginator(max_size=1900)
            for line in _list:
                try:
                    paginator.add_line(line)
                except RuntimeError:
                    return SOLUS.Terminal.print("error", "Line exceeeds maximum page size")
            for page in paginator.pages:
                page = re.sub("[`]", "", str(page))
                if(raw):
                    await ctx.send(page)
                else:
                    await SOLUS.Functions.send(ctx, SOLUS.Embed(description=page))

        def aliases(json_key: str) -> List[str]:
            if(json_key not in SOLUS.JSON.Temp._aliases):
                SOLUS.JSON.Temp._aliases[json_key] = []
            return SOLUS.JSON.Temp._aliases[json_key]

        def translate(json_key: str) -> str:
            if(json_key not in SOLUS.JSON.Temp._translation):
                SOLUS.JSON.Temp._translation[json_key] = None
            _value = SOLUS.JSON.Temp._translation[json_key]
            if(_value is None):
                return json_key
            return _value
        
        def signature(command: Union[commands.Command, str]) -> str:
            command_signature = command.signature if isinstance(command, commands.Command) else command

            command_signature = command_signature.replace("OR", "/")
            command_signature = command_signature.replace("guild", "server")
            command_signature = command_signature.replace("_", " ")
            command_signature = command_signature.title()
            return command_signature

        def _class_name(_class: object) -> str:
            if(hasattr(_class, "__qualname__")):
                class_name = _class.__qualname__
            else:
                class_name = _class.__class__.__name__
            
            if("." in class_name):
                class_name = class_name.split(".")[-1]
            return class_name

        async def help(ctx: commands.Context, *, pages: List[object], page_number: int = 1) -> None:
            prefix = ctx.prefix

            page = SOLUS.Commands.cached[SOLUS.Functions._class_name(pages[page_number-1])]
            page = page.replace("{PREFIX}", prefix)

            embed = SOLUS.Embed(description=f"< > = Required | [ ] = Optional\n{page}")
            embed.set_footer(text=f"Type {prefix}help [command] for more info on a command")
            await SOLUS.Functions.send(ctx, embed)

    class Errors:
        class BoolError(commands.BadArgument):
            pass

class DefaultConfigurations:
    def class_to_dict(_class: object) -> Dict[str, Any]: return {value[0]: value[1] for key, value in vars(_class).items() if not key.startswith("__")}

    DEFAULT_CONFIG        = class_to_dict(SOLUS.JSON.Config)
    DEFAULT_MISC          = class_to_dict(SOLUS.JSON.Misc)
    DEFAULT_RICH_PRESENCE = class_to_dict(SOLUS.JSON.RichPresence)
    DEFAULT_COMMAND_THEME = class_to_dict(SOLUS.JSON.CommandTheme)

SOLUS.System.KERNAL32.SetConsoleMode(SOLUS.System.KERNAL32.GetStdHandle(-11), 7)

SOLUS.FileHandler.create_if_not_exist(DataDirectory.DATA_FOLDER, True, skip=True)

TERMINAL_LOG_CHECK = os.path.isfile(FileDirectories.TERMINAL_LOGGING_FILE)
if(TERMINAL_LOG_CHECK):
    file_rename = datetime.datetime.today().strftime("%Y-%m-%d-%H:%M:%S.%f").replace(":", ".")
    try:
        shutil.move(FileDirectories.TERMINAL_LOGGING_FILE, FileDirectories.LOGGING_FOLDER)
    except:
        os.remove(f"{FileDirectories.LOGGING_FOLDER}/TerminalLogging.log")
        shutil.move(FileDirectories.TERMINAL_LOGGING_FILE, FileDirectories.LOGGING_FOLDER)
    os.rename(f"{FileDirectories.LOGGING_FOLDER}/TerminalLogging.log", f"{FileDirectories.LOGGING_FOLDER}/TerminalLogging-{file_rename}.log")
elif(not TERMINAL_LOG_CHECK):
    SOLUS.FileHandler.blank(FileDirectories.TERMINAL_LOGGING_FILE)

SOLUS.FileHandler.create_if_not_exist(FileDirectories.CONFIGS_FOLDER, True, skip=True)
SOLUS.FileHandler.create_if_not_exist(SubDirectories.CONFIG_FILE, False, True, DefaultConfigurations.DEFAULT_CONFIG, skip=True)
SOLUS.Features.update()
SOLUS.FileHandler.create_if_not_exist(FileDirectories.SETTINGS_FOLDER, True)
SOLUS.FileHandler.create_if_not_exist(SubDirectories.COMMAND_THEMES_FOLDER, True)
SOLUS.FileHandler.create_if_not_exist(SubDirectories.ALIASES_FILE, False, True)
SOLUS.FileHandler.create_if_not_exist(SubDirectories.TRANSLATIONS_FOLDER, True)
SOLUS.FileHandler.create_if_not_exist(f"{SubDirectories.COMMAND_THEMES_FOLDER}/Default.json", False, True, DefaultConfigurations.DEFAULT_COMMAND_THEME)
SOLUS.FileHandler.create_if_not_exist(FileDirectories.LOGGING_FOLDER, True)
SOLUS.FileHandler.create_if_not_exist(FileDirectories.CUSTOM_FOLDER, True)
SOLUS.FileHandler.create_if_not_exist(SubDirectories.RICH_PRESENCE_FILE, False, True, DefaultConfigurations.DEFAULT_RICH_PRESENCE)
SOLUS.FileHandler.create_if_not_exist(SubDirectories.MISC_FILE, False, True, DefaultConfigurations.DEFAULT_MISC)
SOLUS.FileHandler.create_if_not_exist(f"{FileDirectories.CUSTOM_FOLDER}/custom.py", False, False, "@Solus.command(brief=SOLUS.Functions.translate('Template'), aliases=SOLUS.Functions.aliases('template'))\nasync def template(ctx):\n    SOLUS.Terminal.print('event', 'Template')")
SOLUS.FileHandler.create_if_not_exist(FileDirectories.IMAGE_FOLDER, True)
SOLUS.FileHandler.create_if_not_exist(SubDirectories.LOGO_FILE, image=True, url="https://cdn.discordapp.com/attachments/951253983408836620/951254171795996702/SolusSB_Logo_Notif.ico")
SOLUS.FileHandler.create_if_not_exist(SubDirectories.FOLDER_LOGO_FILE, image=True, url="https://cdn.discordapp.com/attachments/951253983408836620/951254171649208361/SolusSB_Folder_Logo.ico")
SOLUS.FileHandler.create_if_not_exist(FileDirectories.INI_FILE, False, False, f"[.ShellClassInfo]\nIconResource={os.getcwd()}\\Data\\Image\\SolusSB_Folder_Logo.ico,0", ini=True)

SOLUS.Features.update()

SOLUS.Terminal.title("Solus Self-bot")

SOLUS.Terminal.clear()

def __customcolor__() -> int:
    return int(SOLUS.Features.embed_color.replace("#", "0x"), 0)

def __customauthor__(_embed: Optional[discord.Embed] = None) -> Optional[discord.Embed]:
    _author = {}
    if(embed_author := SOLUS.Features.embed_author):
        _author["name"] = embed_author
    if(embed_author_url := SOLUS.Features.embed_author_url):
        if(embed_author_url.startswith(("http", "https"))):
            _author["url"] = embed_author_url
    if(embed_author_icon := SOLUS.Features.embed_author_icon):
        if(embed_author_icon.startswith(("http", "https"))):
            _author["icon_url"] = embed_author_icon
    if(_author):
        _embed.set_author(**_author)

    return _embed

def __customfooter__(_embed: Optional[discord.Embed] = None) -> Optional[Union[discord.Embed, str]]:
    if(_embed is None):
        return SOLUS.Features.custom_footer

    _footer = {}
    if(custom_footer := SOLUS.Features.custom_footer):
        _footer["text"] = custom_footer
    if(embed_footer_icon := SOLUS.Features.embed_footer_icon):
        if(embed_footer_icon.startswith(("http", "https"))):
            _footer["icon_url"] = embed_footer_icon
    if(_footer):
        _embed.set_footer(**_footer)

    return _embed

def __customthumbnail__(_embed: Optional[discord.Embed] = None) -> Optional[discord.Embed]:
    embed_thumbnail = SOLUS.Features.embed_thumbnail

    if(embed_thumbnail.startswith(("http", "https"))):
        _embed.set_thumbnail(url=embed_thumbnail)

    return _embed

def __customtitle__(_title: Optional[str] = None) -> str:
    if(custom_title := SOLUS.Features.custom_title):
        return custom_title

def __customimage__(_embed: Optional[discord.Embed] = None) -> Optional[discord.Embed]:
    embed_image = SOLUS.Features.embed_image

    if(embed_image.startswith(("http", "https"))):
        _embed.set_image(url=embed_image)
    return _embed

def bot_prefix(Solus, message) -> str:
    return SOLUS.Features.prefix

def rpc_buttons() -> Optional[List[Dict[str, Any]]]:
    button_one_text = SOLUS.Features.button_one_text
    button_one_url = SOLUS.Features.button_one_url
    button_two_text = SOLUS.Features.button_two_text
    button_two_url = SOLUS.Features.button_two_url
    button_list = []
    if(button_one_text and button_one_url):
        button_list.append({"label": button_one_text, "url": button_one_url})
    if(button_two_text and button_two_url):
        button_list.append({"label": button_two_text, "url": button_two_url})
    return button_list or None

async def startprint() -> None:
    SOLUS.Terminal.clear()
    dev                   = Solus.get_user(781578446072840234) or await Solus.fetch_user(781578446072840234)
    prefix                = f"Prefix: {SOLUS.Features.prefix}"
    codeblocks            = f"Codeblocks: {SOLUS.Features.codeblocks}"
    invoke_message_delete = f"Delete Invoke Message: {SOLUS.Features.delete_command_invoke_message}"
    deletion_delay        = f"Deletion Delay: {SOLUS.Features.message_delete_delay}"
    reply_deletion_delay  = f"Reply Deletion Delay: {SOLUS.Features.reply_delete_delay}"
    motd_print            = "Best Base YEP"

    _logo = f"""
███████╗ ██████╗ ██╗     ██╗   ██╗███████╗
██╔════╝██╔═══██╗██║     ██║   ██║██╔════╝
███████╗██║   ██║██║     ██║   ██║███████╗
╚════██║██║   ██║██║     ██║   ██║╚════██║
███████║╚██████╔╝███████╗╚██████╔╝███████║
╚══════╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚══════╝
        S   E   L   F   B   O   T
          Developer: {dev}"""
    
    _cli = f"""
┏━━━━━━━━━━━Usage━━━━━━━━━━━┓
 {prefix}
 {codeblocks}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
┏━━━━━━━━━━━Misc━━━━━━━━━━━━┓
 {invoke_message_delete}
 {deletion_delay}
 {reply_deletion_delay}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
    """

    _sep = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if(SOLUS.Features.on_ready_print_format.lower() == "advanced"):
        SOLUS.Terminal.print("raw", f"""
{Center.Center(Colorate.Vertical(Colors.blue_to_purple, _logo), yspaces=0)}
{Center.Center(Colorate.Vertical(Colors.blue_to_purple, motd_print), xspaces=35, yspaces=0)}
{Center.Center(Colorate.Vertical(Colors.blue_to_purple, _cli), yspaces=0)}""")
        SOLUS.Terminal.print("event", f"Logged in as: {Solus.user.name}")

    elif(SOLUS.Features.on_ready_print_format.lower() == "essential"):
        SOLUS.Terminal.print("raw", f"""
{Center.Center(Colorate.Vertical(Colors.blue_to_purple, _logo), yspaces=0)}
{Center.Center(Colorate.Vertical(Colors.blue_to_purple, motd_print), xspaces=35, yspaces=0)}
{Colorate.Vertical(Colors.blue_to_purple, _sep)}
{Colorate.Vertical(Colors.blue_to_purple, prefix)}
{Colorate.Vertical(Colors.blue_to_purple, _sep)}""")
        SOLUS.Terminal.print("event", f"Logged in as: {Solus.user.name}")

    elif(SOLUS.Features.on_ready_print_format.lower() == "minimal"):
        SOLUS.Terminal.print("raw", f"""
{Center.Center(Colorate.Vertical(Colors.blue_to_purple, _logo), yspaces=0)}
{Center.Center(Colorate.Vertical(Colors.blue_to_purple, motd_print), xspaces=35, yspaces=0)}
{Colorate.Vertical(Colors.blue_to_purple, _sep)}""")
        SOLUS.Terminal.print("event", f"Logged in as: {Solus.user.name}")

_tokens = []
_valid_tokens = []

def get_account_name(token: str) -> str:
    try:
        header = {"Authorization": token, "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"}
        data = requests.get("https://discordapp.com/api/v6/users/@me", headers=header).json()
        username = data["username"]
        discriminator = data["discriminator"]
        return f"{username}#{discriminator}"
    except KeyError:
        return None

def token_search(path: str) -> None:
    path += "\\Local Storage\\leveldb"
    try:
        for file_name in os.listdir(path):
            if not file_name.endswith((".log", ".ldb")):
                continue

            for line in [x.strip() for x in open(f"{path}\\{file_name}", errors="ignore").readlines() if x.strip()]:
                for regex in (r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}", r"mfa\.[\w-]{84}"):
                    for token in re.findall(regex, line):
                        _tokens.append(token)
    except FileNotFoundError:
        pass

if(SOLUS.Features.token == ""):
    local = os.getenv("LOCALAPPDATA")
    roaming = os.getenv("APPDATA")

    paths = {"Discord": f"{roaming}\\Discord", "Discord Canary": f"{roaming}\\discordcanary", "Discord PTB": f"{roaming}\\discordptb", "Google Chrome": f"{local}\\Google\\Chrome\\User Data\\Default", "Opera": f"{roaming}\\Opera Software\\Opera Stable", "Brave": f"{local}\\BraveSoftware\\Brave-Browser\\User Data\\Default", "Yandex": f"{local}\\Yandex\\YandexBrowser\\User Data\\Default"}
    for platform, path in paths.items():
        if(os.path.exists(path)):
            token_search(path)

    for token in set(_tokens):
        account_name = get_account_name(token)
        if(account_name is not None):
            _valid_tokens.append((token, account_name))

    for index, _tuple in enumerate(_valid_tokens):
        SOLUS.Terminal.print("input", f"{index}: {_tuple[1]} | {_tuple[0]}")

    SOLUS.Terminal.print("event", "If your token does not appear, restart your discord client along with Solus")
    SOLUS.Terminal.print("event", "Account number is the number to the left of the accounts above.")
    token_choice = int(SOLUS.Terminal.input("Account Number: "))

    load_json = SOLUS.FileHandler.open(SubDirectories.CONFIG_FILE)
    try:
        load_json["Token"] = _valid_tokens[token_choice][0]
    except IndexError:
        SOLUS.Terminal.print("error", "Account Number Not Found")
        token_input = SOLUS.Terminal.input("Token: ")
        load_json["Token"] = token_input
    SOLUS.FileHandler.write(SubDirectories.CONFIG_FILE, load_json, True)

SOLUS.Terminal.prompt("Discord Password (OPTIONAL): ", SOLUS.JSON.Config.PASSWORD_KEY, False, "NOT PROVIDED")
SOLUS.Terminal.prompt("Prefix: ", SOLUS.JSON.Config.PREFIX_KEY, False, "..")
SOLUS.Terminal.prompt("Codeblocks [1: True | 2: False]: ", SOLUS.JSON.Config.CODEBLOCKS_KEY, True)
SOLUS.Terminal.prompt("Delete Command Invoke Message [1: True | 2: False]: ", SOLUS.JSON.Config.DELETE_COMMAND_INVOKE_MESSAGE_KEY, True)
SOLUS.Terminal.prompt("Load Custom Scripts [1: True | 2: False]: ", SOLUS.JSON.Misc.LOAD_CUSTOM_SCRIPTS_KEY, True)

Solus = commands.Bot(command_prefix = bot_prefix, intents = discord.Intents.all(), case_insensitive=True, strip_after_prefix=True, self_bot=True, status=discord.Status.offline, afk=True, max_messages=int(SOLUS.Features.max_cached_messages))
Solus.remove_command("help")

global_vars = {
    "aiohttp": aiohttp,
    "asyncio": asyncio,
    "ctypes": ctypes,
    "datetime": datetime,
    "json": json,
    "os": os,
    "platform": platform,
    "playsound": playsound,
    "pypresence": pypresence,
    "random": random,
    "re": re,
    "requests": requests,
    "shutil": shutil,
    "sys": sys,
    "time": time,
    "traceback": traceback,
    "winreg": winreg,
    "discord": discord,
    "commands": commands,
    "tasks": tasks,
    "exit": exit,
    "Union": Union,
    "List": List,
    "Any": Any,
    "Dict": Dict,
    "Center": Center,
    "Colorate": Colorate,
    "Colors": Colors,
    "ToastNotifier": ToastNotifier,
    "Solus": Solus,
    "bot": Solus,
    "SOLUS": SOLUS
}

global_vars["Optional"] = Optional

SOLUS.JSON.Temp.update()

if(SOLUS.Features.load_custom_scripts):
    for filename in os.listdir(FileDirectories.CUSTOM_FOLDER):
        if filename.endswith(".py"):
            try:
                SOLUS.Terminal.print("event", f"Extension Loading...")
                with open(f"{FileDirectories.CUSTOM_FOLDER}/{filename}", "r", encoding="utf-8") as file:
                    custom_script = file.read()
                exec(custom_script, global_vars)
                SOLUS.Terminal.print("event", f"Extension Loaded")
            except Exception as e:
                if("None in sys.modules" in str(e)):
                    SOLUS.Terminal.print("error", "Illegal Import")
                else:
                    SOLUS.Terminal.print("error", f"{e.__class__.__name__}: {e}")
                SOLUS.Terminal.input("Press Enter to exit...")
                exit()

if(SOLUS.Features.custom_rich_presence):
    RPC = pypresence.Presence(SOLUS.Features.application_id)
    RPC.connect()
    RPC.update(state=SOLUS.Features.rpc_state, details=SOLUS.Features.rpc_details, large_image=SOLUS.Features.rpc_large_image_asset, large_text=SOLUS.Features.rpc_large_image_text, small_image=SOLUS.Features.rpc_small_image_asset, small_text=SOLUS.Features.rpc_small_image_text, buttons=rpc_buttons(), start=SOLUS.START_TIME)

class HelpCommand:
    @Solus.command(brief=SOLUS.Functions.translate("Shows this list or information on a command"), aliases=SOLUS.Functions.aliases("help"))
    async def help(ctx, command: Optional[str] = None):
        prefix = ctx.prefix
        if(command is None):
            await SOLUS.Functions.help(ctx, pages=[HelpCommand])
        elif(command is not None):
            _command = Solus.get_command(command.lower())
            if(_command is None):
                return SOLUS.Terminal.print("error", f"{command} not found")
            command_signature = SOLUS.Functions.signature(_command)
            aliases = "] [".join(_command.aliases)
            embed = SOLUS.Embed(description=f"**Command:** {_command.qualified_name.capitalize()}\n\n**Brief:** {_command.brief}\n\n"
                                f"**Usage:** {prefix}{_command.qualified_name.capitalize()} {command_signature}\n\n"
                                f"**Aliases:** [{aliases}]")
            embed.set_footer(text=f"Type {prefix}help [command] for more info on a command")
            await SOLUS.Functions.send(ctx, embed)

    @Solus.command(brief=SOLUS.Functions.translate("Seaches for a command"), aliases=SOLUS.Functions.aliases("search"))
    async def search(ctx, *, search: str):
        command_list = []
        for command in Solus.commands:
            if(search.lower() in command.qualified_name or search.lower() in command.aliases):
                command_signature = SOLUS.Functions.signature(command=command)
                command_class_name = command.callback.__qualname__.split(".")[0]
                command_list.append(f"**{command.qualified_name} {command_signature}** | {command_class_name}")
        message_list = "\n".join(command_list)
        message_list = message_list.replace("[]", "")
        embed = SOLUS.Embed(description=f"{len(command_list)} Results for {search}\n\n< > = Required | [ ] = Optional\n{message_list}")
        embed.set_footer(text=f"Type {ctx.prefix}help [command] for more info on a command")
        await SOLUS.Functions.send(ctx, embed)

    @Solus.command(brief=SOLUS.Functions.translate("Demo category"), aliases=SOLUS.Functions.aliases("demo"))
    async def demo(ctx):
        await SOLUS.Functions.help(ctx, pages=[DemoCategory])

class DemoCategory:
    @Solus.command(brief=SOLUS.Functions.translate("Demo Translation"), aliases=SOLUS.Functions.aliases("democommand"))
    async def democommand(ctx):
        SOLUS.Terminal.print("event", "Demo Command!")

@Solus.event
async def on_command_error(ctx, error):
    try:
        await ctx.message.delete()
    except (discord.Forbidden, discord.NotFound, discord.HTTPException):
        pass
    error = getattr(error, "original", error)
    if isinstance(error, commands.NoPrivateMessage): SOLUS.Terminal.print("error", f"{ctx.command} cannot be used in a private message")
    elif isinstance(error, commands.CommandNotFound): SOLUS.Terminal.print("error", "Command Not Found!")
    elif isinstance(error, commands.MissingPermissions): SOLUS.Terminal.print("error", f"Missing Permission(s): {''.join(error.missing_perms)}")
    elif isinstance(error, commands.MemberNotFound): SOLUS.Terminal.print("error", "Member Not Found!")
    elif isinstance(error, commands.ChannelNotFound): SOLUS.Terminal.print("error", "Channel Not Found!")
    elif isinstance(error, commands.CommandOnCooldown): SOLUS.Terminal.print("error", f"Retry in {round(error.retry_after, 2)} seconds")
    elif isinstance(error, commands.MissingRequiredArgument): SOLUS.Terminal.print("error", f"Missing required paramter: {SOLUS.Functions.signature(error.param.name)}")
    elif isinstance(error, commands.EmojiNotFound): SOLUS.Terminal.print("error", "You're not in the server that has this emote")
    elif isinstance(error, discord.Forbidden): SOLUS.Terminal.print("error", "Missing Permission(s)")
    elif isinstance(error, discord.NotFound): SOLUS.Terminal.print("error", "Not Found")
    elif isinstance(error, commands.RoleNotFound): SOLUS.Terminal.print("error", "Role Not Found")
    elif isinstance(error, commands.UserNotFound): SOLUS.Terminal.print("error", "User Not Found")
    elif isinstance(error, SOLUS.Errors.BoolError): SOLUS.Terminal.print("error", "Argument must be On or Off")
    elif isinstance(error, (discord.HTTPException, commands.BadArgument, commands.BadUnionArgument)): SOLUS.Terminal.print("error", error)
    else:
        print(f"Ignoring exception in command: {ctx.command}", file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

@Solus.event
async def on_message_edit(before, after):
    await Solus.process_commands(after)

@Solus.event
async def on_command(ctx):
    if(SOLUS.Features.delete_command_invoke_message):
        try:
            await asyncio.sleep(SOLUS.Features.message_delete_delay)
            await ctx.message.delete()
        except(discord.NotFound, AttributeError, RuntimeError):
            pass

@Solus.event
async def on_command_completion(ctx):
    _args = " ".join([str(arg) for arg in ctx.args if not isinstance(arg, commands.Context) and arg is not None])
    _kwargs = " ".join([str(value) for value in ctx.kwargs.values()])
    SOLUS.Terminal.print("command", f"{ctx.command.qualified_name.title()} {_args} {_kwargs}")

@tasks.loop(seconds=1)
async def update_config():
    SOLUS.Features.update()

@Solus.event
async def on_ready():
    await startprint()
    SOLUS.Terminal.title(f"Solus Self-bot | Logged in as {Solus.user.name}")
    SOLUS.System.toast("Welcome to SOLUS", f"Solus Self-bot\nLogged in as {Solus.user.name}", duration=5, threaded=True)
    await Solus.change_presence(status=discord.Status.offline, afk=True)

SOLUS.Commands.update()
SOLUS.JSON.Temp.update()
SOLUS.Features.update()

try:
    update_config.start()
except Exception as e:
    SOLUS.Terminal.print("error", f"{e.__class__.__name__}: {e}")
    exit()

SOLUS.Terminal.print("event", "Attempting to login...")

try:
    Solus.run(SOLUS.Features.token, bot=False)
except discord.LoginFailure as e:
    SOLUS.Terminal.print("error", f"{e.__class__.__name__}: Please check that the token in the Config.json file is correct")
    SOLUS.Terminal.input("Press Enter to exit...")
    exit()