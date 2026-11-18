#!/usr/bin/env python3
"""Builds Calc3Tutor/tutor.json, the decision tree the watch app walks.

Each node is one watch screen:
  title    short heading
  tag      section label shown in the nav bar (e.g. "15.8")
  body     plain text (no markdown); "\n" for line breaks
  formula  optional highlighted formula block
  warn     optional "common mistake" callout
  choices  list of (label, next_id) -> narrowing question
  next     single next_id -> "Next" button
A node with neither choices nor next is a finish screen ("Start over").

Run:  python3 tools/build_tree.py      (writes JSON and validates the graph)
"""
import json
import os
import re
import sys

NODES = {}
ORDER = []


STEP_RE = re.compile(r"^(\d+)\.\s+")


def split_steps(text):
    """Numbered lines ("1. ...") become steps shown one at a time on the watch.
    Lines after a step attach to it; lines before the first step stay as intro.
    Fewer than two steps -> plain body."""
    lines = text.split("\n")
    numbered = [i for i, l in enumerate(lines) if STEP_RE.match(l)]
    last = numbered[-1] if numbered else -1
    intro, steps, outro = [], [], []
    for i, line in enumerate(lines):
        m = STEP_RE.match(line)
        if outro:
            outro.append(line)
        elif m:
            steps.append(line[m.end():])
        elif steps and i > last and line.startswith("Ex"):
            outro.append(line)  # worked example after the last step: shown once steps are done
        elif steps:
            steps[-1] += "\n" + line
        else:
            intro.append(line)
    if len(steps) < 2:
        return text, None, None
    return ("\n".join(intro).strip("\n") or None, steps,
            "\n".join(outro).strip("\n") or None)


def N(id, title, tag="", body=None, formula=None, warn=None, choices=None, next=None, next_label=None):
    if id in NODES:
        raise SystemExit(f"duplicate node id: {id}")
    node = {"id": id, "title": title, "tag": tag}
    if body:
        intro, steps, outro = split_steps(body.strip("\n"))
        if intro:
            node["body"] = intro
        if steps:
            node["steps"] = steps
        if outro:
            node["outro"] = outro
    if formula:
        node["formula"] = formula.strip("\n")
    if warn:
        node["warn"] = warn.strip("\n")
    if choices:
        node["choices"] = [{"label": l, "next": n} for l, n in choices]
    if next:
        node["next"] = next
    if next_label:
        node["nextLabel"] = next_label
    NODES[id] = node
    ORDER.append(id)


PARAM_BODY = (
    "Segment A → B: r(t) = A + t(B − A), 0 ≤ t ≤ 1.\n"
    "Circle radius a, CCW: (a cos t, a sin t), 0→2π. Quarter in QI: 0→π/2.\n"
    "Clockwise: (a cos t, −a sin t), or run t backward.\n"
    "Ellipse: (a cos t, b sin t).\n"
    "Graph y = g(x), x: a→b: (t, g(t)), t: a→b.\n"
    "Graph x = g(y) (e.g. x = y²+4): (g(t), t), t from start y to end y.\n"
    "Polygon / piecewise path: do each piece, then add.")
PARAM_WARN = "Direction matters for work: start point at the lower t."

# ---------------------------------------------------------------- root
N("root", "Calc 3 Tutor", "Exam 3",
  body="Work on paper. I'll give you one step at a time.",
  choices=[
      ("Practice exam question #", "exam_map"),
      ("Describe my problem", "classify"),
      ("Reference", "reference"),
  ])

N("reference", "Reference", "Reference",
  choices=[
      ("Formula sheet", "fs_menu"),
      ("Integration toolkit", "tk_menu"),
      ("Choosing a method", "method_table"),
      ("All topics", "topics"),
      ("Final answer check", "final_check"),
  ])

N("topics", "Topics", "Index",
  choices=[
      ("15.1 Rectangles", "rect_eval"),
      ("15.2 General regions", "gen_setup"),
      ("15.2 Reverse order", "reverse_order"),
      ("15.3 Polar", "polar_region"),
      ("15.5 Surface area", "sa_start"),
      ("15.6 Triple integrals", "triple_setup"),
      ("15.6 Change order (3D)", "triple_reorder"),
      ("15.7 Cylindrical", "cyl_setup"),
      ("15.8 Spherical", "sph_region"),
      ("Mass & centroid", "mass_menu"),
      ("16.2 Scalar line ∫ f ds", "scalar_line"),
      ("16.2 Work ∫ F·dr", "work_start"),
      ("Conservative / potential", "cons_start"),
      ("16.4 Green's theorem", "green_start"),
      ("16.5 grad/div/curl", "ops_start"),
      ("Concept & graph Qs", "concept_start"),
  ])

# ---------------------------------------------------------------- classify
N("classify", "What do you see?", "Start",
  body="Pick what best matches the problem statement.",
  choices=[
      ("An integral is already written with bounds", "given_n"),
      ("A region or solid: find area, volume, mass, centroid, average", "region_dim"),
      ("A surface: find its surface area", "sa_start"),
      ("A curve/path: ∫ f ds, work, wire mass, ∫F·dr", "line_start"),
      ("A closed curve in the plane (∮)", "green_start"),
      ("Is F conservative? Find a potential f", "cons_start"),
      ("grad, div, curl, Laplacian", "ops_start"),
      ("Convert a point (cyl/sph → x,y,z)", "point_convert"),
      ("Describe/sketch a solid from inequalities", "describe_solid"),
      ("Cross-section area A(x) or A(y)", "cross_section"),
      ("Concept / pick-the-graph / which integral", "concept_start"),
      ("Not sure which method", "method_table"),
  ])

N("method_table", "Choosing a method", "Strategy",
  body=(
      "Rectangle in 2D → Cartesian ∬\n"
      "Curves/lines bound region → Type I / II\n"
      "Inner antiderivative impossible (e^(x²), sin(y²)) → reverse order\n"
      "Circle, disk, ring, x²+y² → polar\n"
      "Surface z=f(x,y), 'area of the part of' → surface area\n"
      "Box, planes, tetrahedron → Cartesian ∭\n"
      "Cylinder/paraboloid around z-axis → cylindrical\n"
      "Sphere, ball, cone + sphere, x²+y²+z² → spherical\n"
      "Wire density, ds, arc length → scalar line ∫\n"
      "Force, work, F·dr, P dx + Q dy → vector line ∫\n"
      "Endpoints only matter / P_y = Q_x → potential function\n"
      "Closed plane curve → Green\n"
      "Spreading out → div;  spinning → curl"),
  next="classify", next_label="Back to start")

# ---------------------------------------------------------------- given integral
N("given_n", "How many ∫ signs?", "Given ∫",
  choices=[("Two (∬, dA, dx dy)", "given2"), ("Three (∭, dV)", "given3")])

N("given2", "What is asked?", "Given ∬",
  choices=[
      ("Evaluate it", "given2_eval"),
      ("Reverse / change the order", "reverse_order"),
      ("Convert to polar", "polar_from_cart"),
      ("Sketch / identify the region", "read_bounds"),
  ])

N("given2_eval", "Look at the bounds", "Given ∬",
  body="Are all four bounds numbers (constants)?",
  choices=[
      ("Yes, all constants", "rect_eval"),
      ("No, inner bounds have x or y", "given2_inner"),
  ])

N("given2_inner", "Can you do the inner integral?", "Given ∬",
  body="Try the inner antiderivative in your head. Red flags: e^(x²), e^(y²), sin(x²), cos(y³), √(1+x³), e^(x/y) integrated in the wrong variable.",
  choices=[
      ("Yes, looks doable", "eval_iter"),
      ("No / it's a red-flag function", "reverse_order"),
      ("Integrand has x²+y² and bounds look circular", "polar_from_cart"),
  ])

N("given3", "What is asked?", "Given ∭",
  choices=[
      ("Evaluate it", "triple_eval"),
      ("Rewrite in another order", "triple_reorder"),
      ("Convert to cylindrical", "cyl_from_cart"),
      ("Convert to spherical", "sph_from_cart"),
      ("Identify the solid", "read_bounds3"),
  ])

N("read_bounds", "Read bounds → region", "15.2",
  body=(
      "1. Turn bounds into inequalities. Outer bounds are numbers; inner bounds are curves.\n"
      "Ex: ∫0→1 ∫(x²)→(√x) dy dx  ⇒  0≤x≤1, x²≤y≤√x.\n"
      "2. Draw the inner curves (y=x², y=√x) and the outer lines (x=0, x=1).\n"
      "3. Shade between the inner curves, only for x in the outer range.\n"
      "4. Test a point: pick x in the middle, check lower curve < upper curve there."),
  warn="Outer bounds are always constants. If inner bounds depend on x, the outer variable is x.",
  next="final_check", next_label="Done")

N("read_bounds3", "Read bounds → solid", "15.6",
  body=(
      "1. Write all 6 inequalities, innermost first.\n"
      "2. Innermost pair = bottom & top surfaces (e.g. z from 0 to 4−x²−y² ⇒ under a paraboloid, above z=0).\n"
      "3. Outer two pairs = the shadow region in the plane of the other two variables. Sketch it.\n"
      "4. Stack: shadow on the floor, surfaces as floor and ceiling.\n"
      "Recognize: x²+y² terms → round (paraboloid, cone, cylinder); linear → planes; √(a²−x²−y²) → sphere."),
  next="final_check", next_label="Done")

