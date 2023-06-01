from tkinter import *
from time import *
from random import *


def _from_rgb(rgb):
  """translates an rgb tuple of int to a tkinter friendly color code
    """
  r, g, b = rgb
  return f'#{r:02x}{g:02x}{b:02x}'


nb_colonnes = 8
nb_lignes = 12
taille_case = 50

fenetre = Tk()
infos = Label(fenetre, text='Score: 0')
infos.grid(column=0, row=0)
infos.pack()
plateau = Canvas(fenetre,
                 background="#000000",
                 width=nb_colonnes * taille_case + 6 * taille_case,
                 height=nb_lignes * taille_case)
plateau.pack()
plateau.create_rectangle((nb_colonnes + 1) * taille_case,
                         taille_case, (nb_colonnes + 5) * taille_case,
                         5 * taille_case,
                         outline='white')
for x in range(nb_colonnes):
  for y in range(nb_lignes):
    plateau.create_rectangle(x * taille_case,
                             y * taille_case,
                             x * taille_case + taille_case,
                             y * taille_case + taille_case,
                             outline="white")

colors = [
  (0, 0, 0),
  (120, 37, 179),
  (100, 179, 179),
  (80, 34, 22),
  (80, 134, 22),
  (180, 34, 22),
  (180, 34, 122),
]


