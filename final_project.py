from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time
# Camera
c_angle=0
c_height=120
c_radius=400
c_track=True
fovY =80
GRID_LENGTH=800
# Submarine
s_pos=[0.0, 0.0, 60.0]
s_angle=0.0
s_speed=4.0
gun_ang=0.0
headlght_on=True
invincible_frame=0
invincible_dr=60

# Bullets
bullets=[]
bullet_speed=12.0

# Enemies
enemy_id=0
enemy=[]

# Collectibles
collectibles=[]

# HUD
score =0
coins=100
lives=3
oxygen=100.0
oxygen_drain=0.08
level=1
game_over=False
game_win = False
pause = False
cheat_mode = False

# Treasure
treasure_position= [3000.0,0.0,30.0]
treasure_got = False

# Waypoints
w_points = [[ 600.0,80.0, 30.0],[1200.0,-120.0,30.0],[1800.0,100.0,30.0],[2400.0,-80.0,30.0],[3000.0,0.0,30.0]]
current_wpoint=0

# Timing
last_time=time.time()
frame=0
enemy_time=0
collectible_time=0
last_enemy_x=0
enemy_interval=300

# Seabed decorations
seabed_item =[]

# Cheat Mode
cheat_mode_on= False
cheat_cost= 100
target_num = -1
fire_interval= 0

# Challenging Mode
challenging_mode_on=False
jelly_fish=[]
j_fish_life=180
j_fish_interval=45
j_enemy_timer=0
ambient_lght=1.0
lght_dirct=-0.00005
collisions={}
big_fish = None
big_fish_timer = 0
big_fish_interval = 500
bigfish_warning = 0
offset = 0.0
waves = []
def initiate_seabed():
    random.seed(42)
    for _ in range(80):
        item=random.choice(['rock','coral','plant'])
        x =random.uniform(-GRID_LENGTH+50, GRID_LENGTH-50)
        y =random.uniform(-GRID_LENGTH+50, GRID_LENGTH-50)
        s =random.uniform(0.5, 2.0)
        if item =='rock':
            c =(random.uniform(0.35,0.55), random.uniform(0.33,0.45), random.uniform(0.28,0.38))
        elif item =='coral':
            c = (random.uniform(0.7,1.0), random.uniform(0.2,0.5), random.uniform(0.2,0.5))
        else:
            c = (0.0, random.uniform(0.5,0.9), random.uniform(0.2,0.5))
        seabed_item.append({'type':item,'pos':(x,y,0),'scale':s,'color':c, 'id':_})

def initiate_collectibles():
    global collectibles
    collectibles=[]
    offsets = [(-200, -100),(300,-250),(-350,200),(100,-400),(450,-150),(-100,350),(200,300),(-300, -300)]
    types = ['oxygen','oxygen','life','coin_bonus','oxygen','life','coin_bonus','oxygen']
    for i, (x,y) in enumerate(offsets):
        collectibles.append({'type': types[i % len(types)],'pos':[s_pos[0]+x,s_pos[1]+y,0.0],'collected': False})

def collectibles_forward():
    fw_radius=math.radians(s_angle)
    fx =math.cos(fw_radius)
    fy =math.sin(fw_radius)
    px =-fy
    py =fx
    types =['oxygen', 'life', 'oxygen', 'coin_bonus', 'life', 'oxygen']
    for i, t in enumerate(types):
        distance=random.uniform(150, 500)
        spread =random.uniform(-200, 200)
        cx = s_pos[0]+fx*distance+ px*spread
        cy = s_pos[1]+fy*distance + py*spread
        collectibles.append({'type': t,'pos':  [cx, cy, 0.0],'collected': False})
def initiate_enemies():
    global enemy_id,enemy,last_enemy_x
    enemy =[]
    enemy_id =0
    last_enemy_x =s_pos[0]
    base_speed =0.5 +(level - 1)*0.09
    sub_z =s_pos[2]
    for i in range(2):
        fw =random.uniform(400,900)
        side=random.uniform(-200,200)
        add_enemy('shark',[s_pos[0]+fw,s_pos[1]+side,sub_z + random.uniform(-20,20)],base_speed)

    for i in range(3):
        fw =random.uniform(600, 1100)
        side= random.uniform(-150, 150)
        add_enemy('sub', [s_pos[0]+fw, s_pos[1]+side,sub_z +random.uniform(-15,15)], base_speed)

    for i in range(4 + level):
        fw =random.uniform(200,800)
        side  = random.uniform(-300,300)
        add_enemy('coral',[s_pos[0]+fw, s_pos[1]+side, 0.0],0)

def enemy_forward():
    global last_enemy_x
    last_enemy_x = s_pos[0]
    base_speed = 0.5 +(level - 1) * 0.09
    fd_radius = math.radians(s_angle)
    fx= math.cos(fd_radius)
    fy= math.sin(fd_radius)
    px =-fy
    py = fx
    subz =s_pos[2]

    for i in range(2 + level // 2):
        distance= random.uniform(500, 800)
        spread = random.uniform(-200, 200)
        ex = s_pos[0] + fx*distance + px*spread
        ey = s_pos[1] + fy*distance + py*spread
        add_enemy('shark', [ex, ey, subz + random.uniform(-20,20)],base_speed)

    distance=random.uniform(700,1000)
    spread = random.uniform(-100,100)
    ex = s_pos[0] + fx*distance + px*spread
    ey = s_pos[1] + fy*distance + py*spread
    add_enemy('sub', [ex, ey,subz + random.uniform(-15,15)], base_speed *0.6)

    for i in range(2):
        distance= random.uniform(300, 600)
        spread =random.uniform(-250, 250)
        ex = s_pos[0] + fx*distance + px*spread
        ey = s_pos[1] + fy*distance + py*spread
        add_enemy('coral', [ex, ey, 0.0], 0.0)

    collectibles_forward()

def add_enemy(etype,position, speed):
    global enemy_id
    enemy.append({'id':enemy_id,'type':etype,'pos':list(position),'speed':speed,'health': 1 if etype != 'sub' else 2,'dead':False,'anim':random.uniform(0, 360)})
    enemy_id += 1

def draw_text(x, y,text,color=(1,1,1)):
    glDisable(GL_DEPTH_TEST)
    glColor3f(*color)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0,1000, 0,800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)

def set_color(r,g,b,a=1.0):
    glColor4f(r,g,b,a)

def draw_coral():
    q = gluNewQuadric()
    # stalk
    glPushMatrix()
    gluCylinder(q, 5, 3, 35, 8, 4)
    # Branch 1
    glPushMatrix()
    glTranslatef(0, 0, 15)
    glRotatef(45, 1, 0.5, 0)
    gluCylinder(q, 3, 1, 20, 6, 4)
    glTranslatef(0, 0, 20)
    glutSolidSphere(2, 6, 6)
    glPopMatrix()
    # Branch 2
    glPushMatrix()
    glTranslatef(0, 0, 22)
    glRotatef(-40, 0.3, 1, 0)
    gluCylinder(q, 2.5, 1, 18, 6, 4)
    glTranslatef(0, 0, 18)
    glutSolidSphere(2, 6, 6)
    glPopMatrix()
    # Branch 3
    glPushMatrix()
    glTranslatef(0, 0, 10)
    glRotatef(60, -0.5, -1, 0)
    gluCylinder(q, 2, 0.8, 15, 5, 3)
    glPopMatrix()
    glPopMatrix()

