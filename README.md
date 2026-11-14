# Five Pins on a Map

An illustrated world-map infographic summing up the world news of
Friday 13 November 2026 in a single image, for make.fun's
news-image-01.

Five glowing pins carry the day: a chip over North America
(Nvidia chief executive Jensen Huang resigns; Microsoft 365
outage), a dove over Europe (Europe wins a seat at the Ukraine
peace talks), a tanker over the Middle East (Iran says it hit a
US radar in Bahrain; tankers struck in Hormuz), a fleet over the
western Pacific (Taiwan details China's unannounced naval
drills), and a crowd over South America (Pope Leo greets record
crowds in Peru). A caption strip names each pin's story.

## Run

    python3 main.py

Writes the validated picture to `$MAKEFUN_OUTPUT_DIR/entry.png`
(default `./output/entry.png`). The program checks the bundled
`image.png` against the competition rules (PNG/JPEG, ≤ 1 MiB,
≤ 1024×1024) and copies it byte for byte.
