#!/usr/bin/env python3
r"""Builds Calc3Tutor/tutor.json, the menu tree the watch app walks.

Each node is one watch screen:
  title    short heading (plain words)
  tag      section label ("15.8"); also picks the screen's colour
  formula  list of lines shown on the Equations card
  body     list of lines of explanation
  steps    list of process steps (numbered on screen)
  warn     the one mistake to avoid
  choices  list of (label, next_id) -> buttons
  icon     SF Symbol shown on buttons that lead here (see ICONS)

Math markup (rendered as textbook math by Calc3Tutor/Math.swift)
  Text outside $...$ is ordinary words. Inside $...$:
    x^2  x^{n+1}     superscript        x_1  f_{xx}      subscript
    \frac{a}{b}      stacked fraction   \sqrt{x}         square root
    ∫_0^1  ∬_D  ∭_E  ∮_C                integral with limits above/below
    \bar{x}  \bf{F}  \text{Area}        x̄, bold vector, upright words
  Letters are italic; sin cos tan sec csc arcsin arctan ln are upright.
  A space is a place the line may wrap. Unicode (θ φ ρ ∂ ∇ ≤ → ⟨⟩) is used directly.
  A line starting with two spaces continues the line above.

Run:  python3 tools/build_tree.py      (validates links + markup, writes JSON)
"""
import json
import os
import re
import sys

NODES = {}
ORDER = []


def _lines(v):
    if v is None:
        return None
    return v if isinstance(v, list) else [v]


def N(id, title, tag="", formula=None, body=None, steps=None, warn=None, choices=None):
    if id in NODES:
        raise SystemExit(f"duplicate node id: {id}")
    node = {"id": id, "title": title, "tag": tag}
    if formula:
        node["formula"] = "\n".join(_lines(formula))
    if body:
        node["body"] = "\n".join(_lines(body))
    if steps:
        node["steps"] = list(steps)
    if warn:
        node["warn"] = warn
    if choices:
        node["choices"] = [{"label": l, "next": n} for l, n in choices]
    NODES[id] = node
    ORDER.append(id)


# ================================================================ HOME
N("root", "Problem type", "Calc 3",
  choices=[
      ("Double integral: rectangle", "t_rect"),
      ("Double integral: general region", "t_gen"),
      ("Reverse the order", "t_rev"),
      ("Polar coordinates", "t_polar"),
      ("Surface area", "t_sa"),
      ("Triple integral", "t_tri"),
      ("Cylindrical coordinates", "t_cyl"),
      ("Spherical coordinates", "t_sph"),
      ("Mass & centroid", "t_mass"),
      ("Line integral of f ds", "t_scalar"),
      ("Work along a path", "t_work"),
      ("Conservative fields", "t_cons"),
      ("Green's theorem", "t_green"),
      ("Gradient, divergence, curl", "t_ops"),
      ("Points & solids", "t_coords"),
      ("Tricks & rules", "tricks"),
      ("Practice exam Q1–40", "exam_map"),
  ])

# ================================================================ 15.1
N("t_rect", "Double integral over a rectangle", "15.1",
  formula=[
      r"$∬_R f dA = ∫_a^b ∫_c^d f dy dx$",
      r"Area $= ∬_R 1 dA$",
      r"Volume $= ∬_R f dA$ when $f ≥ 0$",
      r"If $f = g(x) h(y)$: $∫_a^b g dx · ∫_c^d h dy$",
      r"Cross-section $A(x) = ∫_c^d f(x, y) dy$",
      r"$V = ∫_a^b A(x) dx$",
  ],
  steps=[
      r"Pick the order with the easy inner integral. For $x e^{xy}$, do $dy$ first.",
      r"Integrate the inner variable and hold the other one constant.",
      r"Integrate the outer variable.",
  ],
  choices=[("Looks like a known solid?", "tr_geometry")])

# ================================================================ 15.2
N("t_gen", "Double integral over a general region", "15.2",
  formula=[
      r"Type I: $∫_a^b ∫_{g_1(x)}^{g_2(x)} f dy dx$",
      r"Type II: $∫_c^d ∫_{h_1(y)}^{h_2(y)} f dx dy$",
      r"Line through two points:",
      r"  $y = y_1 + m(x − x_1)$",
      r"Between surfaces: $∬_D (\text{top} − \text{bottom}) dA$",
  ],
  steps=[
      r"Sketch the region and find where the curves meet.",
      r"A vertical line always enters and leaves through the same curves → Type I. Horizontal → Type II.",
      r"If neither works, split at the corner and add.",
      r"Outer limits are numbers. Inner limits are curves.",
  ],
  warn="Choose the type that avoids splitting.",
  choices=[("Reverse the order", "t_rev")])

