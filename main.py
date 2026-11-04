import pygame
import numpy as np
from numpy import pi, sin, cos, tan
import os

# Centers window
x, y = 300, 70
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x, y)

# Game presets
FPS = 60
WIDTH, HEIGHT = 1000, 600
GREY           = pygame.color.Color("#252323")
RED            = pygame.color.Color("#f83d3d")
FUSHIA         = pygame.color.Color("#ff287b")
BLUE           = pygame.color.Color("#1667fd")
GREEN          = pygame.color.Color("#50ff7b")
GREEN2         = pygame.color.Color("#1afec9")
WHITE          = pygame.color.Color("#f4f4f4")
GREYHICONT     = pygame.color.Color("#3C3C3C")
LIGHT_GREYBLUE = pygame.color.Color("#e3f8ff")
TEAL           = pygame.color.Color(28, 231, 180)
YELLOW         = (255, 211, 40)
CYAN1          = pygame.color.Color("#62aabe")
CYAN2          = pygame.color.Color("#8FC8D8")
GREY1          = pygame.color.Color("#4A4A4A")
GREY2          = pygame.color.Color("#6A6A6A")
GREY3          = pygame.color.Color("#8A8A8A")
GREY4          = pygame.color.Color("#D9D9D9")

Arr_Color = CYAN1
barCol = GREYHICONT
barBor = GREY3
BarHnd = CYAN2

BasicVecCols = [(248, 61, 61, 255), (80, 255, 123, 255), (98, 170, 190, 255), (26, 254, 201, 255), (255, 211, 40), (255, 40, 123, 255)]


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


def draw_circ(center, rad, color=YELLOW, surface=screen):
    pygame.draw.circle(surface, color, center, rad)


def draw_hex(center, side_len, grid=True, color=YELLOW, surface=screen, thickness = 4, bvc=BasicVecCols):
    deltaY = int(side_len * np.sqrt(3)/2) # cos(30)
    deltaX = int(side_len/2) # sin(30)

    top_L  = (center[0] - deltaX, center[1]-deltaY)
    top_R  = (center[0] + deltaX, center[1]-deltaY)
    side_R = (center[0] + side_len, center[1])
    side_L = (center[0] - side_len, center[1])
    bott_L = (center[0] - deltaX, center[1]+deltaY)
    bott_R = (center[0] + deltaX, center[1]+deltaY)


    draw_circ(center, thickness)

    # vertices = [top_L, top_R, side_R, bott_R, 
    #             bott_L, side_L]
    vertices = [side_R, top_R, top_L, side_L, 
                bott_L, bott_R]
    pygame.draw.polygon(surface, color, vertices, width=thickness)
    
    if grid is True:
        for ind in range(6):
            pygame.draw.aaline(surface, bvc[ind], center, vertices[ind])
    
    return vertices


def draw_arrow(start, maxend, slide_value, thickness=4, color=RED):
    
    # end = maxend[0]*slide_value, maxend[1]*slide_value
    dx = maxend[0] - start[0]
    dy = maxend[1] - start[1]
    
    length = np.hypot(dx, dy)
    ux = dx/length
    uy = dy/length

    end = start[0] + dx*slide_value, start[1] + dy*slide_value

    if length <= 1:
        return

    head_length = max(10, min(40, length*slide_value * 0.22))
    head_width = max(8, min(30, head_length * slide_value*0.7))

    base = (end[0] - ux * head_length, end[1] - uy * head_length)
    left = (base[0] - uy * head_width / 2, base[1] + ux * head_width / 2)
    right = (base[0] + uy * head_width / 2, base[1] - ux * head_width / 2)

    pygame.draw.line(screen, color, start, base, thickness)
    pygame.draw.polygon(screen, color, [end, left, right])

    angle = np.arctan2(-uy, ux)
    if angle < 0:
        angle += 2 * np.pi
    return angle

