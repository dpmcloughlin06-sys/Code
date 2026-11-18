#!/usr/bin/env python3
"""Builds Calc3Tutor/tutor.json, the menu tree the watch app walks.

Each node is one watch screen:
  title    short heading
  tag      section label shown in the nav bar (e.g. "15.8")
  body     plain text; numbered lines ("1. ...") become a compact step list
  formula  highlighted equations block
  warn     the one mistake to avoid
  choices  list of (label, next_id) -> submenu
A screen with no choices shows a Home button.

Run:  python3 tools/build_tree.py      (writes JSON and validates links)
"""
import json
import os
import re
import sys

NODES = {}
ORDER = []
STEP_RE = re.compile(r"^(\d+)\.\s+")


def split_steps(text):
    """Numbered lines become steps; lines after a step attach to it."""
    intro, steps = [], []
    for line in text.split("\n"):
        m = STEP_RE.match(line)
        if m:
            steps.append(line[m.end():])
        elif steps:
            steps[-1] += "\n" + line
        else:
            intro.append(line)
    if len(steps) < 2:
        return text, None
    return "\n".join(intro).strip("\n") or None, steps


def N(id, title, tag="", body=None, formula=None, warn=None, choices=None):
    if id in NODES:
        raise SystemExit(f"duplicate node id: {id}")
    node = {"id": id, "title": title, "tag": tag}
    if body:
        intro, steps = split_steps(body.strip("\n"))
        if intro:
            node["body"] = intro
        if steps:
            node["steps"] = steps
    if formula:
        node["formula"] = formula.strip("\n")
    if warn:
        node["warn"] = warn.strip("\n")
    if choices:
        node["choices"] = [{"label": l, "next": n} for l, n in choices]
    NODES[id] = node
    ORDER.append(id)


# ================================================================ HOME
N("root", "Problem type", "Calc 3",
  choices=[
      ("∬ Rectangle", "t_rect"),
      ("∬ General region (Type I/II)", "t_gen"),
      ("Reverse order (2D)", "t_rev"),
      ("Polar ∬", "t_polar"),
      ("Surface area", "t_sa"),
      ("∭ Cartesian", "t_tri"),
      ("Cylindrical ∭", "t_cyl"),
      ("Spherical ∭", "t_sph"),
      ("Mass, centroid, average", "t_mass"),
      ("Line ∫ f ds", "t_scalar"),
      ("Work ∫ F·dr", "t_work"),
      ("Conservative / potential", "t_cons"),
      ("Green's theorem", "t_green"),
      ("grad · div · curl", "t_ops"),
      ("Points & describing solids", "t_coords"),
      ("Tricks & rules", "tricks"),
      ("Practice exam Q1–40", "exam_map"),
  ])

# ================================================================ 15.1
N("t_rect", "∬ over a rectangle", "15.1",
  formula=(
      "∬R f dA = ∫a→b ∫c→d f dy dx\n"
      "        = ∫c→d ∫a→b f dx dy\n"
      "Area = ∬ 1 dA\n"
      "V = ∬ f dA  (f ≥ 0)\n"
      "f = g(x)h(y) ⇒ (∫g dx)(∫h dy)\n"
      "A(x) = ∫c→d f(x,y) dy\n"
      "V = ∫a→b A(x) dx = ∫c→d A(y) dy"),
  body=(
      "1. Pick the order with the easy inner integral (x·e^(xy) → dy first).\n"
      "2. Inner integral, other variable constant.\n"
      "3. Outer integral."),
  choices=[("Integral looks like a known solid?", "tr_geometry")])

