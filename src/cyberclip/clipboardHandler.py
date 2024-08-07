import pyperclip
import re
import sys, os, subprocess
from six import binary_type
from urllib.parse import unquote
from pathlib import Path
from bs4 import BeautifulSoup


"""Random weird cases :

- Copying from Google Chrome only returns one data type :

Detected format : 49346 -> b'Version:0.9\r\nStartHTML:0000000416\r\nEndHTML:0000001075\r\nStartFragment:0000000452\r\nEndFragment:0000001039\r\nSourceURL:https://www.google.com/search?q=python+if+name+%3D%3D+main&rlz=1C1LZQR_frFR1104FR1104&oq=python+if+na&gs_lcrp=EgZjaHJvbWUqBwgAEAAYgAQyBwgAEAAYgAQyBggBEEUYOTIHCAIQABiABDIHCAMQABiABDIHCAQQABiABDIHCAUQABiABDIHCAYQABiABDIHCAcQABiABDIHCAgQABiABDIHCAkQABiABNIBCDQxMzFqMGo0qAIAsAIB&sourceid=chrome&ie=UTF-8\r\n<html>\r\n<body>\r\n<!--StartFragment--><span style="color: rgb(77, 81, 86); font-family: arial, sans-serif; font-size: 14px; font-style: normal; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: 
400; letter-spacing: normal; orphans: 2; text-align: left; text-indent: 0px; text-transform: none; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; white-space: normal; background-color: rgb(255, 255, 255); text-decoration-thickness: initial; text-decoration-style: initial; text-decoration-color: initial; display: inline !important; float: none;">Then it executes the code from the file.</span><!--EndFragment-->\r\n</body>\r\n</html>\x00'

"""


# TODO handle Image in clipboard
"""
    a = get_clipboard_data(debug=True)
    with open("a.txt","wb") as f:
        f.write(a.get(49278)) 
"""


CLIPBOARD_TYPE = {
    1: ["TEXT", "text/plain"],
    13: ["UTF8_STRING"],
    15: ["files"]
}


def get_file_icon(filename: str)-> str:
    if re.search(r"(\.apng|\.avif|\.gif|\.jfif|\.jpeg|\.jpg|\.pjp|\.pjpeg|\.png|\.svg|\.webp)$", filename):
        return "📷 "
    elif re.search(r"(\.3gp|\.8svx|\.aa|\.aac|\.aax|\.act|\.aiff|\.alac|\.amr|\.ape|\.au|\.awb|\.dss|\.dvf|\.flac|\.gsm|\.iklax|\.ivs|\.m4a|\.m4b|\.m4p|\.mmf|\.mogg|\.movpkg|\.mp3|\.mpc|\.msv|\.nmf|\.oga|\.ogg|\.opus|\.ra|\.raw|\.rf64|\.rm|\.sln|\.tta|\.voc|\.vox|\.wav|\.webm|\.wma|\.wv)$", filename):
        return "🔊 "
    elif re.search(r"(\.xlsx|\.tsv|\.csv|\.xls)$", filename):
        return "📊 "
    elif re.search(r"(\.py|\.pyc|\.jsx?|\.c|\.cpp|\.java|\.cs|\.css|\.html?|\.go|\.ruby|\.rb|\.php|\.db|\.exe|\.ba(t|sh))$", filename):
        return "👩‍💻 "
    elif re.search(r"(\.docx?|\.pptx?|\.txt|\.epub|\.md|\.pdf)$", filename):
        return "📝 "
    elif re.search(r"(\.[7bg]?zip|\.[jrt]ar|\.gz)$", filename):
        return "🗂️ "
    else :
        return "📄 "


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
        if 15 in f:
            files = list(win32clipboard.GetClipboardData(15))
        elif 49278 in f:
            filepath = Path(__file__).parent / 'data/tmp.png'
            with open(filepath, "wb+") as file:
                file.write(win32clipboard.GetClipboardData(49278))
                files = [str(filepath)]
        if folders:
            files = [f"📂{f}" for f in files if os.path.isdir(f)] if files else None
        else:
            files = [f"{get_file_icon(f)}{f}" for f in files if os.path.isfile(f)] if files else None
        win32clipboard.CloseClipboard()
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
            files = [f"📂{f}" for f in files if os.path.isdir(str(f))] if files else None
        else:
            files = [f"{get_file_icon(f)}{f}" for f in files if os.path.isfile(str(f))] if files else None
        print(files)
        return files

def get_clipboard_data(debug=False) -> dict:
    clip_data = {}
    if sys.platform.startswith('win'):
        import win32clipboard
        try:
            win32clipboard.OpenClipboard()
            formats = get_clipboard_formats()
            clip_formats = {getattr(win32clipboard, attr):attr for attr in dir(win32clipboard) if not callable(getattr(win32clipboard, attr)) and attr.startswith("CF_")}
            for format in formats:
                if debug:
                    print(f"Detected format : {format} -> {str(win32clipboard.GetClipboardData(format))}")
                if format != 49346:
                    datatype = clip_formats.get(format)
                    if datatype:
                        print(f"Data found : {clip_formats.get(format)}")
                        clip_data.update({format:win32clipboard.GetClipboardData(format)})
                    else:
                        print(f"Data found (Clip Format Id): {format}")
                        try:
                            clip_data.update({format:win32clipboard.GetClipboardData(format)})
                        except:
                            clip_data.update({format:""})
                if format == 14:
                    #14 is a custom datatype for excel, pyperclip handle the text representation
                    clip_data.update({1:pyperclip.paste()})

                if format == 49346 or format == 49278:
                    try:
                        data = win32clipboard.GetClipboardData(format).decode("utf-8")
                        if data.contains("StartHTML"):
                            match = re.search('<!--StartFragment-->(?P<fragment>.*)<!--EndFragment-->', data)
                            if text:= match.group("fragment"):
                                clip_data.update({1:text})
                    except:
                        pass

        except Exception as e:
            print(e)
        finally:
            try:
                win32clipboard.CloseClipboard()
            except:
                pass
    else:
        clip_data.update({1:pyperclip.paste()})
        if get_clipboard_files(folders=False) or get_clipboard_files(folders=True):
            filepath_data = get_clipboard_files(folders=False) + get_clipboard_files(folders=True)
            clip_data.update({15: filepath_data})
    return clip_data

def get_clipboard_text():
    data = get_clipboard_data()
    print(data)
    text_data = data.get(1,"") # 1 is textual data in Windows clipboard
    utf8_data = data.get(13,"") # 13 is UTF8 data in Windows clipboard
    filepath_data = "\n".join(data.get(15, [])) # 15 is file data in textual Clipboard
    if utf8_data:
        str_data = utf8_data
    elif text_data:
        str_data = text_data
    else:
        str_data = filepath_data
    return str_data

if __name__=="__main__":
    a = get_clipboard_data(debug=False)
    print(get_clipboard_text())