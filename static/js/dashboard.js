function updateClock(){

const now=new Date();

document.getElementById("date").innerHTML=
now.toLocaleDateString();

document.getElementById("time").innerHTML=
now.toLocaleTimeString();

}

setInterval(updateClock,1000);

updateClock();