from sys import exit as sysexit
from os import environ, getcwd
import pygame
import chip8

CHIP8 = chip8.CPU()

pygame.init()
environ['SDL_VIDEO_CENTERED'] = '1'
width, height = 1280, 720
scaleMult = 12

screen = pygame.display.set_mode((width, height), pygame.HWSURFACE)
pygame.display.set_caption("CHIP-8")
clock = pygame.time.Clock()

emulationSurface = pygame.Surface((64*scaleMult, 32*scaleMult), pygame.HWSURFACE)



black, white = (0,0,0), (255,255,255)
bgcolor = (57,68,82)

mfont = pygame.font.SysFont("Calibri", 24)


keyReference = [pygame.K_1,
                pygame.K_2, pygame.K_3, pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_a, pygame.K_s, pygame.K_d, pygame.K_x, pygame.K_z, pygame.K_c, pygame.K_4, pygame.K_r, pygame.K_f, pygame.K_v]


UIbuttonsReference = [( pygame.Rect(50,450,120,50), (mfont.render("Reset ROM", True, white, black), (55, 465)) )]

def drawDebug():
    s = pygame.Surface((300, 600), pygame.HWSURFACE)
    s.fill(bgcolor)

    s.blit(mfont.render(( "PC: " + "x" + hex(CHIP8.pc)[2::].upper() ), True, white, bgcolor), (10,0))
    s.blit(mfont.render(( "Opcode: " + "x" + hex(CHIP8.opcode)[2::].upper() ), True, white, bgcolor), (10,20))
    s.blit(mfont.render(( "I: " + "x" + hex(CHIP8.I)[2::].upper() ), True, white, bgcolor), (10,40))

    for i in range(16):
        s.blit(mfont.render( ("V" + hex(i)[-1].upper() + ": " + "x" + hex(CHIP8.V[i])[2::].upper() ), True, white, bgcolor), (10, 80 + i*20))

    return s


def drawHandleUI():
    for b in UIbuttonsReference:
        pygame.draw.rect(screen, black, b[0])

        if b[1]:
            screen.blit(b[1][0], b[1][1])


ROMname = "INVADERS"
CHIP8.loadGame(getcwd() + "\\roms\\" + ROMname)

instructionAdvance = True

while True:
    activekeys = pygame.key.get_pressed()
    mousex, mousey = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sysexit()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                CHIP8.emulationCycle()
            
            elif event.key == pygame.K_p:
                instructionAdvance = not instructionAdvance

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if UIbuttonsReference[0][0].collidepoint(mousex, mousey):
                CHIP8.reInit()
                CHIP8.loadGame(getcwd() + "\\roms\\" + ROMname)


    
    
    for i in range(16):
        CHIP8.key[i] = activekeys[keyReference[i]]
        
    if not instructionAdvance:
        CHIP8.emulationCycle()

    screen.fill(bgcolor)
    emulationSurface.fill((0,0,0))

    for pixelY in range(32):
        for pixelX in range(64):
            pygame.draw.rect(emulationSurface, (black if CHIP8.gfx[(pixelY * 64) + pixelX] == 0 else white), pygame.Rect(pixelX*scaleMult, pixelY*scaleMult, scaleMult, scaleMult))
    
    screen.blit(emulationSurface, (50,50))
    screen.blit(drawDebug(), (830, 50))
    drawHandleUI()


    pygame.display.update()
    clock.tick(150)
