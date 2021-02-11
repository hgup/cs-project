import pygame

pygame.mixer.init()
pygame.mixer.pre_init(44100, -16, 2, 512)

def pathTo(sound):
    return r'/SoundData/'+sound

# MUSIC

main_menu= pathTo('Offenbach - Infernal Galop.mp3')

chase_music_0 = pathTo('Rossini William Tell Overture Final.mp3')

chase_music_1 = pathTo('Offenbach - Can Can Music.mp3')

chase_music_2 = pathTo('Swan Lake - Ballet Suite Op. 20, ACT 3 Spanish Dance')

chase_music_3 = pathTo('Sabre Dance - Aram Khachaturian.mp3')

chase_music_finale = pathTo('Concerto No. 2 in G Minor, RV 315 Summer III. Presto - Vivaldi The Four Seasons.mp3')

# SOUNDS

