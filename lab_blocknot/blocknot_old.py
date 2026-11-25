# блокнот Барахольщика, "оцифрував" племінник у 2019
rich = []  # (назва, категорія, к-сть, ціна, стан, де лежить)


def load(f):
    for l in open(f, encoding="utf-8"):
        x = l.strip().split(";")
        rich.append((x[0], x[1], int(x[2]), float(x[3]), x[4], x[5]))


def add(n, c, q, v, s, loc):
    rich.append((n, c, q, v, s, loc))


def zvit(f):
    load(f)
    vsoho = 0
    for r in rich:
        if r[4] == "зламаний":
            vsoho += r[2] * r[3] * 0.2
        elif r[4] == "уживаний":
            vsoho += r[2] * r[3] * 0.7
        else:
            vsoho += r[2] * r[3]
    print("Барахла:", len(rich))
    for r in sorted(rich, key=lambda t: t[5]):
        if r[4] == "зламаний":
            s = r[2] * r[3] * 0.2
        elif r[4] == "уживаний":
            s = r[2] * r[3] * 0.7
        else:
            s = r[2] * r[3]
        print(r[5], "|", r[0], "|", r[2], "шт |", round(s, 2))
    print("Разом:", round(vsoho, 2))


if __name__ == "__main__":
    zvit("barakhlo.csv")