def simSPVM(svmAngle, DutyCycle):
    sectors   = ["V_1", "V_2", "V_3", "V_4", "V_5", "V_6"]
    ind      = (svmAngle/ (pi/3)) % 6
    ind_up   = int(np.ceil(ind)) # cloest CCW vector
    ind_down = int(ind) # closest CW vector
    # print("--------------")
    # print(f"ind = {ind}")

    # fraction to each phase
    phDown = round((abs(ind_up-ind))*100, 1)
    phUp   = round((abs(ind_down-ind))*100, 1)
    if ind_down == ind_up:
        phDown = 100
        phUp   = 0

    # print(f"Active sectors:\nPhase {sectors[ind_down%6]}: {phDown}%\nPhase {sectors[ind_up%6]}: {phUp}%")
    # print("---------------------------")

    vec1 = (ind_down%6)+1, phDown
    vec2 = (ind_up%6)+1, phUp

    # Compute T1 T2 and T0 relative to T
    T1 = phDown*DutyCycle
    T2 = phUp*DutyCycle
    T0 = 100 - T1 - T2


    return [T1, T2, T0]



def T123toTabc_PWM(T1, T2, T0, sector):
    '''
    sector: is given by svmAngle/60 mod 6 so it is a number between 0 to 5
    '''
    Ta,Tb,Tc = 0, 0, 0
    match sector:
        case 0:
            Ta = T1+T2+T0/2
            Tb = T2+T0/2
            Tc = T0/2
        case 1:
            Ta = T1+T0/2
            Tb = T1+T2+T0/2
            Tc = T0/2
        case 2:
            Ta = T0/2
            Tb = T1+T2+T0/2
            Tc = T2+T0/2
        case 3:
            Ta = T0/2
            Tb = T1+T0/2
            Tc = T1+T2+T0/2
        case 4:
            Ta = T2+T0/2
            Tb = T0/2
            Tc = T1+T2+T0/2
        case 5:
            Ta = T1+T2+T0/2
            Tb = T0/2
            Tc = T1+T0/2
        case _:
            print("invalid Sector input - sector is an int b/w 0 to 5")
    # print(f"Ta={Ta}, Tb={Tb}, Tc={Tc}")
    return [Ta,Tb,Tc]



def square_pulse(center, activeRatio, Tot_width=150, height = 50, 
                 surface=screen, color=TEAL, thickness=3, double=False):
    X, Y = center
    T_width = 2*Tot_width if double else Tot_width
    HW = T_width//2
    PulseWidth = T_width*activeRatio
    # flap_width = (T_width-PulseWidth)//2

    flapL_start = X-HW, Y+height
    flapL_end   = X-PulseWidth//2, Y+height

    pulse_start = X-PulseWidth//2, Y
    pulse_end   = X+PulseWidth//2, Y

    flapR_start = X+PulseWidth//2, Y+height
    flapR_end   = X+HW, Y+height

    vertices = [flapL_start, flapL_end,
                pulse_start, pulse_end,
                flapR_start, flapR_end
    ]

    pygame.draw.lines(surface, color, False, vertices, thickness)