def draw_plant():
    q =gluNewQuadric()
    glColor3f(0.0, 0.7, 0.35)
    for i in range(3):
        glPushMatrix()
        glRotatef(i * 120, 0, 0, 1)
        glRotatef(-20, 1, 0, 0)
        gluCylinder(q, 2, 0.5, 35, 5, 4)
        glPopMatrix()
def initiate_bigfish():
    global big_fish,bigfish_warning
    if big_fish is not None:
        return
    angle =random.uniform(0, 360)
    radian = math.radians(angle)
    distance = random.uniform(600, 900)
    gx =s_pos[0] + math.cos(radian) * distance
    gy =s_pos[1] + math.sin(radian) * distance
    gz =s_pos[2] + random.uniform(-30, 50)
    big_fish = {'pos': [gx, gy, gz],'anim': angle + 180, 'speed': 1.5 + level * 0.3,'health': 5,'dead': False,'rage': False,'jaw_open': 0.0,'jaw_dir': 1,'tail_wave': 0.0,'bite_cooldown': 0,}
    bigfish_warning=180
    print("!!! A GIANT FISH HAS APPEARED !!!")

def update_big_fish():
    global big_fish, big_fish_timer, bigfish_warning, score, coins, lives, invincible_frame
    big_fish_timer += 1
    if bigfish_warning > 0:
        bigfish_warning -= 1

    if big_fish is None:
        if big_fish_timer >= big_fish_interval:
            big_fish_timer = 0
            if random.random() < 0.8:
                initiate_bigfish()

        return

    giantfish = big_fish
    if giantfish['dead']:
        giantfish['anim'] +=1
        if frame % 120 == 0:
            big_fish = None
            big_fish_timer = 0
        return

    giantfish['jaw_open'] += 0.05*giantfish['jaw_dir']
    if giantfish['jaw_open'] >= 1.0: giantfish['jaw_dir'] = -1
    elif giantfish['jaw_open'] <= 0.0: giantfish['jaw_dir'] = 1
    giantfish['tail_wave'] =(giantfish['tail_wave'] + 4) % 360

    dx =s_pos[0] -giantfish['pos'][0]
    dy =s_pos[1] -giantfish['pos'][1]
    dz =s_pos[2] -giantfish['pos'][2]
    dist = math.sqrt(dx*dx + dy*dy + dz*dz) + 0.001
    speed = giantfish['speed'] * (1.5 if giantfish['rage'] else 1.0)
    giantfish['pos'][0] += (dx/dist)*speed
    giantfish['pos'][1] += (dy/dist)*speed
    giantfish['pos'][2] += (dz/dist)*speed*0.4
    giantfish['anim'] = math.degrees(math.atan2(dy,dx))

    if giantfish['health'] <=2: giantfish['rage'] = True

    if dist < 60 and not cheat_mode and invincible_frame == 0:
        if giantfish['bite_cooldown'] <= 0:
            coins = max(0, coins - 20)
            invincible_frame = invincible_dr
            giantfish['bite_cooldown'] = 90
            print("Giant fish bit you! -20 coins!")
    if giantfish['bite_cooldown'] > 0: giantfish['bite_cooldown'] -= 1

    for b in bullets[:]:
        b_position = b['pos']
        gp = giantfish['pos']
        if abs(b_position[0]-gp[0]) < 60 and abs(b_position[1]-gp[1]) < 60 and abs(b_position[2]-gp[2]) < 60:
            giantfish['health'] -= 2 if cheat_mode_on else 1
            if b in bullets: bullets.remove(b)
            if giantfish['health'] <= 0:
                giantfish['dead'] = True
                score += 200
                coins += 200
                print("Giant fish defeated! +200 coins!")
            break


def draw_big_fish():
    if big_fish is None: return
    gf =big_fish
    glPushMatrix()
    glTranslatef(*gf['pos'])
    glRotatef(gf['anim'], 0, 0, 1)
    glScalef(0.5, 0.5, 0.5)
    if gf['dead']: glColor3f(0.5, 0.5, 0.5)
    elif gf['rage']: glColor3f(0.9, 0.25, 0.1)
    else: glColor3f(0.1, 0.45, 0.6)
    glPushMatrix()
    glScalef(4.0, 1.5, 1.3)
    glutSolidSphere(40, 16, 12)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(155, 0, 0)
    glScalef(1.2, 1.0, 0.9)
    if gf['rage']: glColor3f(1.0, 0.3, 0.1)
    else: glColor3f(0.08, 0.38, 0.52)
    glutSolidSphere(32, 14, 10)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(175, 0, 10)
    glRotatef(gf['jaw_open'] * 25, 0, 1, 0)
    glColor3f(0.8, 0.2, 0.15)
    glScalef(1.2, 0.7, 0.4)
    glutSolidSphere(22, 10, 6)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(175, 0, -10)
    glRotatef(-gf['jaw_open'] * 20, 0, 1, 0)
    glColor3f(0.75, 0.18, 0.12)
    glScalef(1.2, 0.7, 0.35)
    glutSolidSphere(20, 10, 6)
    glPopMatrix()
    glColor3f(0.95, 0.95, 0.9)
    for i in range(5):
        rad_t = math.radians((i-2)*18.0)
        glPushMatrix()
        glTranslatef(185+math.cos(rad_t)*5, 0, math.sin(rad_t)*20+gf['jaw_open']*12)
        glScalef(0.4, 0.3, 1.0)
        glutSolidCone(5, 14, 6, 3)
        glPopMatrix()
    if gf['rage']: glColor3f(1.0, 0.15, 0.0)
    else: glColor3f(0.05, 0.30, 0.45)
    glPushMatrix()
    glTranslatef(20, 0, 50)
    glRotatef(90, 1, 0, 0)
    glutSolidCone(20, 55, 8, 4)
    glPopMatrix()
    for side in [1, -1]:
        glPushMatrix()
        glTranslatef(50, side * 60, 0)
        glScalef(0.8, 2.5, 0.25)
        glutSolidSphere(20, 8, 6)
        glPopMatrix()
    glPushMatrix()
    glTranslatef(-160, 0, 0)
    glRotatef(math.sin(math.radians(gf['tail_wave'])) * 30, 0, 0, 1)
    if gf['rage']: glColor3f(0.95, 0.2, 0.05)
    else: glColor3f(0.07, 0.35, 0.50)
    glPushMatrix()
    glRotatef(30, 0, 1, 0)
    glScalef(0.3, 0.7, 1.8)
    glutSolidSphere(35, 10, 8)
    glPopMatrix()
    glPushMatrix()
    glRotatef(-30, 0, 1, 0)
    glScalef(0.3, 0.7, 1.4)
    glutSolidSphere(28, 10, 8)
    glPopMatrix()
    glPopMatrix()
    glPushMatrix()
    glTranslatef(150, 25, 18)
    glColor3f(0.9, 0.1, 0.0)
    glutSolidSphere(8, 8, 8)
    glColor3f(0.0, 0.0, 0.0)
    glTranslatef(4, 0, 0)
    glutSolidSphere(4, 6, 6)
    glPopMatrix()
    if gf['rage'] and not gf['dead']:
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        pulse_r = 0.5 + 0.3 *abs(math.sin(math.radians(frame * 8)))
        glColor4f(1.0, 0.1, 0.0,pulse_r * 0.25)
        glScalef(4.5, 1.8, 1.5)
        glutSolidSphere(40, 12, 10)
        glDisable(GL_BLEND)
    glPopMatrix()

