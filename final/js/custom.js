$(window).load(function(){
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
        url: 'http://api.blockedonline.com/data?url_query=' + encodeURIComponent(query),
        type: 'GET',
        error: function () { callback();},
        success: function (res) { callback(res.result.slice(0, 10));}
      });
    }
  });
  var ctselect = $selectize1[0].selectize;
  //hard coded COUNTRY & URL options 
  //==========================================
  $(".top-countries-blocked > li span").click(function(){
    var countrycode=$(this).data('countrycode'); 
    ctselect.setValue(countrycode);
  });  

  if (hash) $('#bycountry .selectize-input > input').val(hash);//if hash in url set the selectize text  
});//document ready
/*
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
});*/
var Bullet_Boxes_v=[0, 1, 2];//add values in this array to create more boxes
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
      str_html += '<li><i class="fa-li fa fa-chevron-right"></i> <span style="font-family: bebas_neueregular; font-size: 21px ">' + news.news_title + 
      '</span><br>'+ news.description + '</li>';
    });
  }
  $("#"+box_name).html(str_html);
}

//Show or hide panel and also set Title of Panel
function ShowHide_Box(datas,box_name){
  if (datas.status == 'OK'){    
    $(".panel-"+box_name).show();
    $("li.sidenav-"+box_name).show();
    //console.log('going to show-> .panel-'+box_name);
  }else{
    $(".panel-"+box_name).hide();
    $("li.sidenav-"+box_name).hide();// hide sidebar button
    //console.log('going to hide-> .panel-'+box_name);    
  }
}

//Do Ajax Call. 
// country=from Selectize select box,opt=1,2..,box=donutgraph,stacked.. 
function DoAjax_Country(country,opt,box){
  $.get("http://api.blockedonline.com/data",{country: country,v:opt})
  .done(function(datas) {    
    if (datas.status == 'OK'){
      if (box=='donutgraph'){
        //draw donut graph
        drawDonut(datas.data);        
      }else if (box == 'stackedgraph'){
        //draw stacked graph
        drawStacked(datas.data);
      }else if (box =='generalinfo' || box == 'quicksummary'){
        var s='<tr>';
        jQuery.each(datas.bullets, function(index, item) {          
          s+='<td><img style="text-align: center;display: inline-block" src="'+item['logo']+'" class="img-responsive">'+
            '<div class="bottom-header">'+item['key'] +'</div>'+
            '<div class="bottom">'+item['value'];

          if (box=='quicksummary' && item['key']=='Number of reporters from the country') {
            s+= '<div class="link" style="margin-top: 5px;font-size:15px;text-decoration: none " data-toggle="modal" data-target="#myModal">Who are reporters?</div>'//alert('go it');
          }

          s += '</div></td>';
          if ((index+1)%3 == 0){
            s+='</tr><tr>';
          } 
        });
        $('#'+box+'-data').html(s);
      }else{
        box_name='bulletpoints'+opt;
        //$('#quicklinksflag').attr('src',datas.flag);        
        drawCountryBulletin(datas,box,box_name);//box=bullets,websites..
        //box=box_name;//bulletpoints1,bulletpoints2...etc
      }
    }
    ShowHide_Box(datas,box);
  });
}

function doCountrySearch(cty){
  $(".country_map_image").hide();//hide the map image
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
  DoAjax_Country(cty,1,'generalinfo');  //bulletpoints1
  DoAjax_Country(cty,2,'quicksummary');//bulletpoints2
  DoAjax_Country(cty,3,'websites');//bulletpoints3
  DoAjax_Country(cty,5,'news');//bulletpoints5

  if (hash) {//sel_cty.toLowerCase() 
    var country_name= hash;
  }else{
    var country_name=$('#bycountry .selectize-input > .item').text();
  }
  $('#country_nametext').text(country_name);

}

//Selectize Country picker --> on Change function
$("#select-country").on('change',function() {  
  //$("ul.affix-div > li").hide();//hide the side bar links
  var sel_cty=this.value;  
  //alert($(this).html());
  //console.log('selectize country change called'+cty);
  if (sel_cty != ""){
    doCountrySearch(sel_cty.toLowerCase());
  }
});


//=======================================
// ***********HASH TAG IN URL************
//=======================================
if(window.location.hash) {
  var hash = window.location.hash.substring(1); //Puts hash in variable, and removes the # character
  hash = hash.split(" ").map(function (i) {
    return i.substr(0, 1).toUpperCase() + i.substr(1)
  }).join(" ");
  $('#select-country > option').each(function(){
    if ($(this).text() == hash) {//sel_cty.toLowerCase()
      doCountrySearch(this.value);
      //$('#bycountry .selectize-input > input').val(hash);
      return false
    }
    //console.log(this.value);
  });
}

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
  $("<span style='color:#d9ccd0'>In this map green is for open, red is for blocked and orange is for partially blocked</span>" ).prependTo("#"+ename );
  
  //map.legend();
}

// Get and create bulletins for URL 
function DoAjax_Url(urlname,opt){
  var cname='urlbulletpoints'+opt;
  $.get("http://api.blockedonline.com/data",{url: urlname,v:opt})
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
      }else if (datas.v == '0'){//quicksummary
        var str_list='<table class="table-content" id ="quicksummary-data" style="margin-left: auto; margin-right: auto"><tr>';
        jQuery.each(datas.bullets, function(index, item) {          
          str_list+='<td><img style="text-align: center;display: inline-block" src="'+item['logo']+'" class="img-responsive">'+
            '<div class="bottom-header">'+item['key'] +'</div>'+
            '<div class="bottom">'+item['value'];
          if (item['logo']=='http://cdn.blockedonline.com/img/reporters-01.png') {
            str_list+= '<div class="link" style="margin-top: 5px;font-size:15px;text-decoration: none " data-toggle="modal" data-target="#myModal2">What does scanned mean?</div>'//alert('go it');
          } 
          str_list += '</div></td>';

          if ((index+1)%3 == 0){
            str_list+='</tr><tr>';
          }                  
        });
        //alert(str_list);
        $("#"+cname).html(str_list+"</tr></table>");

      } else if (datas.v == '2') {
        var str_list='<ul class="fa-ul sub-title">';
        datas.data.forEach(function(news) {
          str_list+='<li><i class="fa-li fa fa-chevron-right"></i><a href="' + 
          news.link + '" target="_blank" style="font-family: bebas_neueregular; font-size: 21px ">' +
           news.news_title +'</a><br>'+ news.description + '</li>';
          });
        $('#' + cname).html(str_list+'</ul>');       
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
    $('#website_nametext').text(url); 
    //console.log('change url but not empty');
    jQuery.each(Bullet_Boxes_v, function(index, item) {DoAjax_Url(url,item)});
  }//else console.log('change url but empty');
});

//hard coded URL options 
//==========================================
$(".top-sites-blocked > li span").click(function(){  
  var urlsel=$(this).prev().text(); 
  $('#website_nametext').text(urlsel); 
  $('#bywebsite > .url-list').hide();
  $('#bywebsite .selectize-input > input').val(urlsel);
  jQuery.each(Bullet_Boxes_v, function(index, item) {DoAjax_Url(urlsel,item)});
})
