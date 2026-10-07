// Point d'entrée UNIQUE des bundles web-demo/vendor/js-tiktoken-*.min.js
// (voir README.md de ce dossier pour les commandes). esbuild le paramètre :
//   --alias:aac-ranks=js-tiktoken/ranks/<encodage>   (le vocabulaire à embarquer)
//   --define:ENCODING_NAME='"<encodage>"'            (son nom)
import { Tiktoken } from "js-tiktoken/lite";
import ranks from "aac-ranks";

// Registre commun à tous les bundles chargés dans la page : chaque bundle y
// déclare son encodage. Le vocabulaire n'est analysé qu'au premier get().
const registry = (window.AACTiktoken = window.AACTiktoken || {
  factories: {},
  cache: {},
  get(name) {
    if (!this.factories[name]) throw new Error("Encodage non chargé : " + name);
    return this.cache[name] || (this.cache[name] = this.factories[name]());
  },
});
registry.factories[ENCODING_NAME] = () => new Tiktoken(ranks);
