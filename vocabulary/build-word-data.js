const fs = require('fs');

const dictionary = JSON.parse(fs.readFileSync('dictionary-source.json', 'utf8'));
const categoryFor = level => {
  if (level <= 2) return 'BASIC';
  if (level <= 5) return 'DAILY';
  if (level <= 8) return 'ACADEMIC';
  return 'ADVANCED';
};

const words = Object.entries(dictionary)
  .filter(([word, data]) => /^[a-z]+(?:-[a-z]+)?$/.test(word) && word.length > 1 && data.ja?.length)
  .sort((a, b) => a[1].rank - b[1].rank)
  .slice(0, 2000)
  .map(([word, data]) => ({
    word,
    meaning: data.ja.slice(0, 3).join('、'),
    category: categoryFor(data.svl_level || 1),
    level: data.svl_level || 1
  }));

fs.writeFileSync('words-data.js', `window.WORDMARK_WORDS = ${JSON.stringify(words)};\n`);
console.log(`Generated ${words.length} words.`);