# ---------------------------------------------------------------- 15.1
N("rect_eval", "Rectangle ∬", "15.1",
  body=(
      "R = [a,b]×[c,d]. Either order works (Fubini).\n"
      "Area = ∬1 dA; volume under z=f≥0 = ∬f dA; average = (1/Area)∬f dA.\n"
      "Pick the order that makes the inner integral easy."),
  formula="∬R f dA = ∫a→b ∫c→d f(x,y) dy dx",
  choices=[
      ("f = g(x)·h(y) (splits)", "rect_product"),
      ("Has x·e^(xy), x·cos(xy), etc.", "rect_order"),
      ("Plain polynomial / other", "eval_iter"),
      ("Has √(R²−x²) or √(R²−y²): use geometry", "geom_volume"),
  ])

N("rect_product", "Product shortcut", "15.1",
  body="Constant bounds and f = g(x)h(y) ⇒ multiply two single integrals.\nEx: ∬ x·e^y over [0,2]×[0,1] = (∫0→2 x dx)(∫0→1 e^y dy) = 2(e−1).",
  formula="∫a→b∫c→d g(x)h(y) dy dx = (∫a→b g dx)(∫c→d h dy)",
  next="final_check", next_label="Check answer")

N("rect_order", "Choose the order", "15.1",
  body=(
      "If the integrand is x·e^(xy): integrate dy FIRST. The x outside is exactly the chain-rule factor:\n"
      "∫ x·e^(xy) dy = e^(xy).\n"
      "Same for x·cos(xy) → sin(xy). For y·e^(xy) or y·cos(xy), do dx first, since d/dx(xy) = y.\n"
      "Rule: inner variable = the one whose coefficient sits outside the composite."),
  next="eval_iter")

N("eval_iter", "Evaluate iterated ∫", "Evaluate",
  body=(
      "1. Inner integral: integrate in the inner variable only. Every other letter is a constant.\n"
      "2. Plug in inner bounds: (upper) − (lower). Bounds may be functions; substitute them fully.\n"
      "3. Simplify to a single-variable expression.\n"
      "4. Outer integral, plug bounds, subtract.\n"
      "Need an antiderivative trick? See the Integration toolkit."),
  warn="Don't drop a term when plugging in bounds. Write (upper) − (lower) with parentheses.",
  choices=[
      ("Integration toolkit", "tk_menu"),
      ("I'm done → check", "final_check"),
  ])

# ---------------------------------------------------------------- region / solid tasks
N("region_dim", "2D or 3D?", "Setup",
  choices=[
      ("2D region in the plane (∬)", "q2_quantity"),
      ("Volume under/between surfaces z=…", "vol_between"),
      ("3D solid (∭)", "q3_quantity"),
  ])

N("vol_between", "Volume between surfaces", "15.2/15.3",
  body=(
      "Volume = ∬D (top − bottom) dA.\n"
      "1. Identify top surface and bottom surface (bottom may be z=0).\n"
      "2. D = shadow on xy-plane. Edge of shadow: where top = bottom, or given walls.\n"
      "3. Choose coordinates for D."),
  formula="V = ∬D [z_top − z_bottom] dA",
  warn="Check which surface is on top by testing a point inside D.",
  next="shape2d", next_label="Describe D")

N("q2_quantity", "What quantity?", "Setup",
  choices=[
      ("Area of region", "q2_area"),
      ("Volume under z = f(x,y)", "q2_vol"),
      ("Mass (density δ given)", "q2_mass"),
      ("Centroid / center of mass", "lamina_centroid"),
      ("Average value of f", "q2_avg"),
      ("Just ∬ f dA", "shape2d"),
  ])

N("q2_area", "Area", "Setup", body="Integrand = 1.", formula="A = ∬D 1 dA", next="shape2d", next_label="Describe D")
N("q2_vol", "Volume", "Setup", body="Integrand = f(x,y) (height). If between two surfaces, use top − bottom.", formula="V = ∬D f(x,y) dA", next="shape2d", next_label="Describe D")
N("q2_mass", "Mass", "Setup", body="Integrand = density δ(x,y).", formula="m = ∬D δ(x,y) dA", next="shape2d", next_label="Describe D")
N("q2_avg", "Average value", "Setup", body="Compute ∬f dA and the area of D, then divide.", formula="f_avg = (1/Area(D)) ∬D f dA", next="shape2d", next_label="Describe D")

N("shape2d", "Shape of D?", "Setup",
  choices=[
      ("Rectangle (constant bounds)", "rect_eval"),
      ("Bounded by curves / lines / triangle", "gen_setup"),
      ("Disk, sector, ring, centered at origin", "polar_region"),
      ("Circle through the origin (x²+y²=2ay)", "polar_offcenter"),
  ])

# ---------------------------------------------------------------- 15.2
N("gen_setup", "General region", "15.2",
  body=(
      "1. Sketch every boundary curve.\n"
      "2. Find intersection points: set the curves equal and solve.\n"
      "3. Draw a vertical line through D: does it always enter through the same curve and leave through the same curve? Then Type I works.\n"
      "4. Draw a horizontal line: same test for Type II."),
  choices=[
      ("Vertical line test passes (Type I, dy dx)", "type1"),
      ("Horizontal line test passes (Type II, dx dy)", "type2"),
      ("Neither passes cleanly", "split_region"),
      ("Triangle from vertices", "triangle_region"),
  ])

N("type1", "Type I: dy dx", "15.2",
  body=(
      "x runs from leftmost to rightmost point of D (numbers, often intersection x-values).\n"
      "y runs from bottom curve to top curve, both written as y = (in x).\n"
      "Check: at a middle x, bottom value < top value."),
  formula="∫a→b ∫g1(x)→g2(x) f dy dx",
  next="eval_iter")

N("type2", "Type II: dx dy", "15.2",
  body=(
      "y runs from lowest to highest point of D (numbers).\n"
      "Solve each boundary for x. x runs from left curve to right curve.\n"
      "Square roots: x = +√y on the right half, −√y on the left."),
  formula="∫c→d ∫h1(y)→h2(y) f dx dy",
  next="eval_iter")

N("split_region", "Split the region", "15.2",
  body=(
      "Find where the entering (or exiting) curve changes; that's at a corner/intersection.\n"
      "Draw a line there to cut D into pieces that each pass the test.\n"
      "Set up each piece separately and ADD the integrals.\n"
      "Often the other order avoids splitting, so try it first."),
  next="eval_iter")

N("triangle_region", "Triangle region", "15.2",
  body=(
      "1. Plot the 3 vertices.\n"
      "2. Line through (x1,y1),(x2,y2): slope m = (y2−y1)/(x2−x1), then y = y1 + m(x − x1). Solve for x instead if doing dx first.\n"
      "3. Pick the order where one side is the bottom (or left) and one side is the top (or right). Otherwise split at the middle vertex.\n"
      "Area check: ½·base·height."),
  warn="Area of a triangle is ½bh, not bh.",
  choices=[("Type I (dy dx)", "type1"), ("Type II (dx dy)", "type2")])

N("reverse_order", "Reverse the order", "15.2",
  body=(
      "1. Write bounds as inequalities.\n"
      "2. Sketch: inner curves + outer lines; shade.\n"
      "3. Label every corner (solve intersections).\n"
      "4. New OUTER variable: its min and max over the whole region (numbers).\n"
      "5. Solve each boundary curve for the new INNER variable (x = arcsin y ⇔ y = sin x; x = ln y ⇔ y = eˣ; y = x² ⇔ x = √y).\n"
      "6. Draw a line in the new direction: inner bound = curve you enter → curve you exit.\n"
      "7. If the entering/exiting curve changes, split."),
  warn="Never just swap dx and dy. The region stays the same; the bounds change.",
  next="reverse_example", next_label="See an example")

N("reverse_example", "Example", "15.2",
  body=(
      "∫0→1 ∫y→1 e^(x²) dx dy  (can't integrate e^(x²) dx)\n"
      "Region: 0≤y≤1, y≤x≤1. Triangle with corners (0,0),(1,0),(1,1).\n"
      "New outer: x from 0 to 1. Vertical line at x: y from 0 up to y = x.\n"
      "= ∫0→1 ∫0→x e^(x²) dy dx = ∫0→1 x·e^(x²) dx\n"
      "u = x²: = ½(e − 1).\n"
      "Notice the new inner integral created the factor x that u-sub needs."),
  next="eval_iter")

# ---------------------------------------------------------------- 15.3
N("polar_region", "Polar: describe D", "15.3",
  body="x = r cosθ, y = r sinθ, x²+y² = r², dA = r dr dθ.",
  choices=[
      ("Full disk radius R", "polar_disk"),
      ("Part of a disk (half, quadrant, wedge)", "polar_angles"),
      ("Ring between two circles", "polar_ring"),
      ("Circle through origin (x²+y²=2ax or 2ay)", "polar_offcenter"),
      ("Bounded by a line like y=c or x=c", "polar_line"),
      ("Inside a polar curve r = g(θ)", "polar_curve_area"),
  ])

N("polar_disk", "Full disk", "15.3",
  formula="0 ≤ r ≤ R,  0 ≤ θ ≤ 2π",
  body="x²+y² ≤ R² ⇒ r goes to R (not R²).",
  next="polar_convert")

