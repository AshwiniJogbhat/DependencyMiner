var rangeSlider = function(){
  var slider = $('.range-slider'),
      range = $('.range-slider__range'),
      value = $('.range-slider__value');
    
  slider.each(function(){

    value.each(function(){
      var value = $(this).prev().attr('value');
      $(this).html(value);
    });

    range.on('input', function(){
      $(this).next(value).html(this.value);
    });
  });
};

var discoverModel = function(){
    var support = ($('#support')[0].value);
    var confidence = ($('#confidence')[0].value);
    var lift = ($('#lift')[0].value);

    alert(support, confidence, lift);
}


$(document).ready(function(){
  rangeSlider();
});


