import pygame
from settings import *
from support import import_folder
# import pygame_textinput
# from pygame_textinput import TextInput
import random as rand


class Player(pygame.sprite.Sprite):
	'''
	A class for setting player in game
	...
		Attributes:
			pos (tuple): position of player when created
			group <class pygame.sprite.Group>: declare which group the player is in
			obstacles <class pygame.sprite.Group>: declare groups that cause collision
			bullet <class pygame,sprite.Group>: declare bullet groups to generate or get damamge on collision
			status (str): set the status name
			frame_index (int): index for image in the asset
			animations (dict): store the folder name of status and its images
			image <class pygame.surface.Surface>: image of player
			rect <class pygame.rect.Rect>: rectangle of player
			old_rect <class pygame.rect.Rect>: old rectangle to know if collision
			direction <class pygame.math.Vector2>: the direction of the player when move
			pos <class pygame.math.Vector2>: the position of player
			speed (int): the speed of player when moving
			cooldown (int): cooldown after shooting bullet
			angle (int): the angle for aiming
			heal (int): health of player
			screen <class pygame.surface.Surface>: get the background
			ratio (float): how much a bullet can hurt
		------------
		Methods:
			import_assets: import the assets to player
			animate: change the image from assets continously to look more lively
			input: get input from person
			collision: set collision with objects
			window_collision: prevent player get outside the window
			get_status: get the current status of player to set the proper image 
			move: help player moving
			create_bullet: create a bullet
			healh_bar: update the health bar
			get_damage: reduce health when get shoot, print Game Over
		-----------
	'''
	def __init__(self, pos, group, obstacles,bullet):   #vị trí và camera
		'''
		Constructs all the necessary attributes for the player
		...
		Parameters:
			pos (tuple): position of player when created
			group <class pygame.sprite.Group>: declare which group the player is in
			obstacles <class pygame.sprite.Group>: declare groups that cause collision
			bullet <class pygame,sprite.Group>: declare bullet groups to generate or get damamge on collision
		-------------
		Return:
			None
		------------
		'''
		super().__init__(group)
		#load the gif before 
		self.import_assets()
		self.status = 'left'
		self.frame_index = 1
		# general setup
		self.image = self.animations[self.status][self.frame_index]#image
		self.rect = self.image.get_rect(center = pos)
		self.mask = pygame.mask.from_surface(self.image)
		self.old_rect = self.rect.copy()
		self.obstacles = obstacles
		self.bullet = bullet

		# movement attributes
		self.direction = pygame.math.Vector2()  #hướng đi
		self.pos = pygame.math.Vector2(self.rect.center)  #vị trí
		self.speed = 500
		self.cooldown = -1
		self.angle = 0

		## self.heal = 100
		self.gr = group
		self.screen = pygame.display.get_surface()
		self.ratio = 1
		
	def import_assets(self):
		'''
		A function import the image asset for player. Update to self.animations 
		...
		Parameter:
		---------
		Return:
			None
		---------
		'''
		#chứa gif
		self.animations = {'up': [],'down': [],'left': [],'right': [],
						   'right_idle':[],'left_idle':[],'up_idle':[],'down_idle':[]}
		for animation in self.animations.keys():
			full_path = '../graphics/char/' + animation
			self.animations[animation] = import_folder(full_path)

