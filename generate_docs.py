"""P1: Generate test folders with 10, 100 and 1000 files for the benchmark.

Usage: python generate_docs.py
Creates generated_docs/docs_10, docs_100, docs_1000.
Document i is about topic (i % 5), so we know which files are relevant to a topic.
"""
import os
import random

TOPICS = {
    "energy":  "solar wind turbine battery electricity renewable panel power grid",
    "cooking": "bread flour oven dough sugar butter recipe sauce bake garlic",
    "sports":  "football cricket match goal team runner race score player coach",
    "space":   "rocket orbit planet telescope galaxy satellite mars moon launch star",
    "health":  "doctor vaccine diet exercise patient medicine hospital virus heart water",
}
COMMON = "the a of and to in is it for on with was are this that".split()
SIZES = [10, 100, 1000]


def make_folder(size, base="generated_docs"):
    random.seed(42)                              # same files every time
    folder = os.path.join(base, f"docs_{size}")
    os.makedirs(folder, exist_ok=True)
    names = list(TOPICS)
    for i in range(size):
        topic = names[i % len(names)]
        topic_words = TOPICS[topic].split()
        words = []
        for _ in range(random.randint(30, 120)):
            if random.random() < 0.3:
                words.append(random.choice(topic_words))   # topic word
            else:
                words.append(random.choice(COMMON))        # filler word
        with open(os.path.join(folder, f"doc_{i:04d}_{topic}.txt"), "w") as f:
            f.write(" ".join(words))
    print(f"Created {size} files in {folder}")


if __name__ == "__main__":
    for size in SIZES:
        make_folder(size)