N("polar_angles", "Angle bounds", "15.3",
  body=(
      "Quadrant I: 0→π/2   II: π/2→π\n"
      "Upper half (y≥0): 0→π\n"
      "Right half (x≥0): −π/2→π/2\n"
      "Left half: π/2→3π/2   Lower: π→2π\n"
      "Line y = x (QI): θ = π/4\n"
      "y = √3·x: θ = π/3;  y = x/√3: θ = π/6\n"
      "y-axis: θ = π/2. General line y = mx: θ = arctan(m).\n"
      "Go counterclockwise: smaller angle is lower bound."),
  next="polar_convert")

N("polar_ring", "Annulus", "15.3",
  formula="R1 ≤ r ≤ R2,  θ as needed",
  body="Inner circle radius R1, outer circle radius R2.",
  next="polar_convert")

N("polar_offcenter", "Circle through origin", "15.3",
  body=(
      "Substitute r² for x²+y², r sinθ for y, r cosθ for x, cancel one r.\n"
      "x²+y² = 2ay ⇒ r = 2a sinθ, θ from 0 to π (circle above x-axis).\n"
      "x²+y² = 2ax ⇒ r = 2a cosθ, θ from −π/2 to π/2.\n"
      "r goes from 0 to that curve."),
  formula="0 ≤ r ≤ 2a sinθ, 0 ≤ θ ≤ π",
  warn="If the problem gives (x−a)²+y² = a², expand it first: x²+y² = 2ax.",
  next="polar_convert")

N("polar_line", "Line boundary", "15.3",
  body=(
      "y = c ⇒ r sinθ = c ⇒ r = c/sinθ = c·cscθ.\n"
      "x = c ⇒ r = c·secθ.\n"
      "Ex: inside x²+y²=4, above y=1: r from cscθ to 2.\n"
      "θ where they meet: 2 sinθ = 1 ⇒ θ = π/6 to 5π/6."),
  next="polar_convert")

N("polar_from_cart", "Cartesian → polar", "15.3",
  body=(
      "1. Read the bounds as a region (sketch).\n"
      "Clues: y from 0 to √(R²−x²) ⇒ upper half disk radius R.\n"
      "x from −√(R²−y²) to √(R²−y²) ⇒ full width of a disk.\n"
      "y from x to √(2−x²) ⇒ wedge between line y=x and circle r=√2.\n"
      "y from 0 to √(2ax − x²), x from 0 to 2a ⇒ upper half of x²+y² = 2ax ⇒ r ≤ 2a cosθ, 0 ≤ θ ≤ π/2.\n"
      "2. Write polar bounds for that region."),
  choices=[("Write the polar bounds", "polar_region"), ("Bounds done, convert integrand", "polar_convert")])

N("polar_convert", "Convert & integrate", "15.3",
  body=(
      "1. Replace x = r cosθ, y = r sinθ, x²+y² = r².\n"
      "2. Multiply by the Jacobian r.\n"
      "3. Usually integrate dr first, then dθ.\n"
      "4. If integrand = g(r)h(θ) and bounds are constants, split into a product.\n"
      "Ex: ∬(x²+y²) dA → ∫∫ r²·r dr dθ = ∫∫ r³ dr dθ.\n"
      "Ex: e^(−(x²+y²)) → e^(−r²)·r, u = r²."),
  formula="∬D f dA = ∫α→β ∫ r1→r2 f(r cosθ, r sinθ) r dr dθ",
  warn="Forgetting the extra r is the #1 polar mistake. Use radians.",
  choices=[("Integration toolkit (sin², cos²…)", "tk_trig"), ("Done → check", "final_check")])

# ---------------------------------------------------------------- 15.5 surface area
N("sa_start", "How is the surface given?", "15.5",
  choices=[
      ("z = f(x,y)", "sa_graph"),
      ("A plane ax+by+cz=d", "sa_plane"),
      ("Part of a sphere", "sa_sphere"),
      ("Parametric r(u,v)", "sa_param"),
  ])

N("sa_graph", "Surface area, z = f(x,y)", "15.5",
  body=(
      "1. Compute f_x and f_y.\n"
      "2. Integrand √(1 + f_x² + f_y²).\n"
      "3. D = shadow in the xy-plane: 'part of z=f above region D' or 'below z=h' ⇒ f(x,y) ≤ h.\n"
      "4. Choose coordinates for D."),
  formula="A = ∬D √(1 + f_x² + f_y²) dA",
  warn="Don't forget the 1 inside the root. You integrate the stretch factor, not f.",
  choices=[
      ("Radicand has x²+y² / D is a disk", "sa_polar"),
      ("Radicand is a constant", "sa_const"),
      ("Radicand has one variable only", "sa_onevar"),
  ])

N("sa_polar", "Use polar", "15.5",
  body=(
      "Ex: z = x²+y² below z = 4.\n"
      "f_x=2x, f_y=2y ⇒ √(1+4x²+4y²) = √(1+4r²).\n"
      "D: r ≤ 2.\n"
      "A = ∫0→2π ∫0→2 √(1+4r²)·r dr dθ\n"
      "u = 1+4r², du = 8r dr\n"
      "= 2π·(1/12)[(1+4r²)^(3/2)]0→2 = (π/6)(17^(3/2) − 1)."),
  warn="Still need the polar r. It's what makes the u-sub work.",
  next="final_check", next_label="Check answer")

N("sa_const", "Constant factor", "15.5",
  body="If √(1+f_x²+f_y²) = k is constant, A = k · Area(D).\nEx: z = 2x+3y ⇒ k = √(1+4+9) = √14.",
  formula="A = k · Area(D)",
  next="final_check", next_label="Check answer")

N("sa_onevar", "One-variable radicand", "15.5",
  body=(
      "Ex: z = y² ⇒ √(1+4y²); z = x^(3/2) ⇒ √(1 + 9x/4).\n"
      "Integrate the OTHER variable first (it's just length of D in that direction), so the inner gives a factor that helps the u-sub.\n"
      "If D is a triangle with y-dependent bounds, choose the order so the outer variable matches the radicand."),
  next="eval_iter")

N("sa_plane", "Part of a plane", "15.5",
  body="Solve for z, or use the shortcut. D is the shadow on the xy-plane (e.g. first octant ⇒ triangle cut by z=0: ax+by=d).",
  formula="A = (√(a²+b²+c²)/|c|) · Area(D)",
  next="final_check", next_label="Check answer")

N("sa_sphere", "Part of a sphere", "15.5",
  body=(
      "z = √(a²−x²−y²) ⇒ √(1+f_x²+f_y²) = a/√(a²−r²).\n"
      "A = ∫∫ a/√(a²−r²) · r dr dθ. u = a² − r².\n"
      "Shadow D: where the sphere meets the other surface (set equal, solve for r)."),
  next="final_check", next_label="Check answer")

N("sa_param", "Parametric surface", "15.5",
  body="Compute r_u, r_v, their cross product, and its length.",
  formula="A = ∬D |r_u × r_v| du dv",
  next="final_check", next_label="Check answer")

# ---------------------------------------------------------------- 3D quantity and shape
N("q3_quantity", "What quantity?", "Setup",
  choices=[
      ("Volume", "q3_vol"),
      ("Mass (density δ)", "q3_mass"),
      ("Centroid / center of mass", "solid_centroid"),
      ("Just ∭ f dV", "shape3d"),
  ])
N("q3_vol", "Volume", "Setup", formula="V = ∭E 1 dV", next="shape3d", next_label="Describe solid")
N("q3_mass", "Mass", "Setup", formula="m = ∭E δ dV", next="shape3d", next_label="Describe solid")

N("shape3d", "What does the solid look like?", "Setup",
  choices=[
      ("Box, planes, tetrahedron, parabolic cylinder", "triple_setup"),
      ("Cylinder, paraboloid, cone with flat top, x²+y²", "cyl_setup"),
      ("Paraboloid around x- or y-axis (x = y²+z²)", "cyl_other_axis"),
      ("Sphere, ball, ice-cream cone, x²+y²+z²", "sph_region"),
      ("Not sure", "coord_choice"),
  ])

N("coord_choice", "Which coordinates?", "Strategy",
  body=(
      "Look at the surfaces after converting:\n"
      "Only planes → Cartesian.\n"
      "x²+y² appears, round shadow, z-axis symmetry → cylindrical (dV = r dz dr dθ).\n"
      "x²+y²+z² appears, or cone + sphere → spherical (dV = ρ² sinφ dρ dφ dθ).\n"
      "Cone + plane z = h: either works; cylindrical is usually simpler."),
  choices=[("Cartesian", "triple_setup"), ("Cylindrical", "cyl_setup"), ("Spherical", "sph_region")])

# ---------------------------------------------------------------- 15.6
N("triple_setup", "Triple ∫ setup", "15.6",
  body=(
      "1. List all bounding surfaces.\n"
      "2. Innermost variable = the one with a clear floor & ceiling (usually z).\n"
      "3. Write z from bottom(x,y) to top(x,y).\n"
      "4. Shadow D on xy-plane: set top = bottom to find its edge, plus any walls.\n"
      "5. Describe D like a 2D region (Type I/II)."),
  formula="∭E f dV = ∬D ∫ bottom→top f dz dA",
  warn="A bound may use only OUTER variables, never one already integrated.",
  choices=[
      ("Tetrahedron (plane + coordinate planes)", "tetra"),
      ("Describe the shadow D", "gen_setup"),
      ("Bounds done → evaluate", "triple_eval"),
  ])