# ================================================================ 15.2
N("t_gen", "∬ General region", "15.2",
  formula=(
      "Type I:  ∫a→b ∫g₁(x)→g₂(x) f dy dx\n"
      "Type II: ∫c→d ∫h₁(y)→h₂(y) f dx dy\n"
      "Line through 2 pts: y = y₁ + m(x − x₁)\n"
      "V between surfaces = ∬D (top − bottom) dA"),
  body=(
      "1. Sketch; intersections by setting curves equal.\n"
      "2. Vertical line always enters/exits same curves → Type I. Horizontal → Type II.\n"
      "3. Neither → split at the corner, add.\n"
      "4. Outer bounds numbers, inner bounds curves."),
  warn="Pick the type that avoids splitting.",
  choices=[("Reverse the order", "t_rev")])

N("t_rev", "Reverse the order", "15.2",
  formula=(
      "∫0→1 ∫x²→1 f dy dx = ∫0→1 ∫0→√y f dx dy\n"
      "y = x² ⇔ x = √y\n"
      "x = arcsin y ⇔ y = sin x\n"
      "x = ln y ⇔ y = eˣ"),
  body=(
      "Use when the inner integral is non-elementary: e^(x²), sin(y²), √(1+x³), cos x·√(9+cos²x)…\n"
      "1. Bounds → inequalities → sketch, label corners.\n"
      "2. New outer variable: numeric min → max.\n"
      "3. Solve boundaries for new inner variable.\n"
      "4. Inner: curve entered → curve exited. Split if it changes."),
  warn="Never just swap dx and dy.",
  choices=[("Example", "ex_reverse")])

N("ex_reverse", "Example", "15.2",
  body=(
      "∫0→1 ∫y→1 e^(x²) dx dy\n"
      "Region: triangle (0,0),(1,0),(1,1)\n"
      "= ∫0→1 ∫0→x e^(x²) dy dx = ∫0→1 x e^(x²) dx = ½(e − 1)"))

# ================================================================ 15.3
N("t_polar", "Polar ∬", "15.3",
  formula=(
      "x = r cosθ, y = r sinθ\n"
      "x² + y² = r²,  tanθ = y/x\n"
      "dA = r dr dθ\n"
      "∬ f dA = ∫α→β ∫r₁→r₂ f(r cosθ, r sinθ) r dr dθ"),
  body=(
      "1. Convert region and integrand.\n"
      "2. Multiply by r.\n"
      "3. dr first, then dθ."),
  warn="The extra r.",
  choices=[
      ("Region bounds", "t_polar_bounds"),
      ("Area inside r = g(θ)", "t_polar_area"),
      ("Cartesian bounds → polar", "t_polar_cart"),
  ])

N("t_polar_bounds", "Polar bounds", "15.3",
  formula=(
      "Disk: 0≤r≤R, 0≤θ≤2π\n"
      "Annulus: R₁ ≤ r ≤ R₂\n"
      "QI: 0→π/2 · upper half: 0→π\n"
      "right half: −π/2→π/2\n"
      "y = mx: θ = arctan m\n"
      "  y=x: π/4 · y=√3x: π/3 · y=x/√3: π/6\n"
      "x²+y² = 2ax: r = 2a cosθ, −π/2→π/2\n"
      "x²+y² = 2ay: r = 2a sinθ, 0→π\n"
      "y = c: r = c cscθ · x = c: r = c secθ"),
  body="θ goes counterclockwise; it may start negative (−π/4 → 3π/4).")

N("t_polar_area", "Area inside r = g(θ)", "15.3",
  formula="A = ∫α→β ∫0→g(θ) r dr dθ = ∫α→β ½ g(θ)² dθ",
  body="θ range: where the curve starts and ends in the picture.")

N("t_polar_cart", "Cartesian → polar", "15.3",
  formula=(
      "y: 0→√(R²−x²) ⇒ upper half disk\n"
      "x: ±√(R²−y²) ⇒ full disk\n"
      "y: 0→√(2ax−x²), x: 0→2a\n"
      "  ⇒ 0≤r≤2a cosθ, 0≤θ≤π/2\n"
      "√(x²+y²) → r,  x²+y² → r²"),
  body="Read the bounds as a region first, then write polar bounds.")

