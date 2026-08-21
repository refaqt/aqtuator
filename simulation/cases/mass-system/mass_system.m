clc
close all
clear all

syms a1 a2 a3 aF F F3 M m Meq

A = [ sym(1)/2   sym(1)/2   sym(0)   sym(-1)  sym(0)  ;
      m          M          sym(0)   sym(0)   sym(-1) ;
      m         -M          sym(0)   sym(0)   sym(0)  ;
      sym(0)     sym(0)     sym(2)   sym(-1)  sym(0)  ;
      sym(0)     sym(0)     Meq      sym(0)   sym(2)  ];

b = sym([ 0 ; 0 ; 0 ; 0 ; 1 ]);

sol = A \ b;        % solve rather than form inv(A) explicitly
a2_sol = sol(2);    % was: a2_sol = a2sol(2)  -- undefined variable

disp('a2 =')
pretty(simplify(a2_sol))

