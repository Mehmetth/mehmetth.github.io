/* Video Compressor site: ?lang= language switcher (instant, no reload), menus, gallery.
   No dependencies and no network requests except this site's own language files. */
(function(){
  "use strict";
  var d=document, root=d.documentElement, T=window.VC, cache={}, cur="en", token=0;
  var KEY="vc-site-lang", ALIAS={"pt-br":"pt","pt-pt":"pt","in":"id","es-419":"es"};
  function store(k,v){try{return v===undefined?localStorage.getItem(k):localStorage.setItem(k,v)}catch(e){return null}}
  function known(c){c=(c||"").toLowerCase();c=ALIAS[c]||c;return c&&Object.prototype.hasOwnProperty.call(T.langs,c)?c:null}
  function fromBrowser(){
    var want=(navigator.languages&&navigator.languages.length?navigator.languages:[navigator.language||""]);
    for(var i=0;i<want.length;i++){
      var w=(want[i]||"").toLowerCase(), base=w.split("-")[0];
      if(known(w)) return known(w);
      if(known(base)) return known(base);
    }
    return null;
  }
  function wanted(){
    var q=new URLSearchParams(location.search).get("lang");
    return known(q)||known(store(KEY))||fromBrowser()||"en";
  }
  function meta(sel,attr,val){var el=d.querySelector(sel);if(el)el.setAttribute(attr,val)}
  function load(code){
    if(cache[code]) return Promise.resolve(cache[code]);
    return fetch("assets/lang/"+code+".json?v="+T.v).then(function(r){if(!r.ok)throw new Error(code+" "+r.status);return r.json()}).then(function(j){cache[code]=j;return j});
  }
  function withLang(href,code){
    if(!href||/^(mailto:|https?:|#)/.test(href)) return href;
    var h=href.indexOf("#"), hash=h<0?"":href.slice(h), path=h<0?href:href.slice(0,h);
    path=path.replace(/[?&]lang=[^&#]*/,"");
    if(code!=="en") path+=(path.indexOf("?")<0?"?":"&")+"lang="+code;
    return (path||"./")+hash;
  }
  function apply(code,frag){
    root.lang=frag.lang; root.dir=frag.dir; root.setAttribute("data-lang",code);
    d.title=frag.title;
    meta('meta[name="description"]',"content",frag.desc);
    meta('meta[property="og:title"]',"content",frag.ogTitle); meta('meta[name="twitter:title"]',"content",frag.ogTitle);
    meta('meta[property="og:description"]',"content",frag.ogDesc); meta('meta[name="twitter:description"]',"content",frag.ogDesc);
    meta('meta[property="og:locale"]',"content",T.langs[code].og);
    var url=T.base+T.page+(code==="en"?"":"?lang="+code);
    meta('link[rel="canonical"]',"href",url); meta('meta[property="og:url"]',"content",url);
    meta('meta[property="og:image"]',"content",T.base+"assets/og/"+code+".jpg"); meta('meta[name="twitter:image"]',"content",T.base+"assets/og/"+code+".jpg");
    [].forEach.call(d.querySelectorAll('script[type="application/ld+json"]'),function(s,i){if(frag.ld[i])s.textContent=JSON.stringify(frag.ld[i])});
    d.getElementById("app").innerHTML=frag.body;
    cur=code;
    decorate();
  }
  function onScroll(){var top=d.querySelector(".top");if(top)top.classList.toggle("scrolled",window.scrollY>4)}
  function decorate(){
    /* keep the chosen language on links between this site's pages */
    [].forEach.call(d.querySelectorAll("a[data-keep]"),function(a){a.setAttribute("href",withLang(a.getAttribute("href"),cur))});
    onScroll();
    var menus=[].slice.call(d.querySelectorAll("details.menu"));
    menus.forEach(function(m){m.addEventListener("toggle",function(){if(m.open)menus.forEach(function(o){if(o!==m)o.open=false})})});
    var track=d.querySelector(".gal-track");
    if(track){[].forEach.call(d.querySelectorAll(".gal-btn"),function(btn){btn.addEventListener("click",function(){
      var dirn=(btn.classList.contains("next")?1:-1)*(root.dir==="rtl"?-1:1);
      track.scrollBy({left:track.clientWidth*0.8*dirn,behavior:"smooth"})})})}
    if(location.hash){var t=d.getElementById(decodeURIComponent(location.hash.slice(1)));if(t)t.scrollIntoView()}
  }
  function go(code,push){
    var my=++token;
    if(code==="en"&&cur==="en"&&!push) return Promise.resolve();
    return load(code).then(function(j){
      if(my!==token) return;
      var frag=j[T.kind]; if(!frag) throw new Error("no "+T.kind+" in "+code);
      apply(code,frag);
      if(push){var u=new URL(location.href);if(code==="en")u.searchParams.delete("lang");else u.searchParams.set("lang",code);history.replaceState(null,"",u.pathname+u.search+u.hash)}
    }).catch(function(e){if(window.console)console.warn("Language load failed:",e.message)});
  }
  d.addEventListener("click",function(e){
    var a=e.target.closest&&e.target.closest("a[data-lang]");
    if(a){
      e.preventDefault(); var c=a.getAttribute("data-lang"); store(KEY,c);
      var m=a.closest("details");if(m)m.open=false;
      go(c,true); return;
    }
    [].forEach.call(d.querySelectorAll("details.menu"),function(m){if(m.open&&!m.contains(e.target))m.open=false});
  });
  d.addEventListener("keydown",function(e){if(e.key==="Escape")[].forEach.call(d.querySelectorAll("details.menu"),function(m){if(m.open){m.open=false;var s=m.querySelector("summary");if(s)s.focus()}})});
  window.addEventListener("scroll",onScroll,{passive:true});
  var first=wanted(); decorate();
  if(first!=="en") go(first,false);
  window.addEventListener("popstate",function(){go(wanted(),false)});
})();
