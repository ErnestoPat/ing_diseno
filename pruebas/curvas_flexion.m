clear,clc,clear bass;
cla;
%calculo de resistencia a compresion

%datos geometrico
tipos = string({'W','W','W'}); % "W","M", "S","HP","C", "MC", "L", "WT","MT","ST","2L","HSS","PIPE"
perfiles = string({'W18X86','W18X76','W18X71'});% "W8X21","C9X15","WT22X167.5"
soporte = 'no';%'si' o 'no'
inercia = 'mayor';%inercia 'mayor' o 'menor'
%datos de acero y cargas
Fy = 50;
E = 29000;
Cb = 1;
L = 500;
%vectores ocupados
L_vector = 1:1:L;
Mn_vector = zeros(1,length(L_vector));

    
for j=1:length(perfiles)
    tipo=strcat(tipos(1,j));
    perfil=strcat(perfiles(1,j));
    [propiedades_seccion]=import_secciones(tipo,perfil);
    bf = propiedades_seccion(8);
    tf = propiedades_seccion(16);
    h = propiedades_seccion(6);
    Zx = propiedades_seccion(36);
    Sx = propiedades_seccion(37);
    Zy = propiedades_seccion(40);
    Sy = propiedades_seccion(41);
    rts = propiedades_seccion(71);
    h0 = propiedades_seccion(72);
    J = propiedades_seccion(46);
    ry =propiedades_seccion(42);
    Iy =propiedades_seccion(39);
    Ix =propiedades_seccion(35);
    Cw =propiedades_seccion(47);
    Ag =propiedades_seccion(2);
    %secciones cuadradas
    b =propiedades_seccion(11);
    t = propiedades_seccion(20);
    h = propiedades_seccion(6);
    H =  propiedades_seccion(5);
    %calculo de resistencia a compresión
    
    for i = 1:length(L_vector)
        Lb = L_vector(i);
        [Mn,Ml,Mp,Mtb,Lp,Lr,compact]=flexion(tipo,soporte,inercia,Fy,E,Lb,Cb,Zx,Sx,Zy,Sy,rts,h0,J,ry,bf,tf,Iy,Ix,Cw,b,t,h,Ag,H);
        Mn_vector(i)=Mn;
    end
    
    f1=figure(1);
    plot(L_vector,Mn_vector,'LineWidth',2);
    hold on
    xlabel(['\fontsize{14}' 'Lb']);
    ylabel(['\fontsize{14}' 'Mn']);
    xlim([0,L]);
    axis square;
    title('Gráfica de momento vs relación Lb');
    legend(perfiles,'Location','northeast');
    grid on
    set(f1, 'Visible', 'off');
    saveas(f1,'Gráficas_flexion.jpg');
end
close all