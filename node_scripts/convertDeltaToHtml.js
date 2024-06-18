const { QuillDeltaToHtmlConverter } = require('quill-delta-to-html');

const delta = JSON.parse(process.argv[2]); // Leer el delta de los argumentos de línea de comandos
const converter = new QuillDeltaToHtmlConverter(delta.ops, {});
const html = converter.convert();

console.log(html); // Imprimir el HTML resultante
