if (document.getElementById("id_1-violation_summary")) {
  document.getElementById("id_1-violation_summary").onkeyup = function () {
      document.getElementById("display_count").innerHTML =  (500 - this.value.match(/\S+/g).length);
      var words = this.value.match(/\S+/g).length;
      if (words > 500) {
        // Split the string on first 500 words and rejoin on spaces
        var trimmed = this.value.split(/\s+/, 500).join(" ");
        // replace the input with trimmed text
        document.getElementById("id_1-violation_summary").value = trimmed;
        document.getElementById("count_message").innerHTML = ' word limit reached';
        document.getElementById("display_count").innerHTML = '500';
      } else {
        document.getElementById("display_count").innerHTML =  (500 - this.value.match(/\S+/g).length);
        document.getElementById("count_message").innerHTML = ' word(s) remaining'
      }
  };
};