# ================================================================ 15.5
N("t_sa", "Surface area", "15.5",
  formula=(
      "z = f(x,y):\n"
      "A = ∬D √(1 + f_x² + f_y²) dA\n"
      "Plane ax+by+cz = d:\n"
      "A = (√(a²+b²+c²)/|c|)·Area(D)\n"
      "Sphere z = √(a² − r²): √(…) = a/√(a² − r²)\n"
      "Paraboloid z = x²+y²: √(1 + 4r²)\n"
      "Parametric: A = ∬ |r_u × r_v| du dv"),
  body=(
      "1. D = shadow on xy-plane (inside x²+y² = R² ⇒ disk; below z = h ⇒ f ≤ h).\n"
      "2. Radicand has x²+y² → polar, keep the r.\n"
      "3. Constant radicand → factor × Area(D)."),
  warn="The 1 inside the root.")

# ================================================================ 15.6
N("t_tri", "∭ Cartesian", "15.6",
  formula=(
      "∭E f dV = ∬D ∫u₁(x,y)→u₂(x,y) f dz dA\n"
      "V = ∭ 1 dV = ∬D (top − bottom) dA\n"
      "Tetrahedron x/a + y/b + z/c = 1:\n"
      "  z: 0→c(1 − x/a − y/b)\n"
      "  y: 0→b(1 − x/a),  x: 0→a\n"
      "  V = abc/6"),
  body=(
      "1. Inner variable = one with clear floor/ceiling.\n"
      "2. Shadow D: set top = bottom, plus walls.\n"
      "3. Describe D as Type I/II."),
  warn="A bound may only use outer variables.",
  choices=[("Change the order", "t_tri_order")])

N("t_tri_order", "Change ∭ order", "15.6",
  body=(
      "1. Write all 6 inequalities; sketch.\n"
      "2. Solve surfaces for the new inner variable.\n"
      "3. Shadow on the other two: eliminate the inner variable (set its surfaces equal / substitute).\n"
      "4. Describe the shadow in the new order; split if needed."),
  choices=[("Six orders example", "ex_six")])

N("ex_six", "Six orders", "15.6",
  body=(
      "y = x², z = 0, y + 2z = 4\n"
      "dz dy dx: x −2→2, y x²→4, z 0→(4−y)/2\n"
      "dz dx dy: y 0→4, x ±√y, z 0→(4−y)/2\n"
      "dx dz dy: y 0→4, z 0→(4−y)/2, x ±√y\n"
      "dx dy dz: z 0→2, y 0→4−2z, x ±√y\n"
      "dy dz dx: x −2→2, z 0→(4−x²)/2, y x²→4−2z\n"
      "dy dx dz: z 0→2, x ±√(4−2z), y x²→4−2z"))

# ================================================================ 15.7
N("t_cyl", "Cylindrical", "15.7",
  formula=(
      "x = r cosθ, y = r sinθ, z = z\n"
      "dV = r dz dr dθ\n"
      "∫θ ∫r ∫z f(r cosθ, r sinθ, z) r dz dr dθ\n"
      "cylinder x²+y² = R² → r = R\n"
      "cone z = k√(x²+y²) → z = kr\n"
      "paraboloid z = a ± (x²+y²) → a ± r²\n"
      "sphere → z = ±√(R² − r²)\n"
      "plane z = y → z = r sinθ\n"
      "x²+y² = 2ax → r = 2a cosθ"),
  body=(
      "1. z: bottom → top surface.\n"
      "2. r: 0 → shadow edge (top = bottom, or wall).\n"
      "3. θ: 0→2π unless cut."),
  warn="The extra r. Cone z = r is above paraboloid z = r² for 0<r<1.",
  choices=[("Axis is x or y (x = y²+z²)", "t_cyl_x")])

N("t_cyl_x", "Around the x-axis", "15.7",
  formula=(
      "x = a(y² + z²), plane x = c\n"
      "y = r cosθ, z = r sinθ\n"
      "x: ar² → c,  r: 0 → √(c/a),  θ: 0→2π\n"
      "dV = r dx dr dθ"),
  body="Integrand x stays x. Same idea for the y-axis with x, z.")

