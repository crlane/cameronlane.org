import '../stylesheets/main.styl';

var WordCloud = require('wordcloud');
var wc_container = document.getElementById('wordcloud');

// TODO: figure out how to get this stupid thing to inherit style from parent
if (wc_container !== null) {
  var url = '/blog/tag/.tags'
  fetch(url).then(function(response) {
        return response.json();
      }).then(function(tags) {

          var list_of_tags = []
          for (var i = 0; i < tags.length; i++) {
              var item = tags[i]
              list_of_tags.push([item.text, item.weight])
          }
          var options = {
            list: list_of_tags,
            gridSize: 18,
            fontFamily: "Palatino, Hoefler Text, Georgia, serif",
            weightFactor: 6,
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