def slideBar(anch, length, slideval, 
             thickness=10, bar_color=barCol, hand_color=BarHnd, border_color=barBor):

    end_pos = (anch[0]+length, anch[1])
    pygame.draw.line(screen, border_color,(anch[0]-2, anch[1]), (end_pos[0]+2, anch[1]), thickness+4)
    pygame.draw.line(screen, bar_color, anch, end_pos, thickness)

    # drawing the handle
    base_left  = (anch[0] + length*slideval-thickness//1.4, anch[1]-thickness//1.4) 
    base_right = (anch[0] + length*slideval+thickness//1.4, anch[1]-thickness//1.4) 
    bottom_tip = (anch[0] + length*slideval, anch[1]+thickness//2)
    invTriVerts = [base_left, base_right, bottom_tip]

    pygame.draw.polygon(screen, hand_color, invTriVerts)



hex_center = [WIDTH//5, HEIGHT // 2]
hex_sidelength = 150
arrow_start = hex_center
pulse_center1 = [WIDTH*3//6, HEIGHT//6]
pulse_center2 = [WIDTH*3//6, HEIGHT*3// 6]
pulse_center3 = [WIDTH*3//6, HEIGHT*5//6]
PWM_center1 = [WIDTH*5//6, HEIGHT//6]
PWM_center2 = [WIDTH*5//6, HEIGHT*3// 6]
PWM_center3 = [WIDTH*5//6, HEIGHT*5//6]
arrow_length = hex_sidelength-20
arrow_end = [arrow_start[0] + arrow_length, arrow_start[1]]
dragging = False


#slide bar settings
LockRef = True
DutyCycle = 0.5
barlen = hex_sidelength*2
baranc = (hex_center[0]-barlen//2, hex_center[1]+hex_sidelength+30)
barthic = 10

Theta = 0


while True:
    screen.fill(GREY)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            quit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            dragging = False
            
    # Rotating Space Vector
    mouse_pos = pygame.mouse.get_pos()
    mpos = np.array(mouse_pos)
    hc   = np.array(hex_center)
    if dragging and (np.linalg.norm(hc-mpos) < arrow_length+10):
        dx = mouse_pos[0] - arrow_start[0]
        dy = mouse_pos[1] - arrow_start[1]
        dist = np.hypot(dx, dy)

        if dist > 0: # normalize
            arrow_end = [
                arrow_start[0] + (dx / dist) * arrow_length,
                arrow_start[1] + (dy / dist) * arrow_length,
            ]
    # Sliding Reference bar
    if dragging:
        mposx, mposy = mouse_pos[0], mouse_pos[1]
        base_left  = (baranc[0] + barlen*DutyCycle-barthic//1.5, baranc[1]-barthic//1.5) 
        base_right = (baranc[0] + barlen*DutyCycle+barthic//1.5, baranc[1]-barthic//1.5) 
        bottom_tip = (baranc[0] + barlen*DutyCycle, baranc[1]+barthic//2)
        
        between_x = (mposx > baranc[0]) and (mposx < baranc[0]+barlen+30)
        between_y = (mposy > base_left[1]-barthic) and (mposy < bottom_tip[1]+barthic)

        if between_y and between_x:
            value_raw = (mouse_pos[0] - baranc[0])/barlen
            # clamp if beyong thresholds
            if value_raw > 1:
                DutyCycle = 1
            elif value_raw < 0.1:
                DutyCycle = 0.1
            else: DutyCycle = value_raw


    # Implement GUI here

    draw_hex(hex_center, hex_sidelength)


    arrow_start
    
    
    svmAngle = draw_arrow(arrow_start, arrow_end, DutyCycle, color=(30, 200, 200))
    SPVM_Vectors = simSPVM(svmAngle, DutyCycle)
    slideBar(baranc, barlen, DutyCycle, thickness=barthic)
    # print(f"slideVal = {slide_value}")
    # print(SPVM_Vectors)
    T1 = SPVM_Vectors[0]
    T2 = SPVM_Vectors[1]
    T0 = SPVM_Vectors[2]
    
    # square_pulse(pulse_center1,T1/100)
    # square_pulse(pulse_center2,T2/100, color=RED)
    # square_pulse(pulse_center3,T0/100, color=GREEN)
    
    sector = (svmAngle/ (pi/3)) % 6
    Ta,Tb,Tc = T123toTabc_PWM(T1, T2, T0, int(sector))
    
    square_pulse(PWM_center1,Ta/100, color=BLUE , double=True)
    square_pulse(PWM_center2,Tb/100, color=RED  , double=True)
    square_pulse(PWM_center3,Tc/100, color=GREEN, double=True)
    
    pygame.draw.line(screen, GREY4, (PWM_center1[0], PWM_center1[1]-40), 
                    (PWM_center3[0], PWM_center3[1]+60), width=3)

    # pygame.draw.line(screen, color=GREY3, )








    # plot time contribution of each basic space vector
    BasicVectors = {
        0:[0, RED], 1:[0, GREEN], 2:[0, CYAN1],
        3:[0, GREEN2],4:[0, YELLOW],5:[0, FUSHIA],
    }
    VecUP   = (int(sector)+1) % 6
    VecDOWN = (int(sector)%6)

    BasicVectors[VecDOWN][0] = T1
    BasicVectors[VecUP][0] = T2

    for basicVecor in range(6):
        contrib_value = BasicVectors[basicVecor][0]
        c = BasicVectors[basicVecor][1]
        h = 80
        pulse_center = [WIDTH//2, HEIGHT//6 + h*basicVecor]
        square_pulse(pulse_center,contrib_value/100, height=30, color=c)



    pygame.display.update()
    clock.tick(FPS)
