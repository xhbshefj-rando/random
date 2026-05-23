import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import numpy as np
from enum import Enum

# Game constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60

class TrackType(Enum):
    STREET = 1
    MOTOCROSS = 2

class BikePhysics:
    def __init__(self):
        # Bike state
        self.position = [0, 0, 0]
        self.rotation = [0, 0, 0]
        self.velocity = [0, 0, 0]
        self.angular_velocity = [0, 0, 0]
        
        # Engine state
        self.throttle = 0.0  # 0-1
        self.clutch = 0.0   # 0-1 (0 = engaged, 1 = disengaged)
        self.rpm = 0
        self.speed = 0
        self.gear = 1
        self.max_gears = 6
        
        # Engine properties
        self.max_rpm = 12000
        self.idle_rpm = 800
        self.power_curve = self._create_power_curve()
        
        # Physical properties
        self.mass = 200  # kg
        self.friction = 0.98
        self.acceleration = 0
        self.wheelbase = 1.5
        self.bike_width = 0.8
        
        # Suspension
        self.suspension_y = 0
        self.suspension_rest = 0
        self.suspension_spring = 0.5
        self.suspension_damping = 0.3
        
    def _create_power_curve(self):
        """Create a realistic power delivery curve"""
        curve = {}
        for rpm in range(0, 13000, 500):
            if rpm < 2000:
                power = (rpm / 2000) * 50
            elif rpm < 8000:
                power = 50 + (rpm - 2000) / 6000 * 150
            else:
                power = 200 - (rpm - 8000) / 4000 * 100
            curve[rpm] = max(0, power)
        return curve
    
    def get_power(self, rpm):
        """Get power output at given RPM"""
        rpm = max(self.idle_rpm, min(self.max_rpm, rpm))
        lower_rpm = (rpm // 500) * 500
        upper_rpm = lower_rpm + 500
        
        if upper_rpm not in self.power_curve:
            return self.power_curve.get(lower_rpm, 0)
        
        ratio = (rpm - lower_rpm) / 500
        power1 = self.power_curve.get(lower_rpm, 0)
        power2 = self.power_curve.get(upper_rpm, 0)
        return power1 + (power2 - power1) * ratio
    
    def get_gear_ratio(self):
        """Get gear ratio for current gear"""
        ratios = [4.5, 3.5, 2.8, 2.2, 1.8, 1.5]
        return ratios[min(self.gear - 1, len(ratios) - 1)]
    
    def update(self, dt):
        """Update physics simulation"""
        # RPM calculation based on speed and gear
        if self.clutch > 0.1:  # Clutch disengaged
            # Decelerate RPM when clutch is out
            self.rpm = max(self.idle_rpm, self.rpm - 2000 * dt)
        else:  # Clutch engaged
            # RPM based on ground speed
            wheel_rpm = (self.speed / (math.pi * 0.3)) * 60  # Assuming 0.3m radius wheel
            self.rpm = max(self.idle_rpm, wheel_rpm * self.get_gear_ratio())
            self.rpm = min(self.max_rpm, self.rpm)
        
        # Throttle input affects RPM
        if self.clutch < 0.1:  # Only when clutch engaged
            self.rpm = min(self.max_rpm, self.rpm + self.throttle * 5000 * dt)
        else:
            self.rpm = min(self.max_rpm, self.rpm + self.throttle * 3000 * dt)
        
        # Calculate traction force from engine
        power = self.get_power(self.rpm)
        traction_force = 0
        
        if self.clutch < 0.1:  # Clutch engaged
            # Slip ratio based on clutch position
            slip = 1.0 - self.clutch * 0.2
            traction_force = power * slip * self.throttle / max(1, self.speed + 0.1)
        
        # Calculate acceleration
        drag = self.speed * self.speed * 0.02
        self.acceleration = (traction_force - drag) / self.mass
        
        # Update velocity and position
        self.speed += self.acceleration * dt
        self.speed = max(0, self.speed)
        
        # Suspension simulation
        target_suspension = -0.3 if self.speed > 0 else 0
        suspension_force = (target_suspension - self.suspension_y) * self.suspension_spring
        suspension_damping_force = -self.suspension_y * self.suspension_damping
        suspension_accel = (suspension_force + suspension_damping_force) / self.mass
        
        self.suspension_y += suspension_accel * dt
        self.position[1] = self.suspension_y
        self.position[2] += self.speed * dt
        
        # Lean angle based on speed and input
        self.rotation[2] = self.speed * 0.15 * 0.1  # Roll
        self.rotation[0] = math.sin(self.suspension_y * 5) * 0.1  # Pitch from suspension
        self.rotation[1] = 0  # Yaw


class Track:
    def __init__(self, track_type):
        self.track_type = track_type
        self.segments = []
        self._generate_track()
    
    def _generate_track(self):
        """Generate track segments"""
        if self.track_type == TrackType.STREET:
            self._generate_street_track()
        else:
            self._generate_motocross_track()
    
    def _generate_street_track(self):
        """Generate a smooth street track"""
        self.segments = []
        for i in range(100):
            z = i * 5
            x = math.sin(i * 0.3) * 10
            width = 4
            height = 0
            self.segments.append({
                'x': x,
                'z': z,
                'width': width,
                'height': height,
                'type': 'asphalt'
            })
    
    def _generate_motocross_track(self):
        """Generate a bumpy motocross track with jumps"""
        self.segments = []
        for i in range(100):
            z = i * 5
            x = math.sin(i * 0.2) * 15
            width = 6
            
            # Create jumps every 20 segments
            if i % 20 == 0:
                height = 3
            elif i % 20 == 1:
                height = -2
            elif i % 20 == 2:
                height = 1
            else:
                height = 0.5 * math.sin(i * 0.5)
            
            self.segments.append({
                'x': x,
                'z': z,
                'width': width,
                'height': height,
                'type': 'dirt'
            })


class MotocrossGame:
    def __init__(self, track_type):
        pygame.init()
        pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("3D Motocross Game")
        
        # Setup OpenGL
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_DIFFUSE)
        
        # Setup perspective
        gluPerspective(45, (WINDOW_WIDTH / WINDOW_HEIGHT), 0.1, 500.0)
        
        # Setup lighting
        light_pos = [10, 10, 10, 1]
        glLight(GL_LIGHT0, GL_POSITION, light_pos)
        glLight(GL_LIGHT0, GL_AMBIENT, [0.5, 0.5, 0.5, 1])
        glLight(GL_LIGHT0, GL_DIFFUSE, [1, 1, 1, 1])
        
        self.clock = pygame.time.Clock()
        self.bike = BikePhysics()
        self.track = Track(track_type)
        self.track_type = track_type
        self.running = True
        self.camera_distance = 5
        self.camera_height = 2
        
    def handle_input(self):
        """Handle keyboard input"""
        keys = pygame.key.get_pressed()
        
        # Throttle
        if keys[K_UP] or keys[K_w]:
            self.bike.throttle = min(1.0, self.bike.throttle + 0.05)
        else:
            self.bike.throttle = max(0.0, self.bike.throttle - 0.05)
        
        # Clutch
        if keys[K_LCTRL] or keys[K_c]:
            self.bike.clutch = min(1.0, self.bike.clutch + 0.05)
        else:
            self.bike.clutch = max(0.0, self.bike.clutch - 0.05)
        
        # Gear up/down
        if keys[K_e]:
            if self.bike.rpm > 8000 and self.bike.gear < self.bike.max_gears:
                self.bike.gear += 1
                self.bike.rpm = self.bike.idle_rpm
        if keys[K_q]:
            if self.bike.gear > 1:
                self.bike.gear -= 1
                self.bike.rpm = self.bike.idle_rpm
        
        # Brakes
        if keys[K_SPACE]:
            self.bike.acceleration -= 15
        
        # Check for quit
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
    
    def update(self):
        """Update game state"""
        dt = self.clock.tick(FPS) / 1000.0
        self.handle_input()
        self.bike.update(dt)
    
    def draw_track(self):
        """Draw the track"""
        glDisable(GL_LIGHTING)
        
        for i, segment in enumerate(self.track.segments):
            glPushMatrix()
            glTranslatef(segment['x'], segment['height'], segment['z'])
            
            # Set color based on track type
            if self.track.track_type == TrackType.STREET:
                glColor3f(0.3, 0.3, 0.3)  # Dark asphalt
            else:
                glColor3f(0.6, 0.4, 0.2)  # Brown dirt
            
            # Draw track segment
            width = segment['width']
            length = 5
            self._draw_box(width, 0.2, length)
            
            glPopMatrix()
        
        glEnable(GL_LIGHTING)
    
    def draw_bike(self):
        """Draw the motorcycle"""
        glPushMatrix()
        glTranslatef(self.bike.position[0], self.bike.position[1], self.bike.position[2])
        glRotatef(self.bike.rotation[0] * 180 / math.pi, 1, 0, 0)
        glRotatef(self.bike.rotation[1] * 180 / math.pi, 0, 1, 0)
        glRotatef(self.bike.rotation[2] * 180 / math.pi, 0, 0, 1)
        
        glColor3f(1, 0, 0)  # Red bike
        
        # Main body
        self._draw_box(0.4, 0.8, 0.8)
        
        # Wheels
        glPushMatrix()
        glTranslatef(0, -0.5, -0.4)
        glColor3f(0.2, 0.2, 0.2)
        self._draw_cylinder(0.3, 0.2, 16)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(0, -0.5, 0.4)
        self._draw_cylinder(0.3, 0.2, 16)
        glPopMatrix()
        
        glPopMatrix()
    
    def _draw_box(self, width, height, depth):
        """Draw a box"""
        vertices = [
            [-width/2, -height/2, -depth/2],
            [width/2, -height/2, -depth/2],
            [width/2, height/2, -depth/2],
            [-width/2, height/2, -depth/2],
            [-width/2, -height/2, depth/2],
            [width/2, -height/2, depth/2],
            [width/2, height/2, depth/2],
            [-width/2, height/2, depth/2]
        ]
        
        faces = [
            (0, 1, 2, 3), (4, 5, 6, 7),
            (0, 1, 5, 4), (2, 3, 7, 6),
            (0, 3, 7, 4), (1, 2, 6, 5)
        ]
        
        glBegin(GL_QUADS)
        for face in faces:
            for vertex in face:
                glVertex3fv(vertices[vertex])
        glEnd()
    
    def _draw_cylinder(self, radius, height, slices):
        """Draw a cylinder"""
        quad = GLUquadric()
        glTranslatef(0, 0, -height/2)
        gluCylinder(quad, radius, radius, height, slices, 32)
    
    def draw_hud(self):
        """Draw HUD information"""
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, WINDOW_WIDTH, WINDOW_HEIGHT, 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        
        # Draw HUD text (simplified - using colored rectangles to represent data)
        glColor3f(0, 1, 0)
        
        # RPM bar
        rpm_ratio = self.bike.rpm / self.bike.max_rpm
        self._draw_rect(10, 10, 200 * rpm_ratio, 20)
        
        # Speed
        speed_kmh = self.bike.speed * 3.6
        
        # Clutch indicator
        clutch_ratio = self.bike.clutch
        glColor3f(1, 1, 0)
        self._draw_rect(10, 40, 200 * clutch_ratio, 20)
        
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    
    def _draw_rect(self, x, y, width, height):
        """Draw a 2D rectangle for HUD"""
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + width, y)
        glVertex2f(x + width, y + height)
        glVertex2f(x, y + height)
        glEnd()
    
    def render(self):
        """Render the scene"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # Position camera behind and above the bike
        cam_x = self.bike.position[0] - math.sin(self.bike.rotation[1]) * self.camera_distance
        cam_y = self.bike.position[1] + self.camera_height
        cam_z = self.bike.position[2] - math.cos(self.bike.rotation[1]) * self.camera_distance
        
        gluLookAt(cam_x, cam_y, cam_z,
                  self.bike.position[0], self.bike.position[1], self.bike.position[2],
                  0, 1, 0)
        
        # Draw scene
        self.draw_track()
        self.draw_bike()
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        print("=" * 50)
        print("3D MOTOCROSS GAME")
        print("=" * 50)
        print(f"Track Type: {self.track_type.name}")
        print("\nCONTROLS:")
        print("  UP/W          - Throttle")
        print("  CTRL/C        - Clutch (hold for smooth starts)")
        print("  SPACE         - Brake")
        print("  Q/E           - Down/Up Gear")
        print("  ESC           - Quit")
        print("\nTIPS:")
        print("  - Use clutch to prevent stalling at low RPM")
        print("  - Shift gears when RPM is high")
        print("  - On motocross track, watch for jumps!")
        print("=" * 50)
        
        while self.running:
            self.update()
            self.render()
        
        pygame.quit()


def show_menu():
    """Show track selection menu"""
    print("\n" + "=" * 50)
    print("TRACK SELECTION")
    print("=" * 50)
    print("1. STREET TRACK - Smooth asphalt, long straights")
    print("2. MOTOCROSS TRACK - Rough terrain with jumps")
    print("=" * 50)
    
    while True:
        choice = input("Select track (1 or 2): ").strip()
        if choice == "1":
            return TrackType.STREET
        elif choice == "2":
            return TrackType.MOTOCROSS
        else:
            print("Invalid choice. Please enter 1 or 2.")


if __name__ == "__main__":
    track_type = show_menu()
    game = MotocrossGame(track_type)
    game.run()

