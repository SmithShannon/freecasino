      function getUser(token){
        fetch('http://localhost:5000/user',{
            method:'POST',
            headers:{
                'Authorization':'bearer '+token
            }
        }).then(function(r){
            return r.json();
        }).then(function(response){
            document.getElementById('username').innerHTML = response['username'];
            document.getElementById('winnings').innerHTML = response['winnings'];
            document.getElementById('credits').innerHTML = response['credits'];
            console.log(response);
        }).catch(function(error){
            console.log(error);
        });
    }