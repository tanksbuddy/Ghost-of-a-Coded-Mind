##  GHOST OF A CODED MIND
##
## A game for Dreamscapes.
## A user can insert "dreams" (poems) into a computer, which will be typed onto the display.
## Represents an old 90s terminal.
##
## Authors: Nami Eskandarian & Joseph Norton
## Version: 1.2

import json
import pyodide
import copy
import os
import time
import asyncio
from typing import NamedTuple
import pygame, random
from time import sleep
from enum import Enum

from fetch import RequestHandler

pygame.init()
lock = asyncio.Lock()
clock = pygame.time.Clock()

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

    # Method to swap selected type of word with a direction (used for keyboard)
    def swapSelectedWithDirection(self, right):
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

    # Method to swap selected type of word with the type (used for mouse)
    def swapSelectedWithWordType(self, wordType):
        self.select = wordType

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
    
    # Returns a boolean determining if poem is ready to submit
    def checkForValidEntry(self):
        return self.pronounIndex != 0 and self.nounIndex != 0 and self.senseIndex != 0 and self.verbIndex != 0

# URL for poetry database
session = RequestHandler()
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
display_surface = pygame.display.set_mode((width, height))
pygame.display.set_caption('Ghost of a Coded Mind')

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
interactableFont = pygame.font.Font('ModernDOS9x16.ttf', 40)

# Create text for instructions
instructionText = interactableFont.render("INSERT DREAM...", True, green, black)
instructionTextHighlight = interactableFont.render("INSERT DREAM...", True, black, green)
instructionRect = instructionText.get_rect()
instructionRect.center = (width / 8 + instructionRect.width / 2, height - 150)

# Create text for offline text box
offlineText = font.render("OFFLINE", True, blue, black)
offlineRect = offlineText.get_rect()
offlineRect.center = (offlineRect.width / 2, offlineRect.height / 2)

# Create text for loading
bootText = font.render("...LOADING DREAMS...", True, green, black)
bootText2 = pygame.font.Font('ModernDOS9x16.ttf', 16).render("(This may take up to a minute)", True, green, black)
bootRect = bootText.get_rect()
bootRect2 = bootText2.get_rect()
bootRect.center = (width / 2, height / 2)
bootRect2.center = (width / 2, height - 200)

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
poemAnimationQueue = [] # List of poems yet to be typed onto screen
poetryBank = list() # List of recorded poems
newLine = False # Flag for cursor animation
cursor = cursorStart = pygame.Rect(width / 6, height / 4 - 17, 24, 32)
cursorCensor = cursorCensorStart = pygame.Rect(width / 6 + 24, height / 4 - 17, 1000, 32)

gamestring = GameString(pronouns, senses, random.sample(nouns, wordLimit), random.sample(verbs, wordLimit)) # Current editable poem
theText = interactableFont.render(" The ", True, green, black) # Render "The" part of each poem
theRect = theText.get_rect()

creditLine = titlefont.render("Nami Eskandarian, Joseph Norton, RJ Walker", True, green, black)
creditRect = creditLine.get_rect()
creditRect.center = (width / 8 + creditRect.width / 2, height - 100)
lastMove = time.time()
mouseOverWord = False

