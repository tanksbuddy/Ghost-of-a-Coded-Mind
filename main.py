##  GHOST OF A CODED MIND
##
## A game for Dreamscapes.
## A user can insert "dreams" (poems) into a computer, which will be typed onto the display.
## Represents an old 90s terminal.
##
## Authors: Nami Eskandarian & Joseph Norton
## Version: 1.2

import copy
import multiprocessing
import os
import time
import asyncio
from typing import NamedTuple
import pygame, random
import requests
from timeloop import Timeloop
from datetime import timedelta
from time import sleep
from enum import Enum

pygame.init()
tl = Timeloop()
lock = multiprocessing.Lock()

# Enum class to denote which word is selected
class WordSelection(Enum):
    pronoun = 1
    sense = 2
    noun = 3
    verb = 4

class Poem(NamedTuple):
    id: str
    text: str

# Class that defines a string representing a poem
class GameString:

    # Constructor class
    def __init__(self, pronouns, senses, nouns, verbs):

        # Which word is selected
        self.select = WordSelection.pronoun

        # Word banks
        self.pronouns = pronouns
        self.senses = senses
        self.nouns = nouns
        self.verbs = verbs

        # Replace beginning of nouns and verbs banks with defaults
        self.nouns.insert(0, "[NOUN]")
        self.verbs.insert(0, "[VERB]")

        # Current index of each bank
        self.pronounIndex = 0
        self.senseIndex = 0
        self.nounIndex = 0
        self.verbIndex = 0

    # Method to swap selected type of word
    def swapSelected(self, right):
        if right == 1:
            if self.select == WordSelection.pronoun:
                self.select = WordSelection.sense
            elif self.select == WordSelection.sense:
                self.select = WordSelection.noun
            elif self.select == WordSelection.noun:
                self.select = WordSelection.verb
            elif self.select == WordSelection.verb:
                self.select = WordSelection.pronoun
        else:
            if self.select == WordSelection.pronoun:
                self.select = WordSelection.verb
            elif self.select == WordSelection.sense:
                self.select = WordSelection.pronoun
            elif self.select == WordSelection.noun:
                self.select = WordSelection.sense
            elif self.select == WordSelection.verb:
                self.select = WordSelection.noun

    # Method to swap word based on selection
    def swapWord(self, up):
        if up:
            if self.select == WordSelection.pronoun:
                if self.pronounIndex >= len(self.pronouns) - 1:
                    self.pronounIndex = 1
                else:
                    self.pronounIndex += 1
            elif self.select == WordSelection.sense:
                if self.senseIndex >= len(self.senses) - 1:
                    self.senseIndex = 1
                else:
                    self.senseIndex += 1
            elif self.select ==  WordSelection.noun:
                if self.nounIndex >= len(self.nouns) - 1:
                    self.nounIndex = 1
                else:
                    self.nounIndex += 1
            elif self.select == WordSelection.verb:
                if self.verbIndex >= len(self.verbs) - 1:
                    self.verbIndex = 1
                else:
                    self.verbIndex += 1
        else:
            if self.select == WordSelection.pronoun:
                if self.pronounIndex <= 1:
                    self.pronounIndex = len(self.pronouns) - 1
                else:
                    self.pronounIndex -= 1
            elif self.select == WordSelection.sense:
                if self.senseIndex <= 1:
                    self.senseIndex = len(self.senses) - 1
                else:
                    self.senseIndex -= 1
            elif self.select == WordSelection.noun:
                if self.nounIndex <= 1:
                    self.nounIndex = len(self.nouns) - 1
                else:
                    self.nounIndex -= 1
            elif self.select == WordSelection.verb:
                if self.verbIndex <= 1:
                    self.verbIndex = len(self.verbs) - 1
                else:
                    self.verbIndex -= 1

    # Returns a list of selected words
    def getList(self):
        retVal = [self.pronouns[self.pronounIndex], self.senses[self.senseIndex], "The", self.nouns[self.nounIndex], self.verbs[self.verbIndex]]
        return retVal

