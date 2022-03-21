const toc = document.getElementById("toc");
if (toc) {
  const spy = new Gumshoe("#toc a", {
    nested: true,
    nestedClass: "active-parent"
  });

  toc.addEventListener("click", function(event) {
    if (event.target.tagName !== "A") return;
  });

  toc.addEventListener('gumshoeActivate', function (event) {
	  let link = event.detail.link;
    link.className = "usa-current"
  });

  toc.addEventListener('gumshoeDeactivate', function (event) {
	  let link = event.detail.link;
    link.className = null
  });
}