N("t_rev", "Reverse the order", "15.2",
  formula=[
      r"$∫_0^1 ∫_{x^2}^1 f dy dx = ∫_0^1 ∫_0^{\sqrt{y}} f dx dy$",
      r"$y = x^2 ⟺ x = \sqrt{y}$",
      r"$x = arcsin y ⟺ y = sin x$",
      r"$x = ln y ⟺ y = e^x$",
  ],
  body=r"Use it when the inner integral can't be done, like $e^{x^2}$, $sin(y^2)$ or $\sqrt{1 + x^3}$.",
  steps=[
      r"Write the limits as inequalities and sketch the region.",
      r"New outer variable: its smallest to largest value.",
      r"Solve each boundary for the new inner variable.",
      r"Inner limits run from the curve you enter to the curve you leave.",
  ],
  warn="Never just swap dx and dy.",
  choices=[("Example", "ex_reverse")])

N("ex_reverse", "Example", "15.2",
  formula=[
      r"$∫_0^1 ∫_y^1 e^{x^2} dx dy$",
      r"Region: triangle $(0,0), (1,0), (1,1)$",
      r"$= ∫_0^1 ∫_0^x e^{x^2} dy dx$",
      r"$= ∫_0^1 x e^{x^2} dx = \frac{1}{2}(e − 1)$",
  ])

# ================================================================ 15.3
N("t_polar", "Polar coordinates", "15.3",
  formula=[
      r"$x = r cos θ$,  $y = r sin θ$",
      r"$x^2 + y^2 = r^2$",
      r"$dA = r dr dθ$",
      r"$∬_D f dA = ∫_α^β ∫_{r_1}^{r_2} f(r cos θ, r sin θ) r dr dθ$",
  ],
  steps=[
      r"Convert the region and the integrand.",
      r"Multiply by the extra $r$.",
      r"Integrate $dr$ first, then $dθ$.",
  ],
  warn="Don't forget the extra r.",
  choices=[
      ("Region limits", "t_polar_bounds"),
      ("Area inside r = g(θ)", "t_polar_area"),
      ("Converting from x and y", "t_polar_cart"),
  ])

N("t_polar_bounds", "Polar limits", "15.3",
  formula=[
      r"Disk: $0 ≤ r ≤ R$,  $0 ≤ θ ≤ 2π$",
      r"Ring: $R_1 ≤ r ≤ R_2$",
      r"Quadrant I: $0 ≤ θ ≤ \frac{π}{2}$",
      r"Upper half: $0 ≤ θ ≤ π$",
      r"Right half: $−\frac{π}{2} ≤ θ ≤ \frac{π}{2}$",
      r"Line $y = mx$: $θ = arctan m$",
      r"  $y = x → \frac{π}{4}$,  $y = \sqrt{3} x → \frac{π}{3}$",
      r"$x^2 + y^2 = 2ax$: $r = 2a cos θ$",
      r"$x^2 + y^2 = 2ay$: $r = 2a sin θ$",
      r"$y = c$: $r = c csc θ$,  $x = c$: $r = c sec θ$",
  ],
  body=r"Angles go counterclockwise and may start negative, like $−\frac{π}{4}$ to $\frac{3π}{4}$.")

N("t_polar_area", "Area inside r = g(θ)", "15.3",
  formula=r"$A = ∫_α^β ∫_0^{g(θ)} r dr dθ = ∫_α^β \frac{1}{2} g(θ)^2 dθ$",
  body="Read the θ limits from where the curve starts and ends in the picture.")

N("t_polar_cart", "Converting from x and y", "15.3",
  formula=[
      r"$y$ from $0$ to $\sqrt{R^2 − x^2}$ → upper half-disk",
      r"$x$ from $−\sqrt{R^2 − y^2}$ to $\sqrt{R^2 − y^2}$ → full disk",
      r"$y$ from $0$ to $\sqrt{2ax − x^2}$ →",
      r"  $0 ≤ r ≤ 2a cos θ$,  $0 ≤ θ ≤ \frac{π}{2}$",
      r"$\sqrt{x^2 + y^2} → r$,  $x^2 + y^2 → r^2$",
  ],
  body="Sketch the region from the limits first, then write polar limits.")