# ================================================================ 15.8
N("t_sph", "Spherical", "15.8",
  formula=(
      "x = ρ sinφ cosθ\n"
      "y = ρ sinφ sinθ\n"
      "z = ρ cosφ\n"
      "ρ² = x²+y²+z²,  r = ρ sinφ\n"
      "dV = ρ² sinφ dρ dφ dθ\n"
      "0 ≤ φ ≤ π,  0 ≤ θ ≤ 2π"),
  body=(
      "1. ρ: origin outward to the surface (may depend on φ).\n"
      "2. φ from the +z axis.\n"
      "3. Constant bounds ⇒ product of 3 integrals."),
  warn="ρ² sinφ. φ is from the z-axis, θ is around it.",
  choices=[("Bounds for common solids", "t_sph_bounds"), ("Cones & surfaces", "t_sph_conv")])

N("t_sph_bounds", "Spherical bounds", "15.8",
  formula=(
      "Ball: ρ 0→R, φ 0→π, θ 0→2π\n"
      "Upper half: φ 0→π/2\n"
      "First octant: φ, θ both 0→π/2\n"
      "Inside sphere, above cone φ₀: φ 0→φ₀\n"
      "Outside cone (z ≥ 0): φ φ₀→π/2\n"
      "Shell: R₁ ≤ ρ ≤ R₂\n"
      "x²+y²+z² = 2az: ρ ≤ 2a cosφ\n"
      "Below plane z = h: ρ ≤ h secφ\n"
      "Cap above z = h: h secφ ≤ ρ ≤ R,\n"
      "  φ ≤ arccos(h/R)"))

N("t_sph_conv", "Cones & surfaces", "15.8",
  formula=(
      "z = √(x²+y²): φ = π/4\n"
      "z = √3·√(x²+y²): φ = π/6\n"
      "z = √(x²+y²)/√3: φ = π/3\n"
      "z = k√(x²+y²): tanφ = 1/k\n"
      "sphere radius R: ρ = R\n"
      "plane z = h: ρ = h secφ\n"
      "cylinder x²+y² = a²: ρ = a cscφ\n"
      "xy-plane: φ = π/2"))

# ================================================================ mass
N("t_mass", "Mass, centroid, average", "Mass",
  formula=(
      "2D: m = ∬ δ dA\n"
      "M_y = ∬ xδ dA,  M_x = ∬ yδ dA\n"
      "x̄ = M_y/m,  ȳ = M_x/m\n"
      "3D: m = ∭ δ dV\n"
      "x̄ = ∭ xδ dV / m  (same for ȳ, z̄)\n"
      "f_avg = ∬ f dA / Area(D)"),
  body=(
      "1. Symmetry first: round around z-axis ⇒ x̄ = ȳ = 0.\n"
      "2. Uniform δ cancels: use V (or A).\n"
      "3. Spherical z = ρ cosφ ⇒ integrand ρ³ sinφ cosφ."),
  warn="z̄ must lie inside the solid.",
  choices=[("Example: cone under sphere", "ex_centroid2"), ("Example: cone in 2az sphere", "ex_centroid")])

N("ex_centroid2", "Cone under sphere, R = 2", "Mass",
  body=(
      "ρ 0→R, φ 0→π/4, θ 0→2π\n"
      "V = 2π·(R³/3)(1 − √2/2) = (16π/3)(1 − √2/2)\n"
      "M = 2π·(R⁴/4)·(1/4) = 2π\n"
      "z̄ = M/V ≈ 1.28,  x̄ = ȳ = 0"))

N("ex_centroid", "Cone in x²+y²+z² = 2z", "Mass",
  body=(
      "ρ 0→2cosφ, φ 0→π/4, θ 0→2π\n"
      "V = 2π∫(8cos³φ/3) sinφ dφ = π\n"
      "M = 2π∫4cos⁵φ sinφ dφ = 7π/6\n"
      "z̄ = 7/6"))