# URL for poetry database
session = requests.Session()
url = os.environ["API_URL"]
offlineMode = False # If any HTTP request fails at any point, the game will switch to offline mode

# Declare constants
wordLimit = 11
poemLimit = 12
white = (255, 255, 255)
black = (0, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 128)
width = 1920
height = 1080

# Setup screen of game
# display_surface = pygame.display_set_mode((width, height))
display_surface = pygame.display.set_mode((width, height), pygame.SCALED)
pygame.display.set_caption('Ghost of a Coded Mind')
pygame.display.toggle_fullscreen()

# Format of the poem
# PRONOUNS SENSES "The" NOUNS VERBS

# Import words from text files

file = open("Pronoun Wordbank.txt")
pronouns = file.read().split("\n")
pronouns[0] = "[PRONOUN]" # "[Pronoun]"
file.close()

file = open("Senses Wordbank.txt")
senses = file.read().split("\n")
senses[0] = "[SENSE]" # "[Sense]"
file.close()

the = "The"

file = open("Noun Wordbank.txt")
nouns = file.read().split("\n")
nouns.pop(0)
file.close()

file = open("Verb Wordbank.txt")
verbs = file.read().split("\n")
verbs.pop(0)
for i in range(len(verbs)):
    verbs[i] = verbs[i].strip().capitalize()
file.close()

# Setup font for terminal
font = pygame.font.Font('ModernDOS9x16.ttf', 32)

# Create text for instructions
instructionText = font.render("INSERT DREAM...", True, green, black)
instructionRect = instructionText.get_rect()
instructionRect.center = (width / 6 + instructionRect.width / 2, height - 150)

# Create text for offline text box
offlineText = font.render("OFFLINE", True, blue, black)
offlineRect = offlineText.get_rect()
offlineRect.center = (offlineRect.width / 2, offlineRect.height / 2)

# Create text for title
title = [
    r"  ________.__                    __            _____           _________            .___         .___    _____  .__            .___", 
    r" /  _____/|  |__   ____  _______/  |_    _____/ ____\ _____    \_   ___ \  ____   __| _/____   __| _/   /     \ |__| ____    __| _/", 
    r"/   \  ___|  |  \ /  _ \/  ___/\   __\  /  _ \   __\  \__  \   /    \  \/ /  _ \ / __ |/ __ \ / __ |   /  \ /  \|  |/    \  / __ | ", 
    r"\    \_\  \   Y  (  <_> )___ \  |  |   (  <_> )  |     / __ \_ \     \___(  <_> ) /_/ \  ___// /_/ |  /    Y    \  |   |  \/ /_/ | ", 
    r" \______  /___|  /\____/____  > |__|    \____/|__|    (____  /  \______  /\____/\____ |\___  >____ |  \____|__  /__|___|  /\____ | ", 
    r"        \/     \/           \/                             \/          \/            \/    \/     \/          \/        \/      \/ "]
titlefont = pygame.font.Font('ModernDOS9x16.ttf', 16)
titleText1 = titlefont.render(title[0], True, green, black)
titleText2 = titlefont.render(title[1], True, green, black)
titleText3 = titlefont.render(title[2], True, green, black)
titleText4 = titlefont.render(title[3], True, green, black)
titleText5 = titlefont.render(title[4], True, green, black)
titleText6 = titlefont.render(title[5], True, green, black)
lineText = titlefont.render("______________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________________", True, green, black)

titleRect1 = titleText1.get_rect()
titleRect2 = titleText2.get_rect()
titleRect3 = titleText3.get_rect()
titleRect4 = titleText4.get_rect()
titleRect5 = titleText5.get_rect()
titleRect6 = titleText6.get_rect()
lineRectTop = lineText.get_rect()
lineRectBot = copy.deepcopy(lineRectTop)

titleRect1.center = (width / 2, 90)
titleRect2.center = (width / 2, 90 + 18)
titleRect3.center = (width / 2, 90 + 36)
titleRect4.center = (width / 2, 90 + 54)
titleRect5.center = (width / 2, 90 + 72)
titleRect6.center = (width / 2, 90 + 90)
lineRectTop.center = (width / 2, 90 + 108)
lineRectBot.center = (width / 2, height - 200)

