#!/usr/bin/env python3
"""Ajoute (ou remplace) les quiz d'un chapitre dans le catalogue intégré de Cartes-réponses.

Usage :
  python3 outils/ajouter_chapitre.py --niveau 10e --num 5 --nom "Puissances et racines" quiz.json
  python3 outils/ajouter_chapitre.py --lire quiz/10e/ch5-puissances-et-racines.dat   (pour relire un fichier)

Le fichier quiz.json contient {"sets": {"<id>": {"title": "...", "order": 1,
  "questions": [{"q": "...", "c": ["A", "B", "C", "D"], "a": 0, "e": "explication"}]}}}
(c'est aussi le format d'« Importer des séries » et des copies de l'application).
Règles vérifiées : 4 réponses non vides, a entre 0 et 3, 7 questions au maximum par quiz.
Les réponses sont brouillées dans le fichier publié (dissuasion, pas un vrai chiffrement).
"""
import argparse, base64, json, os, re, sys, unicodedata

KEY = b"cartes-reponses/quiz"
MAXQ = 7
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = os.path.join(ROOT, "quiz", "catalogue.json")

def scramble(obj):
    raw = json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return base64.b64encode(bytes(b ^ KEY[i % len(KEY)] for i, b in enumerate(raw))).decode("ascii")

def unscramble(txt):
    raw = base64.b64decode(txt.strip())
    return json.loads(bytes(b ^ KEY[i % len(KEY)] for i, b in enumerate(raw)).decode("utf-8"))

def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")

def check(sets):
    errs = []
    for sid, st in sets.items():
        qs = st.get("questions") or []
        t = st.get("title") or sid
        if not qs: errs.append(f"{t} : aucune question")
        if len(qs) > MAXQ: errs.append(f"{t} : {len(qs)} questions (7 au maximum)")
        for i, q in enumerate(qs, 1):
            c = q.get("c") or []
            if not str(q.get("q", "")).strip(): errs.append(f"{t} Q{i} : énoncé vide")
            if len(c) != 4 or any(not str(x).strip() for x in c): errs.append(f"{t} Q{i} : il faut 4 réponses non vides")
            if q.get("a") not in (0, 1, 2, 3): errs.append(f"{t} Q{i} : bonne réponse invalide")
    return errs

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fichier", nargs="?")
    ap.add_argument("--niveau"); ap.add_argument("--num", type=int); ap.add_argument("--nom")
    ap.add_argument("--lire")
    a = ap.parse_args()
    if a.lire:
        print(json.dumps(unscramble(open(a.lire, encoding="ascii").read()), ensure_ascii=False, indent=1)); return
    if not (a.fichier and a.niveau and a.nom):
        ap.error("il faut le fichier, --niveau et --nom")
    src = json.load(open(a.fichier, encoding="utf-8"))
    sets = {k: {"title": v["title"], "order": v.get("order", i + 1), "questions": v["questions"]}
            for i, (k, v) in enumerate((src.get("sets") or src).items())}
    errs = check(sets)
    if errs:
        print("Fichier refusé :\n  " + "\n  ".join(errs)); sys.exit(1)
    chap_id = f"{slug(a.niveau)}-ch{a.num}-{slug(a.nom)}" if a.num else f"{slug(a.niveau)}-{slug(a.nom)}"
    rel = f"quiz/{slug(a.niveau)}/{chap_id[len(slug(a.niveau))+1:]}.dat"
    os.makedirs(os.path.join(ROOT, os.path.dirname(rel)), exist_ok=True)
    open(os.path.join(ROOT, rel), "w", encoding="ascii").write(scramble({"sets": sets}) + "\n")
    cat = json.load(open(CAT, encoding="utf-8")) if os.path.exists(CAT) else {"version": 1, "niveaux": []}
    niv = next((n for n in cat["niveaux"] if n["id"] == slug(a.niveau)), None)
    if not niv:
        niv = {"id": slug(a.niveau), "nom": a.niveau, "chapitres": []}; cat["niveaux"].append(niv)
    niv["chapitres"] = [c for c in niv["chapitres"] if c["id"] != chap_id]
    niv["chapitres"].append({"id": chap_id, "num": a.num, "nom": a.nom, "fichier": rel, "quiz": len(sets)})
    niv["chapitres"].sort(key=lambda c: (c.get("num") or 999, c["nom"]))
    cat["niveaux"].sort(key=lambda n: n["nom"])
    json.dump(cat, open(CAT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"OK : {len(sets)} quiz → {rel} ; catalogue mis à jour ({a.niveau}, chapitre {a.num or '-'} : {a.nom})")

if __name__ == "__main__":
    main()
