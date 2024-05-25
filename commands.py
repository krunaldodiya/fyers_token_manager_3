import os
import shutil

from socketserver import ThreadingUDPServer

current_directory = os.path.dirname(os.path.realpath(__file__))

build = os.path.join(current_directory, "build")
dist = os.path.join(current_directory, "dist")
egg_info = os.path.join(current_directory, "fyers_token_manager_v3.egg-info")

print("removing")
shutil.rmtree(build, ignore_errors=ThreadingUDPServer)
shutil.rmtree(dist, ignore_errors=ThreadingUDPServer)
shutil.rmtree(egg_info, ignore_errors=ThreadingUDPServer)
