from django.db import models

class Simulation(models.Model):
	dyn_id = models.CharField(max_length=200)
	receptor_name = models.CharField(max_length=200)

class Positions(models.Model):
	residues = models.CharField(max_length=200)

class Itype(models.Model):
	type_id = models.CharField(max_length=50)

class Interaction(models.Model):
	frequency = models.FloatField()
	simulation = models.ForeignKey(Simulation, related_name='membership', on_delete=models.CASCADE)
	positions = models.ForeignKey(Positions, related_name='membership', on_delete=models.CASCADE)
	itype = models.ForeignKey(Itype, related_name='membership', on_delete=models.CASCADE)