N("tetra", "Tetrahedron", "15.6",
  body=(
      "Plane x/a + y/b + z/c = 1 in the first octant.\n"
      "z: 0 → c(1 − x/a − y/b)\n"
      "Shadow (set z=0): line x/a + y/b = 1.\n"
      "y: 0 → b(1 − x/a);  x: 0 → a.\n"
      "Plane given as 2x+3y+z=6? Intercepts: x=3, y=2, z=6.\n"
      "Volume check: abc/6."),
  next="triple_eval")

N("triple_eval", "Evaluate ∭", "15.6",
  body=(
      "Inside out: innermost variable first, treat others as constants, plug bounds.\n"
      "After the first integration you have a double integral; after the second, a single.\n"
      "For volume, the inner dz integral gives (top − bottom)."),
  next="eval_iter")

N("triple_reorder", "Change order (3D)", "15.6",
  body=(
      "1. Write all 6 inequalities. Sketch the solid.\n"
      "2. Pick the new innermost variable; solve every surface for it.\n"
      "3. Inner bounds: the two surfaces it runs between.\n"
      "4. Project onto the plane of the remaining 2 variables: eliminate the inner variable (set the two surfaces equal, or set it to its extreme like 0).\n"
      "5. Describe that 2D shadow in the new order.\n"
      "6. Split if a boundary changes partway."),
  next="triple_reorder_ex", next_label="See an example")

N("triple_reorder_ex", "Example", "15.6",
  body=(
      "∫0→1 ∫0→(1−x) ∫0→(1−x−y) f dz dy dx  (tetrahedron x+y+z ≤ 1)\n"
      "Want dx dz dy:\n"
      "x: 0 → 1−y−z (solve plane for x)\n"
      "Shadow on yz-plane (x=0): y+z ≤ 1 ⇒ z: 0 → 1−y\n"
      "y: 0 → 1\n"
      "⇒ ∫0→1 ∫0→(1−y) ∫0→(1−y−z) f dx dz dy\n"
      "Curved example: z ≤ 1−y², x from 0 to 2: shadow in yz-plane is under the parabola."),
  next="six_orders", next_label="All six orders example")

# ---------------------------------------------------------------- 15.7
N("cyl_setup", "Cylindrical setup", "15.7",
  body=(
      "Convert each surface:\n"
      "x²+y² = R² → r = R (cylinder)\n"
      "z = √(x²+y²) → z = r (cone); z = k√(x²+y²) → z = kr\n"
      "z = x²+y² → z = r² (paraboloid)\n"
      "z = a − x²−y² → z = a − r²\n"
      "sphere → z = ±√(R² − r²)\n"
      "plane z = y → z = r sinθ"),
  formula="dV = r dz dr dθ",
  choices=[
      ("Round around the z-axis (usual)", "cyl_bounds"),
      ("Round around x- or y-axis (x = y²+z²)", "cyl_other_axis"),
  ])

N("cyl_bounds", "Cylindrical bounds", "15.7",
  body=(
      "z: bottom surface → top surface (in r, θ).\n"
      "r: 0 → edge of shadow. Edge = where top = bottom (solve for r) or the cylinder wall.\n"
      "θ: 0 → 2π unless cut (first octant 0→π/2; y≥0: 0→π; x≥0: −π/2→π/2).\n"
      "Off-center cylinder x²+y² = 2ax ⇒ r ≤ 2a cosθ, −π/2 ≤ θ ≤ π/2."),
  formula="∫θ ∫r ∫ z_bot→z_top f · r dz dr dθ",
  warn="Cone z=r vs paraboloid z=r²: they meet at r = 1. Which is on top for 0<r<1? r > r², so the cone.",
  next="cyl_example", next_label="Examples")

N("cyl_example", "Examples", "15.7",
  body=(
      "Between z = x²+y² and z = 4:\n"
      "V = ∫0→2π ∫0→2 (4 − r²) r dr dθ = 2π(8 − 4) = 8π.\n\n"
      "Inside sphere x²+y²+z² = 2, above cone z = r:\n"
      "z: r → √(2 − r²); meet: r = √(2−r²) ⇒ r = 1.\n"
      "V = ∫0→2π ∫0→1 (√(2−r²) − r) r dr dθ."),
  next="eval_iter")

N("cyl_from_cart", "Cartesian → cylindrical", "15.7",
  body=(
      "1. Outer two bounds (x, y) describe the shadow: convert it to r, θ like polar.\n"
      "2. z bounds: replace x²+y² with r².\n"
      "3. Integrand: x = r cosθ, y = r sinθ, x²+y² = r².\n"
      "4. Multiply by r."),
  choices=[("Polar region help", "polar_region"), ("Continue", "cyl_bounds")])

# ---------------------------------------------------------------- 15.8
N("sph_region", "Spherical: the solid", "15.8",
  body="ρ = distance from origin. φ = angle down from +z axis (0 to π). θ = angle around z-axis.",
  choices=[
      ("Ball / hemisphere / octant of ball", "sph_ball"),
      ("Ice-cream: above a cone, inside a sphere", "sph_icecream"),
      ("Sphere not centered at origin (x²+y²+z²=2az)", "sph_shifted"),
      ("Between two spheres (shell)", "sph_shell"),
      ("Cut by a plane z = h", "sph_plane"),
      ("Convert a cone or surface", "sph_convert"),
  ])

N("sph_ball", "Ball pieces", "15.8",
  body=(
      "Full ball radius R: ρ 0→R, φ 0→π, θ 0→2π.\n"
      "Upper hemisphere (z ≥ 0): φ 0→π/2.\n"
      "Lower: φ π/2→π.\n"
      "First octant: φ 0→π/2 and θ 0→π/2.\n"
      "y ≥ 0 half: θ 0→π."),
  next="sph_integrand")

N("sph_convert", "Converting surfaces", "15.8",
  body=(
      "x²+y²+z² = R² → ρ = R\n"
      "z = √(x²+y²) → φ = π/4\n"
      "z = √3·√(x²+y²) → φ = π/6\n"
      "z = √((x²+y²)/3) → φ = π/3\n"
      "General cone z = k√(x²+y²) → tanφ = 1/k\n"
      "z = h (plane) → ρ = h secφ\n"
      "x²+y² = a² (cylinder) → ρ = a cscφ\n"
      "xy-plane → φ = π/2"),
  next="sph_region", next_label="Back to shapes")

N("sph_icecream", "Above cone, inside sphere", "15.8",
  body=(
      "Inside the cone (the part near the +z axis) ⇒ φ from 0 to the cone's angle φ0.\n"
      "Cone z = √(x²+y²): φ0 = π/4.\n"
      "Sphere centered at origin radius R: ρ 0→R.\n"
      "θ 0→2π."),
  formula="0≤ρ≤R, 0≤φ≤φ0, 0≤θ≤2π",
  warn="Outside/below the cone (but above xy-plane) is φ0 → π/2, not 0 → φ0.",
  next="sph_integrand")

N("sph_shifted", "Shifted sphere", "15.8",
  body=(
      "x²+y²+z² = 2az ⇒ ρ² = 2aρ cosφ ⇒ ρ = 2a cosφ.\n"
      "(Sphere radius a, center (0,0,a), touches origin.)\n"
      "ρ: 0 → 2a cosφ. Whole thing: φ 0→π/2.\n"
      "Inside sphere AND above cone z = √(x²+y²): φ 0→π/4.\n"
      "Inside sphere but OUTSIDE (below) that cone: φ π/4→π/2."),
  formula="0 ≤ ρ ≤ 2a cosφ",
  warn="The ρ bound depends on φ, so integrate ρ first.",
  next="sph_integrand")

N("sph_shell", "Spherical shell", "15.8",
  formula="R1 ≤ ρ ≤ R2",
  body="Then the φ, θ bounds of whatever piece is described.",
  next="sph_integrand")

N("sph_plane", "Plane z = h", "15.8",
  body=(
      "z = h ⇒ ρ cosφ = h ⇒ ρ = h secφ.\n"
      "Cone capped by plane (below z=h, above cone): ρ 0 → h secφ, φ 0 → φ0.\n"
      "Cap of sphere above z=h: ρ h secφ → R, φ 0 → arccos(h/R).\n"
      "(arccos from where plane meets sphere: R cosφ = h.)"),
  next="sph_integrand")

N("sph_from_cart", "Cartesian → spherical", "15.8",
  body=(
      "1. Identify the solid from the bounds:\n"
      "z from √(x²+y²) to √(R²−x²−y²) ⇒ ice-cream cone.\n"
      "z from 0 to √(R²−x²−y²) ⇒ upper half ball.\n"
      "2. Write spherical bounds.\n"
      "3. Convert integrand and multiply by ρ² sinφ."),
  next="sph_region", next_label="Choose solid")

N("sph_integrand", "Integrand & Jacobian", "15.8",
  body=(
      "x = ρ sinφ cosθ\ny = ρ sinφ sinθ\nz = ρ cosφ\n"
      "x²+y²+z² = ρ²;  √(x²+y²) = ρ sinφ\n"
      "Order dρ dφ dθ. If all bounds are constants, it splits into 3 single integrals."),
  formula="dV = ρ² sinφ dρ dφ dθ",
  warn="Don't forget ρ² sinφ. Don't swap φ (from z-axis) and θ (around).",
  next="sph_eval")

