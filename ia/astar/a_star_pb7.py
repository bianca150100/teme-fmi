"""Problema 7 - Evadarea lui Mormolocel"""

from collections import namedtuple
from copy import deepcopy
from math import sqrt


Punct = namedtuple("Punct", ("x, y"))

Frunza = namedtuple("Frunza", ("ident", "poz", "insecte", "gmax"))


# Centrul lacului
centru = Punct(0, 0)

frunze_initiale = {}

with open("pb7.in") as fin:
	raza = float(next(fin))
	greutate_initiala = float(next(fin))
	frunza_start = next(fin).strip()

	for line in fin:
		ident, x, y, nr_insecte, greutate_max = line.split()
		poz = Punct(float(x), float(y))
		frunze_initiale[ident] = Frunza(ident, poz, int(nr_insecte), float(greutate_max))

def distanta(p1, p2):
	"Distanța euclidiană între `p1` și `p2`"
	return sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)


def distanta_cerc(p):
	"Distanța de la `p` la cercul care formează lacul"
	return raza - distanta(p, centru)

""" definirea problemei """
class Nod:
	def __init__(self, frunze, ident_frunza, greutate):
		self.frunze = frunze
		self.ident_frunza = ident_frunza
		self.greutate = greutate
		self.info = (frunze, ident_frunza, greutate)
		self.h = distanta_cerc(self.frunza.poz)

	@property
	def frunza(self):
		return self.frunze[self.ident_frunza]

	def __repr__ (self):
		return f"({self.frunza}, {self.greutate}, h={self.h})"


class Arc:
	def __init__(self, capat, varf, cost):
		self.capat = capat
		self.varf = varf
		self.cost = cost

""" Sfarsit definire problema """



""" Clase folosite in algoritmul A* """

class NodParcurgere:
	"""O clasa care cuprinde informatiile asociate unui nod din listele open/closed
		Cuprinde o referinta catre nodul in sine (din graf)
		dar are ca proprietati si valorile specifice algoritmului A* (f si g).
		Se presupune ca h este proprietate a nodului din graf

	"""


	def __init__(self, nod_graf, parinte=None, g=0, f=None):
		self.nod_graf = nod_graf	# obiect de tip Nod
		self.parinte = parinte		# obiect de tip Nod
		self.g = g					# costul drumului de la radacina pana la nodul curent
		self.f = self.g + self.nod_graf.h


	def drum_arbore(self):
		"""
			Functie care calculeaza drumul asociat unui nod din arborele de cautare.
			Functia merge din parinte in parinte pana ajunge la radacina
		"""
		nod_c = self
		drum = [nod_c]
		while nod_c.parinte is not None :
			drum = [nod_c.parinte] + drum
			nod_c = nod_c.parinte
		return drum


	def contine_in_drum(self, nod):
		"""
			Functie care verifica daca nodul "nod" se afla in drumul dintre radacina si nodul curent (self).
			Verificarea se face mergand din parinte in parinte pana la radacina
			Se compara doar informatiile nodurilor (proprietatea info)
			Returnati True sau False.

			"nod" este obiect de tip Nod (are atributul "nod.info")
			"self" este obiect de tip NodParcurgere (are "self.nod_graf.info")
		"""
		nod_curent = self
		while nod_curent:
			if nod_curent.nod_graf.info == nod.info:
				return True
			nod_curent = nod_curent.parinte
		return False

	#se modifica in functie de problema
	def expandeaza(self):
		"""Pentru nodul curent (self) parinte, trebuie sa gasiti toti succesorii (fiii)
		si sa returnati o lista de tupluri (nod_fiu, cost_muchie_tata_fiu),
		sau lista vida, daca nu exista niciunul.
		(Fiecare tuplu contine un obiect de tip Nod si un numar.)
		"""
		frunze, ident_frunza, greutate = self.nod_graf.info
		frunza = frunze[ident_frunza]
		succesori = []
		for frunza_noua in frunze.values():
			if frunza.ident == frunza_noua.ident:
				continue

			for insecte_consumate in range(0, frunza.insecte + 1):
				greutate_noua = greutate + insecte_consumate

				if distanta(frunza.poz, frunza_noua.poz) > greutate_noua / 3:
					continue

				greutate_noua -= 1

				if greutate_noua > frunza_noua.gmax:
					continue

				if greutate_noua == 0:
					continue

				frunze_noi = deepcopy(frunze)
				frunze_noi[frunza.ident] = Frunza(
					frunza.ident,
					frunza.poz,
					frunza.insecte - insecte_consumate,
					frunza.gmax,
				)

				nod = Nod(frunze_noi, frunza_noua.ident, greutate_noua)
				succesori.append((nod, 1))

		return succesori


	#se modifica in functie de problema
	def test_scop(self):
		frunza = self.nod_graf.frunza
		greutate = self.nod_graf.greutate
		return distanta_cerc(frunza.poz) <= greutate / 3


	def __str__ (self):
		parinte = self.parinte if self.parinte is None else self.parinte.nod_graf.info
		return f"({self.nod_graf}, parinte={parinte}, f={self.f}, g={self.g})"



