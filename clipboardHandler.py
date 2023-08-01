import win32clipboard
import pyperclip
import sys, os, subprocess
from six import binary_type
from urllib.parse import unquote

CLIPBOARD_TYPE = {
    1: ["TEXT", "text/plain"],
    13: ["UTF8_STRING"],
    15: ["files"]
}


def get_clipboard_formats():
    '''
    Return list of all data formats currently in the clipboard
    '''
    formats = []
    if sys.platform.startswith('linux'):
        encoding = "utf-8"
        com = ["xclip", "-o", "-t", "TARGETS"]
        try:
            p = subprocess.Popen(com,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                stdin=subprocess.PIPE,
                                )
            for line in iter(p.stdout.readline, b''):
                if isinstance(line, binary_type):
                    line = line.decode(encoding)
                    formats.append(line.strip())
        except Exception as e:
            print("Exception from starting subprocess {0}: " "{1}".format(com, e))

    if sys.platform.startswith('win'):
        import win32clipboard  # pylint: disable=import-error
        f = win32clipboard.EnumClipboardFormats(0)
        while f:
            formats.append(f)
            f = win32clipboard.EnumClipboardFormats(f)    

    if not formats:
        print("get_clipboard_formats: formats are {}: Not implemented".format(formats))
    else:
        #print(formats)
        return formats

def enum_files_from_clipboard(mime):
    '''
    Generates absolute paths from clipboard 
    Returns unverified absolute file/dir paths based on defined mime type
    '''
    paths = []
    if sys.platform.startswith('linux'):
        encoding = "utf-8"
        com = ["xclip", "-selection", "clipboard","-o", mime]
        try:
            p = subprocess.Popen(com,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                stdin=subprocess.PIPE,
                                )
            for line in iter(p.stdout.readline, b''):
                if isinstance(line, binary_type):
                    line = line.decode(encoding).strip()
                    if line.startswith("file://"):
                        paths.append(unquote(line.replace("file://", "")))
                    else:
                        paths.append(unquote(line)) # Will append line which will be checked against isfile\isdir
            #print(paths)
            return paths
        except Exception as e:
            print("Exception from starting subprocess {0}: " "{1}".format(com, e))


def get_clipboard_files(folders=False):
    '''
    Enumerate clipboard content and return files/folders either directly copied or
    highlighted path copied
    '''
    files = None
    if sys.platform.startswith('win'):
        import win32clipboard  # pylint: disable=import-error
        win32clipboard.OpenClipboard()
        f = get_clipboard_formats()
        if win32clipboard.CF_HDROP in f:
            files = win32clipboard.GetClipboardData(win32clipboard.CF_HDROP)
        elif win32clipboard.CF_UNICODETEXT in f:
            files = [win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)]
        elif win32clipboard.CF_TEXT in f:
            files = [win32clipboard.GetClipboardData(win32clipboard.CF_TEXT)]
        elif win32clipboard.CF_OEMTEXT in f:
            files = [win32clipboard.GetClipboardData(win32clipboard.CF_OEMTEXT)]
        if folders:
            files = [f for f in files if os.path.isdir(f)] if files else None
        else:
            files = [f for f in files if os.path.isfile(f)] if files else None
        win32clipboard.CloseClipboard()
        print(files)
        return files

    if sys.platform.startswith('linux'):
        f = get_clipboard_formats()
        if "UTF8_STRING" in f:
            files = enum_files_from_clipboard("UTF8_STRING")
        elif "TEXT" in f:
            files = enum_files_from_clipboard("TEXT")
        elif "text/plain" in f:
            files = enum_files_from_clipboard("text/plain")
        if folders:
            files = [f for f in files if os.path.isdir(str(f))] if files else None
        else:
            files = [f for f in files if os.path.isfile(str(f))] if files else None
        print(files)
        return files

def get_clipboard_data() -> dict:
    clip_data = {}
    if sys.platform.startswith('win'):
        import win32clipboard
        try:
            win32clipboard.OpenClipboard()
            formats = get_clipboard_formats()
            clip_formats = {getattr(win32clipboard, attr):attr for attr in dir(win32clipboard) if not callable(getattr(win32clipboard, attr)) and attr.startswith("CF_")}
            for format in formats:
                datatype = clip_formats.get(format)
                if datatype:
                    print(f"Data found : {clip_formats.get(format)}")
                    clip_data.update({i:win32clipboard.GetClipboardData(format)})
                else:
                    print(f"Data found (Clip Format Id): {format}")
                    try:
                        clip_data.update({format:win32clipboard.GetClipboardData(format)})
                    except:
                        clip_data.update({format:""})
        except Exception as e:
            print(e)
        finally:
            win32clipboard.CloseClipboard()
    else:
        clip_data.update({1:pyperclip.paste()})
        if get_clipboard_files(folders=False) or get_clipboard_files(folders=True):
            filepath_data = get_clipboard_files(folders=False) + get_clipboard_files(folders=True)
            clip_data.update({15: filepath_data})
    return clip_data