def big_fish_warning():
    if bigfish_warning <= 0: return
    pulsate = abs(math.sin(math.radians(frame * 10)))
    if pulsate > 0.5:
        draw_text(300, 450, "!!! GIANT FISH APPROACHING !!!", color=(1.0, 0.2, 0.0))
        draw_text(340, 425, "PREPARE TO DEFEND!", color=(1.0, 0.6, 0.0))


wave_z =200
wave_parts=40
w_width=2000

def draw_ocean_waves():
    t = frame *0.04
    h_width = w_width // 2
    step= w_width //wave_parts
    cx,cy = s_pos[0], s_pos[1]
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    for row in range(wave_parts):
        for col in range(wave_parts):
            x0 = cx - h_width + col*step
            x1 = x0 + step
            y0 = cy - h_width + row*step
            y1 = y0 + step
            def wz(wx,wy):
                return wave_z + 18*math.sin(wx*0.008+t*1.3) + 12*math.sin(wy*0.010+t*0.9+1.2) + \
                       7*math.sin((wx+wy)*0.006+t*1.7) + 5*math.cos(wx*0.013-wy*0.009+t*2.1) + 10*math.sin(t*0.5)
            z00, z10, z11, z01 = wz(x0, y0),wz(x1, y0), wz(x1, y1), wz(x0, y1)
            nx = (z10 - z00) /step
            ny = (z01 - z00) /step
            nm = math.sqrt(nx*nx + ny*ny + 1)
            light = max(0.4, min(1.0, 0.7 + ny/nm*0.5))
            avg_z = (z00 + z10 + z11 + z01) / 4
            is_up = avg_z > wave_z + 15
            if is_up: glColor4f(light*0.7+0.3,light*0.85+0.1,light*0.9+0.1,0.95)
            else: glColor4f(light*0.05,light*0.38+0.05,light*0.72+0.10, 0.85)
            glBegin(GL_QUADS)
            glVertex3f(x0, y0, z00)
            glVertex3f(x1, y0, z10)
            glVertex3f(x1, y1, z11)
            glVertex3f(x0, y1, z01)
            glEnd()
            if is_up:
                glColor4f(1.0, 1.0, 1.0, 0.9)
                glLineWidth(1.5)
                glBegin(GL_LINE_LOOP)
                glVertex3f(x0, y0, z00 + 2)
                glVertex3f(x1, y0, z10 + 2)
                glVertex3f(x1, y1, z11 + 2)
                glVertex3f(x0, y1, z01 + 2)
                glEnd()
    glDisable(GL_BLEND)

def draw_wave_caustics():
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    t = frame * 0.03
    for i in range(12):
        rad = math.radians(i*30.0 + t*20)
        cx2, cy2 = s_pos[0]+math.cos(rad)*200,s_pos[1]+math.sin(rad)*200
        r, alpha = 40+20*math.sin(t*1.5+i), 0.06+0.04*math.sin(t*2.2+i*0.7)
        glColor4f(0.5, 0.85, 1.0,alpha)
        glPushMatrix()
        glTranslatef(cx2,cy2,2)
        glScalef(1.0, 0.5, 1.0)
        gluDisk(gluNewQuadric(), 0, r, 12, 2)
        glPopMatrix()
    glDisable(GL_BLEND)

def draw_seabed():
    tile = GRID_LENGTH * 2
    tx = int(math.floor(s_pos[0] /tile))
    ty = int(math.floor(s_pos[1] /tile))
    glColor3f(0.76, 0.65, 0.40)
    glBegin(GL_QUADS)
    for x in range(-1, 2):
        for y in range(-1, 2):
            bx = (tx + x) * tile
            by = (ty + y) * tile
            glVertex3f(bx,by,0)
            glVertex3f(bx + tile,by,0)
            glVertex3f(bx + tile,by + tile,0)
            glVertex3f(bx,by + tile,0)
    glEnd()
    for d in seabed_item:
        dx_raw =d['pos'][0]
        dy_raw =d['pos'][1]
        nearest_tx =round((s_pos[0] - dx_raw) /tile)
        nearest_ty =round((s_pos[1] - dy_raw) /tile)
        wx =dx_raw + nearest_tx * tile
        wy =dy_raw + nearest_ty * tile
        glPushMatrix()
        glTranslatef(wx, wy, 0)
        glScalef(d['scale'],d['scale'],d['scale'])
        glColor3f(*d['color'])
        t = d['type']
        if t =='rock':
            glutSolidSphere(15, 8, 8)
        elif t == 'coral':
            draw_coral()
        else:
            draw_plant()
        glPopMatrix()

def draw_submarine(px,py,pz,angle):
    glPushMatrix()
    glTranslatef(px, py, pz)
    glRotatef(angle, 0, 0, 1)

    glPushMatrix()
    glColor3f(0.15, 0.55, 0.25)
    glScalef(2.5, 1.0, 0.9)
    glutSolidSphere(30, 16, 12)
    glPopMatrix()

    glPushMatrix()
    glColor3f(0.10, 0.42, 0.18)
    glTranslatef(0, 0, 28)
    glScalef(0.6, 0.5, 1.0)
    glutSolidSphere(18, 10, 8)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(-78, 0, 0)
    glColor3f(0.7, 0.7, 0.2)
    for i in range(3):
        glPushMatrix()
        glRotatef(i * 120 + frame * 6, 1, 0, 0)
        glScalef(0.15, 1.0, 0.3)
        glutSolidCube(30)
        glPopMatrix()
    glPopMatrix()

    glColor3f(0.10,0.42,0.18)
    for fy in [1, -1]:
        glPushMatrix()
        glTranslatef(-50, fy * 30, 0)
        glScalef(1.5, 0.2, 0.6)
        glutSolidCube(20)
        glPopMatrix()

    draw_gun()

    if headlght_on:
        glPushMatrix()
        glTranslatef(78, 0, 5)
        glColor3f(1.0, 1.0, 0.6)
        glutSolidSphere(5, 8, 8)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(1.0, 1.0, 0.5, 0.08)
        glTranslatef(10, 0, 0)
        glRotatef(-90, 0, 1, 0)
        glutSolidCone(30, 120, 12, 4)
        glDisable(GL_BLEND)
        glPopMatrix()

    glPopMatrix()

def draw_gun():
    glPushMatrix()
    glTranslatef(10, 0, 38)
    glRotatef(gun_ang, 0, 0, 1)
    glColor3f(0.3, 0.6, 0.3)
    gluCylinder(gluNewQuadric(), 10, 8, 8, 8, 4)
    glTranslatef(0, 0, 8)
    glRotatef(-90, 0, 1, 0)
    glColor3f(0.25, 0.5, 0.25)
    gluCylinder(gluNewQuadric(), 3, 2, 45, 8, 4)
    glPopMatrix()

def draw_bullet(pos):
    glPushMatrix()
    glTranslatef(*pos)
    glColor3f(1.0, 0.8, 0.0)
    glutSolidSphere(5, 8, 6)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(1.0, 0.5, 0.0, 0.4)
    glScalef(2.5, 0.4, 0.4)
    glutSolidCube(10)
    glDisable(GL_BLEND)
    glPopMatrix()

