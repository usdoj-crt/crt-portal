var toc = document.getElementById("toc");
if (toc) {
  var spy = new Gumshoe("#toc a", {
    nested: true,
    nestedClass: "active-parent"
  });

  toc.addEventListener("click", function(event) {
    if (event.target.tagName !== "A") return;
  });
}
