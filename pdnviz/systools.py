import openpyxl, datetime, os, subprocess, tempfile


def is_linux() -> bool:
    return os.name == 'posix'


def open_file(filename: str):
    if is_linux():
        subprocess.Popen(['xdg-open', filename])
    else:
        os.startfile(filename)


def ensure_directories(path: str, is_filename: bool = False):
    if is_filename:
        path = os.path.dirname(path)
    os.makedirs(path, exist_ok=True)


def get_tempfile_path() -> str:
    fd, path = tempfile.mkstemp()
    os.close(fd)
    return path
