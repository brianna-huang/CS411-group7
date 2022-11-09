const query = document.getElementById('search');
console.log(query);

const options = {
	method: 'POST',
	headers: {
		'content-type': 'text/plain',
        "X-RapidAPI-Key": "a4e2fc244bmshd6877fd389df594p162eb8jsn5b123867a7d7",
		'X-RapidAPI-Host': 'mycookbook-io1.p.rapidapi.com'
	},
	body: query,
};

fetch('https://mycookbook-io1.p.rapidapi.com/recipes/rapidapi', options)
	.then(response => response.json())
	.then(response => console.log(response))
	.catch(err => console.error(err));



const requestURL = "https://mycookbook-io1.p.rapidapi.com/recipes/rapidapi";
fetch(requestURL).then(response =>response.JSON().then(data => {}));