# ================================================================ 16.2
N("t_scalar", "Line ∫ f ds", "16.2",
  formula=(
      "∫C f ds = ∫a→b f(r(t)) |r'(t)| dt\n"
      "ds = √(x'² + y'² + z'²) dt\n"
      "Mass = ∫ δ ds,  Length = ∫ ds\n"
      "∫C f dx = ∫ f(r(t)) x'(t) dt\n"
      "∫C f dy = ∫ f(r(t)) y'(t) dt"),
  body=(
      "1. Parameterize.\n"
      "2. Speed |r'(t)|.\n"
      "3. Plug in and integrate."),
  warn="ds needs the speed; dx and dy don't.",
  choices=[("Parameterizations", "t_param")])

N("t_param", "Parameterizations", "16.2",
  formula=(
      "Segment A→B: r = A + t(B − A), 0≤t≤1\n"
      "Circle CCW: (a cos t, a sin t), 0→2π\n"
      "Ellipse: (a cos t, b sin t)\n"
      "y = g(x): (t, g(t))\n"
      "x = g(y): (g(t), t)\n"
      "Helix: (cos t, sin t, t)"),
  body="Piecewise path: one piece at a time, then add.")

N("t_work", "Work ∫ F·dr", "16.2",
  formula=(
      "W = ∫C F·dr = ∫a→b F(r(t))·r'(t) dt\n"
      "  = ∫C P dx + Q dy + R dz\n"
      "∫−C F·dr = −∫C F·dr"),
  body=(
      "1. Shortcuts: closed plane curve → Green; curl F = 0 → potential.\n"
      "2. Else parameterize, dot F(r(t)) with r'(t), integrate.\n"
      "Pick-the-figure: arrow at r(t) is F(r(t)), slope F_y/F_x."),
  warn="Dot product, not magnitude.",
  choices=[("Parameterizations", "t_param"), ("Conservative?", "t_cons")])

# ================================================================ 16.3
N("t_cons", "Conservative fields", "16.3",
  formula=(
      "2D: P_y = Q_x\n"
      "3D: curl F = 0\n"
      "  P_y = Q_x, P_z = R_x, Q_z = R_y\n"
      "∫C ∇f·dr = f(B) − f(A)\n"
      "∮ ∇f·dr = 0"),
  body=(
      "1. f = ∫ P dx + g(y,z).\n"
      "2. f_y = Q ⇒ g.\n"
      "3. f_z = R ⇒ h(z).\n"
      "4. Answer f(end) − f(start)."),
  warn="Needs a simply connected domain (no holes).")

# ================================================================ 16.4
N("t_green", "Green's theorem", "16.4",
  formula=(
      "∮C P dx + Q dy = ∬D (Q_x − P_y) dA\n"
      "CCW = positive; CW ⇒ negate\n"
      "Area = ∮ x dy = −∮ y dx\n"
      "     = ½∮ (x dy − y dx)"),
  body=(
      "1. P = dx coefficient, Q = dy coefficient.\n"
      "2. ∬D (Q_x − P_y) dA.\n"
      "3. Constant k ⇒ k·Area(D).\n"
      "4. Direct check: each edge A + t(B − A), sum."),
  warn="Q_x − P_y, Q first. Closed curve only.",
  choices=[("Example both ways", "ex_green")])

N("ex_green", "Example", "16.4",
  body=(
      "∮ y² dx + 3xy dy, triangle (0,0)→(1,0)→(1,2)\n"
      "Green: Q_x − P_y = y; ∫0→1 ∫0→2x y dy dx = 2/3\n"
      "Direct: 0 + 6 − 16/3 = 2/3"))

