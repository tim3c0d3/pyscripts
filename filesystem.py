import string
import re
from string import Template
from StringIO import StringIO
import os
import hashlib

regex = r'[a-zA-Z0-9_]*'
rx = re.compile(regex)

whitespace = string.whitespace
lowercase = string.lowercase
uppercase = string.uppercase


class FileLoader:
    """
        Load file and read into file contents into string object in memory
        Example usage:

        >>> fs = FileLoader("/home/public_html/", include_only=('*/html','*.html')) # only html files in 'html' folder
        >>> fd = FileLoader("/home/public_html/", include_only=('html/*', 'files/*'), exclude=('*.mp4','*.m4a'))

    """
    MAX_FILE_SIZE = 50*1024*1024  # Max file size to read is 50 MB
    all_files = dict()

    def __init__(self, path, maxsize=MAX_FILE_SIZE, include_only=(), exclude=()):
        # check if the path given exists on the filesystem
        if not os.path.exists(path):
            raise PathError(path)

        self.path = path
        self.file_directory = dict()
        self.maxsize = maxsize
        self.include_only = include_only
        self.exclude = exclude

        # if path is a directory check to see if empty
        if os.path.isdir(self.path):
            if os.listdir(self.path):
                self.traverse(self.path, self.exclude, self.include_only)
            else:
                # directory is empty, path updated to NoneType
                self.file_directory.update({self.path: None})

    def traverse(self, root_path, excluded, include_only):
        """
            Update the file_directory dict {hash("PATH/ONE"): <string>,
                                            hash("PATH/ONE"):<string>,
                                            hash("PATH/TWO"):<string>, ...}
                                        :type root_path: str
                                        :type excluded: tuple
                                        :type include_only: tuple
        """

        try:
            for root_dir, directories, files in os.walk(root_path):

                for directory in directories:
                    # remove excluded directories
                    if include_only:
                        if directory not in [folder.strip(os.sep + "*") for folder in include_only
                                             if folder.endswith(os.sep) or folder.startswith('*' + os.sep)]:

                            # trim all directories not in include_only
                            directories.remove(directory)

                    if excluded:
                        if directory in [sub_folder.strip('*' + os.sep) for sub_folder in excluded
                                         if sub_folder.startswith('*' + os.sep)]:

                            # if sub_folder in excluded, remove the sub_folder from the directory list
                            directories.remove(directory)

                        if directory in [folder.strip(os.sep) for folder in excluded
                                         if folder.endswith(os.sep)]:
                            directories.remove(directory)

                for file_in_directory in files:
                    normalized_path = os.path.normpath(os.path.join(root_dir, file_in_directory))
                    if include_only:
                        if ext(normalized_path) in [extension.lstrip("*.")
                                                    for extension in include_only if extension.startswith("*.")]:
                            self._open(normalized_path)
                            # if extension specified in include_only, exclude all other extensions continue to next file
                    if excluded:
                        if ext(normalized_path) not in excluded:
                            # load all files not explicitly excluded
                            self._open(normalized_path)

        except StopIteration:
            pass

    def _open(self, path):

        f_length = size(path)
        if f_length > self.maxsize:
            raise FileSizeError(path)

        # file not in exclude list and smaller than MAX_FILE_SIZE
        # should be refactored into separate function
        with open(path, "rb") as fo:
            try:
                max_attempt = 15

                while True:
                    attempt = 0  # Number of attempts
                    fc = StringIO()
                    fc.write(fo.read())
                    if len(fc.getvalue()) != f_length:
                        # incomplete file read for some reason, try again
                        fc.seek(0)
                        fc.close()
                        attempt += 1
                        if attempt < max_attempt:
                            continue
                        else:
                            break
                    else:

                        # store in dict with md5(file_path) as key
                        # and StringIO object as value
                        self.file_directory.update({md5(path): fc})
                        break

            except OSError:
                raise
    
    @classmethod
    def get(cls, path):
        """
            Return file represented by path as a StringIO object 
            or empty string if no such file exists
        """
        h = md5(path)
        return cls.all_files[h]
    
    @classmethod
    def load_hashes(cls, a):
        """
            Load the file_directory dicts to class variable all files
            TODO: call this method automatically when the class object is created
        """
        cls.all_files.update(a)

    @classmethod
    def all(cls):
        """
            Return the all_files class variables
        """
        return cls.all_files
    

def ext(path):
    """ Returns the associated extension for file 'path.ext' -> 'ext' """
    filename = os.path.basename(path)
    return filename.split(".")[-1] if (len(filename.split(".")) > 1) else ""


def size(path):
    """ Return the size of the file in 'path' -> int """
    return os.path.getsize(path)


def md5(arg):
    """
        Return an md5 hash of arg
        Use this function to get the key of the file
        in the file_directory dict of the FileLoader instance
    """
    return hashlib.md5(arg).hexdigest()


class PathError(Exception):
    def __init__(self, arg):
        self.message = "Path Does Not Exist"
        self.args = arg


class FileSizeError(Exception):
    def __init__(self, arg):
        self.message = "File payload too LARGE to read into memory"
        self.args = arg
