      // Functions to lookup by name or address and show list of landlords

    function showLandlords(results) {

        console.log(results);

        if (results == "found-no-landlords") {
            $('#results-message').empty();
            $('#results-message').prepend('<p>Could not find any landlords matching your search.</p>');

        }
            
        else if (results == "found-no-addresses") {
            $('#results-message').empty();
            $('#results-message').prepend('<p>Could not find any addresses matching your search.</p>');
    
        }

        else if(results == "found-address-no-reviews") {
            $('#results-message').empty();
            $('#results-message').prepend('<p>No reviews exist for this address yet.</p>');
        }
        
        else if(results == "address-not-valid") {
            $('#results-message').empty();
            $('#results-message').prepend('<p>Address is not valid.</p>');
        }
        // Otherwise display each landlord as a link to the page for that landlord
        else {
            $('#results-message').empty();
            for (var landlordID in results) {
                if (results.hasOwnProperty(landlordID)) {
                    $('#results-message').append("<p>Landlord: <a href='/landlord/"+ landlordID + "'> " + results[landlordID]['fname'] + " " + results[landlordID]['lname'] + "</a> </p>");
                }
            }
        }
    }


    function lookupByName(evt) {
        evt.preventDefault();
        var name = $('#search-by-name').serialize();

        $.get('/lookup-by-name.json', name, showLandlords);
        console.log("Finished sending name");
        $('#modalResultsWindow').modal('show');
    }


    $("#search-by-name").on("submit", lookupByName);

    // // When user finishes entering landlord last name in modal review form, 
    // // check if landlord in database
    // $('#lname-field-review').on('blur', function() {
    //     var fname = $('#fname-field-review').val();
    //     var lname = $('#lname-field-review').val();
    //     var name = {fname: fname, lname: lname};
    //     console.log(name);

    //   $.get('/lookup-by-name.json', name, displayResultsMessage);
    // });

    function displayResultsMessage(results) {
            var fname = $('#fname-field-review').val();
            var lname = $('#lname-field-review').val();
            var msg = '';

            if (results == "found-no-landlords") {
                console.log('found no landlords');
                msg = '<div class="alert alert-danger">Found no landlords matching ' + fname + ' ' + lname + '.' +
                'Would you like to add ' + fname + ' ' + lname + 'as a landlord?  ' +
                '<button class="btn btn-default" id="add-landlord-btn" data-fname="' + fname + '" data-lname="' + lname +
                '">Yes</button> <button class="btn btn-default" id="dont-add-landlord-btn">No</button>';
                $('#landlord-verification-results').html(msg);
            }
            else if (results.landlords) {
                msg = '<div class="alert alert-info"> Found no landlords named ' + fname + ' ' + lname + '. Did you mean one of the following? (See dropdown) <br>';
                console.log(results);

                msg += '<div class="dropdown">' +
                  '<button class="btn btn-default dropdown-toggle" type="button" id="dropdownMenuSelectLandlord" data-toggle="dropdown" aria-haspopup="true" aria-expanded="true">' +
                    'Select a similar name' +
                    '<span class="caret"></span>' +
                  ' </button>' +
                  '<ul class="dropdown-menu" aria-labelledby="dropdownMenuSelectLandlord">';

                for (var landlord in results.landlords) {
                    var thisFname = results.landlords[landlord].fname;
                    var thisLname = results.landlords[landlord].lname;
                    
                    msg += '<li><a href="#" class="select-landlord" data-fname="' + thisFname +
                    '" data-lname="' + thisLname + '">' + thisFname + ' ' + thisLname +
                    '</a></li>';
                }

                msg += '</ul></div>Or would you like to add ' + fname + ' ' + lname + ' as a landlord?  ' +
                '<button type="button" class="btn btn-default" id="add-landlord-btn" data-fname="' + fname + '" data-lname="' + lname +
                '">Yes</button> <button type="button" class="btn btn-default" id="dont-add-landlord-btn">No</button></div>';
                $('#landlord-verification-results').html(msg);
            }
            else if (results=='address-not-valid') {
                msg = '<div class="alert alert-danger">Could not find the address as entered. Please try again.</div>';
            }

            else if (results['success']) {
                alert('Success!');
                console.log(results);
                console.log(results['success']);
                $('#modalRatingForm').modal('hide');
                $.get('/get_recent_reviews', displayReviews);
                // var url = '/landlord/'+ results['success'];
                
            }
            
            
            
    }

    // When user selects a landlord, populate the review form with that landlord's info
    // Use Event delegation to bind click event to landlord links that have not been created yet
    $(document).on('click', 'a.select-landlord', function(evt) {
        console.log('selected landlord');
        fname = $(this).attr('data-fname');
        lname = $(this).attr('data-lname');
        // console.log(fname);
        // console.log(lname);
        $('#fname-field-review').val(fname);
        $('#lname-field-review').val(lname);
        $('#landlord-verification-results').html('');

    });

    // When a user clicks on the add landlord button, add the landlord to the database
    // Use Event delegation to bind click event to button that has not been created yet
    $(document).on('click', '#add-landlord-btn', function(e) {
        e.preventDefault();
        console.log('clicked add landlord button');
       $.post('/add-new-landlord.json', {'fname-add': $(this).attr('data-fname'), 'lname-add': $(this).attr('data-lname')}, function(res){
            console.log('finished add-new-landlord request.');
            if (res == "added-landlord") {
                console.log('added-landlord');
                $('#landlord-verification-results').html('<div class="alert alert-success">Successfully added!</div>');
            }
            else {alert('something went wrong');}
       });

    });

    $(document).on('click', '#dont-add-landlord-btn', function(evt) {
        console.log('clicked dont add landlord button');
        var fname = $('#fname-field-review').val();
        var lname = $('#lname-field-review').val();
        $('#landlord-verification-results').html('<div class="alert alert-danger">Found no landlords matching' +
            fname + ' ' + lname + '. Please try again with a different name.</div>');
    } );


    function autoCompleteAddress() {
        var street = $('#street-field').val();
        var city = $('#city-field').val();
        var zipcode = '';
        var state = '';
        var country = '';

        // Set up geocoder for mapbox geocoding queries
        var geocoder = L.mapbox.geocoder('mapbox.places');

        // geocoder.query('683 Sutter St', {proximity: (37.773972, -122.431297)}, function(results) { console.log(results);});
        geocoder.query({query: street, proximity: L.latLng(37.773972, -122.431297)}, function(err, results) {
            console.log(results);
            var features = results.results.features;
            console.log(features);
            var closest_result = '';
            var cityRegex = new RegExp(city);

            // If the request returned any features
            if (features) {
                // Find the feature that matches 
                for (var feature in features) {
                    if (features[feature].place_name.match(cityRegex)) {
                        console.log('matches');
                        closest_result = features[feature];
                        console.log(closest_result);
                        break;
                    }
                }
                if (closest_result) {
                    for (var item in closest_result.context) {
                        if (closest_result.context[item]['id'].match(/postcode/)) {
                            zipcode = closest_result.context[item]['text'];
                        }
                        else if (closest_result.context[item]['id'].match(/region/)) {
                            state = closest_result.context[item]['text'];
                        }
                        else if (closest_result.context[item]['id'].match(/country/)) {
                            country = closest_result.context[item]['text'];
                        }
                    }

                    $('#state-field').val(state);
                    $('#zipcode-field').val(zipcode);
                    $('#country-field').val(country);

                }
  
            }
        });

    }



    $('#city-field').on('change', autoCompleteAddress);

    // Function that takes in rating and returns string of html stars
    function generateStarRating(rating) {
        var roundedRating = Math.round(rating);
        var outputHTML = "";
                for (var j = 1; j<=5; j++) {
                if (roundedRating >= j) {
                    outputHTML += "<i class='glyphicon glyphicon-star'></i>";
                }
                else {
                    outputHTML += "<i class='glyphicon glyphicon-star-empty'></i>";
                }
                
            }
        return outputHTML;
    }

    function displayReviews(results) {
        var resultSidebar = $('#results-sidebar');

        resultSidebar.html('');
        results = results['results'];
        for (var review in results) {

            var reviewHTML = "<b>Review of <a href='/landlord/" + results[review].landlord_id +
                             "'>" + results[review].landlord_fname +
                             " " + results[review].landlord_lname + "</a></b><br>" +
                             "<span class='review-label'>User: </span>" + results[review].user_id + "<br>" +
                             "<span class='review-label'>Address: </span>" + results[review].address_street + "<br>" +
                             "<span class='review-label'>Created at: </span>" + results[review].created_at + "<br>" +
                             "<span class='rating'><span class='review-label'>Overall rating: </span>" + generateStarRating(results[review].rating_overall);
                            
             reviewHTML +=  "<br></span>" +
                             "<span class='review-label hidden'>Maintenance and Repairs: <br>" + generateStarRating(results[review].rating1) + "<br></span>" +
                             "<span class='review-label hidden'>Responsiveness: <br>" + generateStarRating(results[review].rating2) + "<br></span>" +
                             "<span class='review-label hidden'>Pest Management: <br>" + generateStarRating(results[review].rating3) + "<br></span>" +
                             "<span class='review-label hidden'>Respect in Communications: <br>" + generateStarRating(results[review].rating4) + "<br></span>" +
                             "<span class='review-label hidden'>Fairness in Rent Increases: <br>" + generateStarRating(results[review].rating5) + "<br></span>" +
                             "<p> <span class='comment'><span class='review-label'>Comment: </span>" + results[review].comment + "</span></br><hr>";

            resultSidebar.append(reviewHTML);
        }
    }

    
    $('#modal-review-form').on('submit', function (evt) {
      evt.preventDefault();

          var inputs = $('#modal-review-form').serialize();
          $.post('/process-rating2.json', inputs, displayResultsMessage);
    });

    // Clear out auto-populated landlord info if user changes landlord name in form
    $('#hidden-landlord-id').val('');
