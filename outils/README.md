# Ajouter les quiz d'un chapitre à Cartes-réponses

Les quiz intégrés sont rangés dans `quiz/` :

- `quiz/catalogue.json` : la liste des niveaux et des chapitres (lisible) ;
- `quiz/<niveau>/ch<N>-<nom>.dat` : les quiz d'un chapitre, réponses brouillées.

L'application les charge au démarrage. Dans l'onglet **Projeter**, on choisit
Niveau → Chapitre → Quiz. Ils sont en lecture seule (bouton « Copier dans Mes séries » pour en modifier un).

## Format d'entrée

Un fichier JSON au format des séries de l'application :

```json
{"sets": {"set-<chapitre>-q1": {"title": "Quiz 1 – Titre", "order": 1,
  "questions": [{"q": "Énoncé", "c": ["A", "B", "C", "D"], "a": 2, "e": "Explication"}]}}}
```

Règles : **7 questions au maximum par quiz**, 4 réponses non vides, `a` = index de la bonne
réponse (0 = A … 3 = D), place de la bonne réponse variée, commencer par les bases et finir
par les cas spéciaux, explication pour chaque question. Écriture : `2^5`, `10^{-3}`, `10^n`
pour les exposants, `[3/4]` pour une fraction superposée.

## Ajouter ou remplacer un chapitre

```bash
python3 outils/ajouter_chapitre.py --niveau 10e --num 5 --nom "Puissances et racines" quiz.json
git add quiz && git commit -m "Quiz : 10e ch. 5 Puissances et racines" && git push
```

Le script refuse un fichier qui ne respecte pas les règles. Relancer avec le même niveau,
le même numéro et le même nom remplace le chapitre. Pour relire un fichier publié :
`python3 outils/ajouter_chapitre.py --lire quiz/10e/ch5-puissances-et-racines.dat`.

Après le `git push`, GitHub Pages met environ une minute à publier.

## Confidentialité

Le dépôt est public. Les réponses sont brouillées et l'application demande un code
enseignant : c'est une dissuasion, pas un vrai chiffrement. Ne jamais mettre de prénoms
ni de résultats d'élèves dans ce dépôt.
