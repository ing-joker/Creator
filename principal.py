import tkinter as tk
from tkinter import ttk, scrolledtext,filedialog,messagebox
from tkinter.font import Font
import sqlite3,shutil
import threading
import crea_imagen_completa as ci
from PIL import Image,ImageTk
class EntryWithPlaceholder(tk.Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey',width=10,relief='solid',font=None):
        super().__init__(master)
        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']
        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)
        self["width"]=width
        self.put_placeholder()
        self["relief"]=relief
        self["font"]=font
    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color
    def foc_in(self, *args):
        if self['fg'] == self.placeholder_color:
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color
    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()

class APP(tk.Frame):
    db='fuentes/database2.db'
    arra_no_imag=[False]*37    
    posiciones=([[0,1,2,3,4,30],[5,6,7,8,9,31],[10,11,12,13,14,32],[15,16,17,18,19,33],[20,21,22,23,24,34],[25,26,27,28,29,35],[-1,-1,-1,-1,-1,36]])
    btns=[None]*37
    color_fondo_main='#060b17'
    color_fondo_extra='#2b0226'
    imagenes_main=[None]*37
    cont=0
    cont_copias=0
    con_extra=0
    con_todo=0
    copias_cartas=([[None]*37,[None]*37])
    limitaciones=[0,0,0]
    solo_nombre=["zz"]*37
    variable_tipo_c='Todas'
    variable_elemento='Todos'
    variable_rareza=''
    variable_nivel=''
    variable_tipo_m=''
    variable_limite=''
    orden='DESC'
    clave=''
    mames=True
    para_crear=[None]*37
    banlist=True
    
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.init_ui()
    
    def init_ui(self):
        self.variable_hd=tk.IntVar() 
        self.configure(bg='#c0c0c0')
        font=Font(family='Arial',size=16)
        font.metrics()
        self.font2=Font(family='Lucida Fax', size=12)
        self.font2.metrics()

###########         IMÁGENES    IMÁGENES    IMÁGENES    IMÁGENES    IMÁGENES    IMÁGENES    IMÁGENES    ########
        self.otraimage = tk.PhotoImage(file="fuentes/fondov.png" )
        self.otraimage2 = tk.PhotoImage(file="fuentes/fondom.png" )
        self.img_card = tk.PhotoImage(file='fuentes/btn_add.png')

        self.flechas = tk.PhotoImage(file = "fuentes/flecha.png")
        self.sahcelf = tk.PhotoImage(file = "fuentes/ahcelf.png")
        self.search = tk.PhotoImage(file = "fuentes/search.png")

############ ÁRBOL   ÁRBOL   ÁRBOL   ÁRBOL   ÁRBOL   ÁRBOL   ÁRBOL   #############

        style = ttk.Style()
        style.configure(".", font=('Lucida Fax', 8), foreground="black")
        style.configure("Treeview.Heading", foreground='blue',font=('Lucida Fax', 14))
        style.configure('Treeview' , rowheight=80 , font=font)

        self.mostrador = ttk.Treeview(self,height = 7,columns=("size", "lastmod"), style="mystyle.Treeview")
        self.mostrador.grid(row = 5, column = 0, columnspan = 5, rowspan=30,sticky="NSEW")
        
        self.mostrador.heading('#0', text = '', anchor = 'center')
        self.mostrador.column("#0",width=70, anchor = 'center')
        self.mostrador.heading('#1', text = 'Nombre', anchor = 'center')
        self.mostrador.column("#1",width=400, anchor = 'center')
        self.mostrador.heading('lastmod', text = 'Rareza', anchor = 'center')
        self.mostrador.column("lastmod",width=100, anchor = 'center')
        style = ttk.Style()
        style.configure("Treeview",background="#E1E1E1",foreground="#000000",fieldbackground="#E1E1E1")

        style.map('Treeview', background=[('selected', '#0000f0')], foreground=[('selected', 'white')])
        self.mostrador.bind("<Button-3>", self.popup)
        self.mostrador.bind('<<TreeviewSelect>>' and '<Button-1>', self.revision_agregado)
        vsb = ttk.Scrollbar(self,orient="vertical",   command=self.mostrador.yview)
        self.mostrador.configure(yscrollcommand=vsb.set)
        vsb.grid(column=5, row=5,rowspan=30, sticky='ns')

        self.aMenu = tk.Menu(self, tearoff=0)
        self.aMenu.add_command(label='Agregar', command=self.revision_agregado)
        self.aMenu.add_command(label='Ver', command=self.ver_carta)

###########         LABELFRAMES   LABELFRAMES   LABELFRAMES   LABELFRAMES   LABELFRAMES   LABELFRAMES   #######

        self.label=tk.LabelFrame(self,text="MAIN DECK",foreground="white" ,height=600 ,bg=self.color_fondo_main , width=400 , font=("Courier" ,18))
        self.label.grid( row=5 , column=7 ,rowspan=30, sticky="NSEW",columnspan=4)
        self.label2=tk.LabelFrame(self,text="EXTRA" ,foreground="white", height=600 ,bg=self.color_fondo_extra , width=100 ,font=("Courier" ,18))
        self.label2.grid(row=5 , column=11 ,rowspan=30, sticky="NSEW")

###########         LABELS    LABELS    LABELS    LABELS    LABELS    LABELS    LABELS    ##################
        self.letrero_tipo=ttk.Label(self, text='Tipo de Carta',font=self.font2,background='#093992',foreground='white',anchor = 'center')
        self.letrero_tipo.grid(row=4,column=0,sticky="NSEW")

        self.letrero_limite=ttk.Label(self,text='Limitación:',font=self.font2,background='#093992',foreground='white',anchor = 'center',width=12)
        self.letrero_limite.grid(row=4,column=2,sticky="NSEW")

        self.letrero_busqueda=ttk.Label(self, text='Búsqueda:              ',font=self.font2,background='#093992',foreground='white',anchor = 'center',relief='solid')
        self.letrero_busqueda.grid(row=3,column=0,sticky="NSW", pady=(0,2),columnspan=2,ipadx=25)

        self.letrero_habilidad=ttk.Label(self, text='Habilidad:',font=self.font2,background='#093992',foreground='white',anchor = 'center')
        self.letrero_habilidad.grid(row=3,column=7,rowspan=2,sticky="W",ipady=8)

        self.letrero_rareza=ttk.Label(self, text='Rareza',font=self.font2,background='#093992',foreground='white',anchor = 'center',width=9)
        self.letrero_rareza.grid(row=3,column=2,sticky="NSEW",pady=(0,2),padx=(25,0))

        self.letrero_tipo_m=ttk.Label(self, text='Tipo',font=self.font2,background='#093992',foreground='white',anchor = 'center',width=4)
        self.letrero_tipo_m.grid(row=8,column=6,sticky='EW')
                
        self.letrero_nivel=ttk.Label(self, text='Nivel',font=self.font2,background='#093992',foreground='white',anchor = 'center',width=5)
        self.letrero_nivel.grid(row=10,column=6,sticky='EW')
                
        self.letrero_atributo=ttk.Label(self, text='Atributo',font=self.font2,background='#093992',foreground='white',anchor = 'center')
        self.letrero_atributo.grid(row=6,column=6,sticky='EW')

        self.letroro_hd=ttk.Label(self, text='Imagen en HD',font=self.font2,background='#093992',foreground='white',anchor = 'center')
        self.letroro_hd.grid(row=13,column=6,sticky='EW')
        
############        MENÚS    MENÚS    MENÚS    MENÚS    MENÚS    MENÚS    MENÚS    MENÚS    ##################
        self.ns=ttk.Combobox(self,values=['Todas','Monstruos','Trampas','Mágicas','Sincros','Fusión','Xyz'] , state="readonly",width=10, font=self.font2,justify = 'center')
        self.ns.current(0)
        self.ns.grid(column=1,row=4,sticky="NSEW")
        self.ns.bind("<<ComboboxSelected>>",self.filtro_principal)
        
        self.ns2=ttk.Combobox(self,values=['Todos','Agua','Fuego','Viento','Tierra','Luz','Oscuridad','Divinidad'] , state="readonly",width=12, font=self.font2,justify = 'center')
        self.ns2.current(0)
        self.ns2.grid(column=6,row=7,sticky="EW")
        self.ns2.bind("<<ComboboxSelected>>",self.filtro_elemento)

        self.option_add('*TCombobox*Listbox.font',self.font2)
        query='SELECT Nombre FROM habilidades ORDER BY Nombre ASC'
        valores=self.consulta(query)
        nombres = [r for (r,) in valores]
        self.habilidad=ttk.Combobox(self,values=nombres, state="readonly",width=23, font=self.font2,justify = 'center')
        self.habilidad.current(0)
        self.habilidad.grid(column=7,row=3,columnspan=4,rowspan=2,sticky="E",ipady=8)

        self.rarezas=ttk.Combobox(self,values=['','UR','SR','R','N'],state="readonly",width=4, font=self.font2,justify = 'center')
        self.rarezas.current(0)
        self.rarezas.grid(row=3,column=3,pady=(0,2),sticky="NSW")
        self.rarezas.bind("<<ComboboxSelected>>",self.filtro_rareza)

        self.tipo_m=ttk.Combobox(self,values=['','Aqua','Bestia','Bestia Alada','Ciberso','Demonio','Dinosaurio','Dragón','Guerrero','Guerrero-Bestia','Hada','Insecto','Lanzador de Conjuros','Máquina','Pez','Piro','Planta','Psíquico','Reptil','Roca','Serpiente Marina','Trueno','Wyrn','Zombi'],state="readonly",width=12, font=self.font2,justify = 'center')
        self.tipo_m.grid(row=9,column=6,sticky="EW")
        self.tipo_m.current(0)
        self.tipo_m.bind("<<ComboboxSelected>>",self.filtro_tipo_m)

        self.nivel=ttk.Combobox(self,values=['','1','2','3','4','5','6','7','8','9','10','11','12'],state="readonly",width=2, font=self.font2,justify = 'center')
        self.nivel.grid(row=11,column=6,sticky="EW")
        self.nivel.current(0)
        self.nivel.bind("<<ComboboxSelected>>",self.filtro_nivel)

        self.limites=ttk.Combobox(self, values=['','3','2','1','P'],state="readonly",width=4, font=self.font2,justify = 'center')
        self.limites.current(0)
        self.limites.grid(column=3,row=4,sticky="WNS")
        self.limites.bind("<<ComboboxSelected>>",self.filtro_limitacion)

