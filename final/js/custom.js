$(window).load(function(){
var Bullet_Boxes_v=[0, 1, 2];//add values in this array to create more boxes
//Selectize select boxes
var $selectize1=$('#select-country').selectize();
var $selectize2=$('#select-url').selectize({
  valueField: 'url',
  labelField: 'url',
  searchField: 'url',
  create: false,
  render: {
    option: function (item, escape) {
      return '<div><span class="url">' + escape(item.url) + '</span></div>';
    }
  },
  load: function (query, callback) {
    if (!query.length) return callback();
    $.ajax({
      url: 'http://kiarash.me/blocked/data?url_query=' + encodeURIComponent(query),
      type: 'GET',
      error: function () { callback();},
      success: function (res) { callback(res.result.slice(0, 10));}
    });
  }
});
var control1 = $selectize1[0].selectize;
var control2 = $selectize2[0].selectize;

// Show Hide, Selectize select box based on the radio buttion clicks
$('.btn-group input[type=radio]').change(function () { 
  if (this.value == 'country'){
    $('#div-url').hide();//Hide the Url selectize box
    alert('contry');
    $('.bulletpoints-container').empty()
    control1.clear();
  }else{
    $("#div-country").hide();//Hide the country selectize box
    $(".country-panels").hide();//complete country panels
    control2.clear(); 
  }
  $('#div-' + this.value).show();
});

//Donut graph
function drawDonut(data){
	nv.addGraph(function () {
	  var chart = nv.models.pieChart().x(function (d){
	    return d.label
	  }).y(function (d) {
	    return d.value
	  })
	  .showLabels(true) //Display pie labels
	  .labelThreshold(.05) //Configure the minimum slice size for labels to show up
	  .labelType("percent") //what type of data to show in the label("key", "value" or "percent")
	  .donut(true) //Turn on Donut mode.
	  .donutRatio(0.35) //Configure how big you want the donut hole size to be.
	  ;
	  d3.select("div#donutgraph svg").datum(data).transition().duration(350).call(chart);
	  return chart;
	});
}

//Horizontal Graph
function drawStacked(data){
  nv.addGraph(function() {
    var chart = nv.models.multiBarHorizontalChart()
        .x(function(d) { return d.x })
        .y(function(d) { return d.y })
        .margin({top: 30, right: 20, bottom: 50, left: 175})
        .showValues(true)           //Show bar value next to each bar.
        .tooltips(true)             //Show tooltips on hover.
        .transitionDuration(350)
        .stacked(true)
        .showControls(true); //Allow user to switch between "Grouped" and "Stacked" mode.
    chart.yAxis.tickFormat(d3.format(',f')); //(d3.format(',.2f'));
    chart.valueFormat(d3.format('d'));
    d3.select('#stackedgraph svg').datum(data).call(chart);
    nv.utils.windowResize(chart.update);
    return chart;
  });
}

// Create Country Bulletins
function drawCountryBulletin(data,box,box_name){
  var str_html='';  
  if (box=="websites"){
    jQuery.each(data.websites, function(index, item) {
      str_html+= "<li>"+item+"</li>";
    });
  } else if (box == 'news') {
    data.data.forEach(function(news) {
      str_html += '<li class="list-group-item"><strong><a href="' + news.link + '" target="_blank">' + news.news_title + 
      '</a></strong><br>'+ news.description + '</li>';
    });
  }
  $("#"+box_name).html(str_html);
}

//Show or hide panel and also set Title of Panel
function ShowHide_Box(datas,box_name){
  if (datas.status == 'OK'){
    //$("#for_"+box_name).text(datas.title);
    $(".panel-"+box_name).show();
  }else{
    $(".panel-"+box_name).hide();
  }
}

//Do Ajax Call. 
// country=from Selectize select box,opt=1,2..,box=donutgraph,stacked.. 
function DoAjax_Country(country,opt,box){
  $.get("http://kiarash.me/blocked/data",{country: country,v:opt})
  .done(function(datas) {    
    if (datas.status == 'OK'){
      if (box=='donutgraph'){
        //draw donut graph
        drawDonut(datas.data);        
      }else if (box == 'stackedgraph'){
        //draw stacked graph
        drawStacked(datas.data);
      }else if (box == 'quicksummary'){
        jQuery.each(datas.bullets, function(index, item) {
          $('#quick-summary-data-'+index).text(item['value']);            
        });
      }else if (box == 'generalinfo'){
        jQuery.each(datas.bullets, function(index, item) {          
          $('#generalinfo-data-'+index).text(item['value']);          
        });
      }else{
        box_name='bulletpoints'+opt;
        //$('#quicklinksflag').attr('src',datas.flag);        
        drawCountryBulletin(datas,box,box_name);//box=bullets,websites..
        box=box_name;//bulletpoints1,bulletpoints2...etc
      }
    }
    ShowHide_Box(datas,box);
  });
}

//Selectize Country picker --> on Change function
$("#select-country").on('change',function() {
  cty=this.value;
  cty=cty.toLowerCase();
  //console.log('selectize country change called'+cty);
  if (cty != ""){
    // BUG Fix:  
    $('.panel-donutgraph').hide();
    $('.panel-stackedgraph').hide();
    $('.panel-news').hide();
    for (var i=1; i < 4; i++){
      var bx_name = '.panel-bulletpoints' + i;
      $(bx_name).hide();
    } 
    // End of BUG Fix
    $(".country-panels").show();
  	//first ajax for donut
    DoAjax_Country(cty,4,"donutgraph");
    //second ajax for stacked graph
    DoAjax_Country(cty,0,"stackedgraph");
    //ajax for bulletpoints
    DoAjax_Country(cty,1,'generalinfo');  
    DoAjax_Country(cty,2,'quicksummary');
    DoAjax_Country(cty,3,'websites');
    DoAjax_Country(cty,5,'news');
  }
});

//#######################################
//*************** URL *******************
//#######################################
//DataMaps for url
function createMap(ename,d){
  $("#"+ename).empty();
  var map = new Datamap({
    element: document.getElementById(ename),
    fills: {
        defaultFill: '#575757',
        highlight: '#787878',
        open: '#228b22',
        partially_blocked: '#ff8c00',
        blocked: '#8b0000'
    },
    data: d,
    geographyConfig: {
      highlightOnHover: false/*,
      popupTemplate: function(geo, data) {
        if ( !data ) return;
        return ['<div class="hoverinfo"><strong>',
            'Number of things in ' + geo.properties.name,
            ': ' + data.number,'</strong></div>'].join('');
      }*/
    }
  });
  //map.legend();
}

// Get and create bulletins for URL 
function DoAjax_Url(urlname,opt){
  var cname='urlbulletpoints'+opt;
  $.get("http://kiarash.me/blocked/data",{url: urlname,v:opt})
  .done(function(datas) {
    if (datas.status == 'OK'){      
      var html_panel_bulletpoints=''+
      '<div class="portlet">'+
        '<div class="box ucase">'+
          '<p class="caption-title">'+datas.title+'<span class="collapse-icon"></span></p>'+
          '<div class="clearfix"></div>'+
        '</div>'+
        '<div class="portlet-body" id="'+cname+'"></div>'+
      '</div>';

      
      $('#bulletpoints' + opt + '-container').empty().append(html_panel_bulletpoints).css('opacity', 1);
      if (datas.v == '1'){
        createMap(cname,datas.data);
      }else if (datas.v == '0'){
        var str_list='<ul>'; 
        jQuery.each(datas.bullets, function(index, item) {
          str_list+= "<li>"+item+"</li>"      
        });
        $("#"+cname).html(str_list+"</ul>");
      } else if (datas.v == '2') {
        datas.data.forEach(function(news) {
          $('<ul class="list-group">' +
            '<li class="list-group-item"><a href="' + news.link + '" target="_blank">' + news.news_title + '</a></li>' +
            '<li class="list-group-item">' + news.description + '</li>' +
            '</ul>').appendTo($('#' + cname));
        });
      }
    }
  });
}

//Selectize URL picker --> on Change function
$("#select-url").on('change',function() {   
  $('.bulletpoints-container').css('opacity', 0);
  url=this.value;
  url=url.toLowerCase();
  if (url != ""){
    //console.log('change url but not empty');
    jQuery.each(Bullet_Boxes_v, function(index, item) {DoAjax_Url(url,item)});
  }//else console.log('change url but empty');
});
});//document ready