async def main():
    global gamestring, newLine, lastMove, alph, cursor, cursorCensor, offlineMode, poemAnimationQueue, mouseOverWord

    # Boot up game
    display_surface.fill(black)
    display_surface.blit(bootText, bootRect)
    display_surface.blit(bootText2, bootRect2)
    pygame.display.update()

    # INITIAL 'GET' REQUEST TO START WRITING POEMS ON STARTUP
    if (not offlineMode):
        try:
            initialResponse = await session.get(url)
            poemAnimationQueue = list(map(lambda entry: Poem(entry["id"], entry["text"]), json.loads(initialResponse)["data"]))

            # Start animating poems if we already have poems initially
            if (len(poemAnimationQueue) != 0):
                poetryBank.append(poemAnimationQueue.pop())
                newLine = True
        except:
            offlineMode = True

    # Update poems every 10 seconds concurrently
    asyncio.gather(update_poems())

    while True:
        # Get the current editable poem words
        pronounText = interactableFont.render(" " + gamestring.getList()[0] + " ", True, green, black)
        senseText = interactableFont.render(" " + gamestring.getList()[1] + " ", True, green, black)
        nounText = interactableFont.render(" " + gamestring.getList()[3] + " ", True, green, black) 
        verbText = interactableFont.render(" " + gamestring.getList()[4] + " ", True, green, black)

        # Change whichever word is selected to have a different background
        if gamestring.select == WordSelection.pronoun:
            pronounText = interactableFont.render(" " + gamestring.getList()[0] + " ", True, black, green)
        elif gamestring.select == WordSelection.sense:
            senseText = interactableFont.render(" " + gamestring.getList()[1] + " ", True, black, green)
        elif gamestring.select == WordSelection.noun:
            nounText = interactableFont.render(" " + gamestring.getList()[3] + " ", True, black, green)
        elif gamestring.select == WordSelection.verb:
            verbText = interactableFont.render(" " + gamestring.getList()[4] + " ", True, black, green)

        # Setup text boxes for editable poem
        verbRect = verbText.get_rect()
        verbRect.center = (7 * width / 8 - verbRect.width / 2, height - 125)

        nounRect = nounText.get_rect()
        nounRect.center = (verbRect.center[0] - verbRect.width / 2 - nounRect.width / 2, height - 125)

        theRect.center = (nounRect.center[0] - nounRect.width / 2 - theRect.width / 2, height - 125)

        senRect = senseText.get_rect()
        senRect.center = (theRect.center[0] - theRect.width / 2 - senRect.width / 2, height - 125)

        proRect = pronounText.get_rect()
        proRect.center = (senRect.center[0] - senRect.width / 2 - proRect.width / 2, height - 125)

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
        display_surface.blit(creditLine, creditRect)

        # Display the editable poem
        display_surface.blit(pronounText, proRect)
        display_surface.blit(senseText, senRect)
        display_surface.blit(theText, theRect)
        display_surface.blit(nounText, nounRect)
        display_surface.blit(verbText, verbRect)

        # Display instructions/button
        if gamestring.checkForValidEntry():
            display_surface.blit(instructionTextHighlight, instructionRect)
        else:
            display_surface.blit(instructionText, instructionRect)

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
                async with lock:
                    if (len(poemAnimationQueue) != 0):
                        # Limit for poems on screen
                        if len(poetryBank) == poemLimit:
                            poetryBank.pop()

                        poetryBank.insert(0, poemAnimationQueue.pop())
                        cursor = cursorStart
                        cursorCensor = cursorCensorStart
                    else:
                        newLine = False
                
        # Update graphics
        pygame.display.update()

        # Keep track of events
        for event in pygame.event.get():

            # MOUSE
            if event.type == pygame.MOUSEMOTION:
                mouseOverWord = True

                if proRect.collidepoint(event.pos): # Select pronouns
                    if gamestring.select != WordSelection.pronoun:
                        gamestring.swapSelectedWithWordType(WordSelection.pronoun)
                elif senRect.collidepoint(event.pos): # Select senses
                    if gamestring.select != WordSelection.sense:
                        gamestring.swapSelectedWithWordType(WordSelection.sense)
                elif nounRect.collidepoint(event.pos): # Select nouns
                    if gamestring.select != WordSelection.noun:
                        gamestring.swapSelectedWithWordType(WordSelection.noun)
                elif verbRect.collidepoint(event.pos): # Select verbs
                    if gamestring.select != WordSelection.verb:
                        gamestring.swapSelectedWithWordType(WordSelection.verb)
                else: # Do not register click unless mouse is hovering over a word bank
                    mouseOverWord = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if mouseOverWord: # Cycle through selected word
                    gamestring.swapWord(True)
                elif instructionRect.collidepoint(event.pos) and gamestring.checkForValidEntry(): # Successful poem submission
                    await submit_poem()

            # KEYBOARD
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT: # Move to left word
                    gamestring.swapSelectedWithDirection(False) 
                if event.key == pygame.K_RIGHT: # Move to right word
                    gamestring.swapSelectedWithDirection(True) 
                if event.key == pygame.K_UP: # Cycle through selected bank up
                    gamestring.swapWord(True) 
                if event.key == pygame.K_DOWN: # Cycle through selected bank down
                    gamestring.swapWord(False) 
                if event.key == pygame.K_RETURN and gamestring.checkForValidEntry(): # User has successfully submitted a poem
                    await submit_poem()   

        clock.tick(30)

        await asyncio.sleep(0)

def convert_poem_to_json_format(poem):
    return { "poem": { "text": poem } }

async def submit_poem():
    global gamestring, poetryBank, poemAnimationQueue, newLine, lock, offlineMode

    poemText = " ".join(gamestring.getList())
    poemId = ""

    # Post the poem onto the database if the game is online
    if (not offlineMode):
        try:
            postMessage = await session.post(url, data=convert_poem_to_json_format(poemText))
            poemId = json.loads(postMessage)["data"]["id"]
        except:
            offlineMode = True

    # Reset Text box
    gamestring = GameString(pronouns, senses, random.sample(nouns, wordLimit), random.sample(verbs, wordLimit))

    async with lock:
        # Also will add poem to the queue if poetry bank isn't empty
        if (len(poetryBank) != 0):
            poemAnimationQueue.append(Poem(poemId, poemText))
        else:
            poetryBank.insert(0, Poem(poemId, poemText))

        # Setup animation to start adding a new line of poetry
        newLine = True        

async def update_poems():
    global poetryBank, poemAnimationQueue, newLine, lock, offlineMode

    while (not offlineMode):
        await asyncio.sleep(10)
        try:
            response = await session.get(url)

            poems = map(lambda entry: Poem(entry["id"], entry["text"]), json.loads(response)["data"])

            async with lock:
                poemAnimationQueue += list(set(poems) - set(poetryBank + poemAnimationQueue))
                newLine = True
        except:
            offlineMode = True

asyncio.run(main())