# ================================================================ 15.5
N("t_sa", "Surface area", "15.5",
  formula=[
      r"$A = ∬_D \sqrt{1 + f_x^2 + f_y^2} dA$",
      r"Plane $ax + by + cz = d$:",
      r"  $A = \frac{\sqrt{a^2 + b^2 + c^2}}{|c|} · \text{Area}(D)$",
      r"Sphere: $\sqrt{1 + f_x^2 + f_y^2} = \frac{a}{\sqrt{a^2 − r^2}}$",
      r"Paraboloid $z = x^2 + y^2$: $\sqrt{1 + 4r^2}$",
      r"Parametric: $A = ∬_D |\bf{r}_u × \bf{r}_v| du dv$",
  ],
  steps=[
      r"$D$ is the shadow on the $xy$-plane. Inside $x^2 + y^2 = R^2$ means a disk.",
      r"If the root has $x^2 + y^2$, switch to polar and keep the $r$.",
      r"If the root is a constant, multiply it by the area of $D$.",
  ],
  warn="Keep the 1 inside the square root.")

# ================================================================ 15.6
N("t_tri", "Triple integral", "15.6",
  formula=[
      r"$∭_E f dV = ∬_D ∫_{u_1}^{u_2} f dz dA$",
      r"$V = ∬_D (\text{top} − \text{bottom}) dA$",
      r"Tetrahedron $\frac{x}{a} + \frac{y}{b} + \frac{z}{c} = 1$:",
      r"  $0 ≤ z ≤ c(1 − \frac{x}{a} − \frac{y}{b})$",
      r"  $0 ≤ y ≤ b(1 − \frac{x}{a})$,  $0 ≤ x ≤ a$",
      r"  $V = \frac{abc}{6}$",
  ],
  steps=[
      r"The inner variable is the one with a clear floor and ceiling, usually $z$.",
      r"Find the shadow $D$: set top = bottom and add any walls.",
      r"Describe $D$ as a Type I or Type II region.",
  ],
  warn="A limit can only use variables that are integrated later.",
  choices=[("Change the order", "t_tri_order")])

N("t_tri_order", "Change the order", "15.6",
  steps=[
      r"Write all six inequalities and sketch the solid.",
      r"Solve each surface for the new inner variable.",
      r"Find the shadow on the other two variables by eliminating the inner one.",
      r"Describe that shadow in the new order. Split if a boundary changes.",
  ],
  choices=[("All six orders example", "ex_six")])

N("ex_six", "All six orders", "15.6",
  formula=[
      r"Solid: $y = x^2$,  $z = 0$,  $y + 2z = 4$",
      r"$∫_{−2}^2 ∫_{x^2}^4 ∫_0^{(4−y)/2} dz dy dx$",
      r"$∫_0^4 ∫_{−\sqrt{y}}^{\sqrt{y}} ∫_0^{(4−y)/2} dz dx dy$",
      r"$∫_0^4 ∫_0^{(4−y)/2} ∫_{−\sqrt{y}}^{\sqrt{y}} dx dz dy$",
      r"$∫_0^2 ∫_0^{4−2z} ∫_{−\sqrt{y}}^{\sqrt{y}} dx dy dz$",
      r"$∫_{−2}^2 ∫_0^{(4−x^2)/2} ∫_{x^2}^{4−2z} dy dz dx$",
      r"$∫_0^2 ∫_{−\sqrt{4−2z}}^{\sqrt{4−2z}} ∫_{x^2}^{4−2z} dy dx dz$",
  ])

# ================================================================ 15.7
N("t_cyl", "Cylindrical coordinates", "15.7",
  formula=[
      r"$x = r cos θ$,  $y = r sin θ$,  $z = z$",
      r"$dV = r dz dr dθ$",
      r"Cylinder $x^2 + y^2 = R^2$ → $r = R$",
      r"Cone $z = k\sqrt{x^2 + y^2}$ → $z = kr$",
      r"Paraboloid $z = a ± (x^2 + y^2)$ → $z = a ± r^2$",
      r"Sphere → $z = ±\sqrt{R^2 − r^2}$",
      r"Plane $z = y$ → $z = r sin θ$",
      r"$x^2 + y^2 = 2ax$ → $r = 2a cos θ$",
  ],
  steps=[
      r"$z$ runs from the bottom surface to the top surface.",
      r"$r$ runs from 0 to the edge of the shadow, where top = bottom or a wall.",
      r"$θ$ runs from 0 to $2π$ unless the solid is cut.",
  ],
  warn="Don't forget the extra r. The cone z = r is above the paraboloid z = r² when r < 1.",
  choices=[("Paraboloid along the x-axis", "t_cyl_x")])

N("t_cyl_x", "Paraboloid along the x-axis", "15.7",
  formula=[
      r"Paraboloid $x = a(y^2 + z^2)$, plane $x = c$",
      r"$y = r cos θ$,  $z = r sin θ$",
      r"$ar^2 ≤ x ≤ c$,  $0 ≤ r ≤ \sqrt{\frac{c}{a}}$",
      r"$dV = r dx dr dθ$",
  ],
  body=r"An integrand of $x$ stays $x$. Do the same for the $y$-axis using $x$ and $z$.")

