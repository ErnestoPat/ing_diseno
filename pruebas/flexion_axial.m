clear,clc,clear bass;

%esfuerxos combinados

Pc =179.7;
Pr =47.2;
Mcx =349;
Mcy =123;
Mrx =185;
Mry =27;

Pr_Pc = Pr/Pc;
if Pr_Pc >= 0.2
    Rcombinada = Pr_Pc + ((8/9)* ((Mrx/Mcx)+(Mry/Mcy)));
else
    Rcombinada = (Pr_Pc*.5) + ((Mrx/Mcx)+(Mry/Mcy));
end
if Rcombinada <= 1
    disp('la sección pasa');
end
disp(Rcombinada);

