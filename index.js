var Tesseract = require('tesseract.js');

//var langPath = 'eng.traineddata';
var imageURL = 'images/eng_bw.png';

/*var tesseractPromise = Tesseract.create({
  langPath : langPath
});*/

Tesseract
.recognize(imageURL, 'eng')
.progress(function (p) {
  console.log(p);
})
.then(function (result) {
  console.log(result);
});
