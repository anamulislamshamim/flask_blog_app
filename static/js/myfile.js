document.getElementById('demo').innerHTML = "This was created with JavaScript!";

/* 
toast button
*/

const toast_div = document.getElementById('toast-div');
const toast_btn = document.getElementById("toast-button");


toast_btn.addEventListener('click', () => {
    toast_div.style = "display: none;"
})