# ================================================================ 15.8
N("t_sph", "Spherical coordinates", "15.8",
  formula=[
      r"$x = ρ sin φ cos θ$",
      r"$y = ρ sin φ sin θ$",
      r"$z = ρ cos φ$",
      r"$ρ^2 = x^2 + y^2 + z^2$",
      r"$dV = ρ^2 sin φ dρ dφ dθ$",
      r"$0 ≤ φ ≤ π$,  $0 ≤ θ ≤ 2π$",
  ],
  steps=[
      r"$ρ$ runs from the origin out to the surface. It may depend on $φ$.",
      r"$φ$ is measured down from the positive $z$-axis.",
      r"With constant limits, split into three single integrals.",
  ],
  warn="Include ρ² sin φ. φ is from the z-axis; θ goes around it.",
  choices=[("Limits for common solids", "t_sph_bounds"), ("Cones and surfaces", "t_sph_conv")])

N("t_sph_bounds", "Spherical limits", "15.8",
  formula=[
      r"Ball: $0 ≤ ρ ≤ R$,  $0 ≤ φ ≤ π$,  $0 ≤ θ ≤ 2π$",
      r"Upper half: $0 ≤ φ ≤ \frac{π}{2}$",
      r"First octant: $0 ≤ φ ≤ \frac{π}{2}$,  $0 ≤ θ ≤ \frac{π}{2}$",
      r"Inside sphere, above cone: $0 ≤ φ ≤ φ_0$",
      r"Outside cone, above $xy$-plane: $φ_0 ≤ φ ≤ \frac{π}{2}$",
      r"Shell: $R_1 ≤ ρ ≤ R_2$",
      r"$x^2 + y^2 + z^2 = 2az$ → $ρ ≤ 2a cos φ$",
      r"Below the plane $z = h$ → $ρ ≤ h sec φ$",
      r"Cap above $z = h$: $h sec φ ≤ ρ ≤ R$",
      r"  $0 ≤ φ ≤ arccos \frac{h}{R}$",
  ])

N("t_sph_conv", "Cones and surfaces", "15.8",
  formula=[
      r"$z = \sqrt{x^2 + y^2}$ → $φ = \frac{π}{4}$",
      r"$z = \sqrt{3} \sqrt{x^2 + y^2}$ → $φ = \frac{π}{6}$",
      r"$z = \frac{1}{\sqrt{3}} \sqrt{x^2 + y^2}$ → $φ = \frac{π}{3}$",
      r"$z = k \sqrt{x^2 + y^2}$ → $tan φ = \frac{1}{k}$",
      r"Sphere of radius $R$ → $ρ = R$",
      r"Plane $z = h$ → $ρ = h sec φ$",
      r"Cylinder $x^2 + y^2 = a^2$ → $ρ = a csc φ$",
  ])

# ================================================================ mass
N("t_mass", "Mass & centroid", "Mass",
  formula=[
      r"$m = ∬_D δ dA$",
      r"$M_y = ∬_D x δ dA$,  $M_x = ∬_D y δ dA$",
      r"$\bar{x} = \frac{M_y}{m}$,  $\bar{y} = \frac{M_x}{m}$",
      r"Solid: $m = ∭_E δ dV$",
      r"  $\bar{z} = \frac{1}{m} ∭_E z δ dV$",
      r"Average: $f_{avg} = \frac{1}{\text{Area}} ∬_D f dA$",
  ],
  steps=[
      r"Use symmetry first. Round about the $z$-axis means $\bar{x} = \bar{y} = 0$.",
      r"With constant density, it cancels: use the volume or area for $m$.",
      r"In spherical, $z = ρ cos φ$, so the integrand becomes $ρ^3 sin φ cos φ$.",
  ],
  warn="The centroid has to land inside the solid.",
  choices=[("Example: cone under a sphere", "ex_centroid2"), ("Example: cone in a shifted sphere", "ex_centroid")])

N("ex_centroid2", "Cone under a sphere", "Mass",
  formula=[
      r"$0 ≤ ρ ≤ R$,  $0 ≤ φ ≤ \frac{π}{4}$,  $0 ≤ θ ≤ 2π$",
      r"$V = \frac{2πR^3}{3} (1 − \frac{\sqrt{2}}{2})$",
      r"$M_{xy} = 2π · \frac{R^4}{4} · \frac{1}{4}$",
      r"With $R = 2$: $V = \frac{16π}{3} (1 − \frac{\sqrt{2}}{2})$,  $M_{xy} = 2π$",
      r"$\bar{z} = \frac{M_{xy}}{V} ≈ 1.28$,  $\bar{x} = \bar{y} = 0$",
  ])

