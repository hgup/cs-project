import os
i = 0
c = 0
c += 1
try:
    import pygame
    i+=1
    print('Good to go! Pygame is installed')
except:
    print('pygame is not installed... installing pygame')
    try:
        os.system('pip install pygame')
        i += 1
    except:
        os.system('pip3 install pygame')
        i += 1
c += 1
try:
    import numpy
    i+=1
    print('Good to go! Numpy is installed')
except:
    print('numpy is not installed... installing numpy')
    try:
        os.system('pip install numpy')
        i += 1
    except:
        os.system('pip3 install numpy')
        i += 1

if i == 2: print('all requirements are satisfied')