# ================================================================ 16.5
N("t_ops", "grad · div · curl", "16.5",
  formula=(
      "∇f = ⟨f_x, f_y, f_z⟩   S→V\n"
      "∇·F = P_x + Q_y + R_z   V→S\n"
      "∇×F = ⟨R_y−Q_z, P_z−R_x, Q_x−P_y⟩   V→V\n"
      "∇²f = f_xx + f_yy + f_zz   S→S\n"
      "∇×(∇f) = 0\n"
      "∇·(∇×F) = 0\n"
      "∇·(∇f) = ∇²f"),
  warn="Curl's middle component: P_z − R_x.",
  choices=[("r = ⟨x,y,z⟩ results", "t_rvec"), ("Is it meaningful?", "t_meaning")])

N("t_rvec", "r and r = |r|", "16.5",
  formula=(
      "∇r = r/r\n"
      "∇×r = 0,  ∇·r = 3\n"
      "∇(1/r) = −r/r³\n"
      "∇(ln r) = r/r²\n"
      "∇g(r) = g'(r)·r/r\n"
      "∇(rⁿ) = n rⁿ⁻² r"))

N("t_meaning", "Meaningful?", "16.5",
  body=(
      "Track scalar/vector inside out.\n"
      "OK: div(grad f), curl(grad f), grad(div F), div(curl F), curl(curl F)\n"
      "Nonsense: curl(div F), div(div F), grad(grad f), grad F, div f"))

# ================================================================ coordinates
N("t_coords", "Points & solids", "15.7/15.8",
  formula=(
      "Cyl (r, θ, z) → (r cosθ, r sinθ, z)\n"
      "Sph (ρ, θ, φ) →\n"
      "  (ρ sinφ cosθ, ρ sinφ sinθ, ρ cosφ)\n"
      "r = √(x²+y²), tanθ = y/x\n"
      "ρ = √(x²+y²+z²), cosφ = z/ρ"),
  body=(
      "Describing a solid:\n"
      "θ 0→π/2: x, y ≥ 0 · θ 0→π: y ≥ 0\n"
      "r ≤ z or φ ≤ π/2: z ≥ 0\n"
      "z = c plane · z = r cone · ρ = c sphere · φ = c cone\n"
      "xz-plane slice: θ = 0, π · yz-plane: θ = π/2"),
  warn="Spherical points are (ρ, θ, φ): θ second.")

# ================================================================ TRICKS
N("tricks", "Tricks & rules", "Tricks",
  choices=[
      ("Symmetry → 0", "tr_symmetry"),
      ("Pick / swap the order", "tr_order"),
      ("Known areas & volumes", "tr_geometry"),
      ("Trig identities & values", "tr_trig"),
      ("u-sub patterns", "tr_usub"),
      ("By parts", "tr_parts"),
      ("Line integral rules", "tr_line"),
      ("Sanity checks", "tr_checks"),
  ])

N("tr_symmetry", "Symmetry", "Tricks",
  body=(
      "D symmetric across the y-axis and f(−x,y) = −f(x,y) ⇒ ∬ f dA = 0.\n"
      "Same for y/x-axis, and in 3D.\n"
      "∬ x dA, ∬ xy² dA over a disk = 0.\n"
      "Solid round about z-axis ⇒ x̄ = ȳ = 0.\n"
      "∫0→2π sinθ dθ = ∫0→2π cosθ dθ = 0."))

N("tr_order", "Choosing the order", "Tricks",
  body=(
      "Constant bounds + f = g(x)h(y): split into a product.\n"
      "x·e^(xy), x·cos(xy): integrate dy first (x is the chain-rule factor).\n"
      "Non-elementary inner (e^(x²), sin(y²)): reverse the order; the new inner creates the u-sub factor.\n"
      "Pick the order that avoids splitting the region."))