######################################################################
	def animate(self,dt):
		'''
		A function that change the image from asset
		Parameters:
			dt (float): delta time to make the image update following the frame
		Return:
			None
		'''
		self.frame_index += 4 * dt #tốc độ gif
		if self.frame_index >= len(self.animations[self.status]):
			self.frame_index = 0

		self.image = self.animations[self.status][int(self.frame_index)]

	def input(self):
		'''
		A function that receive input from person
		Parameters:
		Return:
			None
		'''
		keys = pygame.key.get_pressed()
		#hướng đi của character
		if keys[pygame.K_w] or keys[pygame.K_UP] :
			self.direction.y = -1
			self.status = 'up'
		elif keys[pygame.K_s] or keys[pygame.K_DOWN] :
			self.direction.y = 1
			self.status = 'down'
		else:
			self.direction.y = 0

		if keys[pygame.K_d] or keys[pygame.K_RIGHT] :
			self.direction.x = 1
			self.status = 'right'
		elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
			self.direction.x = -1
			self.status = 'left'
		else:
			self.direction.x = 0
		
		click = pygame.mouse.get_pressed()
		current_time = pygame.time.get_ticks()
		
		if self.cooldown >= 0:
			self.cooldown -= 4
		if keys[pygame.K_SPACE]:
			if self.cooldown < 0:
				self.create_bullet()
				self.cooldown = 1000
		 
	def collision(self):
		'''
		A function that detect collision and prevent player go overlap the objects
		Parameters:
		Return
			None
		'''
		collision_sprites = pygame.sprite.spritecollide(self,self.obstacles, False)
		if collision_sprites:
			for sprite in collision_sprites:
					#collision on the right
				if self.rect.right >= sprite.rect.left and self.old_rect.right <= sprite.old_rect.left:
					self.rect.right  = sprite.rect.left
					self.pos.x = self.rect.x
						
					#collision on the left
				if self.rect.left <= sprite.rect.right and self.old_rect.left >= sprite.old_rect.right:
					self.rect.left  = sprite.rect.right
					self.pos.x = self.rect.x
						 	
					#collision on the bottom
				if self.rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.old_rect.top:
					self.rect.bottom  = sprite.rect.top
					self.pos.y = self.rect.y
						
					#collision on the top
				if self.rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.old_rect.bottom:
					self.rect.top  = sprite.rect.bottom
					self.pos.y = self.rect.y	
	def window_collision(self):
		'''
		A function that prevent player go outside of the screen
		Parameters:
		Return:
			None
		'''
		if self.rect.left < 0:
			self.rect.left = 0
			self.pos.x = self.rect.x
			# self.direction.x *= -1
		if self.rect.right > 1280:
			self.rect.right = 1280
			self.pos.x = self.rect.x
			# self.direction.x *= -1
		
		if self.rect.top < 0:
			self.rect.top = 0
			self.pos.y = self.rect.y
			# self.direction.y *= -1
		if self.rect.bottom > 720:
			self.rect.bottom = 720
			self.pos.y = self.rect.y
			# self.direction.y *= -1

	def get_status(self): 
		"""
		A function check if the player not moving then set the status to idle
		Parameters:
		Return:
			None
		"""
		if self.direction.magnitude() == 0:  #khong di chuyen
			self.status = self.status.split('_')[0] + '_idle'

	def move(self,dt):
		'''
		A function that move the player as the direction and the pos changing
		Parameters:
			dt (float): delta time to make the player move along with the frame
		Return:
			None
		'''
		# normalizing a vector 
		if self.direction.magnitude() > 0:
			self.direction = self.direction.normalize()

		# horizontal movement
		self.pos.x += self.direction.x * self.speed * dt
		
		self.pos.y += self.direction.y * self.speed * dt
		#self.rect.centerx = round(self.pos.x)	
		self.rect.x = round(self.pos.x)	

		# vertical movement
		self.rect.y = self.pos.y
		self.collision()
		self.window_collision()

	def create_bullet(self):
		'''
		A function create a bullet when it's called
		Parameter:
			rect.center (tuple): current location of player
			gr, bullet <class Group>: set the bullet group
			0: set the bullet id to know who shoot it
		Return:
			a bullet class
		'''
		direction = pygame.mouse.get_pos()
		return Bullet(self.rect.center,[self.gr,self.bullet],self.obstacles,0,direction)

	def health_bar(self,x = 0,y = 0,w = 640,h = 10,ratio = 1):
		'''
		A function draw a health bar and update it along to ratio
		Parameters:
			x, y (int): x, y is the left top location of the bar
			w, h (int): w, h is the width and height of the bar
			ratio (float): the rate of health
		Return:
			None
		'''
		pygame.draw.rect(self.screen, 'red', (x,y,w,h))
		pygame.draw.rect(self.screen, 'green', (x,y,w*ratio,h))
	def get_damage(self):
		'''
		A function update the health through self.ratio whenever get shoot
		Parameters:
		Return:
			None
		'''
		if pygame.sprite.spritecollide(self, self.bullet, True, pygame.sprite.collide_mask):
			self.ratio -= 0.01

		if self.ratio < 0:
			pygame.font.init()
			my_font = pygame.font.SysFont('Comic Sans MS', 30)
			text_surface = my_font.render(f'Game Over: Bear Win!', False, (0, 0, 0))
			self.screen.blit(text_surface, (500,0))
	
	def update(self, dt):
		'''
		A function update every data of the player 
		Parameter:
			dt (float): delta time
		Return:
			None
		'''
		self.old_rect = self.rect.copy()
		self.input()
		self.get_status()
		self.move(dt)
		self.animate(dt)
		self.health_bar(ratio = self.ratio)
		self.get_damage()

