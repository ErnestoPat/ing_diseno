function [Cb]=calculo_Cb(ecuacion,curvatura,Mmax,Ma,Mb,Mc,M1,M2,Iytop,Iy,M0)
Mcl =Mb ;
switch ecuacion
    case 'linea_recta' %solo aplica para lineas rectas
        if strcmp(curvatura,"simple")
            Cb = max(1.75+1.05*(M1/M2)+0.3*(-(M1/M2))^2,2.3);
        else 
            Cb = max(1.75+1.05*(M1/M2)+0.3*(M1/M2)^2,2.3);
        end
    case 'kirby' %es  una ecuacion general
        if strcmp(curvatura,"simple")
            Rm = 1;
        else 
            Rm = 0.5+2*(Iytop/Iy)^2;
        end
        Cb = max(((12.5*Mmax)/(2.5*Mmax+3*Ma+4*Mb+3*Mc))*Rm,3);
    case 'Wong'%es general se ocupan valores absolutos y sirve para I dobnlemente simetrica
        Cb = (4*Mmax)/((Mmax^2)+(4*Ma^2)+(7*Mb^2)+(4*Mc^2))^0.5;
    case 'Yura' %no lo voy a ocupar
        Cb =3-(2/3)*(M1/M0)-(8/3)*(Mcl/(M0+M1));
    case 'casoA' %los dos momentos son positivos o zero y es para cargas hacia arriba
        Cb = 2-(M0+0.6*M1)/Mcl;
    case 'casoB'%uno de los momentos es negativo la carga es hacia arriba
        Cb = (2*M1-2*Mcl+0.165*M0)/(0.5*M1-Mcl);
    case 'casoC'%los dos momentos son negativos 
        Cb = 2-((M0+M1)/Mcl)*(0.165+(1/3)*(M1/M0));
    case 'conservador'%es el caso conservador a excepcion a algunos casos
        Cb = 1;
end

end
