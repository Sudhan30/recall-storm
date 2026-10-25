"""Real captures of the project viewer, frame by frame (deterministic, 30 fps).

Runs with a separate Python that has Playwright (not the project .venv), e.g.
  <scratch>/pwvenv/bin/python videos/capture_viewer.py --url http://localhost:8001/viewer/ --out videos/raw/cap [scene ...]

The viewer is driven exactly as a presenter would (keys 1-5, Space, clicks, mouse drags). Playwright's fake
clock advances requestAnimationFrame/performance.now by 1/30 s per frame, so the replay runs at its real
speed setting regardless of how fast headless WebGL renders. Nothing in the page is modified.
Each scene becomes <out>/<scene>.mp4 (1920x1080, 30 fps) plus element stills (*.png).
"""
import argparse, asyncio, pathlib, shutil, subprocess
from playwright.async_api import async_playwright

FFMPEG = "/opt/homebrew/bin/ffmpeg"
FPS = 30


class Rec:
    def __init__(self, pg, out, name):
        self.pg, self.dir, self.name, self.n = pg, out / f"_frames_{name}", name, 0
        shutil.rmtree(self.dir, ignore_errors=True); self.dir.mkdir(parents=True)

    async def frames(self, n, each=None):
        for i in range(n):
            if each:
                await each(i)
            await self.pg.clock.run_for(33 if self.n % 3 else 34)
            await self.pg.screenshot(path=str(self.dir / f"{self.n:05d}.jpg"), type="jpeg", quality=92)
            self.n += 1

    def encode(self, out):
        subprocess.run([FFMPEG, "-v", "error", "-y", "-framerate", str(FPS), "-i", str(self.dir / "%05d.jpg"),
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", str(out / f"{self.name}.mp4")],
                       check=True)
        shutil.rmtree(self.dir)
        print(self.name, self.n, "frames")


async def boot(p, url):
    b = await p.chromium.launch(args=["--use-angle=metal", "--enable-gpu", "--ignore-gpu-blocklist"])
    ctx = await b.new_context(viewport={"width": 1920, "height": 1080})
    pg = await ctx.new_page()
    await pg.clock.install()
    await pg.goto(url)
    for _ in range(20):                      # let fetches resolve and the first frames draw
        await pg.wait_for_timeout(250)
        await pg.clock.run_for(100)
    await pg.uncheck("#autoref")
    return b, pg


async def key(pg, k):
    await pg.evaluate("document.activeElement && document.activeElement.blur()")
    await pg.keyboard.press(k)


async def dot_center(pg, sid):
    return await pg.evaluate("""(sid) => { const c = document.querySelector(`circle.store[data-id="${sid}"]`);
        const r = c.getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2]; }""", sid)


async def scene_map(pg, out):
    """Tab 1: core_patched replay in 20 s, all 20 dots go grey -> amber -> green; then click a Supercenter."""
    await key(pg, "1")
    await pg.select_option("#speed", "20")
    await pg.click("#restart")
    r = Rec(pg, out, "map_replay")
    await r.frames(30)
    await key(pg, " ")
    await r.frames(21 * FPS)
    x, y = await dot_center(pg, "WM1563")
    await pg.mouse.move(x - 200, y - 120)
    async def glide(i):
        f = min(1, (i + 1) / 30)
        await pg.mouse.move(x - 200 * (1 - f), y - 120 * (1 - f))
    await r.frames(50, glide)
    r.encode(out)
    await pg.screenshot(path=str(out / "map_done.png"))


async def scene_store(pg, out):
    """Tab 2: WM1563 Supercenter in 3D, replay playing, tags flashing, associates walking; slow orbit."""
    x, y = await dot_center(pg, "WM1563")
    await key(pg, "1")
    await pg.mouse.click(x, y)               # map click opens the 3D store (tab 2)
    await pg.clock.run_for(500)
    await pg.select_option("#speed", "45")
    await pg.click("#restart")
    await pg.click("#viewbtn")               # follow associates
    await pg.clock.run_for(200)
    await key(pg, " ")
    r = Rec(pg, out, "store3d")
    await r.frames(4 * FPS)
    box = await pg.locator("#store3d").bounding_box()
    cx, cy = box["x"] + box["width"] * 0.5, box["y"] + box["height"] * 0.55
    await pg.mouse.move(cx, cy); await pg.mouse.down()
    async def orbit(i):
        await pg.mouse.move(cx + i * 2.2, cy - i * 0.25)
    await r.frames(6 * FPS, orbit)
    await pg.mouse.up()
    await r.frames(2 * FPS)
    await pg.click("#viewbtn")               # whole store
    await r.frames(5 * FPS)
    r.encode(out)
    await pg.screenshot(path=str(out / "store3d.png"))


async def scene_cards(pg, out):
    """Evidence: demo trio -> three cards as element stills."""
    await key(pg, "2")
    await pg.click("#trio")
    await pg.clock.run_for(300)
    cards = pg.locator("#cards > .card")
    n = await cards.count()
    for i in range(min(3, n)):
        await cards.nth(i).scroll_into_view_if_needed()
        await cards.nth(i).screenshot(path=str(out / f"card{i + 1}.png"))
    print("cards", n)


async def scene_verifier(pg, out):
    await key(pg, "5")
    await pg.clock.run_for(500)
    await pg.screenshot(path=str(out / "verifier.png"))
    vc = pg.locator("#vcards > *")
    for i in range(min(8, await vc.count())):
        await vc.nth(i).screenshot(path=str(out / f"vcard{i + 1}.png"))


async def scene_hops(pg, out):
    await key(pg, "3")
    await pg.select_option("#runsel", "live:expansion")
    await pg.clock.run_for(800)
    await pg.screenshot(path=str(out / "hops_expansion.png"))
    seams = pg.locator("#seams > *")
    for i in range(await seams.count()):
        await seams.nth(i).screenshot(path=str(out / f"seam{i + 1}.png"))


async def scene_code(pg, out):
    await key(pg, "4")
    await pg.select_option("#codesel", "live:expansion")
    await pg.clock.run_for(800)
    await pg.screenshot(path=str(out / "codewall_expansion.png"))
    r = Rec(pg, out, "codewall")
    await r.frames(20)
    await pg.click("#longest")
    await r.frames(4 * FPS)
    r.encode(out)
    await pg.screenshot(path=str(out / "codewall_longest.png"))


async def scene_gallery(pg, out):
    await key(pg, "5")
    await pg.select_option("#failsel", "live:expansion")
    await pg.clock.run_for(800)
    g = pg.locator("#gallery")
    await g.scroll_into_view_if_needed()
    await g.screenshot(path=str(out / "gallery_expansion.png"))


SCENES = {"map": scene_map, "store": scene_store, "cards": scene_cards, "verifier": scene_verifier,
          "hops": scene_hops, "code": scene_code, "gallery": scene_gallery}


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:8001/viewer/")
    ap.add_argument("--out", default="videos/raw/cap")
    ap.add_argument("scenes", nargs="*")
    a = ap.parse_args()
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        for s in a.scenes or list(SCENES):
            b, pg = await boot(p, a.url)
            try:
                await SCENES[s](pg, out)
            finally:
                await b.close()

asyncio.run(main())
