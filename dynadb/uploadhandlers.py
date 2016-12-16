import os
from django.core.files.uploadhandler import TemporaryFileUploadHandler, StopUpload, StopFutureHandlers
from rdkit.Chem import MolFromMolBlock, ForwardSDMolSupplier
from .customized_errors import MultipleMoleculesinSDF,InvalidMoleculeFileExtension
from django.conf import settings
from .molecule_properties_tools import MOLECULE_EXTENSION_TYPES


class TemporaryFileUploadHandlerMaxSize(TemporaryFileUploadHandler):
    def __init__(self,request,max_size,*args,**kwargs):
        self.max_size = max_size
        self.__acum_size = 0
        super(TemporaryFileUploadHandlerMaxSize, self).__init__(request,*args, **kwargs)
        
    def handle_raw_input(self, input_data, META, content_length, boundary, encoding=None):
        """
        Use the content_length to signal whether or not this handler should be in use.
        """
        # Check the content-length header to see if we should
        # If the post is too large, reset connection.
        if content_length > self.max_size:
            raise StopUpload(connection_reset=True)
    def receive_data_chunk(self,raw_data, start):
        self.__acum_size += len(raw_data)
        if self.__acum_size > self.max_size:
            #close tempfile. It gets automatically deleted.
            #self.file.close()
            raise StopUpload(connection_reset=True)
        return super(TemporaryFileUploadHandlerMaxSize, self).receive_data_chunk(raw_data, start)
        
class TemporaryMoleculeFileUploadHandlerMaxSize(TemporaryFileUploadHandlerMaxSize):
    def __init__(self,request,max_size,*args,**kwargs):
        self.chunk_size=64*2**10
        self.filetype = None
        self.exception = None
        self.charset = None
        self.__previous_last_line = ''
        self.__end_mol_found = False
        self.__invalid = False
        self.__invalidtoomols = False
        
        super(TemporaryMoleculeFileUploadHandlerMaxSize, self).__init__(request,max_size,*args, **kwargs)
        
    def new_file(self, field_name, file_name, content_type, content_length, charset=None, content_type_extra=None):
        
        basename, ext = os.path.splitext(file_name)
        ext = ext.lower()
        ext = ext.strip('.')
        self.charset = 'utf-8'
        #if charset is None:
            #self.charset = 'utf-8'
        #else:
            #self.charset = charset
         
          
        if ext in MOLECULE_EXTENSION_TYPES.keys():
            self.filetype = MOLECULE_EXTENSION_TYPES[ext]
        else:
            try:
                raise InvalidMoleculeFileExtension(ext=ext)
            except Exception as e:
                self.exception = e
                raise StopUpload(connection_reset=False)
        
        super(TemporaryMoleculeFileUploadHandlerMaxSize, self).new_file(field_name, file_name, content_type, content_length, self.charset, content_type_extra)
        raise StopFutureHandlers()

    def receive_data_chunk(self,raw_data, start):


        if self.filetype == 'sdf':
            encoded_raw_data = raw_data.decode(self.charset)
            encoded_raw_data = end_of_line_normalitzation(encoded_raw_data)
            block = self.__previous_last_line + encoded_raw_data

            
            if self.__end_mol_found and block.strip() != '':
                self.__invalidtoomols = True
            else:
                idx = block.rfind("\n$$$$\n")
                if idx > 0:
                    self.__end_mol_found = True
                    if len(block) > 6 and block[idx+6:].strip() == '':
                        self.__invalidtoomols = False
                    else:
                        self.__invalidtoomols = True
                elif block[0:6] == "$$$$\n":
                    self.__end_mol_found = True
                    if len(block) > 5 and block[idx+5:].strip() == '':
                        self.__invalidtoomols = False
                    else:
                        self.__invalidtoomols = True

            if self.__invalidtoomols == True:
                #self.file.close()
                try:
                    raise MultipleMoleculesinSDF()
                except Exception as e:
                    self.exception = e
                    raise StopUpload(connection_reset=False)
                
            splited_block = block.rsplit(sep="\n",maxsplit=1)
            if len(splited_block) == 1:
                self.__previous_last_line = block
            else:
                self.__previous_last_line = splited_block[1]
            
        return super(TemporaryMoleculeFileUploadHandlerMaxSize, self).receive_data_chunk(raw_data, start)

    def file_complete(self, *args, **kwargs):
        self.file.filetype = self.filetype
        self.file.charset = self.charset 
        return super(TemporaryMoleculeFileUploadHandlerMaxSize, self).file_complete(*args, **kwargs)
        
        
def end_of_line_normalitzation(string):
       return string.replace('\r\n','\n').replace('\r','\n')