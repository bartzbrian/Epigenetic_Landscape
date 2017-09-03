import launchpad_py as lpad

class LP:

	def __init__(self):
		self.controller = lpad.Launchpad()
		self.model_params = [] #initialize model parameters

		#these are tedious mappings that bind the launchpad buttons to certain motor functionality and model parameters
		self.init_map = {0:[23,'u'],1:[24,'u'],2:[0,'u'],3:[1,'u'],4:[2,'u'],5:[3,'u'],16:[23,'d'],17:[24,'d'],18:[0,'d'],19:[1,'d'],20:[2,'d'],21:[3,'d'],32:[4,'u'],33:[5,'u'],34:[6,'u'],35:[7,'u'],36:[8,'u'],37:[9,'u'],48:[4,'d'],49:[5,'d'],50:[6,'d'],51:[7,'d'],52:[8,'d'],53:[9,'d'],64:[10,'u'],65:[11,'u'],66:[12,'u'],67:[13,'u'],68:[14,'u'],69:[15,'u'],80:[10,'d'],81:[11,'d'],82:[12,'d'],83:[13,'d'],84:[14,'d'],85:[15,'d'],96:[16,'u'],97:[17,'u'],98:[18,'u'],99:[19,'u'],100:[20,'u'],101:[21,'u'],102:[22,'u'],112:[16,'d'],113:[17,'d'],114:[18,'d'],115:[19,'d'],116:[20,'d'],117:[21,'d'],118:[22,'d']}
		self.param_map = {0:100,1:100,2:100,3:100,4:100,5:100,6:100,7:100,16:85.8,17:85.8,18:85.8,19:85.8,20:85.8,21:85.8,22:85.8,23:85.8,32:71.6,33:71.6,34:71.6,35:71.6,36:71.6,37:71.6,38:71.6,39:71.6,48:57.4,49:57.4,50:57.4,51:57.4,52:57.4,53:57.4,54:57.4,55:57.4,64:43.2,65:43.2,66:43.2,67:43.2,68:43.2,69:43.2,70:43.2,71:43.2,80:29,81:29,82:29,83:29,84:29,85:29,86:29,87:29,96:14.4,97:14.4,98:14.4,99:14.4,100:14.4,101:14.4,102:14.4,103:14.4,112:0.1,113:0.1,114:0.1,115:0.1,116:0.1,117:0.1,118:0.1,119:0.1,}


	def get_params(self):
		self.controller.Open()
		self.controller.Reset()
		active = True
		params = []
		while active:
			if len(params) == 8:
				return params
			else:
				xs = self.controller.ButtonStateRaw()
				if xs != []:
					if xs[0] in self.param_map:
						params.append(self.param_map[xs[0]])
						self.controller.LedCtrlRaw(xs[0],0,3)

				if xs[0] == 207:
					lp.LedCtrlString( "RANDOM!", 0,3, direction = -1, waitms = 100 )
					return 'random'




	def init_mode_LED(self):

		self.controller.Reset()

		for x in xrange(0,6):
			self.controller.LedCtrlRaw(x,0,3)

		for x in xrange(16,22):
			self.controller.LedCtrlRaw(x,0,3)

		for x in xrange(32,38):
			self.controller.LedCtrlRaw(x,3,3)

		for x in xrange(48,54):
			self.controller.LedCtrlRaw(x,3,3)

		for x in xrange(64,70):
			self.controller.LedCtrlRaw(x,3,0)

		for x in xrange(80,86):
			self.controller.LedCtrlRaw(x,3,0)

		for x in xrange(96,103):
			self.controller.LedCtrlRaw(x,0,3)

		for x in xrange(112,119):
			self.controller.LedCtrlRaw(x,0,3)
			
