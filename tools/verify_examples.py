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

# ---- examples added from practice-exam formats
checks["cross_section A(x)=4x"]=(integrate(x*y,(y,1,3)),4*x)
checks["cross_section V=8"]=(integrate(4*x,(x,0,2)),8)
checks["geom_volume 18pi"]=(integrate(integrate(sqrt(9-y**2),(y,-3,3)),(x,0,4)),18*pi)
checks["cardioid 3pi/2"]=(integrate((1+cos(th))**2/2,(th,0,2*pi)),3*pi/2)
checks["cyl_other_axis pi/3"]=(2*pi*integrate(integrate(x*r,(x,r**2,1)),(r,0,1)),pi/3)
vol=lambda inner,mid,outer: integrate(integrate(integrate(1,inner),mid),outer)
V0=vol((z,0,(4-y)/2),(y,x**2,4),(x,-2,2))
orders=[vol((z,0,(4-y)/2),(x,-sqrt(y),sqrt(y)),(y,0,4)),
        vol((x,-sqrt(y),sqrt(y)),(z,0,(4-y)/2),(y,0,4)),
        vol((x,-sqrt(y),sqrt(y)),(y,0,4-2*z),(z,0,2)),
        vol((y,x**2,4-2*z),(z,0,(4-x**2)/2),(x,-2,2)),
        vol((y,x**2,4-2*z),(x,-sqrt(4-2*z),sqrt(4-2*z)),(z,0,2))]
checks["six_orders agree"]=(tuple(orders),tuple([V0]*5))
P_=lambda rr,tt,pp:(rr*sin(pp)*cos(tt),rr*sin(pp)*sin(tt),rr*cos(pp))
checks["point cyl (2,pi/3,1)"]=((2*cos(pi/3),2*sin(pi/3),1),(1,sqrt(3),1))
checks["point sph (4,pi/2,pi/3)"]=(P_(4,pi/2,pi/3),(0,2*sqrt(3),2))
R=2
Vc=2*pi*integrate(integrate(rho**2*sin(ph),(rho,0,R)),(ph,0,pi/4))
Mc=2*pi*integrate(integrate(rho**3*sin(ph)*cos(ph),(rho,0,R)),(ph,0,pi/4))
checks["centroid_ex2 V"]=(Vc,Rational(16,3)*pi*(1-sqrt(2)/2))
checks["centroid_ex2 M"]=(Mc,2*pi)
checks["centroid_ex2 zbar"]=(Mc/Vc,3/(8*(1-sqrt(2)/2)))
X,Y,Z=symbols('X Y Z',positive=True); RR=sqrt(X**2+Y**2+Z**2); v=Matrix([X,Y,Z])
grad=lambda g: Matrix([diff(g,X),diff(g,Y),diff(g,Z)])
checks["grad r = r/r"]=(tuple(grad(RR)),tuple(v/RR))
checks["grad 1/r = -r/r^3"]=(tuple(grad(1/RR)),tuple(-v/RR**3))
checks["grad ln r = r/r^2"]=(tuple(grad(log(RR))),tuple(v/RR**2))
checks["sin^3 0..pi/2"]=(integrate(sin(ph)**3,(ph,0,pi/2)),Rational(2,3))

# ---- tricks & formula screens
a_,R_,h_,L_,c_=symbols('a R h L c',positive=True)
d=lambda F,v: simplify(diff(F,v))
checks["usub x e^(x^2)"]=(d(exp(x**2)/2,x),x*exp(x**2))
checks["usub r e^(-r^2)"]=(d(-exp(-r**2)/2,r),r*exp(-r**2))
checks["usub r sqrt(1+4r^2)"]=(d((1+4*r**2)**Rational(3,2)/12,r),r*sqrt(1+4*r**2))
checks["usub r/sqrt(a^2-r^2)"]=(d(-sqrt(a_**2-r**2),r),r/sqrt(a_**2-r**2))
checks["usub cos^3 sin"]=(d(-cos(ph)**4/4,ph),cos(ph)**3*sin(ph))
checks["parts x e^x"]=(d((x-1)*exp(x),x),x*exp(x))
checks["parts x cos x"]=(d(x*sin(x)+cos(x),x),x*cos(x))
checks["parts x sin x"]=(d(sin(x)-x*cos(x),x),x*sin(x))
checks["parts ln x"]=(d(x*log(x)-x,x),log(x))
checks["trig sin^2 2pi"]=(integrate(sin(th)**2,(th,0,2*pi)),pi)
checks["trig sin 0..pi/4"]=(integrate(sin(ph),(ph,0,pi/4)),1-sqrt(2)/2)
checks["ball 4/3 pi R^3"]=(integrate(integrate(integrate(rho**2*sin(ph),(rho,0,R_)),(ph,0,pi)),(th,0,2*pi)),4*pi*R_**3/3)
checks["cone pi R^2 h/3"]=(2*pi*integrate((h_-h_*r/R_)*r,(r,0,R_)),pi*R_**2*h_/3)
checks["half cylinder"]=(integrate(sqrt(R_**2-x**2),(x,-R_,R_))*L_,pi*R_**2*L_/2)
x1,y1,x2,y2,x3,y3=symbols('x1 y1 x2 y2 x3 y3')
tri=Rational(1,2)*Matrix([[x2-x1,x3-x1],[y2-y1,y3-y1]]).det()
checks["triangle vertex formula"]=(expand(tri),expand(Rational(1,2)*(x1*(y2-y3)+x2*(y3-y1)+x3*(y1-y2))))
f_=sqrt(a_**2-x**2-y**2)
checks["sphere SA factor"]=((sqrt(1+diff(f_,x)**2+diff(f_,y)**2)-a_/sqrt(a_**2-x**2-y**2)).subs({a_:3,x:1,y:Rational(3,2)}).simplify(),0)
A_,B_,C_=symbols('A B C',positive=True)
fp=(c_-A_*x-B_*y)/C_
checks["plane SA factor"]=(simplify(sqrt(1+diff(fp,x)**2+diff(fp,y)**2)-sqrt(A_**2+B_**2+C_**2)/C_),0)
checks["div r = 3"]=(diff(X,X)+diff(Y,Y)+diff(Z,Z),3)
checks["Green area 1/2(x dy - y dx) unit circle"]=(integrate(Rational(1,2)*(cos(t)*cos(t)+sin(t)*sin(t)),(t,0,2*pi)),pi)
checks["cone z=sqrt3 r -> pi/6"]=(atan(1/sqrt(3)),pi/6)
checks["cone z=r/sqrt3 -> pi/3"]=(atan(sqrt(3)),pi/3)
bad=0
for k,(a,b) in checks.items():
    ok = simplify(Matrix(a)-Matrix(b))==zeros(len(a),1) if isinstance(a,(tuple,list)) else simplify(a-b)==0
    print(("PASS " if ok else "FAIL ")+k, "" if ok else f"got {a} want {b}")
    bad += not ok
raise SystemExit(bad)
