##  GHOST OF A CODED MIND
##
## A game for Dreamscapes.
## A user can insert "dreams" (poems) into a computer, which will be typed onto the display.
## Represents an old 90s terminal.
##
## Authors: Nami Eskandarian & Joseph Norton
## Version: 1.0

import copy
from multiprocessing.connection import wait
import sys, pygame, random
from time import sleep
from enum import Enum
pygame.init()

# Enum class to denote which word is selected
class WordSelection(Enum):
    pronoun = 1
    sense = 2
    noun = 3
    verb = 4

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
        self.nouns.insert(0, "[Noun]")
        self.verbs.insert(0, "[Verb]")

        # Current index of each bank
        self.pronounIndex = 0
        self.senseIndex = 0
        self.nounIndex = 0
        self.verbIndex = 0

    # Method to swap selected type of word
    def swapSelected(self, right):
        if right == 1:
            match self.select:
                case WordSelection.pronoun:
                    self.select = WordSelection.sense
                    return
                case WordSelection.sense:
                    self.select = WordSelection.noun
                    return
                case WordSelection.noun:
                    self.select = WordSelection.verb
                    return
                case WordSelection.verb:
                    self.select = WordSelection.pronoun
                    return
        else:
            match self.select:
                case WordSelection.pronoun:
                    self.select = WordSelection.verb
                    return
                case WordSelection.sense:
                    self.select = WordSelection.pronoun
                    return
                case WordSelection.noun:
                    self.select = WordSelection.sense
                    return
                case WordSelection.verb:
                    self.select = WordSelection.noun
                    return

    # Method to swap word based on selection
    def swapWord(self, up):
        if up:
            match self.select:
                case WordSelection.pronoun:
                    if self.pronounIndex == len(self.pronouns) - 1:
                        self.pronounIndex = 1
                    else:
                        self.pronounIndex += 1
                    return
                case WordSelection.sense:
                    if self.senseIndex == len(self.senses) - 1:
                        self.senseIndex = 1
                    else:
                        self.senseIndex += 1
                    return
                case WordSelection.noun:
                    if self.nounIndex == len(self.nouns) - 1:
                        self.nounIndex = 1
                    else:
                        self.nounIndex += 1
                    return
                case WordSelection.verb:
                    if self.verbIndex == len(self.verbs) - 1:
                        self.verbIndex = 1
                    else:
                        self.verbIndex += 1
                    return
        else:
            match self.select:
                case WordSelection.pronoun:
                    if self.pronounIndex == 1:
                        self.pronounIndex = len(self.pronouns) - 1
                    else:
                        self.pronounIndex -= 1
                    return
                case WordSelection.sense:
                    if self.senseIndex == 1:
                        self.senseIndex = len(self.senses) - 1
                    else:
                        self.senseIndex -= 1
                    return
                case WordSelection.noun:
                    if self.nounIndex == 1:
                        self.nounIndex = len(self.nouns) - 1
                    else:
                        self.nounIndex -= 1
                    return
                case WordSelection.verb:
                    if self.verbIndex == 1:
                        self.verbIndex = len(self.verbs) - 1
                    else:
                        self.verbIndex -= 1
                    return

    # Returns a list of selected words
    def getList(self):
        retVal = [self.pronouns[self.pronounIndex], self.senses[self.senseIndex], "The", self.nouns[self.nounIndex], self.verbs[self.verbIndex]]
        return retVal


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
size = width, height
display_surface = pygame.display.set_mode((width, height))
pygame.display.set_caption('Ghost of a Coded Mind')
# pygame.display.toggle_fullscreen()

# Format of the poem
# PRONOUNS SENSES "The" NOUNS VERBS

# Import words from text files

file = open("Pronoun Wordbank.txt")
pronouns = file.read().split("\n")
pronouns[0] = "[Pronoun]"
file.close()

file = open("Senses Wordbank.txt")
senses = file.read().split("\n")
senses[0] = "[Sense]"
file.close()

the = "The"

file = open("Noun Wordbank.txt")
nouns = file.read().split("\n")
nouns[0] = "[Noun]"
file.close()

file = open("Verb Wordbank.txt")
verbs = file.read().split("\n")
for i in range(len(verbs)):
    verbs[i] = verbs[i].strip().capitalize()
verbs[0] = "[Verb]"
file.close()

# Setup font for terminal
font = pygame.font.Font('ModernDOS9x16.ttf', 32)

# Create text for instructions
instructionText = font.render("INSERT DREAM...", True, green, black)
instructionRect = instructionText.get_rect()
instructionRect.center = (width / 6 + instructionRect.width / 2, height - 150)