# Variables for fading in UI at beginning
alphaSurface = pygame.Surface((width, height))
alphaSurface.fill(black)
alph = 255

# Last setups before loop:
initialResponse = session.get(url)
initialPoems = []
if (initialResponse.status_code == 200):
    initialPoems = map(lambda entry: Poem(entry["id"], entry["text"]), initialResponse.json()["data"])
else:
    offlineMode = True

poemAnimationQueue = list(initialPoems) # List of poems yet to be typed onto screen
poetryBank = list() # List of recorded poems
newLine = False # Flag for cursor animation
cursor = cursorStart = pygame.Rect(width / 6, height / 4 - 17, 24, 32)
cursorCensor = cursorCensorStart = pygame.Rect(width / 6 + 24, height / 4 - 17, 1000, 32)

# Start animating poems if we already have poems initially
if (len(poemAnimationQueue) != 0):
    poetryBank.append(poemAnimationQueue.pop())
    newLine = True

gamestring = GameString(pronouns, senses, random.sample(nouns, wordLimit), random.sample(verbs, wordLimit)) # Current editable poem
theText = font.render(" The ", True, green, black) # Render "The" part of each poem

creditLine = titlefont.render("Nami Eskandarian, Joseph Norton, RJ Walker", True, green, black)
creditRect = creditLine.get_rect()
creditRect.center = (width / 6 + creditRect.width / 2, height - 100)
lastMove = time.time()

