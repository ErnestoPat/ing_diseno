# -*- coding: utf-8 -*-
"""
Created on Thu May 16 22:20:53 2019
Programa para calcular la resistencia de secciones W
@author: ernes
"""
import pandas as pd
#Datos
nombre_excel = "C:\\Users\\Ernesto\\Desktop\\maestria\\estructuras metalicas\\libros clases etc\\aisc-shapes-database-v15.0.xlsx"
nombre_hoja = "Database v15.0"
perfil = "W8X40"
sistema = "decimal_t_m"#"ingles","decimal_t_m"
revision = ["flexion_x","cortante","compresion", "flexo-compresion","flexion_y"] #"flexion_x","flexion_y","cortante", "tension", "compresion", "flexo-compresion"

#Datos del acero
Fy = 35150#35150#29550
Fu = 45700#45700#40800
E = 20000000#20389010#2038901
G= E/2.589

#Factores de seguridad
Fr_flexion = 0.9
Fr_cortante = 0.9
Fr_tension_fluencia = 0.9
Fr_tension_fractura = 0.75
Fr_compresion = 0.9

#calculo de Cb
Mmax = 3.41
MA = .44
MB = 1.6
MC = .44
Cb =(12.5*Mmax)/(2.5*Mmax+3*MA+4*MB+3*MC)
Cb = 1
#Datos de la viga columna

c=1
Lb = 3
Ae = 1 #An*U
kx = 1
ky = 1
kz = 1

#Datos de las acciones
Ma = 6.76
Va = 6

#flexocompresion
P= 5
M1= 3
M2= 10.74
              
xl = pd.ExcelFile(nombre_excel)
doc = xl.parse(nombre_hoja)
fila = doc[doc[ "AISC_Manual_Label"] == perfil]



if sistema == "decimal_t_m":
    Fpeso = 0.000453592
    Farea = (0.00064516)
    F_distancia = (2.54/100)
    F_distancia_cubica = (0.0000163871)
    F_distancia_cuarta = (.00000041623)
    F_distancia_sexta = ((2.54/100)**6)
    
elif sistema == "ingles":
    Fpeso = 1
    Farea = 1
    F_distancia = 1
    F_distancia_cubica = 1
    F_distancia_cuarta = 1
    F_distancia_sexta = 1

W = float(fila["W"]*Fpeso)
Ag = float(fila["A"] *Farea)
d = float(fila["ddet"] *F_distancia)
bf= float(fila["bfdet"]*F_distancia)
tw= float(fila["twdet"]*F_distancia)
tf= float(fila["tfdet"]*F_distancia)
Ix = float(fila["Ix"]*F_distancia_cuarta)
Zx = float(fila["Zx"]*F_distancia_cubica)
Sx = float(fila["Sx"]*F_distancia_cubica)
rx = float(fila["rx"]*F_distancia)
Iy = float(fila["Iy"]*F_distancia_cuarta)
Zy = float(fila["Zy"]*F_distancia_cubica )
Sy = float(fila["Sy"]*F_distancia_cubica )
ry = float(fila["ry"]*F_distancia)
J = float(fila["J"]*F_distancia_cuarta)
Cw=float(fila["Cw"]*F_distancia_sexta)
rts =float( fila["rts"]*F_distancia)
h0 = float(fila["ho"]*F_distancia)
r0 = ((Ix+Iy)/Ag)**0.5

h_t = float(fila["h/tw"])
print("h_t=",h_t)
b_t = float(fila["bf/2tf"])
print("b_t",b_t)
lamda_p_patines = 0.38*(E/Fy)**0.5
print("lamda_p_patines",lamda_p_patines)
lamda_r_patines = 1*(E/Fy)**0.5
print("lamda_r_patines",lamda_r_patines)

lamda_p_alma = 3.76*(E/Fy)**0.5
lamda_r_alma = 5.7*(E/Fy)**0.5

if b_t < lamda_p_patines:
    compact_patines = "compacto_patines"
    print("patines compactos")
elif lamda_p_patines < b_t < lamda_r_patines:
    compact_patines = "no_compacto_patines"
    print("patines no compactos")
elif lamda_r_patines < b_t:
    compact_patines = "esbelto_patines" 
    print("patines esbeltos")

if h_t  < lamda_p_alma:
    compact_alma = "compacto_alma"
    print("alma compactos")    
elif lamda_p_alma < h_t  < lamda_r_alma:
    compact_alma = "no_compacto_alma"
    print("alma no compactos")
elif lamda_r_alma < h_t :
    compact_alma = "esbelto_alma"  
    print("alma esbeltos")

