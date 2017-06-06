# -*- coding: cp1252 -*-
from Tkinter import *
import tkFileDialog as tfd
import PIL
from PIL import Image, ImageTk
import os
import numpy as np
import cv2
from threading import Thread

class Draw(Frame):
    "classe définissant la fenêtre principale du programme"
    def __init__(self, fenetre, **kwargs):
        Frame.__init__(self, fenetre, **kwargs)
        #self.grid(row=3, column=3, sticky="n")
        self.pack(fill=BOTH)

        self.bouton_parcourir = Button(self, text="Parcourir...", command=self.findpicture)
        self.bouton_parcourir.grid(row=0, column=0, sticky="w")
        self.bouton_parcourir.pack()

        self.dem = Image.open(open("demarrer.jpg","rb"))
        x = 50
        y = 50
        resolution = (x,y)
        self.photodem = ImageTk.PhotoImage(self.dem.resize(resolution))
        self.bouton_modifier = Button(self, image=self.photodem, text="Modifier l'image",state='disabled', command=self.play)
        self.bouton_modifier.grid(row=1, column=0, sticky="w")
        self.bouton_modifier.pack()

        self.bouton_quitter = Button(self, text="Quitter", command=fenetre.destroy)
        self.bouton_quitter.grid(row=3, column=0, sticky="w")
        self.bouton_quitter.pack()

        self.consigne = Label(self, text="Consigne 1 : Ajouter une image...",fg="red", font=("Calibri", 18))
        self.consigne.grid(row=4, column=0, sticky="n")
        self.consigne.pack()

        self.can = Canvas(self, bg='white', width=500, height=500)
        self.can.grid(row=0,column=1, sticky="n")
        self.can.pack()

        self._thread = None

        self.createvariables(self.can)
        self.can.bind( "<Button-1>", self.startRect )
        self.can.bind( "<ButtonRelease-1>", self.stopRect )
        self.can.bind( "<Motion>", self.movingRect )

    def createvariables(self,parent):
        self.parent = parent
        self.rectx0 = 0
        self.recty0 = 0
        self.rectx1 = 0
        self.recty1 = 0
        self.rectid = None
        self.move = False

    def startRect(self, event):
        if self.rectid != None :
            self.can.delete(self.rect)
        self.move = True
        #Translate mouse screen x0,y0 coordinates to canvas coordinates
        self.rectx0 = self.can.canvasx(event.x)
        self.recty0 = self.can.canvasy(event.y) 
        #Create rectangle
        self.rect = self.can.create_rectangle(self.rectx0, self.recty0, self.rectx0, self.recty0, fill="#fff")
        #Get rectangle's canvas object ID
        self.rectid = self.can.find_closest(self.rectx0, self.recty0, halo=2)
        print('Rectangle x0, y0 = {1}, {2}'.
              format(self.rect, self.rectx0, self.recty0, self.rectx0,
                     self.recty0))

    def movingRect(self, event):
        if self.move: 
            #Translate mouse screen x1,y1 coordinates to canvas coordinates
            self.rectx1 = self.can.canvasx(event.x)
            self.recty1 = self.can.canvasy(event.y)
            #Modify rectangle x1, y1 coordinates
            self.can.coords(self.rectid, self.rectx0, self.recty0,
                          self.rectx1, self.recty1)

    def stopRect(self, event):
        self.move = False
        #Translate mouse screen x1,y1 coordinates to canvas coordinates
        self.rectx1 = self.can.canvasx(event.x)
        self.recty1 = self.can.canvasy(event.y) 
        #Modify rectangle x1, y1 coordinates (final)
        self.can.coords(self.rectid, self.rectx0, self.recty0,
                      self.rectx1, self.recty1)
        print 'Rectangle x1, y1 = ', self.rectx1, self.recty1
        print 'Rectangle dessiné'

    def findpicture(self):
        self.image = None
        self.filepath = tfd.askopenfilename(title="Ouvrir une image",filetypes=[('jpg files','.jpeg'),('all files','.*')])
        self.displaypicture(self.filepath, True)

    def displaypicture(self,path,isokornot):
        self.image = Image.open(open(path,"rb"))
        x = 1680
        y = 1050
        resolution = (x/2, y/2)
        self.new_img = self.image.resize((x,y))
        self.new_img.save("im_resized.jpg", format="jpeg", optimize=True)
        self.photo = ImageTk.PhotoImage(self.new_img.resize(resolution))
        self.item = self.can.create_image(0,0,anchor = NW,image=self.photo)
        width, height = self.new_img.size
        self.can.config(width=width/2,height=height/2)
        if isokornot is True :            
            self.bouton_modifier.config(state='active')
            self.consigne.config(text="Consigne 2 : Selectionner un rectangle pour appliquer le masque")
        else :
            self.bouton_modifier.config(state='disabled')

            

    def modificationimage(self):
        try:
            os.mkdir("resultat_intermediaire")
        except OSError:
            pass

        self.consigne.config(text="Consigne 3 : Patientez le temps que le programme tourne ... ")

        #Lecture image de base en couleur
        im = cv2.imread("im_resized.jpg")
        #Lecture image de base en noir et blanc
        im0 = cv2.imread("im_resized.jpg",0)

        #Variable pour masque utiliser plus tard
        mask = np.zeros(im.shape[:2],np.uint8)

        #Quantification en 4 couleurs
        imgx75 = 75.*np.floor(im/75.)
        cv2.imwrite("resultat_intermediaire/image75.png", imgx75)
        self.displaypicture("resultat_intermediaire/image75.png",False)

        #Quantification en 3 couleurs
        imgx100 = 100.*np.floor(im/100.)
        cv2.imwrite("resultat_intermediaire/image100.png", imgx100)
        self.displaypicture("resultat_intermediaire/image100.png",False)

        #Quantification en 2 couleurs
        imgx150 = 150.*np.floor(im/150.)
        cv2.imwrite("resultat_intermediaire/image150.png", imgx150)
        self.displaypicture("resultat_intermediaire/image150.png",False)

        #Lecture image quantifiee en 3 couleurs
        img = cv2.imread("resultat_intermediaire/image100.png")

        #Detection des contour image en noir et blanc
        edges = cv2.Canny(im0,200,200)
        #Inversion du noir et blanc
        ret, im_bin3 = cv2.threshold(edges, 50, 255, cv2.THRESH_BINARY_INV)
        print ret
        #Conversion du noir et blanc vers 3 couleurs
        im_hls=cv2.cvtColor(im_bin3, cv2.COLOR_GRAY2RGB)
        cv2.imwrite("resultat_intermediaire/Dessin.png",im_hls)
        self.displaypicture("resultat_intermediaire/Dessin.png",False)

        #Tableau de flottant pour precision du masque
        bgdModel = np.zeros((1,65),np.float64)
        fgdModel = np.zeros((1,65),np.float64)

        #Coordonnees du masque a appliquer sur image de base
        self.rectx0 = int(round(self.rectx0))
        self.recty0 = int(round(self.recty0))
        self.rectx1 = int(round(self.rectx1))
        self.recty1 = int(round(self.recty1))
        if self.rectx0 != 0 :
            rect_corp = (self.rectx0*2,self.recty0,(self.rectx1-self.rectx0)+self.rectx0,(self.recty1+self.recty0)+self.recty0)
        else :
            rect_corp = (580,250,530,800)
        cv2.grabCut(im,mask,rect_corp,bgdModel,fgdModel,1,cv2.GC_INIT_WITH_RECT)

        #Application du masque
        mask2 = np.where((mask==2)|(mask==0),0,1).astype('uint8')
        img1_corp = im*mask2[:,:,np.newaxis]

        #Flouttage image masquee
        im_med_corp = cv2.medianBlur(img1_corp, 9)

        #Separation des couleurs en 3 variables
        b, g, r = cv2.split(im_med_corp)

        #Changer pixel du noir vers le blanc
        for j in range(0,1680):
                for i in range(0,1050):
                        if g[i][j] ==0 & r[i][j] ==0 & b[i][j] ==0:
                                g[i][j]=255
                                r[i][j]=255
                                b[i][j]=255

        #Fusion des pixel entre eux
        im_blc_corp = cv2.merge((b,g,r))

        #Superposition de l'image masquee avec image contour noir et blanc
        superpo = cv2.addWeighted(im_blc_corp,0.7,im_hls,0.5,0)
        cv2.imwrite("resultat_intermediaire/Back_SuperposCorps.png",superpo)
        self.displaypicture("resultat_intermediaire/Back_SuperposCorps.png",False)

        im_hls=cv2.cvtColor(im_bin3, cv2.COLOR_GRAY2RGB)

        #Coordonnees du masque a appliquer sur image de base
        rect_nuage = (10,10,1670,1040)
        cv2.grabCut(img,mask,rect_nuage,bgdModel,fgdModel,1,cv2.GC_INIT_WITH_RECT)

        #Application du masque
        mask2_nuage = np.where((mask==2)|(mask==0),0,1).astype('uint8')
        img1_nuage = img*mask2_nuage[:,:,np.newaxis]

        #Flouttage image masquee
        im_med_nuage = cv2.medianBlur(img1_nuage, 9)

        #Superposition masque du fond et premiere superposition
        superpo1 = cv2.addWeighted(im_med_nuage,0.5,superpo,0.7,0)
        cv2.imwrite("resultat_intermediaire/Back_SuperposFond.png",superpo1)
        self.displaypicture("resultat_intermediaire/Back_SuperposFond.png",False)

        #Stockage horizontale image contour noir et blanc et 1ere superposition
        bd1 = np.hstack((im_hls,superpo))
        cv2.imwrite("resultat_intermediaire/BD1.png",bd1)
        self.displaypicture("resultat_intermediaire/BD1.png",False)

        #Stockage horizontale image precedente et 2nd superposition
        bd2 = np.hstack((bd1,superpo1))
        cv2.imwrite("resultat_intermediaire/BD2.png",bd2)
        self.displaypicture("resultat_intermediaire/BD2.png",False)

        #Stockage horizontale image 2 couleurs et image 3 couleurs
        bd3 = np.hstack((imgx150,imgx100))
        cv2.imwrite("resultat_intermediaire/BD3.png",bd3)
        self.displaypicture("resultat_intermediaire/BD3.png",False)

        #Stockage horizontale image precedente et image 4 couleurs
        bd4 = np.hstack((bd3,imgx75))
        cv2.imwrite("resultat_intermediaire/BD4.png",bd4)
        self.displaypicture("resultat_intermediaire/BD4.png",False)

        #Stockage verticale image contour noir et blanc, 1ere superposition
        #et 2nd superposition avec image precedente
        bd5 = np.vstack((bd2,bd4))
        cv2.imwrite("Rendu.png",bd5)
        self.displaypicture("Rendu.png",False)
        print "Rendu ok !"
        
        self.bouton_parcourir.config(state='active')
        self._thread = None
        self.consigne.config(text="Consigne 4 : Retrouvez toutes les images créées dans le dossier racine !\nRechargez une image si vous le souhaitez pour recommencer")    

    def play(self):
        print "Travail en cours..."
        self.bouton_modifier.config(state='disabled')
        self.bouton_parcourir.config(state='disabled')
        if self._thread is None:
            self._thread = Thread(target=self.modificationimage)
            self._thread.start()       

fenetre = Tk()
fenetre.title("Générateur de Bande Dessinée")
interface = Draw(fenetre)
interface.mainloop()
interface.destroy()