def draw_shark(pos, anim):
    glPushMatrix()
    glTranslatef(*pos)
    glRotatef(anim, 0, 0, 1)
    glColor3f(0.45, 0.45, 0.55)
    glPushMatrix()
    glScalef(2.2, 0.9, 0.7)
    glutSolidSphere(22, 12, 8)
    glPopMatrix()
    glColor3f(0.4, 0.4, 0.5)
    glPushMatrix()
    glTranslatef(0, 0, 20)
    glScalef(0.3, 0.1, 1.0)
    glutSolidCube(22)
    glPopMatrix()
    glColor3f(0.4, 0.4, 0.5)
    glPushMatrix()
    glTranslatef(-45, 0, 0)
    glRotatef(45, 0, 1, 0)
    glScalef(0.2, 0.8, 0.5)
    glutSolidCube(25)
    glPopMatrix()
    glPopMatrix()

def draw_enemy_sub(pos, anim):
    glPushMatrix()
    glTranslatef(*pos)
    glRotatef(anim + 180, 0, 0, 1)
    glColor3f(0.6, 0.15, 0.15)
    glPushMatrix()
    glScalef(2.2, 0.9, 0.85)
    glutSolidSphere(28, 14, 10)
    glPopMatrix()
    glPushMatrix()
    glColor3f(0.5, 0.1, 0.1)
    glTranslatef(0, 0, 24)
    glScalef(0.55, 0.45, 0.9)
    glutSolidSphere(16, 8, 6)
    glPopMatrix()
    glPopMatrix()

def draw_hostile_coral(pos):
    glPushMatrix()
    glTranslatef(*pos)
    glScalef(2.5, 2.5, 2.5)
    glColor3f(1.0, 0.2, 0.0)
    draw_coral()
    glPopMatrix()

def draw_collectible(item):
    if item['collected']:
        return
    glPushMatrix()
    glTranslatef(*item['pos'])
    bob =math.sin(math.radians(frame * 3 + item['pos'][0])) * 5
    glTranslatef(0, 0, 20 + bob)
    t = item['type']
    if t =='oxygen':
        glColor3f(0.2, 0.8, 1.0)
        gluCylinder(gluNewQuadric(), 8, 8, 20, 10, 4)
        glColor3f(0.5, 1.0, 1.0)
        glutSolidSphere(9, 10, 8)
    elif t =='life':
        glColor3f(1.0, 0.2, 0.3)
        glutSolidSphere(10, 10, 8)
    else:
        glColor3f(1.0, 0.85, 0.0)
        glScalef(1.0, 1.0, 0.3)
        glutSolidSphere(12, 10, 8)
    glPopMatrix()

def draw_treasure():
    glPushMatrix()
    glTranslatef(*treasure_position)
    glTranslatef(0, 0, 15)
    pulse = 1.0 + 0.1*math.sin(math.radians(frame * 4))
    glScalef(pulse, pulse, pulse)
    glColor3f(0.55, 0.35, 0.10)
    glScalef(1.5, 1.0, 0.8)
    glutSolidCube(30)
    glScalef(1/1.5, 1.0, 1/0.8)
    glColor3f(0.65, 0.45, 0.12)
    glTranslatef(0, 0, 18)
    glScalef(1.5, 1.0, 0.5)
    glutSolidCube(30)
    glScalef(1/1.5, 1.0, 1/0.5)
    glColor3f(1.0, 0.85, 0.0)
    glutSolidSphere(5, 8, 8)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(1.0, 0.9, 0.2, 0.15)
    glutSolidSphere(40, 12, 10)
    glDisable(GL_BLEND)
    glPopMatrix()

def draw_waypoints():
    pass

def draw_bubbles():
    glPointSize(4)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.7, 0.9, 1.0, 0.5)
    glBegin(GL_POINTS)
    for i in range(20):
        bx = s_pos[0] + math.sin(math.radians(frame*7 + i*37)) *10
        by = s_pos[1] + math.cos(math.radians(frame*5 + i*53)) *10
        bz = s_pos[2] + 30 + ((frame * 2 + i * 17) % 120)
        glVertex3f(bx, by, bz)
    glEnd()
    glDisable(GL_BLEND)

def draw_water_overlay():
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.05, 0.35, 0.70, 0.15)
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(1000, 0)
    glVertex2f(1000, 800)
    glVertex2f(0, 800)
    glEnd()
    glDisable(GL_BLEND)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)

def jellyfish_headlight_collision(x, y, z):
    if not challenging_mode_on or not headlght_on:
        return True
    dx = x - s_pos[0]
    dy = y - s_pos[1]
    dz = z - (s_pos[2] + 5)
    distance = math.sqrt(dx*dx + dy*dy + dz*dz)
    if distance > 300:
        return False
    sub_forward_rad = math.radians(s_angle)
    forward_x = math.cos(sub_forward_rad)
    forward_y = math.sin(sub_forward_rad)
    if distance > 0:
        obj_dir_x = dx / distance
        obj_dir_y = dy / distance
    dot = forward_x * obj_dir_x + forward_y * obj_dir_y
    angle = math.degrees(math.acos(max(-1, min(1, dot))))
    return angle < 45

def rectangle(x1, y1, x2, y2, r, g, b, a=1.0):
    if a < 1.0:
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(r, g, b, a)
    else:
        glColor3f(r, g, b)
    glBegin(GL_QUADS)
    glVertex2f(x1, y1)
    glVertex2f(x2, y1)
    glVertex2f(x2, y2)
    glVertex2f(x1, y2)
    glEnd()
    if a < 1.0:
        glDisable(GL_BLEND)