class Figure:
  x = 0
  y = 0
  figures = [
    [[1, 5, 9, 13], [4, 5, 6, 7]],
    [[4, 5, 9, 10], [2, 6, 5, 9]],
    [[6, 7, 9, 10], [1, 5, 6, 10]],
    [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],
    [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],
    [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],
    [[1, 2, 5, 6]],
  ]

  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.xpre = (nb_colonnes + 1) * taille_case
    self.ypre = taille_case
    self.type = randint(0, len(self.figures) - 1)
    self.color = colors[randint(1, len(colors) - 1)]
    self.rotation = 0
    self.shapes = []
    self.futurs = []

  def destroy(self):
    for i in range(len(self.shapes)):
      print('siuuuu')
      plateau.delete(self.shapes.pop())

  def build(self):
    #construit la forme en fonction du tableau figures
    #co premières case dans figures = self.x et self.y
    for i in self.figures[self.type][self.rotation]:
      self.shapes.append(
        plateau.create_rectangle(self.x + (i % 4) * taille_case,
                                 self.y + i // 4 * taille_case,
                                 self.x + (i % 4) * taille_case + taille_case,
                                 self.y + i // 4 * taille_case + taille_case,
                                 fill=_from_rgb(self.color),
                                 outline='white'))
  def show_futur(self):
    for i in self.figures[self.type][self.rotation]:
      self.futurs.append(  
      plateau.create_rectangle(self.xpre + (i % 4) * taille_case,
                                 self.ypre + i // 4 * taille_case,
                                 self.xpre + (i % 4) * taille_case + taille_case,
                                 self.ypre + i // 4 * taille_case + taille_case,
                                 fill=_from_rgb(self.color),
                                 outline='white'))
  def hide_futur(self):
    for i in self.futurs:
      plateau.delete(i)

  def rotate(self, event):
    print('rotate')
    if event.keysym == 'd':
      self.rotation -= 1
      self.rotation %= len(self.figures[self.type])
      self.destroy()
      self.build()
    elif event.keysym == 'q':
      self.rotation += 1
      self.rotation %= len(self.figures[self.type])
      self.destroy()
      self.build()

  def bloqué(self, side, field):
    #renvoie True si la figures est bloqué du côté side
    #en fonction de side mettre difx et dify pour faire qu'une seule fois le test du 1 dans field
    #pour tester a droite: difx=1 dify=0
    #gauche: difx=-1 dify=0
    #haut: difx=0 dify=-1
    #bas: difx=0 dify=1
    #tester la case {x pièce+difx, y pièce+dify}
    stuck = False
    difx, dify = 0, 0
    if side == 'gauche':
      difx = -1
    elif side == 'droite':
      difx = 1
    elif side == 'haut':
      dify = -1
    elif side == 'bas':
      dify = 1
    i = 0
    while i < len(self.shapes) and not stuck:
      co = plateau.coords(self.shapes[i])
      #print(f"co : {co}")
      #print(f"shapes : {self.shapes}")
      if co[3] + dify * taille_case > taille_case * nb_lignes or co[
          0] + difx * taille_case < 0 or co[
            2] + difx * taille_case > nb_colonnes * taille_case or field[
              int(co[1] // taille_case) + dify][int(co[0] // taille_case) +
                                                difx] == 1:
        stuck = True
      i += 1
    return stuck

  def freeze(self, field):
    #met des 1 au bon endroit dans field
    for i in self.shapes:
      #print('aha')
      co = plateau.coords(i)
      field[int(co[1] // taille_case)][int(co[0] // taille_case)] = 1

  def move(self, x, y):
    for i in self.shapes:
      plateau.move(i, x, y)
    self.x += x
    self.y += y


class Tetris:

  def __init__(self, taille):
    self.futur = [Figure(100, 0), Figure(100, 0), Figure(100, 0)]
    self.loose = False
    self.freq = 500
    self.score = 0
    self.width = taille[0]
    self.height = taille[1]
    self.field = [[0 for x in range(taille[0])] for y in range(taille[1])]

  def ligne_completes(self):
    t = []  #lignes completes
    for i in range(len(self.field)):
      if sum(self.field[i]) == nb_colonnes:
        t.append(i)
    return t

  def supprimer_lignes(self):
    lignes = self.ligne_completes()
    #print(lignes)
    if len(lignes) >= 4:
      self.score += 10 + (len(lignes) - 4) * 2
    elif len(lignes) >= 3:
      self.score += 5
    elif len(lignes) >= 2:
      self.score += 3
    elif len(lignes) >= 1:
      self.score += 1
    else:
      return None
    for i in lignes:
      y = i * taille_case + taille_case // 2
      for x in range(taille_case // 2, self.width * taille_case, 50):
        plateau.delete(plateau.find_closest(x, y))
      self.field[i] = [0 for i in range(self.width)]
      self.descendre_blocs(i)
    print(self.score)

  def descendre_bloc(self, bloc):
    x1, y1, x2, y2 = plateau.coords(bloc)
    self.field[int(y1 // 50)][int(x1 // 50)] = 0
    plateau.move(bloc, 0, taille_case)
    x1, y1, x2, y2 = plateau.coords(bloc)
    self.field[int(y1 // 50)][int(x1 // 50)] = 1

  def descendre_blocs(self, yy):
    #descends tout les blocs du jeu
    for l in range(yy, -1, -1):
      for x in range(0, self.width, 1):
        if self.field[l][x] > 0:
          self.descendre_bloc(
            plateau.find_closest(x * taille_case + 25, l * taille_case + 25))
      l -= 1


a = Tetris((8, 12))
#print(a.field)


def keys(event, obj):
  if event.keysym == 'Right':
    if obj.x < (nb_colonnes - 1) * taille_case and a.field[int(
        obj.y // taille_case)][int(obj.x // taille_case) +
                               1] < 1 and not a.loose:
      obj.move(taille_case, 0)
  if event.keysym == 'Left':
    if obj.x > 0 and a.field[int(
        obj.y // taille_case)][int(obj.x // taille_case) -
                               1] < 1 and not a.loose:
      obj.move(-taille_case, 0)
  if event.keysym == 'Down':
    a.freq = 100
  if event.keysym == 'r' and a.loose:
    a.score = 0
    plateau.delete(plateau.find_closest(175, 25))
    a.field[0][3] = 0
    for y in range(len(a.field)):
      for x in range(len(a.field[y])):
        if a.field[y][x] == 1:
          plateau.delete(
            plateau.find_closest(x * taille_case + taille_case // 2,
                                 y * taille_case + taille_case // 2))
          a.field[y][x] = 0
    print(a.field)
    a.loose = False
    plateau.delete(f.shape)
    ff = plateau.create_rectangle(150, 0, 200, 50, fill='red', outline='white')
    fff = Figure(ff)
    test(fff)


def key(event, obj, jeu):
  if event.keysym == 'Right' and not a.loose:
    if not obj.bloqué('droite', jeu.field):
      obj.move(50, 0)
  elif event.keysym == 'Left' and not a.loose:
    if not obj.bloqué('gauche', jeu.field):
      obj.move(-50, 0)
  elif event.keysym == 'd' or event.keysym == 'q':
    obj.rotate(event)
  elif event.keysym == 'Down' and not a.loose:
    a.freq = 100
  elif event.keysym == 'r' and a.loose:
    a.score = 0
    a.futur[1].hide_futur()
    a.futur = [Figure(100, 0) for i in range(3)]
    a.futur[1].show_futur()
    obj.destroy()
    for y in range(len(a.field)):
      for x in range(len(a.field[y])):
        if a.field[y][x] == 1:
          plateau.delete(
            plateau.find_closest(x * taille_case + taille_case // 2,
                                 y * taille_case + taille_case // 2))
          a.field[y][x] = 0
    print(a.field)
    a.loose = False
    a.futur[0].build()
    test(a.futur[0])


print('a')
"""def test():
  print('a')
  t=True
  if t:
    f = Figure(100, 0)
    f.build()
    t=False
  if not f.bloqué('bas', a.field):
    print('bb')
    f.move(0, 50)
  else:
    f.freeze(a.field)
    f = Figure(100, 0)
    f.build()
    t=True

  fenetre.after(1000, test)

test()"""

def release(event):
  if event.keysym == 'Down':
    a.freq = 500


a.futur[0].build()
a.futur[1].show_futur()


def test(f):
  infos.config(text=f"Score: {a.score}")
  if not f.bloqué('bas', a.field) and sum(a.field[0][2:5]) + sum(
      a.field[1][2:5]) + sum(a.field[2][2:5]) + sum(a.field[3][2:5]) < 1:
    #print('b')
    f.move(0, 50)
    fenetre.bind('<Key>', lambda event: f.rotate(event))
    fenetre.bind('<Key>', lambda event: key(event, f, a))
    fenetre.bind('<KeyRelease-Down>', release)
    fenetre.after(a.freq, test, f)
  elif sum(a.field[0][2:5]) + sum(a.field[1][2:5]) + sum(
      a.field[2][2:5]) + sum(a.field[3][2:5]) >= 1:
    a.loose = True
    print('perdu')
    fenetre.bind('<Key>', lambda event: key(event, f, a))
    infos.config(text=f"Press R to restart - Score: {a.score} - Meilleur Score: {a.bestscore}")
  else:
    #print('c')
    f.freeze(a.field)
    #print(f"field : {a.field}")
    print('yo')
    a.futur.pop(0)
    a.futur[0].hide_futur()
    a.futur.append(Figure(100, 0))
    a.futur[1].show_futur()
    f = a.futur[0]
    f.build()
    a.supprimer_lignes()
    infos.config(text=f"Score: {a.score}")
    test(f)


"""def test(f):
  if not f.bloqué('haut', a.field):
    infos.config(text=f"Score: {a.score}")
    if not f.bloqué('bas', a.field):
      f.move(0, 50)
      fenetre.bind('<Key>', lambda event: keys(event, f))
      fenetre.bind('<KeyRelease-Down>', release)
      fenetre.after(a.freq, test, f)
    else:
      f.freeze(a.field)

      print(a.field)
      f.destroy()
      f = Figure(100, 0)
      f.build()
      a.supprimer_lignes()
      infos.config(text=f"Score: {a.score}")
      test(f)
  else:
    a.loose=True
    print('perdu')
    infos.config(text="Press R to restart")"""

test(a.futur[0])

fenetre.after(a.freq)
fenetre.mainloop()
