#!/usr/bin/env python3
"""Checks the numbers in the app's worked examples with SymPy (pip install sympy)."""
from sympy import *
x,y,z,t,r,th,ph,rho=symbols('x y z t r theta phi rho', real=True)
checks = {
 "rect_product 2(e-1)": (integrate(integrate(x*exp(y),(y,0,1)),(x,0,2)), 2*(E-1)),
 "reverse_example (e-1)/2": (integrate(integrate(exp(x**2),(y,0,x)),(x,0,1)), (E-1)/2),
 "sa_polar (pi/6)(17^1.5-1)": (2*pi*integrate(sqrt(1+4*r**2)*r,(r,0,2)), pi/6*(17**Rational(3,2)-1)),
 "sa_const sqrt14": (sqrt(1+diff(2*x+3*y,x)**2+diff(2*x+3*y,y)**2), sqrt(14)),
 "cyl_example 8pi": (2*pi*integrate((4-r**2)*r,(r,0,2)), 8*pi),
 "centroid V=pi": (2*pi*integrate(integrate(rho**2*sin(ph),(rho,0,2*cos(ph))),(ph,0,pi/4)), pi),
 "centroid M=7pi/6": (2*pi*integrate(integrate(rho**3*sin(ph)*cos(ph),(rho,0,2*cos(ph))),(ph,0,pi/4)), 7*pi/6),
 "scalar_ex 35/2": (integrate((3*t+4*t)*5,(t,0,1)), Rational(35,2)),
 "work_ex 5/3": (integrate(t**2*1+(t*2*t)*2,(t,0,1)), Rational(5,3)),
 "green_ex Green 2/3": (integrate(integrate(diff(3*x*y,x)-diff(y**2,y),(y,0,2*x)),(x,0,1)), Rational(2,3)),
 "tetra abc/6 (3,2,6)": (integrate(integrate(integrate(1,(z,0,6-2*x-3*y)),(y,0,2-2*x/3)),(x,0,3)), 6),
 "tk sin^2 0..pi/2": (integrate(sin(th)**2,(th,0,pi/2)), pi/4),
 "polar_line theta": (solve(Eq(2*sin(th),1),th), [pi/6,5*pi/6]),
}
# Green direct
def seg(P,Q,X,Y,a,b):
    return integrate((P.subs({x:X,y:Y})*diff(X,t)+Q.subs({x:X,y:Y})*diff(Y,t)),(t,a,b))
P,Q=y**2,3*x*y
direct=seg(P,Q,t,0*t,0,1)+seg(P,Q,1+0*t,2*t,0,1)+seg(P,Q,1-t,2-2*t,0,1)
checks["green_ex direct 2/3"]=(direct,Rational(2,3))
# potentials
f2=x**2*y+x+y**3; checks["potential2"]=((diff(f2,x),diff(f2,y)),(2*x*y+1,x**2+3*y**2))
f3=x*y+y*z; checks["potential3"]=((diff(f3,x),diff(f3,y),diff(f3,z)),(y,x+z,y))
bad=0
for k,(a,b) in checks.items():
    ok = simplify(Matrix(a)-Matrix(b))==zeros(len(a),1) if isinstance(a,(tuple,list)) else simplify(a-b)==0
    print(("PASS " if ok else "FAIL ")+k, "" if ok else f"got {a} want {b}")
    bad += not ok
raise SystemExit(bad)
