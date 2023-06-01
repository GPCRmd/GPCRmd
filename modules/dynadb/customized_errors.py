class DownloadGenericError(Exception):
    pass


class StreamSizeLimitError(Exception):
    pass


class StreamTimeoutError(Exception):
    pass


class ParsingError(Exception):
    pass


class MultipleMoleculesinSDF(Exception):
    def __init__(self,*args,file_name='',**kwrags):
        msg="Parsing Error: SD files with more than 1 molecule are not accepted."
        super(MultipleMoleculesinSDF, self).__init__(msg,*args, **kwrags)
        

class InvalidMoleculeFileExtension(Exception):
    def __init__(self,*args,ext=None,**kwrags):
        self.ext = ext
        msg = "Molecule file with invalid extension: '"+ext+"' ."
        super(InvalidMoleculeFileExtension, self).__init__(msg,*args, **kwrags)

class RequestBodyTooLarge(Exception):
    def __init__(self,*args,max_size=None,**kwrags):
        self.max_size = max_size
        if max_size is None:
            msg = "Request body is too large."
        else:
            msg = "Request body is too large (Max. "+sizeof_fmt(max_size)+")."
        super(RequestBodyTooLarge, self).__init__(msg,*args, **kwrags)

class FileTooLarge(Exception):
    def __init__(self,*args,max_size=None,**kwrags):
        self.max_size = max_size
        if max_size is None:
            msg = "Uploaded file is too large."
        else:
            msg = "Uploaded file is too large (Max. "+sizeof_fmt(max_size)+")."
        super(FileTooLarge, self).__init__(msg,*args, **kwrags)
        
class TooManyFiles(Exception):
    def __init__(self,*args,max_files=None,**kwrags):
        self.max_files = max_files
        if max_files is None:
            msg = "Too many files uploaded."
        else:
            msg = "Too many files uploaded (Max.'"+str(max_files)+")."
        super(TooManyFiles, self).__init__(msg,*args, **kwrags)
        
        
class SubmissionValidationError(Exception):
    pass        

class InvalidPNGFileError(Exception):
    pass
    
def sizeof_fmt(num, suffix='B'):
    '''Stack Overflow http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
    By Wai Ha Lee et al. (http://stackoverflow.com/users/1364007/wai-ha-lee) and Fred Cirera
    (https://web.archive.org/web/20111010015624/http://blogmag.net/blog/read/38/Print_human_readable_file_size)'''
    
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)