map_x, map_y = 10, 10
map_w, map_h = 160, 160
map_world    = 1200.0
def draw_minimap():
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Background
    glColor4f(0.0, 0.05, 0.15, 0.80)
    glBegin(GL_QUADS)
    glVertex2f(map_x,map_y)
    glVertex2f(map_x+map_w,map_y)
    glVertex2f(map_x+map_w,map_y+map_h)
    glVertex2f(map_x,map_y+map_h)
    glEnd()

    # Border
    glColor3f(0.2, 0.6, 0.9)
    glLineWidth(2)
    glBegin(GL_LINE_LOOP)
    glVertex2f(map_x,map_y)
    glVertex2f(map_x+map_w,map_y)
    glVertex2f(map_x+map_w,map_y+map_h)
    glVertex2f(map_x,map_y+map_h)
    glEnd()

    def world_to_map(wx, wy):
        ref_x = wx - s_pos[0]
        ref_y = wy - s_pos[1]
        a = math.radians(s_angle)
        map_right = ref_x * math.cos(a) + ref_y * math.sin(a)
        map_up    = -ref_x * math.sin(a)+ ref_y * math.cos(a)
        sx = map_x + map_w/2 + map_right/ map_world * map_w
        sy = map_y + map_h/2 + map_up / map_world * map_h
        return sx, sy

    def draw_dot(wx, wy, size, r, g, b):
        sx, sy = world_to_map(wx, wy)
        if map_x <= sx <= map_x+map_w and map_y <= sy <= map_y+map_h:
            glColor3f(r, g, b)
            glPointSize(size)
            glBegin(GL_POINTS)
            glVertex2f(sx, sy)
            glEnd()

    # Collectibles
    for item in collectibles:
        if item['collected']:
            continue
        if item['type'] == 'oxygen':
            draw_dot(item['pos'][0], item['pos'][1], 4, 0.2, 0.9, 1.0)
        elif item['type'] == 'life':
            draw_dot(item['pos'][0], item['pos'][1], 4, 1.0, 0.3, 0.3)
        else:
            draw_dot(item['pos'][0], item['pos'][1], 4, 1.0, 0.85, 0.0)

    # Enemies
    for e in enemy:
        if e['dead']:
            continue
        if e['type'] =='shark':
            draw_dot(e['pos'][0],e['pos'][1], 4, 0.8, 0.2, 0.2)
        elif e['type'] == 'sub':
            draw_dot(e['pos'][0],e['pos'][1], 5, 1.0, 0.0, 0.0)
        else:
            draw_dot(e['pos'][0],e['pos'][1], 3, 0.9, 0.4, 0.1)

    # Jellyfish
    for j in jelly_fish:
        draw_dot(j['pos'][0],j['pos'][1], 5, 0.2, 0.9, 1.0)

    # Waypoint
    cx2 = map_x +map_w/2
    cy2 = map_y +map_h/2
    max_radius = map_w/ 2 - 8

    if current_wpoint < len(w_points):
        wp = w_points[current_wpoint]
        tx, ty = world_to_map(wp[0], wp[1])
        if map_x <= tx <= map_x+map_w and map_y <= ty <= map_y+map_h:
            glColor3f(1.0, 1.0, 0.3)
            glPointSize(5)
            glBegin(GL_POINTS)
            glVertex2f(tx, ty)
            glEnd()

    # Treasure
    tx2, ty2 = world_to_map(treasure_position[0], treasure_position[1])
    pulse_s = 5 + 3*abs(math.sin(math.radians(frame * 4)))
    glColor3f(1.0, 0.75, 0.0)
    if map_x <= tx2 <= map_x+map_w and map_y <= ty2 <= map_y+map_h:
        glPointSize(pulse_s)
        glBegin(GL_POINTS)
        glVertex2f(tx2, ty2)
        glEnd()
    else:
        tdx = tx2 - cx2
        tdy = ty2 - cy2
        td = math.sqrt(tdx*tdx + tdy*tdy) + 0.001
        etx = cx2 + tdx/td*(max_radius -2)
        ety = cy2 + tdy/td*(max_radius -2)
        glPointSize(pulse_s)
        glBegin(GL_POINTS)
        glVertex2f(etx, ety)
        glEnd()

    # Submarine dot (always centre)
    glColor3f(0.2, 1.0, 0.4)
    glPointSize(7)
    glBegin(GL_POINTS)
    glVertex2f(map_x + map_w/2, map_y + map_h/2)
    glEnd()

    glDisable(GL_BLEND)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)
    draw_text(map_x + 50, map_y + map_h + 4, "MAP", color=(0.5, 0.8, 1.0))


def draw_hud():
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.0, 0.05, 0.15, 0.65)
    glBegin(GL_QUADS)
    glVertex2f(0, 690)
    glVertex2f(380, 690)
    glVertex2f(380, 800)
    glVertex2f(0, 800)
    glEnd()
    glDisable(GL_BLEND)

    glColor3f(0.15, 0.15, 0.25)
    glBegin(GL_QUADS)
    glVertex2f(48, 656)
    glVertex2f(200, 656)
    glVertex2f(200, 672)
    glVertex2f(48, 672)
    glEnd()

    bar_width =int(oxygen * 1.52)
    ox_r =1.0 - oxygen/100.0
    ox_g =oxygen/100.0
    glColor3f(ox_r, ox_g, 0.2)
    glBegin(GL_QUADS)
    glVertex2f(48, 656)
    glVertex2f(48 + bar_width, 656)
    glVertex2f(48 + bar_width, 672)
    glVertex2f(48, 672)
    glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)

    draw_text(10, 778, f"SCORE : {score}", color=(1.0, 0.95, 0.3))
    draw_text(10, 758, f"COINS : {coins}", color=(1.0, 0.85, 0.0))
    draw_text(10, 738, f"LIVES : {lives}", color=(1.0, 0.3, 0.3))
    draw_text(10, 718, f"LEVEL : {level}", color=(0.4, 1.0, 0.6))
    draw_text(10, 695, f"O2: {int(oxygen)}%", color=(0.5, 0.9, 1.0))

    draw_text(750, 778, f"HDG {int(s_angle % 360):03d} deg", color=(0.7, 1.0, 0.7))
    wp = w_points[min(current_wpoint, len(w_points)-1)]
    dx = wp[0] - s_pos[0]
    dy = wp[1] - s_pos[1]
    dist = int(math.sqrt(dx*dx+dy*dy))

    if big_fish is not None and not big_fish['dead']:
        gf = big_fish
        draw_text(390, 778, "!!! GIANT FISH !!!", color=(1.0, 0.2, 0.0) if gf['rage'] else (0.2, 0.8, 1.0))
        hp_pct = gf['health'] / 5.0
        bar_col = (1.0, 0.2, 0.0) if gf['rage'] else (0.2, 0.8, 0.4)
        draw_text(390, 758, f"HP: {'#' * int(hp_pct * 10)}{'-' * (10 - int(hp_pct * 10))}", color=bar_col)

    if cheat_mode_on:
        draw_text(350, 778, "[ CHEAT MODE ACTIVE ]", color=(1.0, 0.2, 0.8))
        draw_text(350, 758, "Auto-aim + Rapid Fire", color=(1.0, 0.5, 0.8))
        draw_text(350, 738, "Press C to deactivate", color=(1.0, 0.6, 0.6))
    elif cheat_mode:
        draw_text(380, 778, "[ INVINCIBLE ]", color=(1.0, 0.3, 1.0))

    if game_over:
        draw_text(320, 430, "GAME  OVER", color=(1.0, 0.2, 0.2))
        draw_text(270, 405, f"Score: {score}   Coins: {coins}", color=(1.0, 0.9, 0.3))
        draw_text(310, 380, "Press R to restart", color=(0.8, 0.8, 0.8))

    if game_win:
        draw_text(240, 430, f"TREASURE FOUND!  Level {level} Complete!", color=(1.0, 0.9, 0.1))
        draw_text(290, 405, f"Score: {score}   Coins: {coins}", color=(1.0, 0.85, 0.0))
        draw_text(275, 380, "Press ENTER for next level", color=(0.8, 1.0, 0.8))

    draw_minimap()
def fire_bullet():
    t_angle = math.radians(s_angle + gun_ang)
    dx = math.cos(t_angle)
    dy = math.sin(t_angle)
    bx = s_pos[0] + dx*90
    by = s_pos[1] + dy*90
    bz = s_pos[2] + 10
    bullets.append({'pos':[bx, by, bz], 'dir':[dx, dy, 0.0], 'life':220})