N("ex_centroid", "Cone in a shifted sphere", "Mass",
  formula=[
      r"Sphere $x^2 + y^2 + z^2 = 2z$, cone $φ = \frac{π}{4}$",
      r"$0 ≤ ρ ≤ 2 cos φ$,  $0 ≤ φ ≤ \frac{π}{4}$",
      r"$V = 2π ∫_0^{π/4} \frac{8 cos^3 φ}{3} sin φ dφ = π$",
      r"$M_{xy} = 2π ∫_0^{π/4} 4 cos^5 φ sin φ dφ = \frac{7π}{6}$",
      r"$\bar{z} = \frac{7}{6}$",
  ])

# ================================================================ 16.2
N("t_scalar", "Line integral of f ds", "16.2",
  formula=[
      r"$∫_C f ds = ∫_a^b f(\bf{r}(t)) |\bf{r}'(t)| dt$",
      r"$ds = \sqrt{x'^2 + y'^2 + z'^2} dt$",
      r"Mass $= ∫_C δ ds$,  length $= ∫_C ds$",
      r"$∫_C f dx = ∫_a^b f(\bf{r}(t)) x'(t) dt$",
  ],
  steps=[
      r"Parameterize the curve as $\bf{r}(t)$.",
      r"Find the speed $|\bf{r}'(t)|$.",
      r"Substitute and integrate in $t$.",
  ],
  warn="ds needs the speed. dx and dy don't.",
  choices=[("Parameterizations", "t_param")])

N("t_param", "Parameterizations", "16.2",
  formula=[
      r"Segment: $\bf{r}(t) = A + t(B − A)$,  $0 ≤ t ≤ 1$",
      r"Circle: $(a cos t, a sin t)$,  $0 ≤ t ≤ 2π$",
      r"Ellipse: $(a cos t, b sin t)$",
      r"Graph $y = g(x)$: $(t, g(t))$",
      r"Graph $x = g(y)$: $(g(t), t)$",
      r"Helix: $(cos t, sin t, t)$",
  ],
  body="For a path made of pieces, do each piece and add.")

N("t_work", "Work along a path", "16.2",
  formula=[
      r"$W = ∫_C \bf{F} · d\bf{r} = ∫_a^b \bf{F}(\bf{r}(t)) · \bf{r}'(t) dt$",
      r"  $= ∫_C P dx + Q dy + R dz$",
      r"$∫_{−C} \bf{F} · d\bf{r} = −∫_C \bf{F} · d\bf{r}$",
  ],
  steps=[
      r"Look for a shortcut: a closed curve in the plane → Green; $∇ × \bf{F} = \bf{0}$ → potential.",
      r"Otherwise parameterize, dot $\bf{F}(\bf{r}(t))$ with $\bf{r}'(t)$, and integrate.",
      r"To match a picture: the arrow at $\bf{r}(t)$ is $\bf{F}(\bf{r}(t))$.",
  ],
  warn="It's a dot product, not a magnitude.",
  choices=[("Parameterizations", "t_param"), ("Is it conservative?", "t_cons")])

# ================================================================ 16.3
N("t_cons", "Conservative fields", "16.3",
  formula=[
      r"In 2D: $\frac{∂P}{∂y} = \frac{∂Q}{∂x}$",
      r"In 3D: $∇ × \bf{F} = \bf{0}$",
      r"$∫_C ∇f · d\bf{r} = f(B) − f(A)$",
      r"$∮_C ∇f · d\bf{r} = 0$",
  ],
  steps=[
      r"$f = ∫ P dx + g(y, z)$",
      r"Match $f_y = Q$ to find $g$.",
      r"Match $f_z = R$ to find $h(z)$.",
      r"The answer is $f(\text{end}) − f(\text{start})$.",
  ],
  warn="The domain can't have holes.")

# ================================================================ 16.4
N("t_green", "Green's theorem", "16.4",
  formula=[
      r"$∮_C P dx + Q dy = ∬_D (\frac{∂Q}{∂x} − \frac{∂P}{∂y}) dA$",
      r"Counterclockwise is positive. Clockwise: flip the sign.",
      r"Area $= ∮_C x dy = −∮_C y dx$",
      r"  $= \frac{1}{2} ∮_C (x dy − y dx)$",
  ],
  steps=[
      r"$P$ multiplies $dx$, $Q$ multiplies $dy$.",
      r"Integrate $\frac{∂Q}{∂x} − \frac{∂P}{∂y}$ over the region inside.",
      r"If that's a constant $k$, the answer is $k$ times the area.",
      r"To check directly, parameterize each edge and add.",
  ],
  warn="It's ∂Q/∂x − ∂P/∂y, Q first. The curve must be closed.",
  choices=[("Example both ways", "ex_green")])

