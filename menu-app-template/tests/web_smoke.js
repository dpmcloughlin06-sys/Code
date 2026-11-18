// Browser smoke test for renderers/web (needs Node + Playwright with Chromium).
//   node tests/web_smoke.js
// Exports a standalone HTML app, opens it, clicks into the first choice,
// checks the rendering order, then uses Back and Home.
const { chromium } = require("playwright");
const { execFileSync } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

const root = path.join(__dirname, "..");
const tree = JSON.parse(fs.readFileSync(path.join(root, "content", "tree.json"), "utf8"));
const byId = Object.fromEntries(tree.nodes.map((n) => [n.id, n]));
const out = path.join(fs.mkdtempSync(path.join(os.tmpdir(), "menu-")), "app.html");
execFileSync("python3", [path.join(root, "tools", "menutree.py"), "export-web",
                         path.join(root, "content", "tree.json"), out]);

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 390, height: 800 } });
  const errors = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("file://" + out);

  const fail = (m) => { console.error("FAIL " + m); process.exitCode = 1; };
  // Navigation re-renders on the async hashchange event, so wait for the title.
  const expectTitle = (t, what) => page
    .waitForFunction((x) => document.querySelector("h1")?.textContent === x, t, { timeout: 3000 })
    .catch(() => fail(what));
  const rootNode = byId[tree.root];

  await expectTitle(rootNode.title, "root title");
  const choice = rootNode.choices[0];
  await page.click(`nav.choices a >> nth=0`);
  const target = byId[choice.next];
  await expectTitle(target.title, "navigate to first choice");

  // Order: h1, highlight, body, steps, caution, choices/home.
  const order = await page.$$eval("main > *", (els) => els.map((e) => e.className || e.tagName.toLowerCase()));
  const want = ["h1", target.highlight && "highlight", target.body && "body", target.steps && "steps",
                target.caution && "caution"].filter(Boolean);
  const got = order.filter((c) => want.some((w) => c.split(" ").includes(w) || c === w));
  if (JSON.stringify(got.map((c) => want.find((w) => c.split(" ").includes(w) || c === w))) !== JSON.stringify(want))
    fail(`render order ${JSON.stringify(order)}`);

  await page.click("header button:has-text('Back')");
  await expectTitle(rootNode.title, "back");
  await page.click(`nav.choices a >> nth=0`);
  await expectTitle(target.title, "navigate again");
  await page.click("header button:has-text('Home')");
  await expectTitle(rootNode.title, "home");
  if (errors.length) fail("page errors: " + errors.join("; "));

  await page.screenshot({ path: path.join(path.dirname(out), "smoke.png") });
  await browser.close();
  console.log(process.exitCode ? "web smoke FAILED" : "web smoke PASSED");
})();