def update_bullets():
    for b in bullets[:]:
        if cheat_mode_on and b.get('homing', False):
            target_enemy = None
            for e in enemy:
                if e['id'] == b.get('target_id', -1) and not e['dead']:
                    target_enemy = e
                    break
            if target_enemy:
                dx = target_enemy['pos'][0] - b['pos'][0]
                dy = target_enemy['pos'][1] - b['pos'][1]
                dz = target_enemy['pos'][2] - b['pos'][2]
                dist = math.sqrt(dx*dx + dy*dy + dz*dz)
                if dist > 0.01:
                    b['dir'][0] = b['dir'][0]*0.95 + (dx/dist)*0.05
                    b['dir'][1] = b['dir'][1]*0.95 + (dy/dist)*0.05
                    b['dir'][2] = b['dir'][2]*0.95 + (dz/dist)*0.05
                    mag = math.sqrt(sum(v**2 for v in b['dir']))
                    if mag > 0:
                        b['dir'] = [v/mag for v in b['dir']]

        b['pos'][0] += b['dir'][0]*bullet_speed
        b['pos'][1] += b['dir'][1]*bullet_speed
        b['pos'][2] += b['dir'][2]*bullet_speed
        b['life'] -= 1
        if b['life'] <= 0:
            bullets.remove(b)
            continue

        for e in enemy:
            if e['dead']:
                continue
            enemy_pos = e['pos']
            bullet_pos= b['pos']
            r = 35 if e['type'] == 'sub' else 28
            if abs(bullet_pos[0]-enemy_pos[0]) < r and abs(bullet_pos[1]-enemy_pos[1]) < r and abs(bullet_pos[2]-enemy_pos[2]) < r:
                e['health'] -= 2 if cheat_mode_on else 1
                if b in bullets:
                    bullets.remove(b)
                if e['health'] <= 0:
                    e['dead'] = True
                    enemy_killed(e)
                break

def enemy_killed(e):
    global score,coins
    gain ={'shark': 30, 'sub': 80, 'coral': 10}
    c = gain.get(e['type'], 20)
    score+= c
    coins+= c
    print(f"Killed {e['type']}! +{c} coins")

def update_enemies():
    global lives, coins, score, invincible_frame
    speed_mul = 1.0 + (level - 1) * 0.5

    if invincible_frame > 0:
        invincible_frame -= 1

    for e in enemy:
        if e['dead']:
            continue
        e['anim'] = (e['anim'] + 2) % 360
        if e['type'] in ('shark', 'sub'):
            dx = s_pos[0] -e['pos'][0]
            dy = s_pos[1] -e['pos'][1]
            dz = s_pos[2] -e['pos'][2]
            dist = math.sqrt(dx*dx + dy*dy + dz*dz) + 0.001
            speed = e['speed'] * speed_mul
            e['pos'][0] +=(dx/dist) *speed
            e['pos'][1] +=(dy/dist) *speed
            e['pos'][2] +=(dz/dist) *speed *0.3

            cdistance = math.sqrt((e['pos'][0]-s_pos[0])**2 +
                              (e['pos'][1]-s_pos[1])**2)
            hit_r = 90 if e['type'] == 'sub' else 80
            if cdistance < hit_r and not cheat_mode and invincible_frame == 0:
                player_hit()
                e['pos'][0] -= dx/dist*80
                e['pos'][1] -= dy/dist*80
        elif e['type'] == 'coral':
            # CORAL COLLISION: -10 coins
            dx = e['pos'][0]-s_pos[0]
            dy = e['pos'][1]-s_pos[1]
            cdistance = math.sqrt(dx*dx + dy*dy)
            COLLISION_RADIUS = 100
            if cdistance < COLLISION_RADIUS and s_pos[2] < 150 and not cheat_mode and invincible_frame == 0:
                coral_k=e['id']
                if coral_k not in collisions or frame - collisions[coral_k] > 30:
                    collisions[coral_k] = frame
                    score =max(0, score - 15)
                    coins =max(0, coins - 10)   # -10 coins on coral collision
                    print(f"Hit coral! -15 score, -10 coins. Score={score}, Coins={coins}")
                    if cdistance > 0.1:
                        push_angle = math.atan2(s_pos[1] - e['pos'][1], s_pos[0] - e['pos'][0])
                        s_pos[0] += math.cos(push_angle) * 30
                        s_pos[1] += math.sin(push_angle) * 30
                    e['dead'] = True
                    # Kill the coral on collision
                    e['dead'] = True
                    print(f"Coral destroyed! Coins={coins}")

def player_hit():
    global lives, coins, score, invincible_frame
    lives -= 1
    coins = max(0, coins - 50)
    score = max(0, score - 50)
    invincible_frame = invincible_dr
    print(f"HIT! Lives={lives}, Coins={coins}, Score={score}")

def update_collectibles():
    global oxygen, lives, coins, score
    for item in collectibles:
        if item['collected']:
            continue
        dx = s_pos[0] - item['pos'][0]
        dy = s_pos[1] - item['pos'][1]
        distance = math.sqrt(dx*dx + dy*dy)
        if distance <40:
            item['collected'] = True
            if item['type'] == 'oxygen':
                oxygen = min(100.0, oxygen + 45.0)
                print("Oxygen tank collected!")
            elif item['type'] == 'life':
                lives += 1
                score += 20
                print("Extra life!")
            else:
                coins += 25
                score += 25
                print("Coin bonus!")

def update_treasure():
    global score, coins, treasure_got, game_win
    dx =s_pos[0] - treasure_position[0]
    dy =s_pos[1] - treasure_position[1]
    distance = math.sqrt(dx*dx + dy*dy)
    if distance < 120 and not treasure_got:
        treasure_got = True
        score += 100
        coins += 100
        game_win = True
        print("TREASURE REACHED! +100 points, +100 coins")

def update_oxygen():
    global oxygen, lives, game_over
    if game_over or game_win or pause:
        return
    oxygen -= oxygen_drain
    if oxygen <= 0:
        oxygen = 0
        lives -= 2
        oxygen = 30.0
        print(f"OUT OF OXYGEN! Lives={lives}")

def check_game_over():
    global game_over
    if lives <= 0 and not game_over:
        game_over = True

def update_waypoint():
    global current_wpoint
    if current_wpoint >= len(w_points):
        return
    wp = w_points[current_wpoint]
    dx = s_pos[0]-wp[0]
    dy = s_pos[1]-wp[1]
    if math.sqrt(dx*dx+dy*dy) < 120:
        current_wpoint = min(current_wpoint+1, len(w_points)-1)
        print(f"Waypoint {current_wpoint}/{len(w_points)} reached!")

def reset_game():
    global s_pos, s_angle, gun_ang, bullets, enemy
    global score, coins, lives, oxygen, level, game_over, game_win
    global treasure_got, current_wpoint, frame, last_enemy_x
    global cheat_mode_on, cheat_mode, challenging_mode_on, jelly_fish
    global ambient_lght, target_num, fire_interval, invincible_frame
    global collisions
    s_pos    = [0.0, 0.0, 60.0]
    s_angle  = 0.0
    gun_ang  = 0.0
    bullets    = []
    score = 0
    coins = 100
    lives = 3
    oxygen = 100.0
    level = 1
    game_over = False
    game_win = False
    treasure_got = False
    current_wpoint = 0
    frame = 0
    last_enemy_x = 0.0
    cheat_mode_on = False
    cheat_mode = False
    challenging_mode_on = False
    jelly_fish = []
    ambient_lght = 1.0
    target_num = -1
    fire_interval = 0
    invincible_frame = 0
    collisions = {}
    giant_fish = None
    giant_fish_timer = 0
    giant_fish_warning = 0
    initiate_collectibles()
    initiate_enemies()
    print("Game Reset!")