N("ex_green", "Example", "16.4",
  formula=[
      r"$∮_C y^2 dx + 3xy dy$",
      r"Triangle $(0,0) → (1,0) → (1,2)$",
      r"Green: $\frac{∂Q}{∂x} − \frac{∂P}{∂y} = y$",
      r"$∫_0^1 ∫_0^{2x} y dy dx = \frac{2}{3}$",
      r"Directly: $0 + 6 − \frac{16}{3} = \frac{2}{3}$ ✓",
  ])

# ================================================================ 16.5
N("t_ops", "Gradient, divergence, curl", "16.5",
  formula=[
      r"$∇f = ⟨f_x, f_y, f_z⟩$",
      r"$∇ · \bf{F} = \frac{∂P}{∂x} + \frac{∂Q}{∂y} + \frac{∂R}{∂z}$",
      r"$∇ × \bf{F} = ⟨R_y − Q_z, P_z − R_x, Q_x − P_y⟩$",
      r"$∇^2 f = f_{xx} + f_{yy} + f_{zz}$",
      r"$∇ × (∇f) = \bf{0}$",
      r"$∇ · (∇ × \bf{F}) = 0$",
  ],
  body=[
      "Gradient: scalar → vector",
      "Divergence: vector → scalar",
      "Curl: vector → vector",
      "Laplacian: scalar → scalar",
  ],
  warn="In the curl, the middle part is P_z − R_x.",
  choices=[("Results for r = ⟨x, y, z⟩", "t_rvec"), ("Does it make sense?", "t_meaning")])

N("t_rvec", "Results for r", "16.5",
  formula=[
      r"$\bf{r} = ⟨x, y, z⟩$,  $r = |\bf{r}|$",
      r"$∇r = \frac{\bf{r}}{r}$",
      r"$∇ × \bf{r} = \bf{0}$,  $∇ · \bf{r} = 3$",
      r"$∇(\frac{1}{r}) = −\frac{\bf{r}}{r^3}$",
      r"$∇(ln r) = \frac{\bf{r}}{r^2}$",
      r"$∇g(r) = g'(r) \frac{\bf{r}}{r}$",
  ])

N("t_meaning", "Does it make sense?", "16.5",
  body=[
      "Work from the inside out and track scalar or vector.",
      "Makes sense: div(grad f), curl(grad f), grad(div F), div(curl F), curl(curl F).",
      "Nonsense: curl(div F), div(div F), grad(grad f), grad F, div f.",
  ])

# ================================================================ coordinates
N("t_coords", "Points & solids", "15.7/15.8",
  formula=[
      r"Cylindrical $(r, θ, z)$ →",
      r"  $(r cos θ, r sin θ, z)$",
      r"Spherical $(ρ, θ, φ)$ →",
      r"  $(ρ sin φ cos θ, ρ sin φ sin θ, ρ cos φ)$",
      r"$r = \sqrt{x^2 + y^2}$,  $tan θ = \frac{y}{x}$",
      r"$ρ = \sqrt{x^2 + y^2 + z^2}$,  $cos φ = \frac{z}{ρ}$",
  ],
  body=[
      r"$0 ≤ θ ≤ \frac{π}{2}$ means $x, y ≥ 0$. $0 ≤ θ ≤ π$ means $y ≥ 0$.",
      r"$r ≤ z$ or $φ ≤ \frac{π}{2}$ means $z ≥ 0$.",
      r"$z = c$ is a plane, $z = r$ a cone, $ρ = c$ a sphere, $φ = c$ a cone.",
  ],
  warn="Spherical points are written (ρ, θ, φ), with θ second.")

# ================================================================ TRICKS
N("tricks", "Tricks & rules", "Tricks",
  choices=[
      ("Symmetry gives zero", "tr_symmetry"),
      ("Choosing the order", "tr_order"),
      ("Known areas & volumes", "tr_geometry"),
      ("Trig identities & values", "tr_trig"),
      ("Substitution patterns", "tr_usub"),
      ("Integration by parts", "tr_parts"),
      ("Line integral rules", "tr_line"),
      ("Sanity checks", "tr_checks"),
  ])