#secciones compactas
if "flexion_x" in revision:
    c=1
    Lp = 1.76*ry*(E/Fy)**0.5
    Lr = 1.95*rts*(E/(0.7*Fy))*(((J*c)/(Sx*h0))+((((J*c)/(Sx*h0))**2)+(6.76*((0.7*Fy)/E)**2))**0.5)**.5
    
    
    #almas compactas y patines compactos
    Mn_plastico_X = Fy*Zx
    Mn_pandeo_patin_X = Mn_plastico_X
    if Lb<=Lp:
        Mn_torsional_X = Mn_plastico_X
    elif Lp<Lb<=Lr:
        Mn_torsional_X = Cb*(Mn_plastico_X-(Mn_plastico_X-(0.7*Fy*Sx))*((Lb-Lp)/(Lr-Lp)))
    elif Lb>Lr:
        Fcr = ((Cb*3.1416*3.1416*E)/(Lb/rts)**2)*(1+0.078*((J*c)/(Sx*h0))*(Lb/rts)**2)**0.5
        Mn_torsional_X = Fcr*Sx        
    
    #almas compactas y patines no compactos
    if (compact_patines =="no_compacto_patines"):
        Mn_pandeo_patin_X = Mn_plastico_X-(Mn_plastico_X-0.7*Fy*Sx)*((b_t-lamda_p_patines)/(lamda_r_patines-lamda_p_patines))
    elif(compact_patines =="esbelto_patines"):
        kc = max(min(4/(h_t)**0.5,0.76),0.35)
        Mn_pandeo_patin_X = (0.9*E*kc*Sx) /(b_t)**2
    #almas no compactas
    if  (compact_alma =="no_compacto_alma"):
        print("no he programado esto aun")        
        
    print("Mp=",Mn_plastico_X) 
    print("M_torsional=",Mn_torsional_X) 
    print("M_pandeo_patines=", Mn_pandeo_patin_X) 
    Mn_X = min(Mn_torsional_X,Mn_plastico_X,Mn_pandeo_patin_X)  
    Mr_X = Mn_X*Fr_flexion    
    print("Lp=",Lp)
    print("Lr=",Lr)
    print("Ma=",Ma)
    print("Mn_X=",Mn_X)    
    print("Mr_X=",Mr_X)


if "flexion_y" in revision:
    Mp_y = Fy*Zy
    Mn_fluencia_y = min(Mp_y,1.6*Fy*Sy)
    if compact_patines == "compacto_patines":
       Mn_pandeo_patin_y = Mn_fluencia_y
    elif compact_patines == "no_compacto_patines":
        Mn_pandeo_patin_y = Mp_y -(Mp_y-0.7*Fy*Sy)*(b_t-lamda_p_patines)/(lamda_r_patines-lamda_p_patines)
    elif compact_patines == "esbelto_patines":
        Fcr = (0.69*E)/((bf*.5)/tf)**2
        Mn_pandeo_patin_y = Fcr*Sy
        
    Mn_y = min(Mn_fluencia_y,Mn_pandeo_patin_y)
    Myr = Mn_y*Fr_flexion
    print("Mr_Y=",Myr)
    
if "cortante" in revision:
    #cortante
    Aw = tw*d
    Cv1 = 1
    Vn = 0.6*Fy*Aw*Cv1
    Vr = Vn*Fr_cortante
    print("Va=",Va)
    print("Vr=",Vr)
    print("eV=",Va/Vr)
    
if "tension" in revision:
    Pn_fluencia = Fy*Ag
    Pn_fractura = Fu*Ae
    Pr_fluencia = Pn_fluencia*Fr_tension_fluencia
    Pr_fractura = Pn_fractura*Fr_tension_fractura

if "compresion" in revision:
    #compresión miembros doblemente simetricos
    Lx=Lb*kx
    Ly=Lb*ky
    Lz=Lb*kz

    Fey = (3.1416*3.1416*E)/(Ly/ry)**2
    Fex = (3.1416*3.1416*E)/(Lx/rx)**2
    Fez = ((G*J)+((3.1416*3.1416*E*Cw)/(Lz)**2))*(1/(Ag*r0*r0))

    Fe_torcional = (((3.1416*3.1416*E*Cw)/Lz**2)+(G*J))*(1/(Ix+Iy))

    if (Ly/ry)<=(4.71*(E/Fy)**0.5):
        Fcry =Fy*0.658**(Fy/Fey)
    elif (Ly/ry)>(4.71*(E/Fy)**0.5):
        Fcry =Fey*0.877
    
    if (Lx/rx)<=(4.71*(E/Fy)**0.5):
        Fcrx =Fy*0.658**(Fy/Fex)
    elif (Lx/rx)>(4.71*(E/Fy)**0.5):
        Fcrx =Fex*0.877

    if (Lz/r0)<=(4.71*(E/Fy)**0.5):
        Fcr_torsional =Fy*0.658**(Fy/Fe_torcional)
    elif (Lx/r0)>(4.71*(E/Fy)**0.5):
        Fcr_torsional =Fe_torcional*0.877
 
    Fcr = min(Fcry,Fcrx,Fcr_torsional)    
    Pn =Fcr*Ag    
    Pr = Pn*Fr_compresion
    print(Lx/rx)
    print(Ly/ry)
    print("Fcr",Fcr)
    print("Pn=",Pn)
    print("Pn=",Pr)


if "flexo-compresion" in revision:
    Mxr = Mr_X
    Myr = Myr
    if P/Pr >=0.2:
        factor = (P/Pr)+(8/9)*((M1/Mxr)+(M2/Myr))    
    else:
        factor = (P/(2*Pr))+((M1/Mxr)+(M2/Myr))
    
    print("Factor debe de ser menor a uno")
    print(factor)