N("sph_eval", "Evaluate", "15.8",
  body=(
      "ρ integral: ∫ρ² dρ = ρ³/3, ∫ρ³ dρ = ρ⁴/4.\n"
      "If ρ bound is 2a cosφ: get (2a cosφ)³/3 · sinφ ⇒ u = cosφ.\n"
      "∫ cosⁿφ sinφ dφ = −cosⁿ⁺¹φ/(n+1).\n"
      "∫0→π sinφ dφ = 2;  ∫0→π/2 sinφ dφ = 1;\n"
      "∫0→π/4 sinφ dφ = 1 − √2/2.\n"
      "∫0→2π dθ = 2π.\n"
      "e^(x²+y²+z²) = e^(ρ²): with ρ² from dV, ∫ρ³e^(ρ²) dρ: u = ρ², then by parts."),
  choices=[("Find a centroid next", "solid_centroid"), ("Done → check", "final_check")])

# ---------------------------------------------------------------- mass & centroid
N("mass_menu", "Mass & centroid", "Mass",
  choices=[("2D lamina", "lamina_centroid"), ("3D solid", "solid_centroid")])

N("lamina_centroid", "Lamina centroid", "Mass",
  body=(
      "1. m = ∬ δ dA (uniform δ: use Area).\n"
      "2. M_y = ∬ x δ dA,  M_x = ∬ y δ dA.\n"
      "3. Same bounds for all three integrals.\n"
      "Symmetry: D symmetric across y-axis (and δ too) ⇒ x̄ = 0."),
  formula="x̄ = M_y / m,   ȳ = M_x / m",
  warn="M_y uses x (moment about the y-axis). Easy to swap.",
  next="shape2d", next_label="Set up bounds")

N("solid_centroid", "Solid centroid", "Mass",
  body=(
      "1. Symmetry: round around z-axis ⇒ x̄ = ȳ = 0. Only find z̄.\n"
      "2. m = ∭ δ dV (uniform: use volume V).\n"
      "3. M_xy = ∭ z δ dV. In spherical z = ρ cosφ ⇒ integrand ρ³ sinφ cosφ. In cylindrical z·r.\n"
      "4. z̄ = M_xy / m."),
  formula="z̄ = (1/m) ∭ z δ dV",
  warn="z̄ can't be 0 if the solid is entirely above the xy-plane. z̄ must be between the lowest and highest z of the solid.",
  choices=[
      ("Example: cone below sphere at origin", "centroid_ex2"),
      ("Example: cone in shifted sphere", "centroid_ex"),
      ("Set up bounds", "shape3d"),
  ])

N("centroid_ex", "Cone in shifted sphere", "Mass",
  body=(
      "Above z = √(x²+y²), inside x²+y²+z² = 2z.\n"
      "ρ: 0→2cosφ, φ: 0→π/4, θ: 0→2π.\n"
      "V = 2π ∫0→π/4 (8cos³φ/3) sinφ dφ\n"
      "  = 2π·(8/3)·¼(1 − ¼) = π\n"
      "M = 2π ∫0→π/4 (16cos⁴φ/4) cosφ sinφ dφ\n"
      "  = 2π·4·(1/6)(1 − 1/8) = 7π/6\n"
      "z̄ = 7/6, x̄ = ȳ = 0. (Solid spans z 0→2 ✓)"),
  next="final_check", next_label="Check answer")

# ---------------------------------------------------------------- 16.2 line integrals
N("line_start", "What's being integrated?", "16.2",
  body="Keywords decide it.",
  choices=[
      ("Scalar: ∫ f ds, arc length, wire density/mass", "scalar_line"),
      ("Vector: work, force, ∫ F·dr, ∫ P dx + Q dy", "work_start"),
      ("∫ f dx  or  ∫ f dy alone", "dx_line"),
      ("How do I parameterize?", "param"),
  ])

N("param", "Parameterize the path", "16.2", body=PARAM_BODY, warn=PARAM_WARN,
  next="final_check", next_label="Done")

N("scalar_line", "Scalar line ∫ f ds", "16.2",
  body=(
      "1. Parameterize r(t), a ≤ t ≤ b.\n"
      "2. r'(t).\n"
      "3. Speed |r'(t)| = √(x'² + y'² + z'²).\n"
      "4. Plug r(t) into f.\n"
      "5. ∫ f(r(t))·|r'(t)| dt.\n"
      "Mass of wire = ∫ δ ds. Length = ∫ 1 ds."),
  formula="∫C f ds = ∫a→b f(r(t)) |r'(t)| dt",
  warn="ds ≠ dt. Include the speed. Don't forget the density.",
  choices=[("Parameterization help", "param_scalar"), ("Example", "scalar_ex")])

N("param_scalar", "Parameterize the path", "16.2", body=PARAM_BODY, warn=PARAM_WARN, next="scalar_ex")

N("scalar_ex", "Example", "16.2",
  body=(
      "∫C (x + y) ds, segment (0,0)→(3,4).\n"
      "r = (3t, 4t), r' = (3,4), speed = 5.\n"
      "f = 3t + 4t = 7t.\n"
      "∫0→1 7t·5 dt = 35/2.\n"
      "Circle radius a: speed = a. Segment: speed = |B − A|."),
  next="final_check", next_label="Check answer")

N("work_start", "Work ∫ F·dr", "16.2",
  body="Before grinding, look for shortcuts.",
  choices=[
      ("Closed curve in the plane", "green_start"),
      ("P_y = Q_x (curl F = 0)? Check it", "cons_start"),
      ("Just compute directly", "work_direct"),
  ])

N("work_direct", "Direct computation", "16.2",
  body=(
      "1. Parameterize r(t) (start → end).\n"
      "2. r'(t).\n"
      "3. F(r(t)): plug x(t), y(t), z(t) into F.\n"
      "4. Dot product F(r(t))·r'(t). It's a scalar.\n"
      "5. Integrate in t.\n"
      "P dx + Q dy form: dx = x'(t) dt, dy = y'(t) dt."),
  formula="W = ∫a→b F(r(t)) · r'(t) dt",
  warn="Dot product, not magnitude. Reversing the path flips the sign.",
  choices=[("Parameterization help", "param_work"), ("Example", "work_ex")])

N("param_work", "Parameterize the path", "16.2", body=PARAM_BODY, warn=PARAM_WARN, next="work_ex")

N("work_ex", "Example", "16.2",
  body=(
      "F = ⟨x², xy⟩, segment (0,0) → (1,2).\n"
      "r = (t, 2t), r' = (1, 2).\n"
      "F(r(t)) = ⟨t², 2t²⟩.\n"
      "F·r' = t² + 4t² = 5t².\n"
      "W = ∫0→1 5t² dt = 5/3."),
  next="final_check", next_label="Check answer")

N("dx_line", "∫ f dx or ∫ f dy", "16.2",
  body="Parameterize, then dx = x'(t) dt (or dy = y'(t) dt). No speed factor.\nShortcut: ∫ g(x) dx alone depends only on the x-endpoints: = G(x_end) − G(x_start).",
  formula="∫C f dx = ∫a→b f(r(t)) x'(t) dt",
  next="param_dx")

N("param_dx", "Parameterize the path", "16.2", body=PARAM_BODY, warn=PARAM_WARN, next="final_check")

# ---------------------------------------------------------------- conservative
N("cons_start", "Conservative?", "16.3",
  choices=[("2D field ⟨P, Q⟩", "cons_2d"), ("3D field ⟨P, Q, R⟩", "cons_3d")])

N("cons_2d", "2D test", "16.3",
  body=(
      "Compute P_y and Q_x.\n"
      "Equal (on all of ℝ² or a simply connected domain) ⇒ conservative.\n"
      "Not equal ⇒ not conservative; line integrals depend on path."),
  formula="P_y = Q_x",
  warn="Watch domains with holes (e.g. F undefined at origin): equal partials there don't guarantee conservative.",
  choices=[("Equal → find potential", "potential2"), ("Not equal → compute directly", "work_direct")])

N("cons_3d", "3D test", "16.3",
  body="Check all three: P_y = Q_x, P_z = R_x, Q_z = R_y.\n(That's curl F = 0.)",
  formula="curl F = 0",
  choices=[("All equal → find potential", "potential3"), ("Some differ → compute directly", "work_direct")])

N("potential2", "Find f (2D)", "16.3",
  body=(
      "1. f = ∫ P dx + g(y).\n"
      "2. Differentiate: f_y = (stuff) + g'(y).\n"
      "3. Set f_y = Q. Solve for g'(y). It must have only y.\n"
      "4. Integrate g'. f is a SCALAR.\n"
      "Ex: F = ⟨2xy + 1, x² + 3y²⟩\n"
      "f = x²y + x + g(y); f_y = x² + g' = x² + 3y² ⇒ g = y³.\n"
      "f = x²y + x + y³. Check: ∇f = F."),
  warn="Don't forget g(y). Integrating P alone misses pure-y terms.",
  next="ftli")

N("potential3", "Find f (3D)", "16.3",
  body=(
      "1. f = ∫ P dx + g(y,z).\n"
      "2. f_y = Q ⇒ find g_y, integrate in y: g = … + h(z).\n"
      "3. f_z = R ⇒ find h'(z), integrate.\n"
      "Ex: F = ⟨y, x + z, y⟩: f = xy + g(y,z); f_y = x + g_y = x + z ⇒ g = yz + h(z); f_z = y + h' = y ⇒ h = 0. f = xy + yz."),
  next="ftli")