def next_level():
    global level, game_win, treasure_got, current_wpoint, oxygen, bullets, last_enemy_x, collisions
    global big_fish, big_fish_timer, bigfish_warning
    level += 1
    game_win = False
    treasure_got = False
    current_wpoint = 0
    oxygen = 100.0
    bullets = []
    s_pos[0] = 0.0
    s_pos[1] = 0.0
    s_pos[2] = 60.0
    last_enemy_x = 0.0
    collisions = {}
    big_fish = None
    big_fish_timer = 0
    bigfish_warning = 0
    initiate_collectibles()
    initiate_enemies()
    print(f"=== LEVEL {level} STARTED ===")

# heat Mode
def toggle_cheat_mode():

    global cheat_mode_on,cheat_mode,coins,cheat_cost

    if cheat_mode_on ==False:
        if coins>=cheat_cost:
            cheat_mode_on=True
            coins-=cheat_cost
            cheat_mode=True
            print(f"Cheat mode activated -{cheat_cost} coins")
        else:
            print(f"You Need {cheat_cost} coins. You have {coins}.")
    else:
        cheat_mode_on=False
        cheat_mode=False
        print("Cheat mode deactivated")

def auto_firing():

    global gun_ang,fire_interval,target_num

    if not cheat_mode_on:
        return
    if fire_interval>0:
        fire_interval-=1 #wating between auto fite
        return
    alive =[i for i in enemy if not i['dead']]
    if not alive:
        return
    ind = 0
    if target_num!=-1:
        for i, j in enumerate(alive):
            if j['id']==target_num:
                ind =(i+1)%len(alive) #pointing to next enemy
                break
    target=alive[ind]
    target_num=target['id']
    d_x=target['pos'][0]-s_pos[0]
    d_y=target['pos'][1]-s_pos[1]
    enemy_ang=math.degrees(math.atan2(d_y, d_x))
    gun_ang=(enemy_ang-s_angle)%360
    total_angle=math.radians(s_angle+gun_ang)
    dx_b=math.cos(total_angle)
    dy_b=math.sin(total_angle)
    bullets.append({
        'pos': [s_pos[0]+dx_b*90, s_pos[1]+dy_b*90,s_pos[2]+10],'dir':[dx_b, dy_b, 0.0],'life':220,'homing':True,'target_id':target['id']})
    fire_interval=2

#Challenge Mode
def toggle_challengeM():

    global challenging_mode_on,headlght_on,ambient_lght,lght_dirct,jelly_fish

    if challenging_mode_on== False:
        challenging_mode_on=True
        lght_dirct=-0.02
        headlght_on=True
        ambient_lght=1.0
        jelly_fish=[]
        print("CHALLENGING MODE ON")
    else:
        challenging_mode_on= False
        ambient_lght=1.0
        jelly_fish=[]
        print("Challenging mode deactivated")

def blinking_ambience():

    global ambient_lght,lght_dirct

    if challenging_mode_on ==False:
        return
    ambient_lght+=lght_dirct
    if ambient_lght<=0.15:
        ambient_lght=0.15 #darker
        lght_dirct=abs(lght_dirct)
    elif ambient_lght>=1:
        ambient_lght=1 #lighter
        lght_dirct=-abs(lght_dirct)


def draw_darkness():

    if  challenging_mode_on==False:
        return
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0,1000,0,800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
    dark= 1-(ambient_lght-0.3)/0.7
    theta = 0.7+dark * 0.3
    glColor4f(0.0,0.0,0.05,theta)
    glBegin(GL_QUADS)
    glVertex2f(0,0)
    glVertex2f(1000,0)
    glVertex2f(1000,800)
    glVertex2f(0,800)
    glEnd()
    glDisable(GL_BLEND)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)

def headlight_cone():

    if challenging_mode_on==False or headlght_on==False:
        return
    glPushMatrix()
    glTranslatef(s_pos[0],s_pos[1],s_pos[2]+5)
    glRotatef(s_angle,0,0,1)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
    glRotatef(-90,0,1,0)
    glColor4f(1.0,0.9,0.5,0.08)
    glutSolidCone(120,300,30,15)
    glColor4f(1.0,0.95,0.4,0.15)
    glutSolidCone(90,250,30,15)
    glColor4f(1.0,1.0,0.6,0.25)
    glutSolidCone(60,200,30,15)
    glColor4f(1.0,1.0,0.8,0.35)
    glutSolidCone(35,150,20,10)
    glDisable(GL_BLEND)
    glPopMatrix()


def draw_jellyfish():

    for j in jelly_fish:
        if challenging_mode_on ==True and not jellyfish_headlight_collision(j['pos'][0],j['pos'][1],j['pos'][2]):
            continue
        glPushMatrix()
        glTranslatef(j['pos'][0], j['pos'][1], j['pos'][2])
        pulse = 0.7+0.3 * math.sin(math.radians(j['anim'] * 3))
        glRotatef(j['anim'],0,0,1)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.5,0.9,1.0,0.5*pulse)
        glutSolidSphere(18,8,8)
        glColor3f(0.3,0.9,1.0)
        glScalef(0.8,0.6,0.5)
        glutSolidSphere(12,10,8)
        glScalef(1/0.8,1/0.6,1/0.5)
        glColor3f(0.5,0.9,1.0)
        glLineWidth(2)
        glBegin(GL_LINES)
        for i in range(8):
            rad = math.radians(i * 45)
            length = 25+math.sin(math.radians(j['anim']*2+i*45))*8
            glVertex3f(math.cos(rad)*15, math.sin(rad)*15,-10)
            glVertex3f(math.cos(rad)*(15+length),math.sin(rad)*(15+length),-35-length*0.5)
        glEnd()
        pulse_b = 0.6+0.4*math.sin(math.radians(frame*8))
        glColor4f(1.0,1.0,0.8, pulse_b)
        glPointSize(4)
        glBegin(GL_POINTS)
        for i in range(6):
            rad =math.radians(j['anim']+i*60)
            glVertex3f(math.cos(rad)*8, math.sin(rad)*8, -5)
        glEnd()
        glDisable(GL_BLEND)
        glPopMatrix()

def spawn_jellyfish():

    global jelly_fish

    if challenging_mode_on ==False:
        return

    for i in range(random.randint(1,3)):
        angle=random.uniform(0, 2*math.pi)
        radius=random.uniform(80, 250)
        j_x=s_pos[0]+ math.cos(angle)*radius
        j_y = s_pos[1]+math.sin(angle)*radius
        j_z = s_pos[2]+random.uniform(-50, 80)
        jelly_fish.append({
            'pos':[j_x,j_y,j_z],'life':j_fish_life,'anim':random.uniform(0, 360),'pulse':random.uniform(0.5, 1.5)})


