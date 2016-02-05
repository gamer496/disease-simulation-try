from random import random,randint,sample
import matplotlib.pyplot as plt

# going by the solution of the previous project no more libraries were imported

def rolldie(p):
	return (random()<=p)

class Disease():
	def __init__(self,name="influenza",t=0.95,E=2,I=7,r=0.0,Q=0):		#Q intriduced and been initialized in the constructor
		self.name=name
		self.t=t
		self.E=E
		self.I=I
		self.r=r
		self.Q=self.I-1

	def quarantine(self,Q):
		self.Q=Q

class Agent():
	def __init__(self,s=0.99,q=1,type=-1,cf=[0]):	#q is the complainer cf the agents contact probability and type is the integer type of person
		# most of the variable are initialized to either empty or None unless given otherwise
		# some initial values have been approprialtely assumed as none were given for them
		self.s=s
		self.v=1.0
		self.c=-1
		self.disease=None
		self.q=rolldie(random())
		if self.q==0 or self.disease==None:
			self.days=0
		else:
			self.days=self.disease.Q
		self.type=type
		self.cf=cf

	def state(self):
		return (self.c>0)

	def vaccinate(self,v):
		self.v=v

	def infect(self,other,disease):		#cf other type included in probability
		if other.state() and self.c<0 and rolldie(self.s*self.v*disease.t*self.cf[other.type]):
			self.c=disease.E+disease.I+1
			self.disease=disease
			return True
		return False

	def update(self):
		# Update method as been modified to accomodate quarantine
		# A person won't affect other people until he's in quarantine
		# his complaince is based on probability of rolldie
		if self.c==1:
			if not rolldie(self.disease.r):
				self.c=-1
			else:
				self.c=0
			self.disease=None
			return False
		elif self.c>1:
			self.c=self.c-1
			if self.days>0:
				self.days-=1
				return False
			else:
				self.q=rolldie(random())
				if self.q==0:
					return True
				else:
					self.days=self.disease.Q
				return False

class Simulation():
	def __init__(self,D=500,m=0.001,agents=None):
		# Init method takes agents as input also.
		# Agents is a list of lists of probability of contact.A matrix.
		# some modifications have been made to the data structures in order to accumulate multiple diseases.
		# self.history has been modified to be a dictionary data sturcture
		# So has been self.vaccine
		# events have been included and appropriate changes made in run and agents quarantine and campaign
		self.steps=D
		self.diseases=[]
		self.agents=[]
		self.history={}
		self.m=0.001
		self.events={}
		self.vaccine={}
		self.type=-1
		for agent_interaction in agents:
			self.type=self.type+1
			self.add(type=self.type,cf=agent_interaction)

	def populate(self,n,m=0.001,type=-1,cf=[0]):
	# populate combined with add generates new agents with parameters specified
		self.m=m
		for i in range(n):
			if type==-1:
				if self.type==-1:
					typ=0
				else:
					typ=randint(0,self.type)
			else:
				typ=type
			if cf==[0]:
				cf=[0]*(self.type+1)
				for i in range(0,self.type+1):
					cf[i]=random()
			self.join(Agent(type=type,cf=cf))

	def add(self,n=1,type=-1,cf=[0]):
		self.populate(n,type=type,cf=cf)

	def join(self,agent):
		self.agents.append(agent)

	def introduce(self,disease,time):
		self.diseases.append((disease,time))

	# campaign and quarantine are the simulations referred to in problem statements as health measures being taken.
	def campaign(self,time=0,disease=None,coverage=0,v=0):
		self.events['time']=time
		self.events['disease']=disease
		self.events['coverage']=coverage
		self.events['v']=v

	def quarantine(self,time=0,disease=None,Q=0):
		self.events['time']=time
		self.events['disease']=disease
		self.events['Q']=Q
		for i in range(0,self.diseases.__len__()):
			if self.diseases[i][0].name==disease.name:
				self.diseases[i][0].Q=Q


	def seed(self,time,disease,n,k=1):
		self.introduce(disease,time)
		l=self.agents.__len__()
		j=0
		while j<n:
			f=randint(0,l-1)
			if self.agents[f].disease==None:
				self.agents[f].c=disease.E+disease.I+1
				self.agents[f].disease=disease
				j+=1


	# run method has been vastly modified primarily to accomodate multiple diseases
	# And due to the updated datastructures
	# It should be noted the run method keeps that of both campaign and quarantine periods.
	# Also it is to be noted that function runs on all diseases it is the plot function that handles specific diseases.
	def run(self):
		for (disease,time) in self.diseases:
			self.history[disease]=[]
		for agent in self.agents:
			if agent.cf.__len__()<self.type:
				le=agent.cf.__len__()
				for i in range(le,self.type):
					agent.cf.append(random())
		for i in range(self.steps):
			for (disease,time) in self.diseases:
				if i>time+disease.I:
					continue
				contagious=[a for a in self.agents if a.update() ]
				self.history[disease].append((len([a for a in contagious if a.c>disease.I]),len([a for a in contagious if a.c>=disease.I])))
				if self.history[disease][-1]==(0,0):
					return i
				for a2 in self.agents:
					flag=False
					for a1 in contagious:
						if rolldie(self.m):
							k=a2.infect(a1,disease)
							flag=flag or k
					if flag:
						if rolldie(self.events['coverage']):
							for a2 in self.agents:
								a2.vaccinate(self.events['v'])
								if self.vaccine.has_key(a2.disease):
									self.vaccine[a2.disease]+=a2.v
								else:
									self.vaccine[a2.disease]=a2.v
				# self.history[disease].append((len([a for a in contagious if a.c>disease.I]),len([a for a in contagious if a.c>=disease.I])),k)
		return self.history

	def plot(self,disease):
		plt.title('Simulation')
		l=[]
		for x in self.agents:
			if x.disease!=None and x.disease.name==disease.name:
				l.append(x)
		plt.axis([0,len(self.history[disease]),0,len(l)])
		plt.xlabel('Days')
		plt.ylabel('N')
		plt.plot([i for i in range(len(self.history[disease]))],[e for (e,i) in self.history[disease]],'g-',label='Exposed')
		plt.plot([i for i in range(len(self.history[disease]))],[i for (e,i) in self.history[disease]],'r-',label='Infected')
		plt.show()

	# config file to run the python commands from a text file right away.
	def config(self,filename):
		f=open(filename,"r")
		for line in f.readlines():
			exec(line)

# if __name__=="__main__":
# 	s=Simulation(500,0.001,[[1.0,0.5,0.5],[0.5,1.0,0.5],[0.5,0.5,1.0]])
# 	s.add(100,0)
# 	s.add(100,1)
# 	s.add(200,2)
# 	influenza=Disease(name="influenza",t=0.95,E=2,I=7,r=0)
# 	mumps=Disease(name="mumps",t=0.99,E=2,I=7,r=0.99)
# 	s.seed(0,influenza,3)
# 	s.seed(24,mumps,10)
# 	s.quarantine(40,mumps,10)
# 	s.campaign(25,influenza,0.9,0.85)
# 	s.run()
# 	s.plot(influenza)
#  	s.plot(mumps)
s=Simulation(500,0.001,[[1.0,0.5,0.5],[0.5,1.0,0.5],[0.5,0.5,1.0]])
s.config("this.txt")