N("ftli", "Fundamental theorem", "16.3",
  body="Work = potential at the end minus potential at the start. Path doesn't matter.\nClosed curve ⇒ 0.",
  formula="∫C ∇f · dr = f(B) − f(A)",
  next="final_check", next_label="Check answer")

# ---------------------------------------------------------------- 16.4 Green
N("green_start", "Green's theorem?", "16.4",
  body="Green needs: closed, simple, plane curve, and P, Q smooth on the whole inside.",
  choices=[
      ("Closed, counterclockwise", "green_steps"),
      ("Closed, clockwise", "green_cw"),
      ("Not closed (open path)", "green_open"),
      ("Asked to verify: do it both ways", "green_both"),
  ])

N("green_cw", "Clockwise", "16.4",
  body="Positive orientation = CCW (region on your left). For clockwise, compute with Green and NEGATE.",
  next="green_steps")

N("green_open", "Open path", "16.4",
  body="Green doesn't apply directly. Options: compute directly, check if conservative, or close the path with a segment, use Green, then subtract the added segment's integral.",
  choices=[("Compute directly", "work_direct"), ("Check conservative", "cons_2d")])

N("green_steps", "Apply Green", "16.4",
  body=(
      "1. P = coefficient of dx, Q = coefficient of dy.\n"
      "2. Compute Q_x and P_y.\n"
      "3. Integrand Q_x − P_y.\n"
      "4. D = region inside C. Set up ∬D."),
  formula="∮C P dx + Q dy = ∬D (Q_x − P_y) dA",
  warn="It's Q_x − P_y (Q first). Reversing it flips the sign.",
  choices=[
      ("Q_x − P_y is a constant k", "green_const"),
      ("D is a disk / circle", "polar_region"),
      ("D is a triangle / polygon", "triangle_region"),
      ("D is a rectangle", "rect_eval"),
  ])

N("green_const", "Constant integrand", "16.4",
  body="∮ = k · Area(D).\nTriangle ½bh, disk πR², ellipse πab, rectangle lw.",
  warn="Use the actual region's area (triangle ≠ rectangle).",
  next="final_check", next_label="Check answer")

N("green_both", "Direct and Green", "16.4",
  body=(
      "Green side: ∬D (Q_x − P_y) dA.\n"
      "Direct side: for each edge, parameterize A + t(B−A) in the CCW order, compute ∫ (P x' + Q y') dt, sum all edges.\n"
      "The two answers must match. That's your check."),
  next="green_ex", next_label="Worked example")

N("green_ex", "Example", "16.4",
  body=(
      "∮ y² dx + 3xy dy, triangle (0,0)→(1,0)→(1,2)→(0,0).\n"
      "Green: Q_x − P_y = 3y − 2y = y.\n"
      "∫0→1 ∫0→2x y dy dx = ∫0→1 2x² dx = 2/3.\n"
      "Direct:\n"
      "Edge 1: y = 0 ⇒ 0.\n"
      "Edge 2: x=1, y=2t: ∫0→1 3·2t·2 dt = 6.\n"
      "Edge 3: (1−t, 2−2t): integrand −16(1−t)² ⇒ −16/3.\n"
      "Sum 6 − 16/3 = 2/3 ✓"),
  next="final_check", next_label="Check answer")

# ---------------------------------------------------------------- 16.5 operators
N("ops_start", "Which operator?", "16.5",
  choices=[
      ("Gradient ∇f", "op_grad"),
      ("Divergence ∇·F", "op_div"),
      ("Curl ∇×F", "op_curl"),
      ("Laplacian ∇²f", "op_lap"),
      ("Is this expression meaningful?", "op_types"),
      ("Identities: curl grad, div curl", "op_ident"),
      ("Position vector r and r = |r|", "op_rvec"),
  ])

N("op_grad", "Gradient", "16.5",
  body="Input: scalar f. Output: vector.\nPoints toward fastest increase of f.",
  formula="∇f = ⟨f_x, f_y, f_z⟩",
  next="final_check", next_label="Done")

N("op_div", "Divergence", "16.5",
  body="Input: vector F = ⟨P,Q,R⟩. Output: scalar.\n>0: net outflow (source). <0: inflow (sink). =0: incompressible.",
  formula="∇·F = P_x + Q_y + R_z",
  warn="Each component is differentiated by its OWN variable only.",
  next="final_check", next_label="Done")

N("op_curl", "Curl", "16.5",
  body=(
      "Input: vector. Output: vector.\n"
      "Cyclic pattern x→y→z→x:\n"
      "i: R_y − Q_z\n"
      "j: P_z − R_x\n"
      "k: Q_x − P_y\n"
      "(Determinant with rows i j k / ∂x ∂y ∂z / P Q R; the j term gets a minus.)\n"
      "curl F = 0 ⇒ irrotational. 2D field: curl = (Q_x − P_y) k."),
  formula="∇×F = ⟨R_y − Q_z, P_z − R_x, Q_x − P_y⟩",
  warn="Order matters in each component. Check the j component's sign.",
  next="final_check", next_label="Done")

N("op_lap", "Laplacian", "16.5",
  body="Input: scalar f. Output: scalar. It's div(grad f).\nNot always zero. (f with ∇²f = 0 is called harmonic.)",
  formula="∇²f = f_xx + f_yy + f_zz",
  next="final_check", next_label="Done")

N("op_types", "Meaningful?", "16.5",
  body=(
      "Work inside out, tracking scalar (S) or vector (V).\n"
      "grad: S→V   div: V→S   curl: V→V   ∇²: S→S\n"
      "OK: div(grad f), curl(grad f), grad(div F), div(curl F), curl(curl F)\n"
      "Meaningless: curl(div F) [curl of scalar], div(div F), grad(grad f), grad F (F vector), div f (f scalar)."),
  next="final_check", next_label="Done")

N("op_ident", "Identities", "16.5",
  body="(For f, F with continuous 2nd partials.)",
  formula="∇×(∇f) = 0\n∇·(∇×F) = 0\n∇·(∇f) = ∇²f",
  warn="curl of grad is the ZERO VECTOR; div of grad is the Laplacian (not 0 in general).",
  next="final_check", next_label="Done")

# ---------------------------------------------------------------- concepts
N("concept_start", "What kind of question?", "Concepts",
  choices=[
      ("Which sketch matches this integral?", "read_bounds"),
      ("Which integral gives this volume?", "concept_which_integral"),
      ("Sign of the integral / is it zero?", "concept_sign"),
      ("Vector field picture: div or curl sign", "concept_field"),
      ("Line integral sign from a picture", "concept_line_sign"),
      ("Which coordinate system?", "coord_choice"),
      ("Pick the integral for a pictured region", "concept_pick_region"),
      ("Pick the figure: field arrows on a curve", "concept_field_curve"),
  ])

N("concept_which_integral", "Match integral to solid", "Concepts",
  body=(
      "Check each candidate:\n"
      "1. Right Jacobian? (r for cyl/polar, ρ² sinφ for spherical, none for Cartesian.)\n"
      "2. Innermost bounds = floor/ceiling of the solid.\n"
      "3. Outer bounds = the shadow; edge where surfaces meet.\n"
      "4. Plug a test point to confirm top > bottom.\n"
      "5. Volume integrand should be 1 (times Jacobian)."),
  next="read_bounds3", next_label="Reading 3D bounds")

N("concept_sign", "Sign / symmetry", "Concepts",
  body=(
      "Integrand > 0 on all of D ⇒ integral > 0.\n"
      "Odd symmetry ⇒ 0: if D is symmetric across the y-axis and f(−x,y) = −f(x,y), ∬ f = 0. E.g. ∬ x dA over a disk = 0; ∬ x y² over a disk = 0.\n"
      "Same with y and the x-axis.\n"
      "For a picture: compare how much region is in f>0 vs f<0."),
  next="final_check", next_label="Done")

N("concept_field", "Reading a field plot", "Concepts",
  body=(
      "Divergence at a point: arrows point away / get longer as you move along the flow ⇒ positive. Arrows converge / shrink ⇒ negative.\n"
      "Curl (k-component): drop a paddle wheel. Spins CCW ⇒ positive, CW ⇒ negative. Arrows longer on one side than the other also means rotation.\n"
      "Uniform parallel arrows ⇒ div = 0 and curl = 0."),
  next="final_check", next_label="Done")

N("concept_line_sign", "Sign from a picture", "Concepts",
  body=(
      "Walk along C in its direction.\n"
      "F mostly WITH your motion ⇒ ∫F·dr > 0. Against ⇒ < 0. Perpendicular ⇒ ≈ 0.\n"
      "Closed loop with nonzero circulation ⇒ F not conservative.\n"
      "Scalar ∫ f ds ignores direction; sign comes from f only."),
  next="final_check", next_label="Done")

# ---------------------------------------------------------------- formula sheet
N("fs_menu", "Formula sheet", "Formulas",
  choices=[
      ("Coordinates & Jacobians", "fs_coords"),
      ("Area, volume, surface, centroid", "fs_geom"),
      ("Line integrals & Green", "fs_line"),
      ("grad / div / curl", "fs_ops"),
  ])