N("tr_geometry", "Known areas & volumes", "Tricks",
  formula=(
      "Disk πR² · sector ½R²θ\n"
      "Ellipse πab · triangle ½bh\n"
      "Triangle from vertices:\n"
      "  ½|x₁(y₂−y₃) + x₂(y₃−y₁) + x₃(y₁−y₂)|\n"
      "Ball 4πR³/3 · hemisphere 2πR³/3\n"
      "Cone πR²h/3 · cylinder πR²h\n"
      "Half cylinder ½πR²·L\n"
      "  (∬ √(R² − x²) over full width)"),
  body="If f ≥ 0 and the solid is a known shape, skip the integral.")

N("tr_trig", "Trig", "Tricks",
  formula=(
      "sin²θ = (1 − cos2θ)/2\n"
      "cos²θ = (1 + cos2θ)/2\n"
      "sinθ cosθ = ½ sin2θ\n"
      "∫0→2π sin² = ∫0→2π cos² = π\n"
      "∫0→π/2 sin² = π/4\n"
      "∫0→π sinφ = 2 · ∫0→π/2 sinφ = 1\n"
      "∫0→π/4 sinφ = 1 − √2/2\n"
      "∫0→π/2 sin³φ = 2/3\n"
      "π/6: (√3/2, ½) · π/4: (√2/2, √2/2)\n"
      "π/3: (½, √3/2)  as (cos, sin)"),
  body="Odd power: peel one factor, sin² = 1 − cos², u = cos.")

N("tr_usub", "u-sub patterns", "Tricks",
  formula=(
      "∫ x e^(x²) dx = ½ e^(x²)\n"
      "∫ r e^(−r²) dr = −½ e^(−r²)\n"
      "∫ r√(1+4r²) dr = (1+4r²)^(3/2)/12\n"
      "∫ r/√(a²−r²) dr = −√(a²−r²)\n"
      "∫ cosⁿφ sinφ dφ = −cosⁿ⁺¹φ/(n+1)\n"
      "∫ ρ³ e^(ρ²) dρ: u = ρ², then parts\n"
      "∫ 1/(1+x²) = arctan x"))

N("tr_parts", "By parts", "Tricks",
  formula=(
      "∫ u dv = uv − ∫ v du\n"
      "u by LIATE: Log, Inv trig, Alg, Trig, Exp\n"
      "∫ x eˣ dx = (x − 1)eˣ\n"
      "∫ x cos x dx = x sin x + cos x\n"
      "∫ x sin x dx = sin x − x cos x\n"
      "∫ ln x dx = x ln x − x"))

N("tr_line", "Line integral rules", "Tricks",
  body=(
      "Reverse path: ∫F·dr flips sign; ∫f ds doesn't.\n"
      "∫ g(x) dx alone depends only on x-endpoints.\n"
      "Conservative + closed ⇒ 0.\n"
      "Speed: circle radius a = a; segment = |B − A|.\n"
      "Closed curve, messy edges ⇒ Green.\n"
      "F mostly along motion ⇒ positive work."))

N("tr_checks", "Sanity checks", "Tricks",
  body=(
      "Jacobian: r (polar/cyl), ρ² sinφ (sph).\n"
      "Outer bounds are numbers; lower < upper.\n"
      "Volume, area, mass, length > 0.\n"
      "Centroid inside the solid.\n"
      "CW or reversed path ⇒ flip sign.\n"
      "Radians.\n"
      "½ for triangles."))

# ================================================================ EXAM MAP
N("exam_map", "Practice exam", "Exam 3",
  choices=[
      ("Q1–2 iterated ∫", "t_rect"),
      ("Q3 cross-sections", "t_rect"),
      ("Q4 ∬√(25−x²): geometry", "tr_geometry"),
      ("Q5, 11 reverse order", "t_rev"),
      ("Q6–9 Type I/II", "t_gen"),
      ("Q10 volume over region", "t_gen"),
      ("Q12–13, 15 polar", "t_polar"),
      ("Q14 area in r = √θ", "t_polar_area"),
      ("Q16 Cartesian → polar", "t_polar_cart"),
      ("Q17 surface area", "t_sa"),
      ("Q18, 21–22 ∭", "t_tri"),
      ("Q19, 23 x = a(y²+z²)", "t_cyl_x"),
      ("Q20, 24 ∭ orders", "t_tri_order"),
      ("Q25, 28 convert points", "t_coords"),
      ("Q26, 29 describe solid", "t_coords"),
      ("Q27 cylindrical", "t_cyl"),
      ("Q30–32 spherical", "t_sph_bounds"),
      ("Q33 volume & centroid", "t_mass"),
      ("Q34 ∫ eˣ dx", "t_scalar"),
      ("Q35–37 work", "t_work"),
      ("Q38 Green", "t_green"),
      ("Q39 curl & div", "t_ops"),
      ("Q40 ∇r, ∇(1/r), ∇ ln r", "t_rvec"),
  ])


