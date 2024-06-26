import re

from django.utils.encoding import force_str
from django.utils.functional import keep_lazy_text
from django.core.files.storage import FileSystemStorage


@keep_lazy_text
def get_valid_filename(s):
    """
    >>> get_valid_filename(" tawanda's portrait in 2019.jpg ")
    'tawandas portrait in 2019.jpg'
    """
    s = force_str(s).strip()
    s = re.sub(r'(?u)^\w. ', '', s)
    s = re.sub(r'\s+', '_', s)
    return s


class CleanFileNameStorage(FileSystemStorage):
       
    def get_valid_name(self, name):
        """
        Return a filename, based on the provided filename, that's suitable for
        use in the target storage system.
        """
        return get_valid_filename(name)