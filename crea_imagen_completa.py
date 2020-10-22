from PIL import Image,ImageDraw, ImageFont
def crear_mini(archivo):
    image2 = Image.open('cartas/'+ archivo)
    image2.thumbnail([55,80], Image.ANTIALIAS)
    image2.save('cartas2/' + archivo)

def crear_normal(archivo):
    image2 = Image.open('cartas/'+ archivo)
    image2.thumbnail(image2.size, Image.ANTIALIAS)
    image2.save('cartas/' + archivo, "JPEG")

def crear(v_cartas=[],v_cartasx=[],HD=False,skill=''):
    cartasm=0
    cartasx=0
    v_cartas2=[]
    v_cartasx2=[]
    extra=False
    for i in v_cartas:
        if i!=None:
            cartasm+=1
            v_cartas2.append(i)
    for i in v_cartasx:
        if i!=None:
            extra=True
            cartasx+=1
            v_cartasx2.append(i)
    y=300
    tmbname=skill + ".jpg"
    if cartasm>18 and cartasm<=24:
        if skill=='':
            size = (3226,3570)
            size1 = (3226,2856)
            y=50
            tmbname="Otro_Deck.jpg"
        else:
            size = (3226,3820)
            size1 = (3226,3106)
        
    elif cartasm>=25 and cartasm<=30:
        if skill=='':
            size = (3226,4334)
            size1 = (3226,3570)
            y=50
            tmbname="Otro_Deck.jpg"
        else:
            size = (3226,4584)
            size1 = (3226,3820)
        
    elif cartasm>7 and cartasm<=12:
        if skill=='':
            size = (3226,2192)
            size1 = (3226,1428)
            y=50
            tmbname="Otro_Deck.jpg"
        else:
            size = (3226,2442)
            size1 = (3226,1678)
    elif cartasm>12 and cartasm<=18:
        if skill=='':
            size = (3226,2906)
            size1 = (3226,2142)
            y=50
            tmbname="Otro_Deck.jpg"
        else:
            size = (3226,3156)
            size1 = (3226,2392)
    elif cartasm<=7:
        v_cartas2.extend(v_cartasx2)
        cartasm=len(v_cartas2)
        extra=False 
        size = (3226,814)
        if cartasm==7:
            size=(3747,814)
        if skill=='':
            size = (3226,714)
            if cartasm==7:
                size=(3747,714)
            y=50
            tmbname="Side_Deck.jpg"
        else:
            size = (3226,1064)
            if cartasm==7:
                size=(3747,1064)
    if not extra and cartasm>7:
        size=size1
    img = Image.new('RGB' ,size)
    fondo1= Image.open('fuentes/fondo_main.png')
    fondo=fondo1.resize(size)
    img.paste(fondo,(0,0))
    x=100
    if skill!='':
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("arial.ttf", 180)
        tama=draw.textsize(skill, font=font)
        inicial= int((size[0]/2)-(tama[0]/2))
        draw.text((inicial, 40), skill, font=font, fill="white")

    im_log= [None]*cartasm
    for i in range(cartasm):
        if x==size[0]:
            x=100
            y+=714
        im_log[i] = Image.open('cartas/' + v_cartas2[i])
        img.paste(im_log[i], (x,y))
        x+=521

    if extra:
        fondo1= Image.open('fuentes/fondo_extra.png')
        fondo=fondo1.resize((size[0] , 764))
        if cartasx==7:
            x=20
        else:
            x=100
        img.paste(fondo,(0,size1[1]))
        for i in range(cartasx):
            im_log[i] = Image.open('cartas/' + v_cartasx2[i])
            img.paste(im_log[i],(x,size1[1]+50))
            if cartasx==7:
                x+=461
            else:
                x+=521
    if HD:
        img.save('../Deck_HD.png')
    if size[1]*0.3<250:
        size= (size[0]*0.3 , size[1]*0.37)
        img=img.resize((int(size[0]),int(size[1])))
    else:
        size= (size[0]*0.3 , size[1]*0.3)
    img.thumbnail(size)
    img.save('../' + tmbname, "JPEG")