""" Algoritmul A* """


def str_info_noduri(l):
	"""
		o functie folosita strict in afisari - poate fi modificata in functie de problema
	"""
	sir="["
	for x in l:
		sir+=str(x)+"  "
	sir+="]"
	return sir


def afis_succesori_cost(l):
	"""
		o functie folosita strict in afisari - poate fi modificata in functie de problema
	"""
	sir=""
	for (x, cost) in l:
		sir+="\nnod: "+str(x)+", cost arc:"+ str(cost)

	return sir


def in_lista(l, nod):
	"""
	lista "l" contine obiecte de tip NodParcurgere
	"nod" este de tip Nod
	"""
	for i in range(len(l)):
		if l[i].nod_graf.info == nod.info:
			return l[i]
	return None


def a_star():
	nod_start = Nod(frunze_initiale, frunza_start, greutate_initiala)
	rad_arbore = NodParcurgere(nod_start)
	open = [rad_arbore]		# open va contine elemente de tip NodParcurgere
	closed = []				# closed va contine elemente de tip NodParcurgere

	while open: # cât timp mai avem noduri neexplorate
		# se scoate nodul din open
		nod_curent = open.pop(0)

		# se pune în closed
		closed.append(nod_curent)

		if nod_curent.test_scop(): # am ajuns la țintă
			break

		drum = nod_curent.drum_arbore()

		for succesor, cost in nod_curent.expandeaza():
			if in_lista(drum, succesor):
				continue

			nod_open = in_lista(open, succesor) # îl caut în lista open
			nod_closed = in_lista(closed, succesor) # îl caut în lista closed

			# calculez distanța dacă ar fi să trec prin `nod_curent` să ajung la succesor
			g_nou = nod_curent.g + cost

			if nod_open: # dacă l-am găsit încerc să îl actualizez
				# dacă am găsit o distanță mai bună
				if g_nou < nod_open.g:
					nod_open.g = g_nou
					nod_open.f = g_nou + nod_open.nod_graf.h
					nod_open.parinte = nod_curent

			elif nod_closed:
				f_nou = g_nou + nod_closed.nod_graf.h

				if f_nou < nod_closed.f:
					nod_closed.g = g_nou
					nod_closed.f = f_nou + nod_closed.nod_graf.h
					nod_closed.parinte = nod_curent

					# dacă l-am actualizat, se mută înapoi în open,
					# ca să îi re-explorez vecini
					open.append(nod_closed)
			else:
				# nu e în nicio listă, îl pun în open inițial
				nod_nou = NodParcurgere(
					nod_graf=succesor,
					parinte=nod_curent,
					g=g_nou
				)

				open.append(nod_nou)

		# teoretic ar trebui ca `open` să fie max heap,
		# dar merge și dacă îl sortez și scot mereu minimul
		open.sort(key=lambda nod: nod.f)

	if(len(open)==0):
		print("Broscuta nu poate ajunge la mal")
	else:
		drum = nod_curent.drum_arbore()
		for nod in drum:
			nod_graf = nod.nod_graf
			frunze, ident_frunza, greutate = nod_graf.info
			print(f"Broscuta a sarit la {ident_frunza}. Greutate: {greutate}")

if __name__ == "__main__":
	a_star()
