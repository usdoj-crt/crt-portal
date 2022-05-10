import './components/redirect_modal';

// set up "continue" button to immediately redirect
export const print = () => {
  var print_el = document.getElementById('print_button');
  print_el.onclick = function() {
    window.print();
  };
};