N("fs_coords", "Coordinates", "Formulas",
  formula=(
      "Polar: x=r cosθ, y=r sinθ\n  dA = r dr dθ\n"
      "Cyl: + z=z\n  dV = r dz dr dθ\n"
      "Sph: x=ρ sinφ cosθ\n  y=ρ sinφ sinθ\n  z=ρ cosφ\n  dV = ρ² sinφ dρ dφ dθ\n"
      "x²+y² = r² = ρ² sin²φ\nx²+y²+z² = ρ²"),
  next="fs_menu", next_label="Back")

N("fs_geom", "Geometry", "Formulas",
  formula=(
      "Area = ∬ 1 dA\nV = ∭ 1 dV = ∬ (top−bot) dA\n"
      "Surf = ∬ √(1+f_x²+f_y²) dA\n"
      "m = ∭ δ dV\n"
      "x̄ = ∭ xδ dV / m (same for ȳ, z̄)\n"
      "2D: x̄ = M_y/m, M_y = ∬ xδ dA\n"
      "avg f = ∬ f dA / Area"),
  next="fs_menu", next_label="Back")

N("fs_line", "Line integrals", "Formulas",
  formula=(
      "∫ f ds = ∫ f(r(t)) |r'(t)| dt\n"
      "∫ F·dr = ∫ F(r(t))·r'(t) dt\n"
      "Segment: r = A + t(B−A)\n"
      "∫ ∇f·dr = f(B) − f(A)\n"
      "2D conservative: P_y = Q_x\n"
      "Green: ∮ P dx + Q dy\n  = ∬ (Q_x − P_y) dA"),
  next="fs_menu", next_label="Back")

N("fs_ops", "Operators", "Formulas",
  formula=(
      "∇f = ⟨f_x, f_y, f_z⟩\n"
      "∇·F = P_x + Q_y + R_z\n"
      "∇×F = ⟨R_y−Q_z, P_z−R_x, Q_x−P_y⟩\n"
      "∇²f = f_xx + f_yy + f_zz\n"
      "∇×∇f = 0,  ∇·(∇×F) = 0"),
  next="fs_menu", next_label="Back")

# ---------------------------------------------------------------- toolkit
N("tk_menu", "Integration toolkit", "Toolkit",
  choices=[
      ("u-substitution", "tk_usub"),
      ("Trig powers (sin², cos²…)", "tk_trig"),
      ("Integration by parts", "tk_parts"),
      ("Standard definite values", "tk_values"),
  ])

N("tk_usub", "u-substitution", "Toolkit",
  body=(
      "Look for a function and its derivative (up to a constant).\n"
      "x·e^(x²): u = x², du = 2x dx ⇒ ½e^(x²)\n"
      "r√(1+4r²): u = 1+4r² ⇒ (1/12)(1+4r²)^(3/2)\n"
      "r·e^(−r²): ⇒ −½e^(−r²)\n"
      "cosⁿφ sinφ: u = cosφ ⇒ −cosⁿ⁺¹φ/(n+1)\n"
      "r/√(a²−r²): ⇒ −√(a²−r²)\n"
      "Change the bounds too, or back-substitute."),
  next="tk_menu", next_label="Back")

N("tk_trig", "Trig powers", "Toolkit",
  body=(
      "sin²θ = (1 − cos2θ)/2\n"
      "cos²θ = (1 + cos2θ)/2\n"
      "sinθ cosθ = ½ sin2θ\n"
      "∫0→2π sin²θ dθ = ∫0→2π cos²θ dθ = π\n"
      "∫0→π/2 sin²θ dθ = π/4\n"
      "Odd power: save one factor, convert the rest with sin² = 1 − cos², then u-sub."),
  next="tk_menu", next_label="Back")

N("tk_parts", "By parts", "Toolkit",
  body=(
      "∫u dv = uv − ∫v du.\n"
      "Pick u by LIATE: Log, Inverse trig, Algebraic, Trig, Exponential.\n"
      "∫ x e^x dx = (x − 1)e^x\n"
      "∫ x cos x dx = x sin x + cos x\n"
      "∫ ln x dx = x ln x − x"),
  next="tk_menu", next_label="Back")

N("tk_values", "Standard values", "Toolkit",
  body=(
      "∫0→π sinφ dφ = 2\n"
      "∫0→π/2 sinφ dφ = 1\n"
      "∫0→π/2 cosθ dθ = 1\n"
      "∫0→2π cosθ dθ = 0 = ∫0→2π sinθ dθ\n"
      "∫0→π/2 sin³φ dφ = 2/3  (sin³ = (1 − cos²)·sin, u = cos)\n"
      "∫ 1/(1+x²) = arctan x\n"
      "∫ 1/√(1−x²) = arcsin x\n"
      "cos(π/4) = sin(π/4) = √2/2\n"
      "cos(π/6) = √3/2, sin(π/6) = ½\n"
      "cos(π/3) = ½, sin(π/3) = √3/2"),
  next="tk_menu", next_label="Back")

# ---------------------------------------------------------------- finish
N("final_check", "Before you box it", "Check",
  body=(
      "☐ Jacobian: r (polar/cyl), ρ² sinφ (sph)\n"
      "☐ Bounds: lower < upper; outer bounds are numbers\n"
      "☐ Every term survived (upper) − (lower)\n"
      "☐ Volume, area, mass, length > 0\n"
      "☐ Orientation: CW or reversed path ⇒ flip sign\n"
      "☐ Green: Q_x − P_y, not P_y − Q_x\n"
      "☐ ds has the speed; dt doesn't\n"
      "☐ Centroid lies inside the solid\n"
      "☐ ½ for triangle area\n"
      "☐ Radians, not degrees"))



# ---------------------------------------------------------------- added from practice exam formats
N("exam_map", "Which question?", "Exam 3",
  choices=[
      ("Q1–11 Double integrals", "em_a"),
      ("Q12–17 Polar & surface area", "em_b"),
      ("Q18–24 Triple integrals", "em_c"),
      ("Q25–33 Cylindrical & spherical", "em_d"),
      ("Q34–40 Line ∫, Green, curl", "em_e"),
  ])

N("em_a", "Q1–11 Double integrals", "Exam 3",
  choices=[
      ("Q1–2 iterated ∫ (constant bounds)", "rect_eval"),
      ("Q3 cross-section areas, volume", "cross_section"),
      ("Q4 ∬√(R²−x²): geometry", "geom_volume"),
      ("Q5, Q11 reverse the order", "reverse_order"),
      ("Q6–9 Type I / Type II regions", "gen_setup"),
      ("Q10 volume under plane over region", "vol_between"),
  ])

N("em_b", "Q12–17 Polar & surface area", "Exam 3",
  choices=[
      ("Q12 pick polar ∫ for picture", "concept_pick_region"),
      ("Q13, Q15 polar evaluate / volume", "polar_region"),
      ("Q14 area inside r = g(θ)", "polar_curve_area"),
      ("Q16 Cartesian → polar", "polar_from_cart"),
      ("Q17 surface area of a plane", "sa_plane"),
  ])

N("em_c", "Q18–24 Triple integrals", "Exam 3",
  choices=[
      ("Q18, Q21, Q22 evaluate ∭", "triple_setup"),
      ("Q19, Q23 paraboloid x = a(y²+z²)", "cyl_other_axis"),
      ("Q20, Q24 orders of a ∭", "triple_reorder"),
  ])

N("em_d", "Q25–33 Cylindrical & spherical", "Exam 3",
  choices=[
      ("Q25, Q28 convert a point", "point_convert"),
      ("Q26, Q29 describe a solid", "describe_solid"),
      ("Q27 cylindrical ∭", "cyl_setup"),
      ("Q30 sphere & cone inequalities", "sph_shifted"),
      ("Q31 shell, set up spherical", "sph_shell"),
      ("Q32 spherical ∭ (first octant)", "sph_ball"),
      ("Q33 volume & centroid, cone/sphere", "solid_centroid"),
  ])

N("em_e", "Q34–40 Line ∫, Green, curl", "Exam 3",
  choices=[
      ("Q34 ∫ f dx along x = g(y)", "dx_line"),
      ("Q35, Q37 work ∫ F·dr", "work_direct"),
      ("Q36 work + pick the figure", "concept_field_curve"),
      ("Q38 Green: direct and theorem", "green_both"),
      ("Q39 curl & divergence", "op_curl"),
      ("Q40 ∇r, ∇(1/r), ∇ ln r", "op_rvec"),
  ])

N("cross_section", "Cross-section area", "15.1",
  body=(
      "Solid under z = f(x,y) over a rectangle.\n"
      "Slice perpendicular to the x-axis at x = k: area A(k) = ∫ f(k, y) dy over the y-range.\n"
      "Slice perpendicular to the y-axis at y = k: A(k) = ∫ f(x, k) dx over the x-range.\n"
      "Volume = ∫ A(x) dx = ∫ A(y) dy (same answer both ways).\n"
      "Ex: z = xy over [0,2]×[1,3]: A(x) = ∫1→3 xy dy = 4x; V = ∫0→2 4x dx = 8."),
  formula="A(x) = ∫c→d f(x,y) dy,   V = ∫a→b A(x) dx",
  warn="In A(x), x is a fixed number: only y is integrated.",
  next="final_check", next_label="Check answer")