class Bullet(pygame.sprite.Sprite):
	'''
	A class create a bullet from player
	Attributes:
		pos (tuple): position of player when created
		group <class pygame.sprite.Group>: declare which group the bullet is in
		obstacles <class pygame.sprite.Group>: declare groups that cause collision
		side (int): to know who this bullet from
		self.image <class Surface>: 
		self.image.fill((0,255,255)):
		self.rect = self.image.get_rect(center = pos)
		self.getmouse_pos = pygame.mouse.get_pos()
		self.side = side
		self.obstacles = obstacles
		self.group = group
		self.speed = 1000
		self.old_rect = self.rect.copy()
		self.direction = pygame.math.Vector2()  #hướng đi
		self.angle = 0
		self.angle_speed = 10
			
	'''
	def __init__(self, pos, group,obstacles,side,direction):
		super().__init__(group)
		self.image = pygame.Surface((10,10))
		self.image.fill((0,255,255))
		self.rect = self.image.get_rect(center = pos)
		self.mask = pygame.mask.from_surface(self.image)
		self.getmouse_pos = pygame.mouse.get_pos()
		self.side = side
		self.obstacles = obstacles
		self.group = group
		self.speed = 1000
		self.old_rect = self.rect.copy()
		self.angle = 0
		self.angle_speed = 10
		self.direction = direction
		self.nor_direct = pygame.math.Vector2()
		self.direct()
		

	def collision(self):
		#if self.rect.colliderect(self.obstacles.rect):
			# collision_sprites.append(self.obstacles)
		if pygame.sprite.spritecollide(self,self.obstacles, False,pygame.sprite.collide_mask):
			self.image = pygame.Surface((20,20))
			self.image.fill((0,255,0))
			self.speed = 2500
		#window
		if self.rect.left < 0 or self.rect.right > 1280 or self.rect.top < 0 or self.rect.bottom > 720:
			# self.group[0].remove(self)
			self.kill()

	def direct(self):
		self.nor_direct.x = self.direction[0] - self.rect.x
		self.nor_direct.y = self.direction[1] - self.rect.y
		if self.nor_direct.magnitude() > 0:
			self.nor_direct = self.nor_direct.normalize()

	def update(self,dt):
		self.old_rect = self.rect.copy()
		self.rect.x += self.speed * dt * self.nor_direct.x
		self.rect.y += self.speed * dt * self.nor_direct.y
		self.collision()
	

class NPC(Player):
	def __init__(self, pos, group, obstacles,bullet):   #vị trí và camera
		super().__init__(pos, group, obstacles,bullet)
		#load the gif before 
		self.import_assets()
		self.status = 'left'
		self.frame_index = 1

		# general setup
		self.image = self.animations[self.status][self.frame_index]#image
		self.rect = self.image.get_rect(center = pos)
		self.old_rect = self.rect.copy()
		self.obstacles = obstacles

		# movement attributes
		self.direction = pygame.math.Vector2()  #hướng đi
		self.destination = pygame.math.Vector2()  #hướng đi
		self.pos = pygame.math.Vector2(self.rect.center)  #vị trí
		self.speed = 300
		self.cooldown = -1

		## self.heal = 100
		self.gr = group
	#animation of character
	def import_assets(self):
		#chứa gif
		self.animations = {'up': [],'down': [],'left': [],'right': [],
						   'right_idle':[],'left_idle':[],'up_idle':[],'down_idle':[],
						   'right_hoe':[],'left_hoe':[],'up_hoe':[],'down_hoe':[],
						   'right_axe':[],'left_axe':[],'up_axe':[],'down_axe':[],
						   'right_water':[],'left_water':[],'up_water':[],'down_water':[]}
		for animation in self.animations.keys():
			full_path = '../graphics/character/' + animation
			self.animations[animation] = import_folder(full_path)

######################################################################
	#Nhận input từ bàn phím
	def input(self):
		keys = pygame.key.get_pressed()
		if pygame.mouse.get_pressed()[2]:
			self.destination.x, self.destination.y = map(int, pygame.mouse.get_pos())
			self.direction.x = self.destination.x - self.rect.center[0]
			self.direction.y = self.destination.y - self.rect.center[1]
		if self.direction.magnitude() > 0:
			self.direction = self.direction.normalize()
		
		if self.direction.x > 0:
			self.status = 'right'
		else:
			self.status = 'left'
		

		if abs(self.destination.x - self.pos.x) < 10 or abs(self.destination.y - self.pos.y) < 10:
			self.direction.x = 0
			self.direction.y = 0
		
		if self.cooldown >= 0:
			self.cooldown -= 4
		if pygame.mouse.get_pressed()[0]:
			if self.cooldown < 0:
				self.create_bullet()
				self.cooldown = 1000
	def create_bullet(self):
		'''
		A function create a bullet when it's called
		Parameter:
			rect.center (tuple): current location of player
			gr, bullet <class Group>: set the bullet group
			0: set the bullet id to know who shoot it
		Return:
			a bullet class
		'''
		direction = pygame.mouse.get_pos()
		return Bullet(self.rect.center,[self.gr,self.bullet],self.obstacles,1,direction)

	def health_bar(self,x = 640,y = 0,w = 640,h = 10,ratio =1):
		pygame.draw.rect(self.screen, 'red', (x,y,w,h))
		pygame.draw.rect(self.screen, 'green', (1280-w*ratio,y,w*ratio,h))		 
	def get_damage(self):
		collision_sprites = pygame.sprite.spritecollide(self,self.bullet, False)
		for sprite in collision_sprites:
			if sprite.side == 0:
				self.ratio -= 0.01
		if self.ratio < 0:
			pygame.font.init()
			my_font = pygame.font.SysFont('Comic Sans MS', 30)
			text_surface = my_font.render(f'Game Over: Soldier Win!', False, (0, 0, 0))
			self.screen.blit(text_surface, (500,0))	 
	