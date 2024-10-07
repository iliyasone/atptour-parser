import json
import os
import time

class RealTimeFileObject:
    """this class just a wrapper under a some json file
    all attributes dynamically saved and loaded from file

    attributes started with '_' are not sync
    """

    _obj_file: str

    def __init__(self,):
        try:
            self._obj_file
        except AttributeError:
            # makes settings file from class name but make first letter lower
            self._obj_file = f'{self.__class__.__name__[0].lower()}{self.__class__.__name__[1:]}.json'
        
        # Ensure the obj file exists
        if not os.path.exists(self._obj_file):
            self._write_file({})
                
        
        data = self._read_file()
        
        # create a default value for each attribute
        # if not already exist
        for name, typ in self.__annotations__.items():
            if name not in data:
                 # I didn't use hasattr() because it calls __getattribute__,
                 # and __getattribute__ read file, not real attributes 
                if name in self.__class__.__dict__:
                    obj = self.__class__.__dict__[name]
                    if callable(obj) and '<lambda>' in obj.__name__:
                        data[name] = obj()
                    else:
                        data[name] = obj
                else:
                    # if no default value, keep it as None
                    data[name] = None
                    
        self._write_file(data)
                
                

    def _read_file(self) -> dict:
        with open(self._obj_file, "r", encoding="utf-8") as file:
            return json.load(file)

    def _write_file(self, settings):
        with open(self._obj_file, "w", encoding="utf-8") as file:
            json.dump(settings, file, indent=4, ensure_ascii=False)

    def __getattribute__(self, name: str):
        if name.startswith("_"):
            return super().__getattribute__(name)
        return self._read_file()[name]

    def __setattr__(self, name: str, value):
        if name.startswith("_"):
            super().__setattr__(name, value)
        else:
            settings = self._read_file()
            settings[name] = value
            self._write_file(settings)

    def __delattr__(self, name):
        settings = self._read_file()
        del settings[name]
        self._write_file


class Settings(RealTimeFileObject):
    """
    The `Settings` class represents configuration settings. 
    Each class variable below serves as both a type hint and a placeholder for data 
    that will be dynamically loaded from or saved to a JSON file.
    
    These variables do not hold initial values directly in the class body but are 
    instead taken from the corresponding JSON file everytime when requested.
    
    Only in case if there is no such field in the file, those default values from 
    bellow would be taken
    """

    
    # _settings_file = "settings.json" (by default)


    # lambda functions called 
    # when obj created if no such value in file
    last_time_saved: int = lambda : int(time.time()) 
    """last time when file was saved"""

settings = Settings()