N("tr_symmetry", "Symmetry gives zero", "Tricks",
  body=[
      r"If $D$ is symmetric across the $y$-axis and $f(−x, y) = −f(x, y)$, then $∬_D f dA = 0$.",
      r"So $∬ x dA = 0$ and $∬ x y^2 dA = 0$ over a disk.",
      r"A solid that's round about the $z$-axis has $\bar{x} = \bar{y} = 0$.",
      r"$∫_0^{2π} sin θ dθ = ∫_0^{2π} cos θ dθ = 0$",
  ])

N("tr_order", "Choosing the order", "Tricks",
  body=[
      r"Constant limits and $f = g(x) h(y)$: split into a product of two integrals.",
      r"For $x e^{xy}$ or $x cos(xy)$, integrate $dy$ first.",
      r"If the inner integral is impossible, like $e^{x^2}$, reverse the order.",
      r"Pick the order that avoids splitting the region.",
  ])

N("tr_geometry", "Known areas & volumes", "Tricks",
  formula=[
      r"Disk $πR^2$,  sector $\frac{1}{2} R^2 θ$",
      r"Ellipse $πab$,  triangle $\frac{1}{2} bh$",
      r"Triangle from its corners:",
      r"  $\frac{1}{2} |x_1(y_2 − y_3) + x_2(y_3 − y_1) + x_3(y_1 − y_2)|$",
      r"Ball $\frac{4}{3} πR^3$,  hemisphere $\frac{2}{3} πR^3$",
      r"Cone $\frac{1}{3} πR^2 h$,  cylinder $πR^2 h$",
      r"Half-cylinder $\frac{1}{2} πR^2 L$",
  ],
  body=r"If $f ≥ 0$ and the solid is a familiar shape, skip the integral.")

N("tr_trig", "Trig identities & values", "Tricks",
  formula=[
      r"$sin^2 θ = \frac{1 − cos 2θ}{2}$",
      r"$cos^2 θ = \frac{1 + cos 2θ}{2}$",
      r"$sin θ cos θ = \frac{1}{2} sin 2θ$",
      r"$∫_0^{2π} sin^2 θ dθ = ∫_0^{2π} cos^2 θ dθ = π$",
      r"$∫_0^{π/2} sin^2 θ dθ = \frac{π}{4}$",
      r"$∫_0^π sin φ dφ = 2$,  $∫_0^{π/2} sin φ dφ = 1$",
      r"$∫_0^{π/4} sin φ dφ = 1 − \frac{\sqrt{2}}{2}$",
      r"$∫_0^{π/2} sin^3 φ dφ = \frac{2}{3}$",
      r"$cos \frac{π}{6} = \frac{\sqrt{3}}{2}$,  $sin \frac{π}{6} = \frac{1}{2}$",
      r"$cos \frac{π}{4} = sin \frac{π}{4} = \frac{\sqrt{2}}{2}$",
  ],
  body=r"Odd power: save one factor, turn the rest into cosines with $sin^2 = 1 − cos^2$, then let $u = cos θ$.")

N("tr_usub", "Substitution patterns", "Tricks",
  formula=[
      r"$∫ x e^{x^2} dx = \frac{1}{2} e^{x^2}$",
      r"$∫ r e^{−r^2} dr = −\frac{1}{2} e^{−r^2}$",
      r"$∫ r \sqrt{1 + 4r^2} dr = \frac{1}{12} (1 + 4r^2)^{3/2}$",
      r"$∫ \frac{r}{\sqrt{a^2 − r^2}} dr = −\sqrt{a^2 − r^2}$",
      r"$∫ cos^n φ sin φ dφ = −\frac{cos^{n+1} φ}{n + 1}$",
      r"$∫ \frac{1}{1 + x^2} dx = arctan x$",
  ],
  body=r"For $∫ ρ^3 e^{ρ^2} dρ$, let $u = ρ^2$, then integrate by parts.")

N("tr_parts", "Integration by parts", "Tricks",
  formula=[
      r"$∫ u dv = uv − ∫ v du$",
      r"$∫ x e^x dx = (x − 1) e^x$",
      r"$∫ x cos x dx = x sin x + cos x$",
      r"$∫ x sin x dx = sin x − x cos x$",
      r"$∫ ln x dx = x ln x − x$",
  ],
  body="Pick u in this order: log, inverse trig, algebraic, trig, exponential.")

N("tr_line", "Line integral rules", "Tricks",
  body=[
      r"Reversing the path flips the sign of $∫ \bf{F} · d\bf{r}$ but not of $∫ f ds$.",
      r"$∫ g(x) dx$ on its own depends only on the $x$ endpoints.",
      r"A conservative field around a closed loop gives 0.",
      r"Speed on a circle of radius $a$ is $a$. On a segment it's $|B − A|$.",
      r"A field pointing mostly along the motion does positive work.",
  ])