##########          BOTONES    BOTONES    BOTONES    BOTONES    BOTONES    BOTONES    BOTONES    ###############
        self.sentido=tk.Button(self , image=self.flechas, command=self.cambiar_sentido, height=25, width=25,cursor='hand2')
        self.sentido.grid(row=3,column=4,columnspan=2,rowspan=2)
        
        self.btn_buscar=tk.Button(self, image=self.search, height=30, width=30,command=self.iniciar_busqueda,cursor='hand2')
        self.btn_buscar.grid(row=3,column=2,sticky='W')

        self.btn_crear_imagen=tk.Button(self,text='Crear Imagen...',height=1,command=self.crear_imagen,font=self.font2,relief='solid',overrelief='solid',cursor='hand2',bg='#76d24f')
        self.btn_crear_imagen.grid(row=17,column=6,rowspan=4)

        self.btn_reiniciar=tk.Button(self, text='Limpiar',height=1,command=self.reiniciar_cartas ,font=self.font2,relief='solid',overrelief='solid',cursor='hand2',bg='#ef3236')
        self.btn_reiniciar.grid(row=3,column=11,rowspan=2)

        self.btn_add_card=tk.Button(self,text='Agregar Carta',compound='top',border='0',bg='#c0c0c0',cursor='hand2',command=self.add_card,image=self.img_card,activebackground='#c0c0c0',activeforeground='#ef3236')
        self.btn_add_card.grid(row=3,column=6,rowspan=2)

        self.btn_reiniciar_busqueda=tk.Button(self,text='Limpiar\n Búsqueda',height=2,command=self.limpiar_busqueda ,font=self.font2,relief='solid',overrelief='solid',cursor='hand2',bg='#ef3236')
        self.btn_reiniciar_busqueda.grid(row=22,column=6)
        self.btn_ilimitado=tk.Button(self,text='Deck \nsin Limitadas',command=self.sin_banlist ,font=self.font2,relief='solid',overrelief='solid',cursor='hand2',bg='#ef3236')
        self.btn_ilimitado.grid(row=30,column=6,padx=(4,4))
 ########        OTROS    OTROS    OTROS    OTROS    OTROS    OTROS    OTROS    OTROS    ##########
        self.text_buscar=EntryWithPlaceholder(self, "Buscar...",width=15,font=self.font2)
        self.text_buscar.grid(row=3,column=1,sticky="NSEW",padx=(7,0),pady=(0,2))
        self.text_buscar.bind("<Return>", self.iniciar_busqueda)

        self.colocar_cartas(main=True,extra=True)
        root.bind("<Button-1>", self.click)
        self.obtener_cartas()
        self.si_hd=ttk.Checkbutton(self,onvalue=True, offvalue=False,text='¿HD?',variable=self.variable_hd)
        self.si_hd.grid(row=14,column=6)
        