# Create text for title
title = ("  ________.__                    __            _____           _________            .___         .___    _____  .__            .___", " /  _____/|  |__   ____  _______/  |_    _____/ ____\ _____    \_   ___ \  ____   __| _/____   __| _/   /     \ |__| ____    __| _/", "/   \  ___|  |  \ /  _ \/  ___/\   __\  /  _ \   __\  \__  \   /    \  \/ /  _ \ / __ |/ __ \ / __ |   /  \ /  \|  |/    \  / __ | ", "\    \_\  \   Y  (  <_> )___ \  |  |   (  <_> )  |     / __ \_ \     \___(  <_> ) /_/ \  ___// /_/ |  /    Y    \  |   |  \/ /_/ | ", " \______  /___|  /\____/____  > |__|    \____/|__|    (____  /  \______  /\____/\____ |\___  >____ |  \____|__  /__|___|  /\____ | ", "        \/     \/           \/                             \/          \/            \/    \/     \/          \/        \/      \/ ")
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

titleRect1.center = (width / 2, 100)
titleRect2.center = (width / 2, 100 + 16)
titleRect3.center = (width / 2, 100 + 32)
titleRect4.center = (width / 2, 100 + 48)
titleRect5.center = (width / 2, 100 + 64)
titleRect6.center = (width / 2, 100 + 80)
lineRectTop.center = (width / 2, 100 + 96)
lineRectBot.center = (width / 2, height - 200)

# Last setups before loop:
poetryBank = list() # List of recorded poems
newLine = False # Flag for cursor animation
gamestring = GameString(pronouns, senses, random.sample(nouns, wordLimit), random.sample(verbs, wordLimit)) # Current editable poem
theText = font.render(" The ", True, green, black) # Render "The" part of each poem

while 1:
    # Get the current editable poem words
    pronounText = font.render(" " + gamestring.getList()[0].capitalize() + " ", True, green, black)
    senseText = font.render(" " + gamestring.getList()[1].capitalize() + " ", True, green, black)
    nounText = font.render(" " + gamestring.getList()[3].capitalize() + " ", True, green, black)
    verbText = font.render(" " + gamestring.getList()[4].capitalize() + " ", True, green, black)

    # Change whichever word is selected to have a different background
    match gamestring.select:
        case WordSelection.pronoun:
                pronounText = font.render(" " + gamestring.getList()[0].capitalize() + " ", True, black, green)
        case WordSelection.sense:
                senseText = font.render(" " + gamestring.getList()[1].capitalize() + " ", True, black, green)
        case WordSelection.noun:
                nounText = font.render(" " + gamestring.getList()[3].capitalize() + " ", True, black, green)
        case WordSelection.verb:
                verbText = font.render(" " + gamestring.getList()[4].capitalize() + " ", True, black, green)

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

    # Display the editable poem
    display_surface.blit(pronounText, proRect)
    display_surface.blit(senseText, senRect)
    display_surface.blit(theText, theRect)
    display_surface.blit(nounText, nounRect)
    display_surface.blit(verbText, verbRect)

    # Display all recorded poems
    for i in range(len(poetryBank)):
        text = font.render("<: " + poetryBank[i], True, green, black)
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
        
        # Otherwise, end the animation
        else:
            newLine = False
        
    # Keep track of events
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                gamestring.swapSelected(False) # Move to left word
            if event.key == pygame.K_RIGHT:
                gamestring.swapSelected(True) # Move to right word
            if event.key == pygame.K_UP:
                gamestring.swapWord(True) # Go through selected bank up
            if event.key == pygame.K_DOWN:
                gamestring.swapWord(False) # Go through selected bank down
            if event.key == pygame.K_e and gamestring.pronounIndex != 0 and gamestring.nounIndex != 0 and gamestring.senseIndex != 0 and gamestring.verbIndex != 0:
                # If this event is reached, the user has successfully submitted a poem
                
                # Limit for poems on screen
                if len(poetryBank) == poemLimit:
                    poetryBank.pop()

                # Insert poem into the bank
                poetryBank.insert(0, " ".join(gamestring.getList()))

                # Reset Text box
                gamestring = GameString(pronouns, senses, random.sample(nouns, wordLimit), random.sample(verbs, wordLimit))
            
                # Setup cursor for animation to play
                cursor = pygame.Rect(width / 6, height / 4 - 17, 24, 32)
                cursorCensor = pygame.Rect(width / 6 + 24, height / 4 - 17, 1000, 32)
                newLine = True

    # Update graphics
    pygame.display.update()
