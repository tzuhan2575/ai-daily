
(function(){
  var chips=document.querySelectorAll(".chip"),items=document.querySelectorAll("[data-cat]:not(.chip)");
  function sel(c){chips.forEach(function(b){b.classList.toggle("on",b.dataset.cat===c)});
    items.forEach(function(x){x.hidden=!!c&&x.dataset.cat!==c});}
  chips.forEach(function(b){b.addEventListener("click",function(){sel(b.dataset.cat)})});
  var uo=document.getElementById("useonly");
  function ap(){var c=(document.querySelector(".chip.on")||{dataset:{cat:""}}).dataset.cat,u=uo&&uo.checked;
    items.forEach(function(x){x.hidden=(!!c&&x.dataset.cat!==c)||(u&&x.dataset.impact!=="use")});}
  if(uo){chips.forEach(function(b){b.addEventListener("click",function(){setTimeout(ap,0)})});uo.addEventListener("change",ap)}
  document.querySelectorAll(".copy").forEach(function(b){b.addEventListener("click",function(){
    var t=document.getElementById(b.dataset.t).textContent;
    (navigator.clipboard?navigator.clipboard.writeText(t):Promise.reject()).then(function(){b.textContent="已複製 ✓"},function(){var r=document.createRange();r.selectNode(document.getElementById(b.dataset.t));getSelection().removeAllRanges();getSelection().addRange(r);b.textContent="已選取，請按複製"})})});
  document.querySelectorAll(".chk input").forEach(function(c){var k="aid-"+c.dataset.k;
    try{c.checked=localStorage.getItem(k)==="1"}catch(e){}
    c.addEventListener("change",function(){try{localStorage.setItem(k,c.checked?"1":"0")}catch(e){}})});
  var fab=document.getElementById("fab"),ls=document.getElementById("lesson");
  if(fab&&ls&&window.IntersectionObserver){new IntersectionObserver(function(en){fab.classList.toggle("gone",en[0].isIntersecting)},{threshold:.05}).observe(ls)}
  var q=document.getElementById("q");
  if(q)q.addEventListener("input",function(){var v=q.value.trim().toLowerCase();
    document.querySelectorAll(".term").forEach(function(t){t.hidden=!!v&&t.dataset.q.indexOf(v)<0})});
  if(location.hash){var t=document.querySelector(location.hash);if(t){var d=t.querySelector("details");if(d)d.open=true}}
})();