# MÉTODOS
    def sin_banlist(self):
        if self.banlist:
            self.btn_ilimitado['text']='Actualmente\nsin Limitadas'
            self.reiniciar_cartas()
            self.banlist=False
        elif not self.banlist:
            self.btn_ilimitado['text']='Deck\nsin Limitadas'
            self.banlist=True
            self.reiniciar_cartas()

    def limpiar_busqueda(self):
        self.nivel.current(0)
        self.limites.current(0)
        self.tipo_m.current(0)
        self.rarezas.current(0)
        self.ns.current(0)
        self.ns2.current(0)
        self.text_buscar.delete(0,'end')
        self.clave=''
        self.variable_tipo_c='Todas'
        self.variable_elemento='Todos'
        self.variable_rareza=''
        self.variable_nivel=''
        self.variable_tipo_m=''
        self.variable_limite=''
        self.orden='ASC'
        self.text_buscar.put_placeholder()  
        self.cambiar_sentido()
        
    def add_card(self):
        self.vista_add_imagen = tk.Toplevel()
        self.vista_add_imagen.configure(bg='#c0c0c0')
        self.vista_add_imagen.ok=''
        self.vista_add_imagen.resizable(0, 0)
        self.vista_add_imagen.title('Agregar Imangen Nueva')
        self.vista_add_imagen.geometry('845x614')
        self.nombre_card=EntryWithPlaceholder(self.vista_add_imagen,'Nombre de la Carta',width=25,font=self.font2)
        self.nombre_card.grid(row=2,column=4,sticky='EW')
        label_rareza=tk.Label(self.vista_add_imagen,text='Rareza de Carta',font=self.font2,background='#093992',foreground='white',anchor = 'center')
        label_rareza.grid(row=3,column=3,sticky='EW',pady=(1,1))
        self.rareza_card=ttk.Combobox(self.vista_add_imagen,values=['UR','SR','R','N'],state="readonly",width=4, font=self.font2,justify = 'center')
        self.rareza_card.current(0)
        self.rareza_card.grid(row=3,column=4,sticky='EW')
        label_limitacion=tk.Label(self.vista_add_imagen,text='Limitación de Carta',font=self.font2,background='#093992',foreground='white',anchor = 'center')
        label_limitacion.grid(row=4,column=3,sticky='EW',pady=(1,1))
        self.limitacion_card=ttk.Combobox(self.vista_add_imagen,values=['Ilimitada','3','2','1','P'],state="readonly",width=11, font=self.font2,justify = 'center')
        self.limitacion_card.current(0)
        self.limitacion_card.grid(row=4,column=4,sticky='EW')
        label_clase=tk.Label(self.vista_add_imagen,text='Tipo de Carta',font=self.font2,background='#093992',foreground='white',anchor = 'center')
        label_clase.grid(row=5,column=3,sticky='EW',pady=(1,1))
        self.clase_card=ttk.Combobox(self.vista_add_imagen,values=['Fusión','Mágicas','Monstruos','Sincros','Trampas','Xyz'],state="readonly",width=10, font=self.font2,justify = 'center')
        self.clase_card.current(0)
        self.clase_card.grid(row=5,column=4,sticky='EW')
        self.clase_card.bind("<<ComboboxSelected>>",self.ocultar_por_tipo)

        label_atributo=tk.Label(self.vista_add_imagen,text='Atributo',font=self.font2,background='#093992',foreground='white',anchor = 'center')
        label_atributo.grid(row=6,column=3,sticky='EW',pady=(1,1))
        self.atributo_card=ttk.Combobox(self.vista_add_imagen,values=['Agua','Fuego','Viento','Tierra','Luz','Oscuridad'],state="readonly",width=9, font=self.font2,justify = 'center')
        self.atributo_card.current(0)
        self.atributo_card.grid(row=6,column=4,sticky='EW')
        label_tipom=tk.Label(self.vista_add_imagen,text='Tipo del Monstruo',font=self.font2,background='#093992',foreground='white',anchor = 'center')
        label_tipom.grid(row=7,column=3,sticky='EW',pady=(1,1))
        self.tipom_card=ttk.Combobox(self.vista_add_imagen,values=['Aqua','Bestia','Bestia Alada','Ciberso','Demonio','Dinosaurio','Dragón','Guerrero','Guerrero-Bestia','Hada','Insecto','Lanzador de Conjuros','Máquina','Pez','Piro','Planta','Psíquico','Reptil','Roca','Serpiente Marina','Trueno','Wyrn','Zombi'],state="readonly",width=9, font=self.font2,justify = 'center')
        self.tipom_card.current(0)
        self.tipom_card.grid(row=7,column=4,sticky='EW')
        self.label_nivelm=tk.Label(self.vista_add_imagen,text='Nivel del Monstruo',font=self.font2,background='#093992',foreground='white',anchor = 'center')
        self.label_nivelm.grid(row=8,column=3,sticky='EW',pady=(1,1))
        self.nivelm_card=ttk.Combobox(self.vista_add_imagen,values=['1','2','3','4','5','6','7','8','9','10','11','12'],state="readonly",width=2, font=self.font2,justify = 'center')
        self.nivelm_card.current(0)
        self.nivelm_card.grid(row=8,column=4,sticky='EW')
        btn_add_new_card=tk.Button(self.vista_add_imagen,text='Agregar...', height=1,command=self.agregar_carta_nueva,font=self.font2,relief='solid',overrelief='solid',cursor='hand2',bg='#76d24f')
        btn_add_new_card.grid(row=10,column=3,columnspan=2)
        label_imagen=tk.Label(self.vista_add_imagen,text='Elija el archivo',font=self.font2,background='#093992',foreground='white',anchor = 'center')
        label_imagen.grid(row=9,column=3,sticky='EW',pady=(1,1))
        btn_add_img=tk.Button(self.vista_add_imagen,text='Seleccionar imagen...', height=1,command=self.abrir_archivo,font=self.font2,relief='solid',overrelief='solid',cursor='hand2',bg='#76d24f')
        btn_add_img.grid(row=9,column=4,sticky='EW')
        self.vista_add_imagen.img=tk.PhotoImage(file='fuentes/fondo_b.png')
        self.img_previa_guardar=ttk.Label(self.vista_add_imagen,image=(self.vista_add_imagen.img))#image=tk.PhotoImage(file='C:/Users/Scarlett/Documents/Programacion/Creador de Mazos/cartas/'+ xd[8]))
        self.img_previa_guardar.grid(row=2,column=2,rowspan=19)

    def abrir_archivo(self):
        archivo=filedialog.askopenfile(initialdir='/',title="Seleccione Imagen",filetypes=(('Png','*.png'),('jpeg files','*.jpg'),('all files','*.*')))
        if archivo.name.endswith('.png') or archivo.name.endswith('.jpg') or archivo.name.endswith('.jpeg'):
            try:
                self.vista_add_imagen.img2=tk.PhotoImage(file=archivo.name)
                if self.vista_add_imagen.img2.width()<=421:
                    self.img_previa_guardar['image']=self.vista_add_imagen.img2
                    self.vista_add_imagen.ok=archivo.name
                else:
                    self.img_previa_guardar['image']=self.vista_add_imagen.img
                    messagebox.showerror(title='Fallo',message='Imagen muy gran (Recomendado 421x614)')
            except:
                messagebox.showerror(self,'Archivo no Válido')
        else:
            messagebox.showerror(title='Fallo',message='Archivo no Válido')

    def ocultar_por_tipo(self,event):
        actual=self.clase_card.get()
        if actual =='Xyz':
            self.label_nivelm["text"]='Rango del Monstruo'
        else:
            self.label_nivelm["text"]='Nivel del Monstruo'
        if actual =='Mágicas' or actual=='Trampas':
            self.atributo_card['state']='disable'
            self.tipom_card['state']='disable'
            self.nivelm_card['state']='disable'
        else:
            self.atributo_card['state']='readonly'
            self.tipom_card['state']='readonly'
            self.nivelm_card['state']='readonly'

    def agregar_carta_nueva(self):
        nombre=self.nombre_card.get()
        if nombre!='Nombre de la Carta' and len(nombre)>=3 and not nombre.isspace() and self.rareza_card.get() and self.limitacion_card.get() and self.clase_card.get():
            if self.vista_add_imagen.ok!='':
                clase=self.clase_card.get() 
                limitacion2=self.limitacion_card.get()
                if limitacion2=='Ilimitada':
                    limitacion2=4
                rareza2=self.rareza_card.get()
                if clase=='Mágicas' or clase=='Trampas':
                    query='INSERT into cartas VALUES(NULL,?,?,?,?,?,?,?,?)'
                    parameters=(clase,nombre,'','','',limitacion2,rareza2,nombre+'.png',)
                    self.consulta(query,parameters)
                    shutil.copy(self.vista_add_imagen.ok,'cartas/'+ nombre + '.png')
                    ci.crear_mini(nombre + '.png')
                    ci.crear_normal(nombre + '.png')
                    self.vista_add_imagen.ok=''
                    self.img_previa_guardar['image']=self.vista_add_imagen.img
                    messagebox.showinfo(title="Hecho",message='Carta Guardada')
                else:
                    if self.nivelm_card.get() and self.tipom_card.get() and self.atributo_card.get():
                        nivel=int(self.nivelm_card.get())    
                        tipom=self.tipom_card.get() 
                        atributo2=self.atributo_card.get()
                        if clase=='Xyz':
                            nivel=int(nivel)*(-1)
                        
                        query='INSERT into cartas VALUES(NULL,?,?,?,?,?,?,?,?)'
                        parameters=(clase,nombre,atributo2,tipom,nivel,limitacion2,rareza2,nombre+'.png',)
                        self.consulta(query,parameters)
                        shutil.copy(self.vista_add_imagen.ok,'cartas/'+ nombre + '.png')
                        ci.crear_mini(nombre + '.png')
                        ci.crear_normal(nombre + '.png')
                        self.vista_add_imagen.ok=''
                        self.img_previa_guardar['image']=self.vista_add_imagen.img
                        messagebox.showinfo(title="Hecho",message='Carta Guardada')
            elif self.vista_add_imagen.ok=='':
                messagebox.showwarning(title="Error",message='Agregue una Imagen')
        else:
            messagebox.showwarning(title="Error",message='Inserte un Nombre Válido')

    def filtro_limitacion(self,event):
        mos=self.limites.get()
        if mos!=self.variable_limite:
            self.variable_limite=mos
            self.obtener_cartas()

    def filtro_nivel(self, event):
        mos=self.nivel.get()
        if mos!=self.variable_nivel:
            if self.variable_tipo_c=='Xyz' and mos!='':
                self.variable_nivel=int(mos)*(-1)
            else:
                self.variable_nivel=mos
            
            self.obtener_cartas()

    def filtro_tipo_m(self,event):
        mos=self.tipo_m.get()
        if mos!=self.variable_tipo_m:
            self.variable_tipo_m=mos
            self.obtener_cartas()

    def reiniciar_cartas(self):
        if self.cont>0 or self.con_extra>0:
            self.solo_nombre.clear()
            self.solo_nombre=["zz"]*37
            self.arra_no_imag.clear()
            self.arra_no_imag=[False]*37
            self.copias_cartas.clear()
            self.copias_cartas=([[None]*37,[None]*37])
            self.limitaciones=[0,0,0]
            self.imagenes_main.clear()
            self.imagenes_main=[None]*37
            self.cont=0
            self.cont_copias=0
            self.con_extra=0
            self.con_todo=0
            self.colocar_cartas(main=True,extra=True)
            self.habilidad.current(0)

    def iniciar_busqueda(self,event=None):
        self.clave=self.text_buscar.get()
        self.obtener_cartas()

    def cambiar_sentido(self):
        if self.orden=='DESC':
            self.sentido["image"]=self.sahcelf
            self.orden='ASC'
        elif self.orden=='ASC':
            self.sentido["image"]=self.flechas
            self.orden='DESC'
        self.mostrador.grid_remove()
        self.mostrador2 = ttk.Treeview(self,height = 7,columns=("size", "lastmod"), style="mystyle.Treeview")
        self.mostrador2.grid(row = 5, column = 0, columnspan = 5, rowspan=30,sticky="NSEW")
        self.mostrador2.heading('#0', text = '', anchor = 'center')
        self.mostrador2.column("#0",width=70, anchor = 'center')
        self.mostrador2.heading('#1', text = 'Nombre', anchor = 'center')
        self.mostrador2.column("#1",width=400, anchor = 'center')
        self.mostrador2.heading('lastmod', text = 'Rareza', anchor = 'center')
        self.mostrador2.column("lastmod",width=100, anchor = 'center')  

        self.rarezas["state"]="disable"
        self.ns["state"]="disable"
        self.ns2["state"]="disable"
        self.limites["state"]="disable"
        self.nivel["state"]="disable"
        self.tipo_m["state"]="disable"
        self.btn_reiniciar_busqueda['state']='disable'
        self.btn_buscar["state"]="disable"
        self.sentido["state"]="disable"
        self.text_buscar["state"]="disable"
        self.btn_crear_imagen["state"]="disable"
        self.btn_reiniciar["state"]="disable"
        self.btn_ilimitado["state"]="disable"

        t = threading.Thread(target=self.obtener_cartas)
        t.start()
        # Comenzar a chequear periódicamente si el hilo ha finalizado.
        self.schedule_check(t)

    def schedule_check(self,t):
        root.after(100, self.check_if_done, t)

    def check_if_done(self,t):
        # Si el hilo ha finalizado, restaruar el botón y mostrar un mensaje.
        if not t.is_alive():
            self.mostrador2.grid_remove()
            self.mostrador.grid(row = 5, column = 0, columnspan = 5, rowspan=30,sticky="NSEW")
            self.ns["state"]="readonly"
            self.ns2["state"]="readonly"
            self.limites["state"]="readonly"
            self.rarezas["state"]="readonly"
            self.nivel["state"]="readonly"
            self.tipo_m["state"]="readonly"
            self.btn_reiniciar_busqueda['state']='normal'
            self.btn_ilimitado['state']='normal'
            self.btn_buscar["state"]="normal"
            self.sentido["state"]="normal"
            self.btn_reiniciar["state"]="normal"
            self.btn_crear_imagen["state"]="normal"
            self.text_buscar["state"]="normal"
            
        else:
            # Si no, volver a chequear en unos momentos.
            self.schedule_check(t)

    def ver_carta(self):
        item = self.mostrador.selection()[0]
        nombre_carta=self.mostrador.item(item,'text')
        query = 'SELECT * FROM cartas WHERE nombre = ?' #ascedente ASC
        db_columnas = self.consulta(query, (nombre_carta,))
        xd=db_columnas.fetchone()
        self.vista_imagen = tk.Toplevel()
        self.vista_imagen.resizable(0, 0)
        self.vista_imagen.title(xd[2])
        self.vista_imagen.geometry('421x614')
        self.vista_imagen.img=ImageTk.PhotoImage(Image.open('cartas/'+ xd[8]))
        img_a_mostrar=ttk.Label(self.vista_imagen,image=self.vista_imagen.img)
        img_a_mostrar.pack()
            
    def popup(self, event):
            self.iid = self.mostrador.identify_row(event.y)
            if self.iid:
                # mouse pointer over item
                self.mostrador.selection_set(self.iid)
                self.aMenu.post(event.x_root, event.y_root)
            else:
                pass

    def filtro_elemento(self, event):
        mos=self.ns2.get()
        if mos !=self.variable_elemento:
            self.variable_elemento=mos
            if self.variable_tipo_c=='Monstruos' or self.variable_tipo_c=='Sincros' or self.variable_tipo_c=='Fusión' or self.variable_tipo_c=='Xyz' or self.variable_tipo_c=='Todas':
                self.obtener_cartas()

    def filtro_principal(self,event):
        mos=self.ns.get()
        if mos != self.variable_tipo_c:
            aux=(self.variable_nivel)
            if mos =='Xyz':
                self.letrero_nivel["text"]='Rango'
                if aux!='':
                    self.variable_nivel=int(aux)*(-1)
            else:
                self.letrero_nivel["text"]='Nivel'
                if aux!='' and int(self.variable_nivel)<0:
                    self.variable_nivel=int(aux)*(-1)
            if mos =='Mágicas' or mos=='Trampas':
                self.nivel.current(0)
                self.tipo_m.current(0)
                self.ns2.current(0)
                self.nivel['state']='disable'
                self.tipo_m['state']='disable'
                self.ns2['state']='disable'
                self.variable_nivel=''
                self.variable_tipo_m=''
                self.variable_elemento='Todos'
            else:
                self.nivel['state']='readonly'
                self.tipo_m['state']='readonly'
                self.ns2['state']='readonly'

            self.variable_tipo_c=mos
            self.obtener_cartas()

    def filtro_rareza(self,event):
        mos=self.rarezas.get()
        if mos!=self.variable_rareza:
            self.variable_rareza=mos
            self.obtener_cartas()

    def crear_imagen(self):
        h=0
        for i in range(37):
            if self.solo_nombre[i]!='zz':

                query = 'SELECT * FROM cartas WHERE nombre = ?' #ascedente ASC
                db_columnas = self.consulta(query, (self.solo_nombre[i],))
                xd=db_columnas.fetchone()
                self.para_crear[i]=xd[8]
                h+=1
        if h>0:
            ci.crear(v_cartas=self.para_crear[0:30],v_cartasx=self.para_crear[30:37],HD=self.variable_hd.get(),skill=self.habilidad.get())
            messagebox.showinfo(title="Hecho",message='Imgen Creada')
            self.para_crear.clear()
            self.para_crear=[None]*37

    def revision_agregado(self,event=None):
        try:
            self.mames=False
            if event!=None:
                self.iid = self.mostrador.identify_row(event.y)
            if self.iid:
                self.mostrador.selection_set(self.iid)
            else:
                pass
            item = self.mostrador.selection()[0]
            nombre_carta=self.mostrador.item(item,'text')
            query = 'SELECT * FROM cartas WHERE nombre = ?' #ascedente ASC
            db_columnas = self.consulta(query, (nombre_carta,))
            xd=db_columnas.fetchone()
            xd[1]
            if xd[1]=='Mágicas' or xd[1]=='Trampas' or xd[1]=='Monstruos':
                principal=True
            else:
                principal=False
            if xd[1]=='Sincros' or xd[1]=='Fusión' or xd[1]=='Xyz':
                secundario=True
            else:
                secundario=False
            hacer=False
            if principal and self.cont<30:

                self.con_todo=self.cont
                for xx in range(6):
                    for yy in range(5):
                        if self.posiciones[xx][yy]==self.cont:
                            hacer=True
                            ok=self.limitadas(xd)
                            break
            elif secundario and self.con_extra<7:
                self.con_todo=self.con_extra + 30
                hacer=True
                ok=self.limitadas(xd)
            try:
                if hacer and ok:
                    va=True
                    if principal:
                        for i in range (30):
                            if nombre_carta ==self.solo_nombre[i]:
                                aux=self.solo_nombre[30:37]                                
                                extension=self.solo_nombre[i:29]
                                inicio=self.solo_nombre[0:i]
                                inicio.append(nombre_carta)
                                inicio.extend(extension)
                                self.solo_nombre.clear()
                                self.solo_nombre[0:29]=inicio
                                self.solo_nombre[30:37]=aux
                                self.solo_nombre.clear()
                                inicio.extend(aux)
                                self.solo_nombre=inicio
                                va=False
                                
                                break
                    if secundario:
                        for i in range(30,37):
                            if nombre_carta ==self.solo_nombre[i]:
                                extension=self.solo_nombre[i:37]
                                inicio=self.solo_nombre[30:i]
                                inicio.append(nombre_carta)
                                inicio.extend(extension)
                                self.solo_nombre[30:37]=inicio
                                aux=self.solo_nombre[0:37]
                                self.solo_nombre.clear()
                                self.solo_nombre=aux
                                va=False
                                break

                    if va:
                        self.solo_nombre[self.con_todo]=nombre_carta
                        i=0
                    if secundario:
                        if va==False:
                            i-=30
                        self.colocar_cartas(extra=True,ie=(i+1),nt=True)
                        self.arra_no_imag[(self.con_extra +30)]=True
                        self.con_extra+=1
                    
                    if principal:
                        self.colocar_cartas(main=True,im=(i),nt=True)
                        self.arra_no_imag[self.cont]=True
                        self.cont+=1
                    no_esta=0
                    for i in range(37):
                        if nombre_carta == self.copias_cartas[0][i]:
                            self.copias_cartas[1][i]+=1
                        else:
                            no_esta+=1
                    if no_esta==37:
                        self.copias_cartas[0][self.cont_copias]=nombre_carta
                        self.copias_cartas[1][self.cont_copias]=1
                        self.cont_copias+=1
            except:
                pass
        except:
            pass

    def limitadas(self, nose):
        if self.banlist:
            copias=nose[6]
        elif not self.banlist:
            copias=4
        nombre=nose[2]

        for i in range(36):
            if nombre == self.copias_cartas[0][i]:
                if copias == 4:
                    if self.copias_cartas[1][i]<3:
                        ok=True
                    elif self.copias_cartas[1][i]==3:
                        ok=False
                elif copias !=4:
                    if copias == 1 and self.limitaciones[0] != 0:
                        ok=False
                    elif copias ==1 and self.limitaciones[0] ==0:
                        ok=True
                    elif copias ==2 and self.limitaciones[1] ==2:
                        ok=False
                    elif copias ==2 and self.limitaciones[1] <2:
                        self.limitaciones[1]+=1
                        ok=True
                    elif copias ==3 and self.limitaciones[2] ==3:
                        ok=False
                    elif copias ==3 and self.limitaciones[2] <3:
                        ok=True
                        self.limitaciones[2]+=1
                break
            elif nombre != self.copias_cartas[0][i]:
                if copias == 4:
                    ok=True
                elif copias !=4:
                    if copias == 1 and self.limitaciones[0] != 0:
                        ok=False
                    elif copias ==1 and self.limitaciones[0] ==0:
                        ok=True
                        self.limitaciones[0]+=1
                        break
                    elif copias ==2 and self.limitaciones[1] ==2:
                        ok=False
                    elif copias ==2 and self.limitaciones[1] <2:
                        ok=True
                        self.limitaciones[1]+=1
                        break
                    elif copias ==3 and self.limitaciones[2] ==3:
                        ok=False
                    elif copias ==3 and self.limitaciones[2] <3:
                        ok=True
                        self.limitaciones[2]+=1
                        break
        return(ok)
     
    def ssgnar(self,z,z1):
        # con los datos recibidos se modifica la imagen del botón presionado y se del main o extra
        try:
            if z[0]<1 or z[1]<0:
                btn_num=None
            elif z[0]>=1 and z[0]<=5 and z1[0]!=0:
                btn_num=self.posiciones[z[1]][z[0]-1]
            elif z1[0]==0 and z1[1]>=0 and z1[1]<=6 and z[0]==6:
                btn_num=z1[1]+30

            if z[0]>=0 and z[0]<6 and z1[0]==(-1):
                if self.arra_no_imag[btn_num]==False:
                    pass
                elif self.arra_no_imag[btn_num]==True:

                    self.cont-=1
                    for i in range(30):
                        if self.solo_nombre[btn_num]==self.copias_cartas[0][i]:
                            self.copias_cartas[1][i]-=1
                            query = 'SELECT * FROM cartas WHERE nombre = ?' #ascedente ASC
                            db_columnas = self.consulta(query, (self.solo_nombre[btn_num],))
                            xd=db_columnas.fetchone()
                            if xd[6]==3:
                                self.limitaciones[2]-=1
                            elif xd[6]==2:
                                self.limitaciones[1]-=1
                            elif xd[6]==1:
                                self.limitaciones[0]-=1
                            for k in range(btn_num,30):
                                
                                if k<29:
                                    self.solo_nombre[k]=self.solo_nombre[k+1]
                                    self.solo_nombre[k+1]="zz"
                                elif k==29:
                                    self.solo_nombre[k]="zz"
                                if self.solo_nombre[k]=="zz":
                                    break

                            if self.copias_cartas[1][i]==0:
                                self.cont_copias-=1
                                self.copias_cartas[0][i]=None
                            break
                    for i in range(37):
                        if self.copias_cartas[1][i]==0 or self.copias_cartas[1][i]==None:
                            if i<35:
                                self.copias_cartas[0][i]=self.copias_cartas[0][i+1]
                                self.copias_cartas[1][i]=self.copias_cartas[1][i+1]
                                self.copias_cartas[0][i+1]=None
                                self.copias_cartas[1][i+1]=None
                            elif i==35:
                                self.copias_cartas[0][i]=None
                                self.copias_cartas[1][i]=None

                    for i in range(btn_num,30):
                        if self.solo_nombre[i]=='zz':
                            self.arra_no_imag[i]=False
                    
                    self.colocar_cartas(main=True,im=btn_num,nt=True)

            if z[0]==6 and z1[0]==0:
                if self.arra_no_imag[btn_num]==False:
                    pass
                elif self.arra_no_imag[btn_num]==True:
                    self.con_extra-=1

                    for i in range(37):
                        if self.solo_nombre[btn_num]==self.copias_cartas[0][i]:
                            self.copias_cartas[1][i]-=1
                            query = 'SELECT * FROM cartas WHERE nombre = ?' #ascedente ASC
                            db_columnas = self.consulta(query, (self.copias_cartas[0][i],))
                            xd=db_columnas.fetchone()
                            if xd[6]==3:
                                self.limitaciones[2]-=1
                            elif xd[6]==2:
                                self.limitaciones[1]-=1
                            elif xd[6]==1:
                                self.limitaciones[0]-=1
                            for k in range(btn_num,37):
                                if k<36:
                                    self.solo_nombre[k]=self.solo_nombre[k+1]
                                    self.solo_nombre[k+1]="zz"
                                elif k==36:
                                    self.solo_nombre[k]="zz"
                                
                            if self.copias_cartas[1][i]==0:
                                self.cont_copias-=1
                                self.copias_cartas[0][i]=None
                            break
                    for i in range(37):
                        if self.copias_cartas[1][i]==0 or self.copias_cartas[1][i]==None:
                            
                            if i<36:
                                self.copias_cartas[0][i]=self.copias_cartas[0][i+1]
                                self.copias_cartas[1][i]=self.copias_cartas[1][i+1]
                                self.copias_cartas[0][i+1]=None
                                self.copias_cartas[1][i+1]=None
                            elif i==36:
                                self.copias_cartas[0][i]=None
                                self.copias_cartas[1][i]=None

                    
                    for i in range(btn_num,37):
                        if self.solo_nombre[i]=='zz':
                            self.arra_no_imag[i]=False
                    self.colocar_cartas(extra=True,ie=btn_num-29,nt=True)
        except:
            pass

    def colocar_cartas(self,main=False,extra=False,im=0,ie=1,nt=False):
        #asignación de cartas por orden
        if main:
            y=0
            z=0
            for xx in range(6):
                    for yy in range(5):
                        if self.posiciones[xx][yy]==im:
                            y=xx
                            z=yy
                            break

            for i in range(im,30):
                z=z+1
                if self.solo_nombre[i]!="zz":
                    query = 'SELECT * FROM cartas WHERE nombre = ?' #ascedente ASC
                    db_columnas = self.consulta(query, (self.solo_nombre[i],))
                    xd=db_columnas.fetchone()
                    imagen=ImageTk.PhotoImage(Image.open('cartas2/'+ xd[8]))
                elif self.solo_nombre[i]=="zz":
    
                    imagen=self.otraimage
                if self.mames:
                    self.btns[i]=tk.Button(self.label , activebackground=self.color_fondo_main,relief="flat",overrelief="flat",bg=self.color_fondo_main, text=(" "))#,image=imagen)
                    self.btns[i].grid(row=y , column=z ,padx=(5,0) , pady=(5,0),sticky="NSEW")
                self.btns[i]["image"]=imagen
                
                self.imagenes_main[i]=imagen
                if nt and self.solo_nombre[i]=="zz":
                    break
                if z==5:
                    y=y+1
                    z=0
        if extra:
            for j in range(ie,8):
                if self.solo_nombre[30+j-1]!="zz":
                    query = 'SELECT * FROM cartas WHERE nombre = ?' #ascedente ASC
                    db_columnas = self.consulta(query, (self.solo_nombre[30+j-1],))
                    xd=db_columnas.fetchone()
                    imagen=ImageTk.PhotoImage(Image.open('cartas2/'+ xd[8]))
                elif self.solo_nombre[30+j-1]=="zz":
                    imagen=self.otraimage2
                if self.mames:
                    self.btns[29+j]=tk.Button(self.label2 , activebackground=self.color_fondo_extra,relief="flat",overrelief="flat",bg=self.color_fondo_extra, text=(" "),height=70)#height=67
                    self.btns[29+j].grid(row=j-1 , column=0 ,padx=(5,0) , pady=(3,0),sticky="NSEW")
                self.btns[29+j]["image"]=imagen
                self.imagenes_main[j+29]=imagen
                if nt and self.solo_nombre[30+j-1]=="zz":
                    break

    def click(self,event): 
        # recibe la ubicación donde se realizó click izquierdo 
        # con ese dato se sabe que espacio se presionó para modeficarse
        x = event.x_root - self.label.winfo_rootx() 
        y = event.y_root - self.label.winfo_rooty() 
        z = self.label.grid_location(x, y)
        x1 = event.x_root - self.label2.winfo_rootx() 
        y1 = event.y_root - self.label2.winfo_rooty() 
        z1 = self.label2.grid_location(x1, y1)
        self.ssgnar(z,z1)

    def consulta(self,query, parameters=()):
        with sqlite3.connect(self.db) as conn:
            cursor = conn.cursor()
            result = cursor.execute(query, parameters)
            conn.commit()
        return result
        
    def obtener_cartas(self):
        # cleaning Table 
        records = self.mostrador.get_children()
        for element in records:
            self.mostrador.delete(element)
        #1 todas las cartas
        #2 magias y trampas
        #3 monstruos sin elemento
        #4 monstruos con elemento
        #5 todos los monstruos con elemento
        #con búsqueda específica pero sin rareza
        if self.clave!='' and self.variable_rareza=='' and self.variable_limite=='' and self.variable_nivel=='' and self.variable_tipo_m=='':
            if self.variable_tipo_c=='Todas' and self.variable_elemento=='Todos':
                query = 'SELECT * FROM cartas WHERE nombre LIKE ?  ORDER BY nombre '+ self.orden #ascedente ASC
                db_columnas = self.consulta(query,('%'+self.clave+'%',))
            elif self.variable_tipo_c=='Mágicas' or self.variable_tipo_c=='Trampas':
                query = 'SELECT * FROM cartas WHERE clase = ? and nombre LIKE ? ORDER BY archivo '+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,'%'+self.clave+'%',))
            elif (self.variable_tipo_c=='Monstruos' or self.variable_tipo_c=='Sincros' or self.variable_tipo_c=='Fusión' or self.variable_tipo_c=='Xyz') and self.variable_elemento=='Todos':
                query = 'SELECT * FROM cartas WHERE clase = ? and nombre LIKE ? ORDER BY archivo '+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,'%'+self.clave+'%',))
            elif (self.variable_tipo_c=='Monstruos' or self.variable_tipo_c=='Sincros' or self.variable_tipo_c=='Fusión' or self.variable_tipo_c=='Xyz') and self.variable_elemento!='Todos':
                query = "SELECT * FROM cartas WHERE clase = ? and atributo = ? and nombre LIKE ? ORDER BY archivo "+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,self.variable_elemento,'%'+self.clave+'%',))
            elif self.variable_tipo_c=='Todas' and self.variable_elemento!='Todos':
                query = "SELECT * FROM cartas WHERE atributo = ? and nombre LIKE ? ORDER BY archivo "+ self.orden
                db_columnas = self.consulta(query,(self.variable_elemento,'%'+self.clave+'%',))
        #sin búsqueda específica pero sin rareza
        elif self.clave=='' and self.variable_rareza=='' and self.variable_limite=='' and self.variable_nivel=='' and self.variable_tipo_m=='':
            if self.variable_tipo_c=='Todas'and self.variable_elemento=='Todos':
                query = 'SELECT * FROM cartas ORDER BY nombre '+ self.orden #ascedente ASC
                db_columnas = self.consulta(query)
            elif self.variable_tipo_c=='Mágicas' or self.variable_tipo_c=='Trampas':
                query = 'SELECT * FROM cartas WHERE clase = ? ORDER BY archivo '+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,))
            elif (self.variable_tipo_c=='Monstruos' or self.variable_tipo_c=='Sincros' or self.variable_tipo_c=='Fusión' or self.variable_tipo_c=='Xyz') and self.variable_elemento=='Todos':
                query = 'SELECT * FROM cartas WHERE clase = ? ORDER BY archivo '+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,))
            elif (self.variable_tipo_c=='Monstruos' or self.variable_tipo_c=='Sincros' or self.variable_tipo_c=='Fusión' or self.variable_tipo_c=='Xyz') and self.variable_elemento!='Todos':
                query = "SELECT * FROM cartas WHERE clase = ? and atributo = ? ORDER BY archivo "+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,self.variable_elemento,))
            elif self.variable_tipo_c=='Todas' and self.variable_elemento!='Todos':
                query = "SELECT * FROM cartas WHERE atributo = ? ORDER BY archivo "+ self.orden
                db_columnas = self.consulta(query,(self.variable_elemento,))
        # con búsqueda específica y con rareza
        elif self.clave!='' and self.variable_rareza!='' and self.variable_limite=='' and self.variable_nivel=='' and self.variable_tipo_m=='':
            if self.variable_tipo_c=='Todas'and self.variable_elemento=='Todos':
                query = 'SELECT * FROM cartas WHERE nombre LIKE ? and rareza=? ORDER BY nombre '+ self.orden #ascedente ASC
                db_columnas = self.consulta(query,('%'+self.clave+'%',self.variable_rareza,))
            elif self.variable_tipo_c=='Mágicas' or self.variable_tipo_c=='Trampas':
                query = 'SELECT * FROM cartas WHERE clase = ? and nombre LIKE ? and rareza=? ORDER BY archivo '+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,'%'+self.clave+'%',self.variable_rareza,))
            elif (self.variable_tipo_c=='Monstruos' or self.variable_tipo_c=='Sincros' or self.variable_tipo_c=='Fusión' or self.variable_tipo_c=='Xyz') and self.variable_elemento=='Todos':
                query = 'SELECT * FROM cartas WHERE clase = ? and nombre LIKE ? and rareza=? ORDER BY archivo '+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,'%'+self.clave+'%',self.variable_rareza,))
            elif (self.variable_tipo_c=='Monstruos' or self.variable_tipo_c=='Sincros' or self.variable_tipo_c=='Fusión' or self.variable_tipo_c=='Xyz') and self.variable_elemento!='Todos':
                query = "SELECT * FROM cartas WHERE clase = ? and atributo = ? and nombre LIKE ? and rareza=? ORDER BY archivo "+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,self.variable_elemento,'%'+self.clave+'%',self.variable_rareza,))
            elif self.variable_tipo_c=='Todas' and self.variable_elemento!='Todos':
                query = "SELECT * FROM cartas WHERE atributo = ? and nombre LIKE ? and rareza = ? ORDER BY archivo "+ self.orden
                db_columnas = self.consulta(query,(self.variable_elemento,'%'+self.clave+'%',self.variable_rareza,))
        # sin búsqueda específica pero con de rareza
        elif self.clave=='' and self.variable_rareza!='' and self.variable_limite=='' and self.variable_nivel=='' and self.variable_tipo_m=='':
            if self.variable_tipo_c=='Todas'and self.variable_elemento=='Todos':
                query = 'SELECT * FROM cartas WHERE rareza=? ORDER BY nombre '+ self.orden #ascedente ASC
                db_columnas = self.consulta(query,(self.variable_rareza,))
            elif self.variable_tipo_c=='Mágicas' or self.variable_tipo_c=='Trampas':
                query = 'SELECT * FROM cartas WHERE clase = ? and rareza=? ORDER BY archivo '+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,self.variable_rareza,))
            elif (self.variable_tipo_c=='Monstruos' or self.variable_tipo_c=='Sincros' or self.variable_tipo_c=='Fusión' or self.variable_tipo_c=='Xyz') and self.variable_elemento=='Todos':
                query = 'SELECT * FROM cartas WHERE clase = ? and rareza=? ORDER BY archivo '+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,self.variable_rareza,))
            elif (self.variable_tipo_c=='Monstruos' or self.variable_tipo_c=='Sincros' or self.variable_tipo_c=='Fusión' or self.variable_tipo_c=='Xyz') and self.variable_elemento!='Todos':
                query = "SELECT * FROM cartas WHERE clase = ? and atributo = ? and rareza=? ORDER BY archivo "+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,self.variable_elemento,self.variable_rareza,))
            elif self.variable_tipo_c=='Todas' and self.variable_elemento!='Todos':
                query = "SELECT * FROM cartas WHERE atributo = ? and rareza = ? ORDER BY archivo "+ self.orden
                db_columnas = self.consulta(query,(self.variable_elemento,self.variable_rareza,))
        #### LIMITACIÓN
        if self.clave!='' and self.variable_rareza=='' and self.variable_limite!='' and self.variable_nivel=='' and self.variable_tipo_m=='':
            if self.variable_tipo_c=='Todas' and self.variable_elemento=='Todos':
                query = 'SELECT * FROM cartas WHERE nombre LIKE ?  and limitacion = ? ORDER BY nombre '+ self.orden #ascedente ASC
                db_columnas = self.consulta(query,('%'+self.clave+'%',self.variable_limite,))
            elif self.variable_tipo_c=='Mágicas' or self.variable_tipo_c=='Trampas':
                query = 'SELECT * FROM cartas WHERE clase = ? and nombre LIKE ?  and limitacion = ? ORDER BY archivo '+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,'%'+self.clave+'%',self.variable_limite,))
            elif (self.variable_tipo_c=='Monstruos' or self.variable_tipo_c=='Sincros' or self.variable_tipo_c=='Fusión' or self.variable_tipo_c=='Xyz') and self.variable_elemento=='Todos':
                query = 'SELECT * FROM cartas WHERE clase = ? and nombre LIKE ?  and limitacion = ? ORDER BY archivo '+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,'%'+self.clave+'%',self.variable_limite,))
            elif (self.variable_tipo_c=='Monstruos' or self.variable_tipo_c=='Sincros' or self.variable_tipo_c=='Fusión' or self.variable_tipo_c=='Xyz') and self.variable_elemento!='Todos':
                query = "SELECT * FROM cartas WHERE clase = ? and atributo = ? and nombre LIKE ?  and limitacion = ? ORDER BY archivo "+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,self.variable_elemento,'%'+self.clave+'%',self.variable_limite,))
            elif self.variable_tipo_c=='Todas' and self.variable_elemento!='Todos':
                query = "SELECT * FROM cartas WHERE atributo = ? and nombre LIKE ?  and limitacion = ? ORDER BY archivo "+ self.orden
                db_columnas = self.consulta(query,(self.variable_elemento,'%'+self.clave+'%',self.variable_limite,))
        #sin búsqueda específica pero sin rareza
        elif self.clave=='' and self.variable_rareza=='' and self.variable_limite!='' and self.variable_nivel=='' and self.variable_tipo_m=='':
            if self.variable_tipo_c=='Todas'and self.variable_elemento=='Todos':
                query = 'SELECT * FROM cartas  WHERE limitacion = ? ORDER BY nombre '+ self.orden #ascedente ASC
                db_columnas = self.consulta(query,(self.variable_limite,))
            elif self.variable_tipo_c=='Mágicas' or self.variable_tipo_c=='Trampas':
                query = 'SELECT * FROM cartas WHERE clase = ?  and limitacion = ? ORDER BY archivo '+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,self.variable_limite,))
            elif (self.variable_tipo_c=='Monstruos' or self.variable_tipo_c=='Sincros' or self.variable_tipo_c=='Fusión' or self.variable_tipo_c=='Xyz') and self.variable_elemento=='Todos':
                query = 'SELECT * FROM cartas WHERE clase = ?  and limitacion = ? ORDER BY archivo '+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,self.variable_limite,))
            elif (self.variable_tipo_c=='Monstruos' or self.variable_tipo_c=='Sincros' or self.variable_tipo_c=='Fusión' or self.variable_tipo_c=='Xyz') and self.variable_elemento!='Todos':
                query = "SELECT * FROM cartas WHERE clase = ? and atributo = ?  and limitacion = ? ORDER BY archivo "+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,self.variable_elemento,self.variable_limite,))
            elif self.variable_tipo_c=='Todas' and self.variable_elemento!='Todos':
                query = "SELECT * FROM cartas WHERE atributo = ?  and limitacion = ? ORDER BY archivo "+ self.orden
                db_columnas = self.consulta(query,(self.variable_elemento,self.variable_limite,))
        # con búsqueda específica y con rareza
        elif self.clave!='' and self.variable_rareza!='' and self.variable_limite!='' and self.variable_nivel=='' and self.variable_tipo_m=='':
            if self.variable_tipo_c=='Todas'and self.variable_elemento=='Todos':
                query = 'SELECT * FROM cartas WHERE nombre LIKE ? and rareza=?  and limitacion = ? ORDER BY nombre '+ self.orden #ascedente ASC
                db_columnas = self.consulta(query,('%'+self.clave+'%',self.variable_rareza,self.variable_limite,))
            elif self.variable_tipo_c=='Mágicas' or self.variable_tipo_c=='Trampas':
                query = 'SELECT * FROM cartas WHERE clase = ? and nombre LIKE ? and rareza=?  and limitacion = ? ORDER BY archivo '+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,'%'+self.clave+'%',self.variable_rareza,self.variable_limite,))
            elif (self.variable_tipo_c=='Monstruos' or self.variable_tipo_c=='Sincros' or self.variable_tipo_c=='Fusión' or self.variable_tipo_c=='Xyz') and self.variable_elemento=='Todos':
                query = 'SELECT * FROM cartas WHERE clase = ? and nombre LIKE ? and rareza=?  and limitacion = ? ORDER BY archivo '+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,'%'+self.clave+'%',self.variable_rareza,self.variable_limite,))
            elif (self.variable_tipo_c=='Monstruos' or self.variable_tipo_c=='Sincros' or self.variable_tipo_c=='Fusión' or self.variable_tipo_c=='Xyz') and self.variable_elemento!='Todos':
                query = "SELECT * FROM cartas WHERE clase = ? and atributo = ? and nombre LIKE ? and rareza=?  and limitacion = ? ORDER BY archivo "+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,self.variable_elemento,'%'+self.clave+'%',self.variable_rareza,self.variable_limite,))
            elif self.variable_tipo_c=='Todas' and self.variable_elemento!='Todos':
                query = "SELECT * FROM cartas WHERE atributo = ? and nombre LIKE ? and rareza = ?  and limitacion = ? ORDER BY archivo "+ self.orden
                db_columnas = self.consulta(query,(self.variable_elemento,'%'+self.clave+'%',self.variable_rareza,self.variable_limite,))
        # sin búsqueda específica pero con de rareza
        elif self.clave=='' and self.variable_rareza!='' and self.variable_limite!='' and self.variable_nivel=='' and self.variable_tipo_m=='':
            if self.variable_tipo_c=='Todas'and self.variable_elemento=='Todos':
                query = 'SELECT * FROM cartas WHERE rareza=?  and limitacion = ? ORDER BY nombre '+ self.orden #ascedente ASC
                db_columnas = self.consulta(query,(self.variable_rareza,self.variable_limite,))
            elif self.variable_tipo_c=='Mágicas' or self.variable_tipo_c=='Trampas':
                query = 'SELECT * FROM cartas WHERE clase = ? and rareza=?  and limitacion = ? ORDER BY archivo '+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,self.variable_rareza,self.variable_limite,))
            elif (self.variable_tipo_c=='Monstruos' or self.variable_tipo_c=='Sincros' or self.variable_tipo_c=='Fusión' or self.variable_tipo_c=='Xyz') and self.variable_elemento=='Todos':
                query = 'SELECT * FROM cartas WHERE clase = ? and rareza=?  and limitacion = ? ORDER BY archivo '+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,self.variable_rareza,self.variable_limite,))
            elif (self.variable_tipo_c=='Monstruos' or self.variable_tipo_c=='Sincros' or self.variable_tipo_c=='Fusión' or self.variable_tipo_c=='Xyz') and self.variable_elemento!='Todos':
                query = "SELECT * FROM cartas WHERE clase = ? and atributo = ? and rareza=?  and limitacion = ? ORDER BY archivo "+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,self.variable_elemento,self.variable_rareza,self.variable_limite,))
            elif self.variable_tipo_c=='Todas' and self.variable_elemento!='Todos':
                query = "SELECT * FROM cartas WHERE atributo = ? and rareza = ?  and limitacion = ? ORDER BY archivo "+ self.orden
                db_columnas = self.consulta(query,(self.variable_elemento,self.variable_rareza,self.variable_limite,))
        ### con tipo de monstruo
                #con búsqueda específica pero sin rareza
        if self.clave!='' and self.variable_rareza=='' and self.variable_limite=='' and self.variable_nivel=='' and self.variable_tipo_m!='':
            if self.variable_tipo_c=='Todas' and self.variable_elemento=='Todos':
                query = 'SELECT * FROM cartas WHERE nombre LIKE ? and pri_tipo = ? ORDER BY nombre '+ self.orden #ascedente ASC
                db_columnas = self.consulta(query,('%'+self.clave+'%',self.variable_tipo_m,))
            elif self.variable_tipo_c=='Mágicas' or self.variable_tipo_c=='Trampas':
                query = 'SELECT * FROM cartas WHERE clase = ? and nombre LIKE ?  and pri_tipo = ? ORDER BY archivo '+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,'%'+self.clave+'%',self.variable_tipo_m,))
            elif (self.variable_tipo_c=='Monstruos' or self.variable_tipo_c=='Sincros' or self.variable_tipo_c=='Fusión' or self.variable_tipo_c=='Xyz') and self.variable_elemento=='Todos':
                query = 'SELECT * FROM cartas WHERE clase = ? and nombre LIKE ?  and pri_tipo = ? ORDER BY archivo '+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,'%'+self.clave+'%',self.variable_tipo_m,))
            elif (self.variable_tipo_c=='Monstruos' or self.variable_tipo_c=='Sincros' or self.variable_tipo_c=='Fusión' or self.variable_tipo_c=='Xyz') and self.variable_elemento!='Todos':
                query = "SELECT * FROM cartas WHERE clase = ? and atributo = ? and nombre LIKE ?  and pri_tipo = ? ORDER BY archivo "+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,self.variable_elemento,'%'+self.clave+'%',self.variable_tipo_m,))
            elif self.variable_tipo_c=='Todas' and self.variable_elemento!='Todos':
                query = "SELECT * FROM cartas WHERE atributo = ? and nombre LIKE ?  and pri_tipo = ? ORDER BY archivo "+ self.orden
                db_columnas = self.consulta(query,(self.variable_elemento,'%'+self.clave+'%',self.variable_tipo_m,))
        #sin búsqueda específica pero sin rareza
        elif self.clave=='' and self.variable_rareza=='' and self.variable_limite=='' and self.variable_nivel=='' and self.variable_tipo_m!='':
            if self.variable_tipo_c=='Todas'and self.variable_elemento=='Todos':
                query = 'SELECT * FROM cartas  WHERE pri_tipo = ? ORDER BY nombre '+ self.orden #ascedente ASC
                db_columnas = self.consulta(query,(self.variable_tipo_m,))
            elif self.variable_tipo_c=='Mágicas' or self.variable_tipo_c=='Trampas':
                query = 'SELECT * FROM cartas WHERE clase = ?  and pri_tipo = ? ORDER BY archivo '+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,self.variable_tipo_m,))
            elif (self.variable_tipo_c=='Monstruos' or self.variable_tipo_c=='Sincros' or self.variable_tipo_c=='Fusión' or self.variable_tipo_c=='Xyz') and self.variable_elemento=='Todos':
                query = 'SELECT * FROM cartas WHERE clase = ?  and pri_tipo = ? ORDER BY archivo '+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,self.variable_tipo_m,))
            elif (self.variable_tipo_c=='Monstruos' or self.variable_tipo_c=='Sincros' or self.variable_tipo_c=='Fusión' or self.variable_tipo_c=='Xyz') and self.variable_elemento!='Todos':
                query = "SELECT * FROM cartas WHERE clase = ? and atributo = ?  and pri_tipo = ? ORDER BY archivo "+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,self.variable_elemento,self.variable_tipo_m,))
            elif self.variable_tipo_c=='Todas' and self.variable_elemento!='Todos':
                query = "SELECT * FROM cartas WHERE atributo = ?  and pri_tipo = ? ORDER BY archivo "+ self.orden
                db_columnas = self.consulta(query,(self.variable_elemento,self.variable_tipo_m,))
        # con búsqueda específica y con rareza
        elif self.clave!='' and self.variable_rareza!='' and self.variable_limite=='' and self.variable_nivel=='' and self.variable_tipo_m!='':
            if self.variable_tipo_c=='Todas'and self.variable_elemento=='Todos':
                query = 'SELECT * FROM cartas WHERE nombre LIKE ? and rareza=?  and pri_tipo = ? ORDER BY nombre '+ self.orden #ascedente ASC
                db_columnas = self.consulta(query,('%'+self.clave+'%',self.variable_rareza,self.variable_tipo_m,))
            elif self.variable_tipo_c=='Mágicas' or self.variable_tipo_c=='Trampas':
                query = 'SELECT * FROM cartas WHERE clase = ? and nombre LIKE ? and rareza=?  and pri_tipo = ? ORDER BY archivo '+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,'%'+self.clave+'%',self.variable_rareza,self.variable_tipo_m,))
            elif (self.variable_tipo_c=='Monstruos' or self.variable_tipo_c=='Sincros' or self.variable_tipo_c=='Fusión' or self.variable_tipo_c=='Xyz') and self.variable_elemento=='Todos':
                query = 'SELECT * FROM cartas WHERE clase = ? and nombre LIKE ? and rareza=?  and pri_tipo = ? ORDER BY archivo '+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,'%'+self.clave+'%',self.variable_rareza,self.variable_tipo_m,))
            elif (self.variable_tipo_c=='Monstruos' or self.variable_tipo_c=='Sincros' or self.variable_tipo_c=='Fusión' or self.variable_tipo_c=='Xyz') and self.variable_elemento!='Todos':
                query = "SELECT * FROM cartas WHERE clase = ? and atributo = ? and nombre LIKE ? and rareza=?  and pri_tipo = ? ORDER BY archivo "+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,self.variable_elemento,'%'+self.clave+'%',self.variable_rareza,self.variable_tipo_m,))
            elif self.variable_tipo_c=='Todas' and self.variable_elemento!='Todos':
                query = "SELECT * FROM cartas WHERE atributo = ? and nombre LIKE ? and rareza = ?  and pri_tipo = ? ORDER BY archivo "+ self.orden
                db_columnas = self.consulta(query,(self.variable_elemento,'%'+self.clave+'%',self.variable_rareza,self.variable_tipo_m,))
        # sin búsqueda específica pero con de rareza
        elif self.clave=='' and self.variable_rareza!='' and self.variable_limite=='' and self.variable_nivel=='' and self.variable_tipo_m!='':
            if self.variable_tipo_c=='Todas'and self.variable_elemento=='Todos':
                query = 'SELECT * FROM cartas WHERE rareza=?  and pri_tipo = ? ORDER BY nombre '+ self.orden #ascedente ASC
                db_columnas = self.consulta(query,(self.variable_rareza,self.variable_tipo_m,))
            elif self.variable_tipo_c=='Mágicas' or self.variable_tipo_c=='Trampas':
                query = 'SELECT * FROM cartas WHERE clase = ? and rareza=?  and pri_tipo = ? ORDER BY archivo '+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,self.variable_rareza,self.variable_tipo_m,))
            elif (self.variable_tipo_c=='Monstruos' or self.variable_tipo_c=='Sincros' or self.variable_tipo_c=='Fusión' or self.variable_tipo_c=='Xyz') and self.variable_elemento=='Todos':
                query = 'SELECT * FROM cartas WHERE clase = ? and rareza=?  and pri_tipo = ? ORDER BY archivo '+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,self.variable_rareza,self.variable_tipo_m,))
            elif (self.variable_tipo_c=='Monstruos' or self.variable_tipo_c=='Sincros' or self.variable_tipo_c=='Fusión' or self.variable_tipo_c=='Xyz') and self.variable_elemento!='Todos':
                query = "SELECT * FROM cartas WHERE clase = ? and atributo = ? and rareza=?  and pri_tipo = ? ORDER BY archivo "+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,self.variable_elemento,self.variable_rareza,self.variable_tipo_m,))
            elif self.variable_tipo_c=='Todas' and self.variable_elemento!='Todos':
                query = "SELECT * FROM cartas WHERE atributo = ? and rareza = ?  and pri_tipo = ? ORDER BY archivo "+ self.orden
                db_columnas = self.consulta(query,(self.variable_elemento,self.variable_rareza,self.variable_tipo_m,))
        #### LIMITACIÓN
        if self.clave!='' and self.variable_rareza=='' and self.variable_limite!='' and self.variable_nivel=='' and self.variable_tipo_m!='':
            if self.variable_tipo_c=='Todas' and self.variable_elemento=='Todos':
                query = 'SELECT * FROM cartas WHERE nombre LIKE ?  and limitacion = ?  and pri_tipo = ? ORDER BY nombre '+ self.orden #ascedente ASC
                db_columnas = self.consulta(query,('%'+self.clave+'%',self.variable_limite,self.variable_tipo_m,))
            elif self.variable_tipo_c=='Mágicas' or self.variable_tipo_c=='Trampas':
                query = 'SELECT * FROM cartas WHERE clase = ? and nombre LIKE ?  and limitacion = ?  and pri_tipo = ? ORDER BY archivo '+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,'%'+self.clave+'%',self.variable_limite,self.variable_tipo_m,))
            elif (self.variable_tipo_c=='Monstruos' or self.variable_tipo_c=='Sincros' or self.variable_tipo_c=='Fusión' or self.variable_tipo_c=='Xyz') and self.variable_elemento=='Todos':
                query = 'SELECT * FROM cartas WHERE clase = ? and nombre LIKE ?  and limitacion = ?  and pri_tipo = ? ORDER BY archivo '+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,'%'+self.clave+'%',self.variable_limite,self.variable_tipo_m,))
            elif (self.variable_tipo_c=='Monstruos' or self.variable_tipo_c=='Sincros' or self.variable_tipo_c=='Fusión' or self.variable_tipo_c=='Xyz') and self.variable_elemento!='Todos':
                query = "SELECT * FROM cartas WHERE clase = ? and atributo = ? and nombre LIKE ?  and limitacion = ?  and pri_tipo = ? ORDER BY archivo "+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,self.variable_elemento,'%'+self.clave+'%',self.variable_limite,self.variable_tipo_m,))
            elif self.variable_tipo_c=='Todas' and self.variable_elemento!='Todos':
                query = "SELECT * FROM cartas WHERE atributo = ? and nombre LIKE ?  and limitacion = ?  and pri_tipo = ? ORDER BY archivo "+ self.orden
                db_columnas = self.consulta(query,(self.variable_elemento,'%'+self.clave+'%',self.variable_limite,self.variable_tipo_m,))
        #sin búsqueda específica pero sin rareza
        elif self.clave=='' and self.variable_rareza=='' and self.variable_limite!='' and self.variable_nivel=='' and self.variable_tipo_m!='':
            if self.variable_tipo_c=='Todas'and self.variable_elemento=='Todos':
                query = 'SELECT * FROM cartas  WHERE limitacion = ?  and pri_tipo = ? ORDER BY nombre '+ self.orden #ascedente ASC
                db_columnas = self.consulta(query,(self.variable_limite,self.variable_tipo_m,))
            elif self.variable_tipo_c=='Mágicas' or self.variable_tipo_c=='Trampas':
                query = 'SELECT * FROM cartas WHERE clase = ?  and limitacion = ?  and pri_tipo = ? ORDER BY archivo '+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,self.variable_limite,self.variable_tipo_m,))
            elif (self.variable_tipo_c=='Monstruos' or self.variable_tipo_c=='Sincros' or self.variable_tipo_c=='Fusión' or self.variable_tipo_c=='Xyz') and self.variable_elemento=='Todos':
                query = 'SELECT * FROM cartas WHERE clase = ?  and limitacion = ?  and pri_tipo = ? ORDER BY archivo '+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,self.variable_limite,self.variable_tipo_m,))
            elif (self.variable_tipo_c=='Monstruos' or self.variable_tipo_c=='Sincros' or self.variable_tipo_c=='Fusión' or self.variable_tipo_c=='Xyz') and self.variable_elemento!='Todos':
                query = "SELECT * FROM cartas WHERE clase = ? and atributo = ?  and limitacion = ?  and pri_tipo = ? ORDER BY archivo "+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,self.variable_elemento,self.variable_limite,self.variable_tipo_m,))
            elif self.variable_tipo_c=='Todas' and self.variable_elemento!='Todos':
                query = "SELECT * FROM cartas WHERE atributo = ?  and limitacion = ?  and pri_tipo = ? ORDER BY archivo "+ self.orden
                db_columnas = self.consulta(query,(self.variable_elemento,self.variable_limite,self.variable_tipo_m,))
        # con búsqueda específica y con rareza
        elif self.clave!='' and self.variable_rareza!='' and self.variable_limite!='' and self.variable_nivel=='' and self.variable_tipo_m!='':
            if self.variable_tipo_c=='Todas'and self.variable_elemento=='Todos':
                query = 'SELECT * FROM cartas WHERE nombre LIKE ? and rareza=?  and limitacion = ?  and pri_tipo = ? ORDER BY nombre '+ self.orden #ascedente ASC
                db_columnas = self.consulta(query,('%'+self.clave+'%',self.variable_rareza,self.variable_limite,self.variable_tipo_m,))
            elif self.variable_tipo_c=='Mágicas' or self.variable_tipo_c=='Trampas':
                query = 'SELECT * FROM cartas WHERE clase = ? and nombre LIKE ? and rareza=?  and limitacion = ?  and pri_tipo = ? ORDER BY archivo '+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,'%'+self.clave+'%',self.variable_rareza,self.variable_limite,self.variable_tipo_m,))
            elif (self.variable_tipo_c=='Monstruos' or self.variable_tipo_c=='Sincros' or self.variable_tipo_c=='Fusión' or self.variable_tipo_c=='Xyz') and self.variable_elemento=='Todos':
                query = 'SELECT * FROM cartas WHERE clase = ? and nombre LIKE ? and rareza=?  and limitacion = ?  and pri_tipo = ? ORDER BY archivo '+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,'%'+self.clave+'%',self.variable_rareza,self.variable_limite,self.variable_tipo_m,))
            elif (self.variable_tipo_c=='Monstruos' or self.variable_tipo_c=='Sincros' or self.variable_tipo_c=='Fusión' or self.variable_tipo_c=='Xyz') and self.variable_elemento!='Todos':
                query = "SELECT * FROM cartas WHERE clase = ? and atributo = ? and nombre LIKE ? and rareza=?  and limitacion = ?  and pri_tipo = ? ORDER BY archivo "+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,self.variable_elemento,'%'+self.clave+'%',self.variable_rareza,self.variable_limite,self.variable_tipo_m,))
            elif self.variable_tipo_c=='Todas' and self.variable_elemento!='Todos':
                query = "SELECT * FROM cartas WHERE atributo = ? and nombre LIKE ? and rareza = ?  and limitacion = ?  and pri_tipo = ? ORDER BY archivo "+ self.orden
                db_columnas = self.consulta(query,(self.variable_elemento,'%'+self.clave+'%',self.variable_rareza,self.variable_limite,self.variable_tipo_m,))
        # sin búsqueda específica pero con de rareza
        elif self.clave=='' and self.variable_rareza!='' and self.variable_limite!='' and self.variable_nivel=='' and self.variable_tipo_m!='':
            if self.variable_tipo_c=='Todas'and self.variable_elemento=='Todos':
                query = 'SELECT * FROM cartas WHERE rareza=?  and limitacion = ?  and pri_tipo = ? ORDER BY nombre '+ self.orden #ascedente ASC
                db_columnas = self.consulta(query,(self.variable_rareza,self.variable_limite,self.variable_tipo_m,))
            elif self.variable_tipo_c=='Mágicas' or self.variable_tipo_c=='Trampas':
                query = 'SELECT * FROM cartas WHERE clase = ? and rareza=?  and limitacion = ?  and pri_tipo = ? ORDER BY archivo '+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,self.variable_rareza,self.variable_limite,self.variable_tipo_m,))
            elif (self.variable_tipo_c=='Monstruos' or self.variable_tipo_c=='Sincros' or self.variable_tipo_c=='Fusión' or self.variable_tipo_c=='Xyz') and self.variable_elemento=='Todos':
                query = 'SELECT * FROM cartas WHERE clase = ? and rareza=?  and limitacion = ?  and pri_tipo = ? ORDER BY archivo '+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,self.variable_rareza,self.variable_limite,self.variable_tipo_m,))
            elif (self.variable_tipo_c=='Monstruos' or self.variable_tipo_c=='Sincros' or self.variable_tipo_c=='Fusión' or self.variable_tipo_c=='Xyz') and self.variable_elemento!='Todos':
                query = "SELECT * FROM cartas WHERE clase = ? and atributo = ? and rareza=?  and limitacion = ?  and pri_tipo = ? ORDER BY archivo "+ self.orden
                db_columnas = self.consulta(query,(self.variable_tipo_c,self.variable_elemento,self.variable_rareza,self.variable_limite,self.variable_tipo_m,))
            elif self.variable_tipo_c=='Todas' and self.variable_elemento!='Todos':
                query = "SELECT * FROM cartas WHERE atributo = ? and rareza = ?  and limitacion = ?  and pri_tipo = ? ORDER BY archivo "+ self.orden
                db_columnas = self.consulta(query,(self.variable_elemento,self.variable_rareza,self.variable_limite,self.variable_tipo_m,))
        ### con nivel o rango
        elif self.variable_nivel!='':
            if self.variable_tipo_m!='':
                if self.variable_limite!='':
                    if self.variable_elemento!='Todos':
                        if self.clave!='':
                            if self.variable_rareza!='':
                                if self.variable_tipo_c!='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and pri_tipo = ? and limitacion = ? and atributo = ? and nombre LIKE ? and rareza = ? and clase = ? ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_tipo_m,self.variable_limite,self.variable_elemento,'%'+self.clave+'%',self.variable_rareza,self.variable_tipo_c,))
                                elif self.variable_tipo_c=='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and pri_tipo = ? and limitacion = ? and atributo = ? and nombre LIKE ? and rareza = ?  ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_tipo_m,self.variable_limite,self.variable_elemento,'%'+self.clave+'%',self.variable_rareza,))
                            elif self.variable_rareza=='':
                                if self.variable_tipo_c!='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and pri_tipo = ? and limitacion = ? and atributo = ? and nombre LIKE ? and clase = ? ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_tipo_m,self.variable_limite,self.variable_elemento,'%'+self.clave+'%',self.variable_tipo_c,))
                                elif self.variable_tipo_c=='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and pri_tipo = ? and limitacion = ? and atributo = ? and nombre LIKE ?  ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_tipo_m,self.variable_limite,self.variable_elemento,'%'+self.clave+'%',))
                        elif self.clave=='':
                            if self.variable_rareza!='':
                                if self.variable_tipo_c!='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and pri_tipo = ? and limitacion = ? and atributo = ? and rareza = ? and clase = ? ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_tipo_m,self.variable_limite,self.variable_elemento,self.variable_rareza,self.variable_tipo_c,))
                                elif self.variable_tipo_c=='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and pri_tipo = ? and limitacion = ? and atributo = ? and rareza = ?  ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_tipo_m,self.variable_limite,self.variable_elemento,self.variable_rareza,))
                            elif self.variable_rareza=='':
                                if self.variable_tipo_c!='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and pri_tipo = ? and limitacion = ? and atributo = ? and clase = ? ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_tipo_m,self.variable_limite,self.variable_elemento,self.variable_tipo_c,))
                                elif self.variable_tipo_c=='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and pri_tipo = ? and limitacion = ? and atributo = ?  ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_tipo_m,self.variable_limite,self.variable_elemento,))
                    elif self.variable_elemento=='Todos':
                        if self.clave!='':
                            if self.variable_rareza!='':
                                if self.variable_tipo_c!='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and pri_tipo = ? and limitacion = ? and nombre LIKE ? and rareza = ? and clase = ? ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_tipo_m,self.variable_limite,'%'+self.clave+'%',self.variable_rareza,self.variable_tipo_c,))
                                elif self.variable_tipo_c=='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and pri_tipo = ? and limitacion = ? and nombre LIKE ? and rareza = ?  ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_tipo_m,self.variable_limite,'%'+self.clave+'%',self.variable_rareza,))
                            elif self.variable_rareza=='':
                                if self.variable_tipo_c!='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and pri_tipo = ? and limitacion = ? and nombre LIKE ? and clase = ? ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_tipo_m,self.variable_limite,'%'+self.clave+'%',self.variable_tipo_c,))
                                elif self.variable_tipo_c=='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and pri_tipo = ? and limitacion = ? and nombre LIKE ?  ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_tipo_m,self.variable_limite,'%'+self.clave+'%',))
                        elif self.clave=='':
                            if self.variable_rareza!='':
                                if self.variable_tipo_c!='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and pri_tipo = ? and limitacion = ? and rareza = ? and clase = ? ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_tipo_m,self.variable_limite,self.variable_rareza,self.variable_tipo_c,))
                                elif self.variable_tipo_c=='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and pri_tipo = ? and limitacion = ? and rareza = ?  ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_tipo_m,self.variable_limite,self.variable_rareza,))
                            elif self.variable_rareza=='':
                                if self.variable_tipo_c!='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and pri_tipo = ? and limitacion = ? and clase = ? ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_tipo_m,self.variable_limite,self.variable_tipo_c,))
                                elif self.variable_tipo_c=='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and pri_tipo = ? and limitacion = ?  ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_tipo_m,self.variable_limite,))
                elif self.variable_limite=='':
                    if self.variable_elemento!='Todos':
                        if self.clave!='':
                            if self.variable_rareza!='':
                                if self.variable_tipo_c!='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and pri_tipo = ? and atributo = ? and nombre LIKE ? and rareza = ? and clase = ? ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_tipo_m,self.variable_elemento,'%'+self.clave+'%',self.variable_rareza,self.variable_tipo_c,))
                                elif self.variable_tipo_c=='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and pri_tipo = ? and atributo = ? and nombre LIKE ? and rareza = ?  ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_tipo_m,self.variable_elemento,'%'+self.clave+'%',self.variable_rareza,))
                            elif self.variable_rareza=='':
                                if self.variable_tipo_c!='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and pri_tipo = ? and atributo = ? and nombre LIKE ? and clase = ? ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_tipo_m,self.variable_elemento,'%'+self.clave+'%',self.variable_tipo_c,))
                                elif self.variable_tipo_c=='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and pri_tipo = ? and atributo = ? and nombre LIKE ?  ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_tipo_m,self.variable_elemento,'%'+self.clave+'%',))
                        elif self.clave=='':
                            if self.variable_rareza!='':
                                if self.variable_tipo_c!='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and pri_tipo = ? and atributo = ? and rareza = ? and clase = ? ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_tipo_m,self.variable_elemento,self.variable_rareza,self.variable_tipo_c,))
                                elif self.variable_tipo_c=='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and pri_tipo = ? and atributo = ? and rareza = ?  ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_tipo_m,self.variable_elemento,self.variable_rareza,))
                            elif self.variable_rareza=='':
                                if self.variable_tipo_c!='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and pri_tipo = ? and atributo = ? and clase = ? ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_tipo_m,self.variable_elemento,self.variable_tipo_c,))
                                elif self.variable_tipo_c=='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and pri_tipo = ? and atributo = ?  ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_tipo_m,self.variable_elemento,))
                    elif self.variable_elemento=='Todos':
                        if self.clave!='':
                            if self.variable_rareza!='':
                                if self.variable_tipo_c!='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and pri_tipo = ? and nombre LIKE ? and rareza = ? and clase = ? ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_tipo_m,'%'+self.clave+'%',self.variable_rareza,self.variable_tipo_c,))
                                elif self.variable_tipo_c=='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and pri_tipo = ? and nombre LIKE ? and rareza = ?  ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_tipo_m,'%'+self.clave+'%',self.variable_rareza,))
                            elif self.variable_rareza=='':
                                if self.variable_tipo_c!='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and pri_tipo = ? and nombre LIKE ? and clase = ? ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_tipo_m,'%'+self.clave+'%',self.variable_tipo_c,))
                                elif self.variable_tipo_c=='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and pri_tipo = ? and nombre LIKE ?  ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_tipo_m,'%'+self.clave+'%',))
                        elif self.clave=='':
                            if self.variable_rareza!='':
                                if self.variable_tipo_c!='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and pri_tipo = ? and rareza = ? and clase = ? ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_tipo_m,self.variable_rareza,self.variable_tipo_c,))
                                elif self.variable_tipo_c=='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and pri_tipo = ? and rareza = ?  ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_tipo_m,self.variable_rareza,))
                            elif self.variable_rareza=='':
                                if self.variable_tipo_c!='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and pri_tipo = ? and clase = ? ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_tipo_m,self.variable_tipo_c,))
                                elif self.variable_tipo_c=='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and pri_tipo = ?  ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_tipo_m,))
            elif self.variable_tipo_m=='':
                if self.variable_limite!='':
                    if self.variable_elemento!='Todos':
                        if self.clave!='':
                            if self.variable_rareza!='':
                                if self.variable_tipo_c!='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and limitacion = ? and atributo = ? and nombre LIKE ? and rareza = ? and clase = ? ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_limite,self.variable_elemento,'%'+self.clave+'%',self.variable_rareza,self.variable_tipo_c,))
                                elif self.variable_tipo_c=='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and limitacion = ? and atributo = ? and nombre LIKE ? and rareza = ?  ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_limite,self.variable_elemento,'%'+self.clave+'%',self.variable_rareza,))
                            elif self.variable_rareza=='':
                                if self.variable_tipo_c!='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and limitacion = ? and atributo = ? and nombre LIKE ? and clase = ? ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_limite,self.variable_elemento,'%'+self.clave+'%',self.variable_tipo_c,))
                                elif self.variable_tipo_c=='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and limitacion = ? and atributo = ? and nombre LIKE ?  ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_limite,self.variable_elemento,'%'+self.clave+'%',))
                        elif self.clave=='':
                            if self.variable_rareza!='':
                                if self.variable_tipo_c!='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and limitacion = ? and atributo = ? and rareza = ? and clase = ? ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_limite,self.variable_elemento,self.variable_rareza,self.variable_tipo_c,))
                                elif self.variable_tipo_c=='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and limitacion = ? and atributo = ? and rareza = ?  ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_limite,self.variable_elemento,self.variable_rareza,))
                            elif self.variable_rareza=='':
                                if self.variable_tipo_c!='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and limitacion = ? and atributo = ? and clase = ? ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_limite,self.variable_elemento,self.variable_tipo_c,))
                                elif self.variable_tipo_c=='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and limitacion = ? and atributo = ?  ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_limite,self.variable_elemento,))
                    elif self.variable_elemento=='Todos':
                        if self.clave!='':
                            if self.variable_rareza!='':
                                if self.variable_tipo_c!='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and limitacion = ? and nombre LIKE ? and rareza = ? and clase = ? ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_limite,'%'+self.clave+'%',self.variable_rareza,self.variable_tipo_c,))
                                elif self.variable_tipo_c=='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and limitacion = ? and nombre LIKE ? and rareza = ?  ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_limite,'%'+self.clave+'%',self.variable_rareza,))
                            elif self.variable_rareza=='':
                                if self.variable_tipo_c!='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and limitacion = ? and nombre LIKE ? and clase = ? ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_limite,'%'+self.clave+'%',self.variable_tipo_c,))
                                elif self.variable_tipo_c=='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and limitacion = ? and nombre LIKE ?  ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_limite,'%'+self.clave+'%',))
                        elif self.clave=='':
                            if self.variable_rareza!='':
                                if self.variable_tipo_c!='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and limitacion = ? and rareza = ? and clase = ? ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_limite,self.variable_rareza,self.variable_tipo_c,))
                                elif self.variable_tipo_c=='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and limitacion = ? and rareza = ?  ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_limite,self.variable_rareza,))
                            elif self.variable_rareza=='':
                                if self.variable_tipo_c!='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and limitacion = ? and clase = ? ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_limite,self.variable_tipo_c,))
                                elif self.variable_tipo_c=='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and limitacion = ?  ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_limite,))
                elif self.variable_limite=='':
                    if self.variable_elemento!='Todos':
                        if self.clave!='':
                            if self.variable_rareza!='':
                                if self.variable_tipo_c!='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and atributo = ? and nombre LIKE ? and rareza = ? and clase = ? ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_elemento,'%'+self.clave+'%',self.variable_rareza,self.variable_tipo_c,))
                                elif self.variable_tipo_c=='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and atributo = ? and nombre LIKE ? and rareza = ?  ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_elemento,'%'+self.clave+'%',self.variable_rareza,))
                            elif self.variable_rareza=='':
                                if self.variable_tipo_c!='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and atributo = ? and nombre LIKE ? and clase = ? ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_elemento,'%'+self.clave+'%',self.variable_tipo_c,))
                                elif self.variable_tipo_c=='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and atributo = ? and nombre LIKE ?  ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_elemento,'%'+self.clave+'%',))
                        elif self.clave=='':
                            if self.variable_rareza!='':
                                if self.variable_tipo_c!='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and atributo = ? and rareza = ? and clase = ? ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_elemento,self.variable_rareza,self.variable_tipo_c,))
                                elif self.variable_tipo_c=='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and atributo = ? and rareza = ?  ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_elemento,self.variable_rareza,))
                            elif self.variable_rareza=='':
                                if self.variable_tipo_c!='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and atributo = ? and clase = ? ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_elemento,self.variable_tipo_c,))
                                elif self.variable_tipo_c=='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and atributo = ?  ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_elemento,))
                    elif self.variable_elemento=='Todos':
                        if self.clave!='':
                            if self.variable_rareza!='':
                                if self.variable_tipo_c!='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and nombre LIKE ? and rareza = ? and clase = ? ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,'%'+self.clave+'%',self.variable_rareza,self.variable_tipo_c,))
                                elif self.variable_tipo_c=='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and nombre LIKE ? and rareza = ?  ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,'%'+self.clave+'%',self.variable_rareza,))
                            elif self.variable_rareza=='':
                                if self.variable_tipo_c!='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and nombre LIKE ? and clase = ? ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,'%'+self.clave+'%',self.variable_tipo_c,))
                                elif self.variable_tipo_c=='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and nombre LIKE ?  ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,'%'+self.clave+'%',))
                        elif self.clave=='':
                            if self.variable_rareza!='':
                                if self.variable_tipo_c!='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and rareza = ? and clase = ? ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_rareza,self.variable_tipo_c,))
                                elif self.variable_tipo_c=='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and rareza = ?  ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_rareza,))
                            elif self.variable_rareza=='':
                                if self.variable_tipo_c!='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ? and clase = ? ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,self.variable_tipo_c,))
                                elif self.variable_tipo_c=='Todas':
                                    query = "SELECT * FROM cartas WHERE nivel = ?  ORDER BY archivo "+ self.orden
                                    db_columnas = self.consulta(query,(self.variable_nivel,))

        records=db_columnas.fetchall()
        i=0
        self.icon2=[None]*len(records)    
        
        for row in records:
            if i%2==0:
                tg='white'
            else:
                tg='#c0c0c0'
            self.icon2[i] = ImageTk.PhotoImage(Image.open('cartas2/'+ row[8]))
            self.mostrador.insert('', 0 , text = row[2], values =(row[2] , row[7]),image=self.icon2[i],tag=(tg))
            self.mostrador.tag_configure(tg, background=tg,foreground="black")
            i+=1

if __name__ == "__main__":
       root = tk.Tk()
       root.title("Creador de Mazo")
       root.geometry("1155x650")
       root.iconphoto(True, tk.PhotoImage(file='fuentes/icono.png'))
       root.resizable(0, 0)
       view = APP(root)
       view.pack(side="top", fill="both", expand=True)
       root.mainloop()