N("geom_volume", "Integral as a volume", "15.1",
  body=(
      "If f ≥ 0 and the solid is a known shape, use geometry.\n"
      "z = √(R² − x²) ⇒ x² + z² = R², z ≥ 0: half of a circular cylinder of radius R lying along the y-axis.\n"
      "Volume = (½πR²) × (length along y).\n"
      "Ex: ∬ √(9 − y²) dA over [0,4]×[−3,3] = ½π(3²)·4 = 18π.\n"
      "Need the x-range to cover the whole −R to R, else it's only part of the half-disk."),
  formula="V = ½πR² · L",
  next="final_check", next_label="Check answer")

N("polar_curve_area", "Area inside r = g(θ)", "15.3",
  body=(
      "r from 0 to the curve g(θ); θ over the sweep that traces the region once.\n"
      "Inner integral ∫0→g r dr = ½g(θ)².\n"
      "Read θ-limits from the picture: where does the curve start and end? (e.g. a spiral r = √θ starts at the origin at θ = 0.)\n"
      "Ex: cardioid r = 1 + cosθ, θ 0→2π: A = ½∫(1+cosθ)² dθ = 3π/2."),
  formula="A = ∫α→β ∫0→g(θ) r dr dθ = ∫α→β ½ g(θ)² dθ",
  next="final_check", next_label="Check answer")

N("cyl_other_axis", "Round around x-axis", "15.7",
  body=(
      "x = a(y² + z²) is a paraboloid opening along the x-axis.\n"
      "Use polar in the yz-plane: y = r cosθ, z = r sinθ, y²+z² = r².\n"
      "x: from a r² up to the plane x = c.\n"
      "Edge: a r² = c ⇒ r = √(c/a). θ: 0 → 2π.\n"
      "dV = r dx dr dθ.\n"
      "Ex: ∭ x dV, x = y²+z², x = 1:\n"
      "∫0→2π ∫0→1 ∫r²→1 x·r dx dr dθ = π/3."),
  formula="∫0→2π ∫0→√(c/a) ∫ar²→c f · r dx dr dθ",
  warn="Integrand x stays x (it's the axis variable). Only y, z become r, θ.",
  next="eval_iter")

N("six_orders", "All six orders", "15.6",
  body=(
      "Solid: y = x², z = 0, y + 2z = 4.\n"
      "Ranges: y 0→4, x ±√y, z 0→(4−y)/2.\n"
      "dz dy dx: x −2→2, y x²→4, z 0→(4−y)/2\n"
      "dz dx dy: y 0→4, x −√y→√y, z 0→(4−y)/2\n"
      "dx dz dy: y 0→4, z 0→(4−y)/2, x −√y→√y\n"
      "dx dy dz: z 0→2, y 0→4−2z, x −√y→√y\n"
      "dy dz dx: x −2→2, z 0→(4−x²)/2, y x²→4−2z\n"
      "dy dx dz: z 0→2, x ±√(4−2z), y x²→4−2z\n"
      "Shadows: xy under y=4; yz triangle; xz under z=(4−x²)/2."),
  warn="Eliminate the inner variable to get the shadow: set y = x² into y + 2z = 4 ⇒ z = (4 − x²)/2.",
  next="final_check", next_label="Done")

N("point_convert", "Convert a point", "15.7/15.8",
  body=(
      "Cylindrical (r, θ, z):\nx = r cosθ, y = r sinθ, z = z.\n"
      "Ex: (2, π/3, 1) → (1, √3, 1).\n\n"
      "Spherical, WebAssign/Stewart order (ρ, θ, φ):\nx = ρ sinφ cosθ, y = ρ sinφ sinθ, z = ρ cosφ.\n"
      "Ex: (4, π/2, π/3) → (0, 2√3, 2).\n\n"
      "Back to cyl: r = √(x²+y²), tanθ = y/x (check quadrant).\n"
      "Back to sph: ρ = √(x²+y²+z²), cosφ = z/ρ."),
  warn="Spherical points are written (ρ, θ, φ): θ is SECOND. φ = π/2 means z = 0.",
  next="final_check", next_label="Done")

N("describe_solid", "Describe a solid", "15.7/15.8",
  body=(
      "θ range → which x, y signs:\n"
      "0→π/2: x ≥ 0, y ≥ 0.  0→π: y ≥ 0, x any sign.\n"
      "−π/2→π/2: x ≥ 0.\n"
      "z sign: r ≤ z or 0 ≤ φ ≤ π/2 ⇒ z ≥ 0.\n"
      "Top / bottom surfaces:\n"
      "z = c plane;  z = r cone;  ρ = c sphere;  φ = c cone (c < π/2 opens up).\n"
      "Slice in the xz-plane: set θ = 0 (and θ = π for x < 0). yz-plane: θ = π/2. Draw the 2D shape you get (triangle, sector, quarter-disk…)."),
  warn="ρ ≤ c with φ ≤ φ0: top is part of a SPHERE, bottom part of a CONE.",
  next="final_check", next_label="Done")

N("centroid_ex2", "Cone below origin sphere", "Mass",
  body=(
      "Above z = √(x²+y²), below x²+y²+z² = R². Ex R = 2.\n"
      "ρ 0→R, φ 0→π/4, θ 0→2π.\n"
      "V = 2π·(R³/3)·(1 − √2/2)\n"
      "  R=2: (16π/3)(1 − √2/2)\n"
      "M = 2π·(R⁴/4)·∫0→π/4 sinφcosφ dφ = 2π·(R⁴/4)·(1/4)\n"
      "  R=2: 2π\n"
      "z̄ = M/V; x̄ = ȳ = 0.\n"
      "R=2: z̄ = 3/(8(1 − √2/2)) ≈ 1.28"),
  next="final_check", next_label="Check answer")

N("concept_pick_region", "Pick integral for a picture", "Concepts",
  body=(
      "1. Round edges centered at origin ⇒ polar.\n"
      "2. Read r: 0 to the radius. Read θ: from the start ray to the end ray, going counterclockwise (can start negative, e.g. −π/4 → 3π/4).\n"
      "3. Correct answer must have f(r cosθ, r sinθ) AND the extra r.\n"
      "Reject: f(r,θ) without conversion, missing r, or Cartesian bounds that don't match the picture."),
  choices=[("Angle reference", "polar_angles"), ("Done", "final_check")])

N("concept_field_curve", "Field arrows on a curve", "Concepts",
  body=(
      "1. Curve shape: plot r(t) at t = 0, ½, 1 and compare. Ex (t³, t²): at t = ½ the point is (0.125, 0.25), so y > x early and the curve leaves the origin steeply.\n"
      "2. For each listed t: point = r(t), arrow = F at that point.\n"
      "3. Arrow direction: slope = F_y/F_x. Compare to the pictures.\n"
      "4. Arrow length grows with |F|."),
  warn="The arrow is F at the point, not the tangent r'(t).",
  next="work_direct", next_label="Part (a): work")

N("op_rvec", "r = ⟨x,y,z⟩, r = |r|", "16.5",
  body=(
      "∇r = r/r   (unit radial vector)\n"
      "∇×r = 0\n"
      "∇·r = 3\n"
      "∇(1/r) = −r/r³\n"
      "∇(ln r) = r/r²\n"
      "General: ∇(g(r)) = g'(r)·r/r\n"
      "So ∇(rⁿ) = n rⁿ⁻² r."),
  warn="Bold r is the vector, plain r is its length. ∇ of a scalar gives a vector: answers must be vectors.",
  next="final_check", next_label="Done")

# ---------------------------------------------------------------- validate + write
def validate():
    errors = []
    for nid, n in NODES.items():
        targets = [c["next"] for c in n.get("choices", [])]
        if "next" in n:
            targets.append(n["next"])
        if n.get("choices") and "next" in n:
            errors.append(f"{nid}: has both choices and next")
        for t in targets:
            if t not in NODES:
                errors.append(f"{nid}: links to missing node '{t}'")
        if not any(n.get(k) for k in ("body", "steps", "formula", "choices")):
            errors.append(f"{nid}: empty screen")
        for field in ("body", "formula", "warn", "steps", "outro"):
            text = "\n".join(n.get(field) or []) if field == "steps" else (n.get(field) or "")
            if "*" in text or "\\" in text:
                errors.append(f"{nid}.{field}: contains '*' or backslash")
    # reachability
    seen, stack = set(), ["root"]
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        n = NODES[cur]
        stack += [c["next"] for c in n.get("choices", [])]
        if "next" in n:
            stack.append(n["next"])
    for nid in NODES:
        if nid not in seen:
            errors.append(f"{nid}: unreachable from root")
    ends = [nid for nid, n in NODES.items() if not n.get("choices") and "next" not in n]
    return errors, ends


if __name__ == "__main__":
    errs, ends = validate()
    if errs:
        print("\n".join(errs))
        sys.exit(1)
    out = os.path.join(os.path.dirname(__file__), "..", "Calc3Tutor", "tutor.json")
    graph = {"root": "root", "nodes": [NODES[i] for i in ORDER]}
    with open(out, "w", encoding="utf-8") as f:
        json.dump(graph, f, ensure_ascii=False, indent=1)
        f.write("\n")
    stepped = [n for n in NODES.values() if "steps" in n]
    print(f"{len(stepped)} screens are step-by-step")
    longest = max(NODES.values(), key=lambda n: len(n.get("body", "")))
    print(f"OK: {len(NODES)} screens, finish screens: {ends}")
    print(f"longest body: {longest['id']} ({len(longest['body'])} chars)")
