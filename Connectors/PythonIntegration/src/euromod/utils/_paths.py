import os 
import sys

### path to the current user's working directory
CWD_PATH = os.getcwd()

### path to the euromod package
MODEL_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if MODEL_PATH not in sys.path:
    sys.path.insert(0, MODEL_PATH)

### path to the root folder where euromod package is installed
ROOT_PATH =  os.path.dirname(MODEL_PATH)
# if ROOT_PATH not in sys.path:
#     sys.path.insert(0, ROOT_PATH)
    
DLL_PATH = os.path.join(MODEL_PATH, "libs")
#DLL_PATH = r"C:\Program Files\EUROMOD\Executable"