def update_jelly_auto():

    global invincible_frame,score,coins

    if challenging_mode_on==False:
        return

    for i in jelly_fish[:]:
        i['life']-=1
        i['anim']=(i['anim']+3)%360 #floating angle
        i['pos'][2]+=math.sin(math.radians(i['anim']))*0.5
        if i['life']<=0:
            jelly_fish.remove(i)
            continue
        dx = s_pos[0]-i['pos'][0]
        dy = s_pos[1]-i['pos'][1]
        dz = s_pos[2]-i['pos'][2]
        if math.sqrt(dx**2+dy**2+dz**2)<40:
            if cheat_mode==False and invincible_frame==0:
                player_hit()
            if i in jelly_fish:
                jelly_fish.remove(i)
            continue
        if cheat_mode_on==True or jellyfish_headlight_collision(i['pos'][0],i['pos'][1],i['pos'][2]):
            for b in bullets[:]:
                bp=b['pos']
                if abs(bp[0]-i['pos'][0])<35 and abs(bp[1]-i['pos'][1])<35 and abs(bp[2]-i['pos'][2])<35:
                    score += 1
                    coins += 75
                    print("Jellyfish killed! +75 coins!")
                    if b in bullets:bullets.remove(b)
                    if i in jelly_fish:jelly_fish.remove(i)
                    break


def draw_challenging_mode_indicator():

    if challenging_mode_on == False:
        return
    if ambient_lght<0.5:
        draw_text(430, 758, "!!! CHALLENGING MODE !!!", color=(1.0, 0.5, 0.0))
        draw_text(450, 718, "KILL FOR 3x COINS!", color=(0.3, 1.0, 0.5))
    else:
        draw_text(430, 758, "CHALLENGING MODE", color=(1.0, 0.6, 0.2))



#  CAMERA
def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 1.0, 3000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    if c_track:
        back_angle =math.radians(s_angle + 180)
        cx = s_pos[0] +math.cos(back_angle) * c_radius
        cy = s_pos[1] + math.sin(back_angle) * c_radius
        cz = s_pos[2] + c_height
        gluLookAt(cx, cy, cz, s_pos[0], s_pos[1], s_pos[2], 0, 0, 1)
    else:
        radi = math.radians(c_angle)
        cx = math.cos(radi) * c_radius
        cy = math.sin(radi) * c_radius
        gluLookAt(cx, cy, c_height, 0, 0, 0, 0, 0, 1)

def keyboardListener(key, x, y):
    global s_pos, s_angle, gun_ang, cheat_mode, c_track
    global headlght_on, game_over, game_win, pause, level

    if key == b'\r' or key == b'\n':
        if game_win: next_level()
        return
    if key == b'r' or key == b'R':
        reset_game()
        return
    if game_over or game_win:
        return

    speed = s_speed + level * 0.5

    if key == b'w' or key == b'W':
        rad = math.radians(s_angle)
        s_pos[0] += math.cos(rad) * speed
        s_pos[1] += math.sin(rad) * speed
    if key == b's' or key == b'S':
        rad = math.radians(s_angle)
        s_pos[0] -= math.cos(rad) * speed
        s_pos[1] -= math.sin(rad) * speed
    if key == b'a' or key == b'A':
        s_angle = (s_angle + 5) %360
    if key == b'd' or key == b'D':
        s_angle = (s_angle - 5) %360
    if key == b'q' or key == b'Q':
        s_pos[2] = min(s_pos[2] + speed*0.6,400)
    if key == b'e' or key == b'E':
        s_pos[2] = max(s_pos[2] - speed*0.6,15)
    if key == b'z' or key == b'Z':
        gun_ang = (gun_ang + 8) %360
    if key == b'x' or key == b'X':
        gun_ang = (gun_ang - 8) %360
    if key == b' ':
        fire_bullet()
    if key == b'h' or key == b'H':
        toggle_challengeM()
    if key == b'c' or key == b'C':
        toggle_cheat_mode()
    #if key == b'v' or key == b'V':
        #c_track = not c_track
    if key == b'p' or key == b'P':
        global pause
        pause = not pause

def specialKeyListener(key, x, y):
    global c_angle, c_height
    if key == GLUT_KEY_UP:    c_height = min(c_height+20, 900)
    if key == GLUT_KEY_DOWN:  c_height = max(c_height-20, 50)
    if key == GLUT_KEY_LEFT:  c_angle  = (c_angle+5)  % 360
    if key == GLUT_KEY_RIGHT: c_angle  = (c_angle-5)  % 360

def mouseListener(button, state, x, y):
    global c_track
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if not game_over and not game_win:
            fire_bullet()
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        c_track = not c_track

def idle():
    global frame, last_enemy_x, j_enemy_timer
    if not pause and not game_over and not game_win:
        frame += 1
        update_bullets()
        update_enemies()
        update_collectibles()
        update_treasure()
        update_oxygen()
        check_game_over()
        update_waypoint()
        auto_firing()
        update_big_fish()
        if challenging_mode_on:
            blinking_ambience()
            update_jelly_auto()
            j_enemy_timer += 1
            if j_enemy_timer >= j_fish_interval:
                j_enemy_timer = 0
                spawn_jellyfish()
        if s_pos[0] - last_enemy_x > enemy_interval:
            enemy_forward()
    glutPostRedisplay()

def showScreen():
    if challenging_mode_on and ambient_lght < 0.5:
        factor = (ambient_lght - 0.3) / 0.7
        glClearColor(0.02+factor*0.03, 0.08+factor*0.22, 0.25+factor*0.40, 1.0)
    else:
        glClearColor(0.05, 0.30, 0.65, 1.0)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    setupCamera()
    draw_seabed()
    for item in collectibles:
        draw_collectible(item)
    draw_treasure()
    draw_waypoints()
    for e in enemy:
        if e['dead']:
            continue
        if e['type'] == 'shark':
            draw_shark(e['pos'], e['anim'])
        elif e['type'] == 'sub':
            draw_enemy_sub(e['pos'], e['anim'])
        elif e['type'] == 'coral':
            draw_hostile_coral(e['pos'])
    draw_jellyfish()
    draw_big_fish()
    for b in bullets:
        draw_bullet(b['pos'])
    draw_submarine(s_pos[0], s_pos[1], s_pos[2], s_angle)
    headlight_cone()
    draw_bubbles()
    draw_ocean_waves()
    draw_water_overlay()
    draw_darkness()
    draw_hud()
    draw_challenging_mode_indicator()
    big_fish_warning()
    glutSwapBuffers()


def print_controls():
    print("""
========================================
   DEEP SEA HUNTER - CONTROLS
========================================
  W/S         Move forward / backward
  A/D         Rotate submarine
  Q/E         Rise / Dive
  Z/X         Rotate gun left / right
  SPACE       Fire torpedo
  H           Toggle Challenging Mode
  C           Toggle Cheat Mode (costs 100 coins)
  V           Toggle camera mode
  P           Pause
  R           Restart
  ENTER       Next level (after win)
  Arrow UP/DOWN    Camera height
  Arrow LEFT/RIGHT Camera orbit
========================================
CORAL COLLISION  : -15 score, -10 coins
PREDATOR HIT     : -1 life, -50 coins
GIANT FISH       : Appears randomly!
  Defeat it      : +200 coins
OCEAN WAVES      : Visible at surface
TREASURE         : +100 score +100 coins
OXYGEN TANK      : Refills O2
EXTRA LIFE       : +1 life
COIN BONUS       : +25 coins
========================================
""")

def main():
    initiate_seabed()
    initiate_collectibles()
    initiate_enemies()
    print_controls()
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(100, 50)
    glutCreateWindow(b"Deep Sea Hunter - Submarine Game")
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    glutMainLoop()

if __name__ == "__main__":
    main()