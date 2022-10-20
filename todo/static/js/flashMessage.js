window.onload = () => {
    const flash = document.getElementsByClassName("flash")
    if(typeof flash !== 'undefined'){
        move()        
    }

    const move = () =>{
            let id = null;
            let pos = 0;
            clearInterval(id);
            id = setInterval(frame, 5);
            function frame() {
              if (pos == 350) {
                clearInterval(id);
              } else {
                pos++;
                elem.style.top = pos + 'px';
                elem.style.left = pos + 'px';
              }
            } 
        }
}