async def main():

    global gamestring, newLine, lastMove, alph, cursor, cursorCensor, offlineMode

    tl.start(block = False)
    jobStopped = False
    
    while True:
        if (not jobStopped and offlineMode):
            tl.stop()
            jobStopped = True

        # Get the current editable poem words
        pronounText = font.render(" " + gamestring.getList()[0] + " ", True, green, black)
        senseText = font.render(" " + gamestring.getList()[1] + " ", True, green, black)
        nounText = font.render(" " + gamestring.getList()[3] + " ", True, green, black) 
        verbText = font.render(" " + gamestring.getList()[4] + " ", True, green, black)

        # Change whichever word is selected to have a different background
        if gamestring.select == WordSelection.pronoun:
            pronounText = font.render(" " + gamestring.getList()[0] + " ", True, black, green)
        elif gamestring.select == WordSelection.sense:
            senseText = font.render(" " + gamestring.getList()[1] + " ", True, black, green)
        elif gamestring.select == WordSelection.noun:
            nounText = font.render(" " + gamestring.getList()[3] + " ", True, black, green)
        elif gamestring.select == WordSelection.verb:
            verbText = font.render(" " + gamestring.getList()[4] + " ", True, black, green)

        # Setup text boxes for editable poem
        verbRect = verbText.get_rect()
        verbRect.center = (5 * width / 6 - verbRect.width / 2, height - 150)
        nounRect = nounText.get_rect()
        nounRect.center = (verbRect.center[0] - verbRect.width / 2 - nounRect.width / 2, height - 150)
        theRect = theText.get_rect()
        theRect.center = (nounRect.center[0] - nounRect.width / 2 - theRect.width / 2, height - 150)
        senRect = senseText.get_rect()
        senRect.center = (theRect.center[0] - theRect.width / 2 - senRect.width / 2, height - 150)
        proRect = pronounText.get_rect()
        proRect.center = (senRect.center[0] - senRect.width / 2 - proRect.width / 2, height - 150)

        # Fill the screen with a black color
        display_surface.fill(black)

        # Display the title, lines, and instructions
        display_surface.blit(titleText1, titleRect1)
        display_surface.blit(titleText2, titleRect2)
        display_surface.blit(titleText3, titleRect3)
        display_surface.blit(titleText4, titleRect4)
        display_surface.blit(titleText5, titleRect5)
        display_surface.blit(titleText6, titleRect6)
        display_surface.blit(lineText, lineRectTop)
        display_surface.blit(lineText, lineRectBot)
        display_surface.blit(instructionText, instructionRect)
        display_surface.blit(creditLine, creditRect)

        # Display the editable poem
        display_surface.blit(pronounText, proRect)
        display_surface.blit(senseText, senRect)
        display_surface.blit(theText, theRect)
        display_surface.blit(nounText, nounRect)
        display_surface.blit(verbText, verbRect)

        # Play fade in (if applicable)
        if (alph >= 0):
            alph -= 1
            alphaSurface.set_alpha(alph)
            display_surface.blit(alphaSurface, (0, 0))

        # Text to signify whether game is connected to server
        if (offlineMode):
            display_surface.blit(offlineText, offlineRect)

        # Display all recorded poems
        for i in range(len(poetryBank)):
            text = font.render("<: " + poetryBank[i].text, True, green, black)
            textRect = text.get_rect()
            textRect.center = (width / 6 + textRect.width / 2, height / 4 + 50*i)
            display_surface.blit(text, textRect)

            if(i == 0):
                newLineRect = textRect

        # Play animation of cursor typing poem if flag is set
        if(newLine):

            # If the cursor has not finished the poem, play the animation
            if(cursor.right < newLineRect.right + 33):
                cursor = cursor.move(16, 0)
                cursorCensor = cursorCensor.move(16, 0)
                pygame.draw.rect(display_surface, white, cursor)
                pygame.draw.rect(display_surface, black, cursorCensor)
                sleep(0.05)
            
            # When a line is finished, add another poem and reset animation
            else:
                lock.acquire()
                if (len(poemAnimationQueue) != 0):
                    # Limit for poems on screen
                    if len(poetryBank) == poemLimit:
                        poetryBank.pop()

                    poetryBank.insert(0, poemAnimationQueue.pop())
                    cursor = cursorStart
                    cursorCensor = cursorCensorStart
                else:
                    newLine = False
                lock.release()
                
        # Update graphics
        pygame.display.update()

        # Keep track of events
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    gamestring.swapSelected(False) # Move to left word
                if event.key == pygame.K_RIGHT:
                    gamestring.swapSelected(True) # Move to right word
                if event.key == pygame.K_UP:
                    gamestring.swapWord(True) # Go through selected bank up
                if event.key == pygame.K_DOWN:
                    gamestring.swapWord(False) # Go through selected bank down
                if event.key == pygame.K_RETURN and gamestring.pronounIndex != 0 and gamestring.nounIndex != 0 and gamestring.senseIndex != 0 and gamestring.verbIndex != 0:
                    # If this event is reached, the user has successfully submitted a poem

                    poemText = " ".join(gamestring.getList())
                    poemId = ""

                    # Post the poem onto the database if the game is online
                    if (not offlineMode):
                        postMessage = session.post(url, json=convert_poem_to_json_format(poemText))

                        if (postMessage.status_code == 201):
                            poemId = postMessage.json()["data"]["id"]
                        else:
                            offlineMode = True

                    # Reset Text box
                    gamestring = GameString(pronouns, senses, random.sample(nouns, wordLimit), random.sample(verbs, wordLimit))
                
                    lock.acquire()
                    # Also will add poem to the queue if poetry bank isn't empty
                    if (len(poetryBank) != 0):
                        poemAnimationQueue.append(Poem(poemId, poemText))
                    else:
                        poetryBank.insert(0, Poem(poemId, poemText))

                    # Setup animation to start adding a new line of poetry
                    newLine = True               
                    lock.release()

        await asyncio.sleep(0)

def convert_poem_to_json_format(poem):
    return { "poem": { "text": poem } }

@tl.job(interval=timedelta(seconds=10))
def update_poems():
    global tl, session, poetryBank, poemAnimationQueue, newLine, lock

    response = session.get(url)
    if (response.status_code != 200): return

    poems = map(lambda entry: Poem(entry["id"], entry["text"]), response.json()["data"])

    lock.acquire()
    poemAnimationQueue += list(set(poems) - set(poetryBank + poemAnimationQueue))
    newLine = True
    lock.release()

asyncio.run(main())