# ================================================================ icons (SF Symbols)
# Shown as a coloured badge on every button that leads to the screen.
ICONS = {
    "t_rect": "square.grid.2x2", "t_gen": "scribble.variable", "t_rev": "arrow.left.arrow.right",
    "t_polar": "scope", "t_sa": "square.3.layers.3d", "t_tri": "cube", "t_cyl": "cylinder",
    "t_sph": "globe", "t_mass": "scalemass", "t_scalar": "scribble", "t_work": "arrow.up.right",
    "t_cons": "mountain.2", "t_green": "arrow.triangle.2.circlepath", "t_ops": "wind",
    "t_coords": "move.3d", "tricks": "lightbulb", "exam_map": "list.number",
    "t_polar_bounds": "circle.dashed", "t_polar_area": "circle.lefthalf.filled",
    "t_polar_cart": "arrow.triangle.swap", "t_rev_x": "arrow.left.arrow.right",
    "t_tri_order": "arrow.up.arrow.down", "t_cyl_x": "arrow.left.and.right",
    "t_sph_bounds": "circle.dashed", "t_sph_conv": "cone", "t_param": "point.topleft.down.curvedto.point.bottomright.up",
    "t_rvec": "arrow.up.forward", "t_meaning": "questionmark.circle",
    "tr_symmetry": "rectangle.split.2x1", "tr_order": "arrow.up.arrow.down",
    "tr_geometry": "triangle", "tr_trig": "waveform.path", "tr_usub": "arrow.2.squarepath",
    "tr_parts": "square.split.2x1", "tr_line": "point.3.connected.trianglepath.dotted",
    "tr_checks": "checkmark.seal",
}
for nid, icon in ICONS.items():
    if nid in NODES:
        NODES[nid]["icon"] = icon


# ================================================================ validate + write
def validate():
    errors = []
    for nid, n in NODES.items():
        for c in n.get("choices", []):
            if c["next"] not in NODES:
                errors.append(f"{nid}: links to missing node '{c['next']}'")
        if not any(n.get(k) for k in ("body", "steps", "formula", "choices")):
            errors.append(f"{nid}: empty screen")
        if "icon" in n and not re.fullmatch(r"[a-z0-9.]+", n["icon"]):
            errors.append(f"{nid}: icon must be an SF Symbol name")
        for field in ("body", "formula", "warn", "steps"):
            v = n.get(field) or ""
            text = "\n".join(v) if isinstance(v, list) else v
            if "*" in text or "\\" in text:
                errors.append(f"{nid}.{field}: contains '*' or backslash")
    seen, stack = set(), ["root"]
    while stack:
        cur = stack.pop()
        if cur not in seen:
            seen.add(cur)
            stack += [c["next"] for c in NODES[cur].get("choices", [])]
    errors += [f"{nid}: unreachable from root" for nid in NODES if nid not in seen]
    return errors


if __name__ == "__main__":
    errs = validate()
    if errs:
        print("\n".join(errs))
        sys.exit(1)
    out = os.path.join(os.path.dirname(__file__), "..", "Calc3Tutor", "tutor.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"root": "root", "nodes": [NODES[i] for i in ORDER]}, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"OK: {len(NODES)} screens")
