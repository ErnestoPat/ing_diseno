function [Mn,Ml,Mp,Mtb,Lp,Lr,compact]=flexion(tipo,soporte,inercia,Fy,E,Lb,Cb,Zx,Sx,Zy,Sy,rts,h0,J,ry,bf,tf,Iy,Ix,Cw,b,t,h,Ag,H)

%calculos de momentos
switch tipo
    case "W"
        %secciones W inercia mayor
        Lp = 1.76*ry*(E/Fy)^0.5;
        if strcmp(tipo,"C")
            c = h0*.5*(Iy/Cw)^0.5;
        else 
            c = 1;
        end
        constante1 = E/(0.7*Fy);
        constante2 = (J*c)/(Sx*h0);
        Lr = 1.95*rts*(constante1)*((constante2)+((constante2^2)+6.76*(1/constante1)^2)^0.5)^0.5;
        lambda = bf/(2*tf);
        lambdap = 0.38*(E/Fy)^0.5;
        lambdaf = (E/Fy)^0.5;

        if lambda <= lambdap
            compact = 'compacta';
        elseif (lambdap<lambda)&&(lambda<=lambdaf)
            compact = 'no compacta';
        elseif lambda > lambdaf
            compact = 'esbelta';
        end
        %Fluencia
        Mp = Fy*Zx;
        %secciones W inercia menor
        if strcmp(inercia,'menor')
            Mp = min([Fy*Zy,1.6*Fy*Sy]);
            soporte = 'si';
        end
        %Pandeo lateral torsional
        if Lb <= Lp
            Mtb = Mp;
        elseif (Lp<Lb)&&(Lb<=Lr)
            Mtb = Cb*(Mp-((Mp-0.7*Fy*Sx))*((Lb-Lp)/(Lr-Lp)));
        elseif Lb>Lr
            Lb_rts = Lb/rts;
            Fcr = ((Cb*pi*pi*E)/((Lb_rts)^2))*(1+0.078*(constante2)*(Lb_rts)^2)^0.5;
            Mtb = Fcr*Sx;
        end
        switch compact
            case 'compacta'
                Ml = Mp;
            case 'no compacta'
                Ml = Mp-((Mp-0.7*Fy*Sx)*((lambda-lambdap)/(lambdaf-lambdap)));
            case 'esbelta'
                Kc = 4/(h/tw)^0.5;
                Kc = min([0.76,Kc]);
                Kc = max([0.35,Kc]);
                Ml = (0.9*E*Kc*Sx)/(lambda)^2;
        end
    %resistencia final
    Mn = min([Mtb,Mp,Ml]);
    if strcmp(soporte,'si')
        Mn = min([Mp,Ml]);
    end
    case "C"
        %secciones W inercia mayor
        Lp = 1.76*ry*(E/Fy)^0.5;
        if strcmp(tipo,"C")
            c = h0*.5*(Iy/Cw)^0.5;
        else 
            c = 1;
        end
        constante1 = E/(0.7*Fy);
        constante2 = (J*c)/(Sx*h0);
        Lr = 1.95*rts*(constante1)*((constante2)+((constante2^2)+6.76*(1/constante1)^2)^0.5)^0.5;
        lambda = bf/(2*tf);
        lambdap = 0.38*(E/Fy)^0.5;
        lambdaf = (E/Fy)^0.5;

        if lambda <= lambdap
            compact = 'compacta';
        elseif (lambdap<lambda)&&(lambda<=lambdaf)
            compact = 'no compacta';
        elseif lambda > lambdaf
            compact = 'esbelta';
        end
        %Fluencia
        Mp = Fy*Zx;
        %secciones W inercia menor
        if strcmp(inercia,'menor')
            Mp = min([Fy*Zy,1.6*Fy*Sy]);
            soporte = 'si';
        end
        %Pandeo lateral torsional
        if Lb <= Lp
            Mtb = Mp;
        elseif (Lp<Lb)&&(Lb<=Lr)
            Mtb = Cb*(Mp-((Mp-0.7*Fy*Sx))*((Lb-Lp)/(Lr-Lp)));
        elseif Lb>Lr
            Lb_rts = Lb/rts;
            Fcr = ((Cb*pi*pi*E)/((Lb_rts)^2))*(1+0.078*(constante2)*(Lb_rts)^2)^0.5;
            Mtb = Fcr*Sx;
        end
        switch compact
            case 'compacta'
                Ml = Mp;
            case 'no compacta'
                Ml = Mp-((Mp-0.7*Fy*Sx)*((lambda-lambdap)/(lambdaf-lambdap)));
            case 'esbelta'
                Kc = 4/(h/tw)^0.5;
                Kc = min([0.76,Kc]);
                Kc = max([0.35,Kc]);
                Ml = (0.9*E*Kc*Sx)/(lambda)^2;
        end
    %resistencia final
    Mn = min([Mtb,Mp,Ml]);
    if strcmp(soporte,'si')
        Mn = min([Mp,Ml]);
    end    
    
    
    case "HSS"
        %Secciones HSS
        if strcmp(inercia,'menor')
            S = Sy;
            Z = Zy;
            I = Iy;
            soporte = 'si';
        elseif strcmp(inercia,'mayor')
            S = Sx;
            Z = Zx;
            I = Ix;
        end    
        lambdaF = b/t;
        lambdapF = 1.12*(E/Fy)^0.5;
        lambdafF = 1.4*(E/Fy)^0.5; 
        %Fluencia
        Mp = Fy*Z;
        %Pandeo local en el patin
        if lambdaF <= lambdapF
            compact = 'compacta';
        elseif (lambdapF<lambdaF)&&(lambdaF<=lambdafF)
            compact = 'no compacta';
        elseif lambdaF > lambdafF
            compact = 'esbelta';
        end  
        
        switch compact
            case 'compacta'
                Ml = Mp;
            case 'no compacta'
                Ml =  Mp - (Mp-Fy*S)*(3.57*(b/t)*((Fy/E)^0.5)-4);
            case 'esbelta'
                b1 = b;
                be = min([1.92*t*((E/Fy)^0.5)*(1-(0.38/(b/t))*(E/Fy)^0.5),b1]);
                bc = b1-be;
                Ie = I - 2*(((bc*t^3)/12)+(bc*t)*(.5*((b+(3*t))-t))^2);
                Se = Ie/(H/2);
                Ml = Se*Fy;
        end
        
        %Pandeo lateral torsional
        Lp = 0.13*E*ry*((J*Ag)^0.5)/Mp;
        Lr = 2*E*ry*((J*Ag)^0.5)/(0.7*Fy*Sx);
        if Lb <= Lp
            Mtb = Mp;
        elseif (Lp<Lb)&&(Lb<=Lr)
            Mtb = Cb*(Mp-((Mp-0.7*Fy*Sx))*((Lb-Lp)/(Lr-Lp)));
        elseif Lb>Lr
            Mtb = 2*E*Cb*((J*Ag)^0.5)/(Lb/ry);
        end
        
        %resistencia final
        Mn = min([Mtb,Mp,Ml]);
        if strcmp(soporte,'si')
            Mn = min([Mp,Ml]);
        end
end

end