N("tr_checks", "Sanity checks", "Tricks",
  body=[
      r"Jacobian: $r$ for polar and cylindrical, $ρ^2 sin φ$ for spherical.",
      "Outer limits are numbers, and lower is below upper.",
      "Volume, area, mass and length come out positive.",
      "The centroid lands inside the solid.",
      "A clockwise or reversed path flips the sign.",
      "Angles are in radians.",
      r"A triangle's area has the $\frac{1}{2}$.",
  ])

# ================================================================ EXAM MAP
N("exam_map", "Practice exam", "Exam 3",
  choices=[
      ("Q1–2  Iterated integrals", "t_rect"),
      ("Q3  Cross-sections", "t_rect"),
      ("Q4  Integral as a volume", "tr_geometry"),
      ("Q5, 11  Reverse the order", "t_rev"),
      ("Q6–9  Type I and Type II", "t_gen"),
      ("Q10  Volume over a region", "t_gen"),
      ("Q12–13, 15  Polar", "t_polar"),
      ("Q14  Area inside r = √θ", "t_polar_area"),
      ("Q16  Cartesian to polar", "t_polar_cart"),
      ("Q17  Surface area", "t_sa"),
      ("Q18, 21–22  Triple integrals", "t_tri"),
      ("Q19, 23  x = a(y² + z²)", "t_cyl_x"),
      ("Q20, 24  Orders of a triple integral", "t_tri_order"),
      ("Q25, 28  Converting points", "t_coords"),
      ("Q26, 29  Describing a solid", "t_coords"),
      ("Q27  Cylindrical", "t_cyl"),
      ("Q30–32  Spherical", "t_sph_bounds"),
      ("Q33  Volume and centroid", "t_mass"),
      ("Q34  Line integral in dx", "t_scalar"),
      ("Q35–37  Work", "t_work"),
      ("Q38  Green's theorem", "t_green"),
      ("Q39  Curl and divergence", "t_ops"),
      ("Q40  Results for r", "t_rvec"),
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
    "t_polar_cart": "arrow.triangle.swap", "t_tri_order": "arrow.up.arrow.down",
    "t_cyl_x": "arrow.left.and.right", "t_sph_bounds": "circle.dashed", "t_sph_conv": "cone",
    "t_param": "point.topleft.down.curvedto.point.bottomright.up",
    "t_rvec": "arrow.up.forward", "t_meaning": "questionmark.circle",
    "tr_symmetry": "rectangle.split.2x1", "tr_order": "arrow.up.arrow.down",
    "tr_geometry": "triangle", "tr_trig": "waveform.path", "tr_usub": "arrow.2.squarepath",
    "tr_parts": "square.split.2x1", "tr_line": "point.3.connected.trianglepath.dotted",
    "tr_checks": "checkmark.seal",
}
for nid, icon in ICONS.items():
    if nid in NODES:
        NODES[nid]["icon"] = icon


# ================================================================ markup check
COMMANDS = {"frac": 2, "sqrt": 1, "bar": 1, "bf": 1, "text": 1, ",": 0}


def check_math(text):
    """Return a list of problems with the $...$ markup in one string."""
    problems = []
    for line in text.split("\n"):
        if line.count("$") % 2:
            problems.append(f"unbalanced $ in: {line}")
            continue
        for k, seg in enumerate(line.split("$")):
            if k % 2 == 0:
                if "\\" in seg or "_{" in seg or "^{" in seg:
                    problems.append(f"markup outside $...$: {seg!r}")
                continue
            depth = 0
            for ch in seg:
                depth += ch == "{"
                depth -= ch == "}"
                if depth < 0:
                    problems.append(f"extra }} in: {seg}")
                    break
            if depth > 0:
                problems.append(f"unclosed {{ in: {seg}")
            for m in re.finditer(r"\\([A-Za-z]+|.)", seg):
                name = m.group(1)
                if name not in COMMANDS:
                    problems.append(f"unknown command \\{name} in: {seg}")
                elif COMMANDS[name] and not seg[m.end():].startswith("{"):
                    problems.append(f"\\{name} needs {{...}} in: {seg}")
            if re.search(r"[_^](\s|$)", seg):
                problems.append(f"dangling _ or ^ in: {seg}")
    return problems


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
        texts = [n.get("formula"), n.get("body"), *(n.get("steps") or [])]
        for t in filter(None, texts):
            errors += [f"{nid}: {p}" for p in check_math(t)]
        for t in filter(None, [n.get("warn"), n["title"]] + [c["label"] for c in n.get("choices", [])]):
            if "$" in t or "\\" in t:
                errors.append(f"{nid}: titles, labels and warnings are plain text: {t}")
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
