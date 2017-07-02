import '../stylesheets/main.styl';

var WordCloud = require('wordcloud');
var wc_container = document.getElementById('wordcloud');

// TODO: figure out how to get this stupid thing to inherit style from parent
if (wc_container !== null) {
  var url = '/blog/tag/.tags'
  fetch(url).then(function(response) {
        return response.json();
      }).then(function(tags) {
          var options = {
            list: tags,
            gridSize: 18,
            weightFactor: 8,
            minFontSize: '6px',
            color: null,
            classes: 'tag',
            hover: window.drawBox,
            rotateRatio: 0,
            shuffle: false,
            click: function(record) {
              var tag = record[0]
              var count = record[1]
              window.location.href = encodeURIComponent(tag)
            }
          }
          WordCloud(wc_container, options);
      })
}

var hljs = require('highlight.js');
hljs.initHighlightingOnLoad();
