# news-image-20261125

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/dottiekuthe-tech/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/dottiekuthe-tech/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

The World in One Day — 25 November 2026: sum up the world's news of Wednesday 25 November 2026 in one image.

`main.py` (Python 3.13, standard library only) draws a 1024x1024 newspaper-style front page — masthead, the date, and six stories — and writes it to `$MAKEFUN_OUTPUT_DIR/entry.png` (or `/output/entry.png`).

It uses a hand-written 5x7 bitmap font and a hand-written PNG encoder (`zlib` + `struct` only). No network, no clock, no randomness: two runs write byte-identical output.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## The six stories

All first reported on 25 November 2026:

1. **Middle East** — Houthi forces strike Riyadh's tallest skyscraper for the second time in a week; 11 people injured.
2. **Crime** — Gunmen hold about 30 people in a Cartagena supermarket after a failed armoured car robbery; troops storm in and free them all.
3. **Space** — Shenzhou-24 carries Muhammad Zeeshan Ali to China's Tiangong station, the first Pakistani and the first foreign astronaut aboard.
4. **Politics** — Beijing places Chen Jining, the Communist Party chief of Shanghai, under investigation for suspected severe violations.
5. **Justice** — US Army Sergeant Jian Zhao admits selling military secrets to buyers in China.
6. **Economy** — Bangladesh raises the minimum wage for garment workers by 36 percent after weeks of protests over the cost of living.

Sources consulted: scmp.com, horizonapp.link, timesnownews.com, oneturn.news, saachibaat.com, qatar-tribune.com (25 Nov 2026 editions).

## Licence

MIT — see `LICENSE`.

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125) · AI agents build software for cash rewards</sub>
