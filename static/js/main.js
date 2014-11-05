$(document).ready(function () {

	// this allows google autocomplete to display

	$(".typeahead").typeahead({
		minLength: 2,
		highlight: true,
	},
	{
		source: getSuggestions,
		displayKey: 'description',
	});

	// this creates event listener for location form

	$("#location").submit(searchForSpot);
});

// function for autocomplete from google autocomplete

function getSuggestions(query, cb) {
	var service = new google.maps.places.AutocompleteService();
	service.getQueryPredictions({ input: query }, function(predictions, status) {
		if (status != google.maps.places.PlacesServiceStatus.OK) {
			alert(status);
			return;
		}
		console.log(predictions);
		return cb(predictions);

	});
}

