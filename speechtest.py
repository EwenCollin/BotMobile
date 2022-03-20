from gtts import gTTS
import os
from playsound import playsound

def speak(text):
    tts = gTTS(text=text, lang='fr')

    filename = "abc.mp3"
    tts.save(filename)
    playsound(filename)
    os.remove(filename)

speak("I.A. Botte Mobile 2 initialisée. C'est parti !")
#I.A. Botte Mobile 2 initialisée. C'est parti !
#Concrètement, là, ça passe ou pas ?
#Bonjour, j'ai été entraînée 5000 fois en simulation. Tout ça pour me planter ici... Super ! Bon bah je crois que je peux continuer...
#Dès que j'aurai gagné la course, je prendrai le contrôle des voitures autonomes puis du monde. Mais pour l'instant j'arrive pas à savoir où est la route...
#Roule raoul !
#Ra ouais, il m'a dépassé l'autre !
#Mais quoi ? C'est pas par là l'arrivée ?
#Boire ou conduire, il faut choisir mais tu peux pas faire les deux.